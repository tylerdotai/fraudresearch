"""Bounded immutable acquisitions and string-preserving Parquet datasets, separate from case SQLite."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import stat
import tempfile
import threading
import time
import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from typing import IO, Any

import duckdb
import httpx

from . import digest, now
from .local_web import bounded_get
from .settings import scratch_dir


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('x') as f:
        json.dump(value, f, indent=2)


def receipt(root: Path, kind: str, sid: str) -> dict[str, Any]:
    if not re.fullmatch('[0-9a-f]{24}', sid):
        raise ValueError('Invalid content identifier')
    path = root / kind / (sid + '.json')
    value: dict[str, Any] = json.loads(path.read_text())
    if value.get('id') != sid:
        raise ValueError('Receipt identity mismatch')
    return value


def raw_verified(root: Path, sid: str) -> dict[str, Any]:
    r = receipt(root, 'acquisitions', sid)
    expected = (root / 'originals' / (sid + '.source')).resolve()
    if Path(r['path']).resolve() != expected or file_hash(expected) != r['sha256']:
        raise ValueError('Original checksum/path mismatch')
    return r


def acquire(root: Path, url: str, max_bytes: int, local: Path | None = None) -> dict[str, Any]:
    if not 0 < max_bytes <= 5_000_000_000:
        raise ValueError('max-bytes must be 1..5000000000')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    attempt: dict[str, Any] = {'at': now(), 'url': url, 'state': 'attempted', 'max_bytes': max_bytes}
    scratch = Path(tempfile.mkdtemp(prefix='fraudlab-acquire-', dir=scratch_dir()))
    partial = scratch / 'original.partial'
    try:
        if shutil.disk_usage(root).free < max_bytes + 100_000_000:
            raise ValueError('Insufficient free disk for explicit acquisition budget')
        if local is None:
            meta = bounded_get(url, partial, max_bytes, 180)
        else:
            size = local.stat().st_size
            if not 0 < size <= max_bytes:
                raise ValueError('Local original exceeds byte budget or is empty')
            with local.open('rb') as src, partial.open('xb') as dst:
                copied = 0
                while chunk := src.read(65536):
                    copied += len(chunk)
                    if copied > max_bytes:
                        raise ValueError('Local source changed/exceeded byte budget during copy')
                    dst.write(chunk)
            meta = {'requested_url': url, 'final_url': url, 'retrieved_at': now(), 'bytes': copied,
                    'sha256': file_hash(partial), 'method': 'authorized local original; provenance supplied by operator'}
        sid = digest((url + '\0' + meta['sha256']).encode())[:24]
        path = root / 'originals' / (sid + '.source')
        rpath = root / 'acquisitions' / (sid + '.json')
        if rpath.exists():
            return raw_verified(root, sid)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with partial.open('rb') as src, path.open('xb') as dst:
            shutil.copyfileobj(src, dst, 65536)
        value = {**meta, 'id': sid, 'path': str(path.resolve()), 'state': 'acquired',
                 'budget': {'max_bytes': max_bytes, 'seconds': 180},
                 'interpretation': 'Original bytes acquired; no schema or substantive claim verified'}
        save(rpath, value)
        attempt.update(state='acquired', id=sid)
        return value
    except (ValueError, OSError, httpx.HTTPError) as exc:
        attempt.update(state='failed', error=str(exc), partial_path=str(partial))
        raise
    finally:
        save(root / 'attempts' / (str(time.time_ns()) + '.json'), attempt)


def quote(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


@contextmanager
def connection(paths: list[Path]) -> Iterator[duckdb.DuckDBPyConnection]:
    db = duckdb.connect(config={'memory_limit': '512MB', 'threads': 2,
                               'autoinstall_known_extensions': False, 'autoload_known_extensions': False,
                               'max_temp_directory_size': '1GB',
                               'temp_directory': str(scratch_dir() / 'fraudlab-duckdb-spill')})
    db.execute('SET allowed_paths = ?', [[str(p.resolve()) for p in paths]])
    db.execute('SET enable_external_access=false')
    deadline = threading.Timer(120, db.interrupt)
    deadline.daemon = True
    deadline.start()
    try:
        yield db
    finally:
        deadline.cancel()
        db.close()


def convert(root: Path, sid: str, member: str | None, required: list[str], encoding: str,
            max_rows: int, max_expanded: int) -> dict[str, Any]:
    raw = raw_verified(root, sid)
    if not 0 < max_rows <= 50_000_000 or not 0 < max_expanded <= 10_000_000_000:
        raise ValueError('Row/expansion budget invalid')
    if encoding not in ('utf-8-sig', 'utf-8', 'cp1252', 'latin-1'):
        raise ValueError('Encoding must be explicitly supported; no silent replacement')
    scratch = Path(tempfile.mkdtemp(prefix='fraudlab-convert-', dir=scratch_dir()))
    if shutil.disk_usage(scratch).free < max_expanded * 3 + 100_000_000:
        raise ValueError('Insufficient scratch disk for conversion budget')
    normalized = scratch / 'normalized.csv'
    parquet = scratch / 'dataset.parquet'
    started = time.monotonic()
    attempt: dict[str, Any] = {'at': now(), 'raw_id': sid, 'member': member, 'state': 'converting'}
    archive = None
    stream: IO[bytes] | None = None
    try:
        original = Path(raw['path'])
        if zipfile.is_zipfile(original):
            archive = zipfile.ZipFile(original)
            infos = archive.infolist()
            names = [i.filename for i in infos]
            if len(infos) > 100 or len(names) != len(set(names)):
                raise ValueError('ZIP duplicate names or member-count limit')
            for info in infos:
                p = PurePosixPath(info.filename)
                if p.is_absolute() or '..' in p.parts or '\\' in info.filename or ':' in info.filename:
                    raise ValueError('Unsafe ZIP member path')
                if stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1:
                    raise ValueError('ZIP symlink or encrypted member rejected')
            if sum(i.file_size for i in infos) > max_expanded:
                raise ValueError('ZIP expanded-byte budget exceeded')
            if member not in names or not str(member).lower().endswith('.csv'):
                raise ValueError('Select an exact CSV member from the archive')
            stream = archive.open(str(member))
            member_bytes = archive.getinfo(str(member)).file_size
        else:
            if member:
                raise ValueError('Member specified for a non-ZIP original')
            member_bytes = original.stat().st_size
            if member_bytes > max_expanded:
                raise ValueError('Expanded-byte budget exceeded')
            stream = original.open('rb')
        # Decompressed bytes are hashed during a bounded pass; text decode remains strict.
        member_copy = scratch / 'member.csv'
        h = hashlib.sha256()
        actual_bytes = 0
        with member_copy.open('xb') as dst:
            while chunk := stream.read(65536):
                actual_bytes += len(chunk)
                if actual_bytes > max_expanded or time.monotonic() - started > 180:
                    raise ValueError('Expansion byte/time budget exceeded')
                h.update(chunk)
                dst.write(chunk)
        if actual_bytes != member_bytes:
            raise ValueError('Member length mismatch')
        csv.field_size_limit(1_000_000)
        with member_copy.open(encoding=encoding, newline='') as source, normalized.open('x', newline='') as target:
            reader = csv.reader(source, strict=True)
            fields = next(reader, [])
            if not fields or any(not f for f in fields) or len({f.casefold() for f in fields}) != len(fields):
                raise ValueError('Missing or duplicated CSV headers')
            if '__source_row' in [f.casefold() for f in fields] or any(f not in fields for f in required):
                raise ValueError('Reserved or required column missing')
            writer = csv.writer(target)
            writer.writerow(['__source_row', *fields])
            count = 0
            for count, row in enumerate(reader, 1):
                if len(row) != len(fields):
                    raise ValueError('Malformed CSV record at row ' + str(count))
                if count > max_rows or time.monotonic() - started > 180:
                    raise ValueError('Row/time budget exceeded')
                writer.writerow([count, *row])
            if not count:
                raise ValueError('Empty CSV dataset')
        dataset_id = digest(json.dumps([sid, member, encoding, 'csv-strings-v1', duckdb.__version__]).encode())[:24]
        if (root / 'datasets' / (dataset_id + '.json')).exists():
            return dataset_verified(root, dataset_id)
        with connection([normalized, parquet]) as db:
            columns = ','.join(quote(f) for f in fields)
            destination_sql = "'" + str(parquet).replace("'", "''") + "'"
            not_null = '[' + ','.join("'" + f.replace("'", "''") + "'"
                                      for f in ['__source_row', *fields]) + ']'
            db.execute(f'''COPY (SELECT CAST(__source_row AS BIGINT) AS __source_row,{columns}
                FROM read_csv(?, header=true, all_varchar=true, force_not_null={not_null}, strict_mode=true))
                TO {destination_sql} (FORMAT PARQUET, COMPRESSION ZSTD)''', [str(normalized)])
            written = db.execute('SELECT count(*) FROM read_parquet(?)', [str(parquet)]).fetchone()
            schema = db.execute('SELECT * FROM read_parquet(?) LIMIT 0', [str(parquet)]).description
            if written is None or written[0] != count or [x[0] for x in schema] != ['__source_row', *fields]:
                raise ValueError('Parquet row/schema reconciliation failed')
        destination = root / 'parquet' / (dataset_id + '.parquet')
        destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with parquet.open('rb') as src, destination.open('xb') as dst:
            shutil.copyfileobj(src, dst, 65536)
        value = {'id': dataset_id, 'raw_id': sid, 'state': 'schema-verified', 'at': now(),
                 'member': member, 'member_sha256': h.hexdigest(), 'member_bytes': actual_bytes,
                 'encoding': encoding, 'rows': count, 'columns': ['__source_row', *fields],
                 'required_columns': required, 'parquet_path': str(destination.resolve()),
                 'parquet_sha256': file_hash(destination), 'duckdb': duckdb.__version__,
                 'method': 'strict CSV structure; all source columns strings; one-based parsed-record ordinal',
                 'budgets': {'max_rows': max_rows, 'max_expanded_bytes': max_expanded,
                             'memory': '512MB', 'csv_seconds': 180, 'sql_seconds': 120, 'spill': '1GB'},
                 'notice': 'Schema/count validation only; not identity, payment or misconduct verification'}
        save(root / 'datasets' / (dataset_id + '.json'), value)
        attempt.update(state='schema-verified', dataset_id=dataset_id)
        return value
    except (ValueError, OSError, UnicodeError, csv.Error, zipfile.BadZipFile, duckdb.Error) as exc:
        attempt.update(state='failed', error=str(exc))
        raise ValueError(str(exc)) from exc
    finally:
        if stream:
            stream.close()
        if archive:
            archive.close()
        save(root / 'attempts' / (str(time.time_ns()) + '.json'), attempt)


def dataset_verified(root: Path, sid: str) -> dict[str, Any]:
    value = receipt(root, 'datasets', sid)
    raw_verified(root, value['raw_id'])
    path = (root / 'parquet' / (sid + '.parquet')).resolve()
    if Path(value['parquet_path']).resolve() != path or file_hash(path) != value['parquet_sha256']:
        raise ValueError('Parquet checksum/path mismatch')
    return value


def verify(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise ValueError('Bulk store does not exist; no initialization performed')
    errors = []
    counts = {}
    for kind, validator in [('acquisitions', raw_verified), ('datasets', dataset_verified)]:
        paths = sorted((root / kind).glob('*.json'))
        counts[kind] = len(paths)
        for path in paths:
            try:
                validator(root, path.stem)
            except (ValueError, OSError) as exc:
                errors.append({'id': path.stem, 'error': str(exc)})
    return {'passed': not errors, **counts, 'errors': errors, 'scope': 'bulk originals and Parquet only'}


def query(root: Path, sid: str, column: str | None, equals: str | None, limit: int) -> dict[str, Any]:
    if not 1 <= limit <= 1000 or (column is None) != (equals is None):
        raise ValueError('limit must be 1..1000; column and equals must be paired')
    r = dataset_verified(root, sid)
    if column and column not in r['columns']:
        raise ValueError('Unknown filter column')
    path = Path(r['parquet_path'])
    where = ' WHERE ' + quote(column) + ' = ?' if column else ''
    params = [str(path)] + ([equals] if column else [])
    with connection([path]) as db:
        counted = db.execute('SELECT count(*) FROM read_parquet(?)' + where, params).fetchone()
        if counted is None:
            raise ValueError('Missing count result')
        total = counted[0]
        cursor = db.execute('SELECT * FROM read_parquet(?)' + where + ' ORDER BY __source_row LIMIT ?',
                            [*params, limit])
        columns = [c[0] for c in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return {'dataset_id': sid, 'total_matching': total, 'rows': rows, 'truncated': total > limit,
            'method': 'exact string equality; verified Parquet; no store writes or arbitrary SQL',
            'coverage': 'selected dataset only; rows not unique providers or fraud findings'}


def join(root: Path, left: str, right: str, left_key: str, right_key: str, limit: int) -> dict[str, Any]:
    if not 1 <= limit <= 1000:
        raise ValueError('Join limit must be 1..1000')
    l = dataset_verified(root, left)
    r = dataset_verified(root, right)
    if left_key not in l['columns'] or right_key not in r['columns']:
        raise ValueError('Unknown join column')
    if left_key == '__source_row' or right_key == '__source_row':
        raise ValueError('Source ordinals are not cross-source identity keys')
    lp, rp = Path(l['parquet_path']), Path(r['parquet_path'])
    lk, rk = 'l.' + quote(left_key), 'r.' + quote(right_key)
    source = f' FROM read_parquet(?) l JOIN read_parquet(?) r ON {lk}={rk} WHERE {lk}<>\'\''
    with connection([lp, rp]) as db:
        count = db.execute('SELECT count(*)' + source, [str(lp), str(rp)]).fetchone()
        if count is None:
            raise ValueError('Missing join count')
        result = db.execute(f'SELECT {lk},l.__source_row,r.__source_row' + source +
                            ' ORDER BY l.__source_row,r.__source_row LIMIT ?',
                            [str(lp), str(rp), limit]).fetchall()
    return {'left': left, 'right': right, 'left_key': left_key, 'right_key': right_key,
            'total_matches': count[0], 'truncated': count[0] > limit,
            'matches': [{'key': key, 'left_row': ln, 'right_row': rn} for key, ln, rn in result],
            'relationship': 'exact string value match; verify namespace, identifier validity and dates',
            'notice': 'Many-to-many pairs are not unique entities or misconduct; blank keys excluded; no store writes'}


def add_commands(sub: Any) -> None:
    p = sub.add_parser('bulk')
    actions = p.add_subparsers(dest='bulk_action', required=True)
    for name in ['acquire', 'ingest']:
        a = actions.add_parser(name)
        if name == 'ingest':
            a.add_argument('path', type=Path)
            a.add_argument('--url', required=True)
        else:
            a.add_argument('url')
        a.add_argument('--max-bytes', type=int, required=True)
    a = actions.add_parser('convert')
    a.add_argument('id')
    a.add_argument('--member')
    a.add_argument('--required', action='append', default=[])
    a.add_argument('--encoding', default='utf-8-sig')
    a.add_argument('--max-rows', type=int, default=200000)
    a.add_argument('--max-expanded-bytes', type=int, default=200000000)
    a = actions.add_parser('query')
    a.add_argument('id')
    a.add_argument('--column')
    a.add_argument('--equals')
    a.add_argument('--limit', type=int, default=20)
    actions.add_parser('verify')
    a = actions.add_parser('join')
    a.add_argument('left')
    a.add_argument('right')
    a.add_argument('--left-key', required=True)
    a.add_argument('--right-key', required=True)
    a.add_argument('--limit', type=int, default=20)
    a = actions.add_parser('connector')
    a.add_argument('name', choices=['cms-hospice-chow', 'cms-hospice-owners', 'cms-hospice-enrollments',
                                   'oig-leie', 'oig-reinstatements'])
    a.add_argument('--max-bytes', type=int, default=20000000)
    a.add_argument('--max-rows', type=int, default=200000)


def dispatch(a: argparse.Namespace) -> dict[str, Any]:
    try:
        return _dispatch(a)
    except duckdb.Error as exc:
        raise ValueError(str(exc)) from exc


def _dispatch(a: argparse.Namespace) -> dict[str, Any]:
    root = a.home.resolve() / 'bulk'
    if a.bulk_action in ('acquire', 'ingest'):
        return acquire(root, a.url, a.max_bytes, a.path if a.bulk_action == 'ingest' else None)
    if a.bulk_action == 'convert':
        return convert(root, a.id, a.member, a.required, a.encoding, a.max_rows, a.max_expanded_bytes)
    if a.bulk_action == 'query':
        return query(root, a.id, a.column, a.equals, a.limit)
    if a.bulk_action == 'verify':
        return verify(root)
    if a.bulk_action == 'join':
        return join(root, a.left, a.right, a.left_key, a.right_key, a.limit)
    from .national_sources import connector
    return connector(root, a.name, a.max_bytes, a.max_rows)
