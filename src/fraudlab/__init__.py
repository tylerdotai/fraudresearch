"""Private, source-backed research tools. No submission or messaging commands."""
import argparse
import csv
import hashlib
import io
import json
import os
import sqlite3
import subprocess
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import httpx

MAX_BYTES = 20_000_000
MAX_ROWS = 25_000


def now() -> str:
    return datetime.now(UTC).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hidden = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in ('script', 'style'):
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in ('script', 'style'):
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data: str) -> None:
        if not self.hidden and data.strip():
            self.parts.append(data.strip())


class Store:
    def __init__(self, home: Path):
        self.home = home.resolve()
        self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.originals = self.home / 'originals'
        self.originals.mkdir(exist_ok=True, mode=0o700)
        self.db = sqlite3.connect(self.home / 'evidence.sqlite3')
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS sources (
          id TEXT PRIMARY KEY, sha256 TEXT NOT NULL, path TEXT NOT NULL,
          textpath TEXT NOT NULL, url TEXT NOT NULL, label TEXT NOT NULL,
          format TEXT NOT NULL, fetched_at TEXT NOT NULL, bytes INTEGER NOT NULL,
          records INTEGER NOT NULL, extraction_status TEXT NOT NULL, text_sha256 TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS records (
          source_id TEXT REFERENCES sources(id), ordinal INTEGER, data TEXT NOT NULL,
          PRIMARY KEY(source_id, ordinal));
        CREATE TABLE IF NOT EXISTS events (
          sequence INTEGER PRIMARY KEY, at TEXT NOT NULL, action TEXT NOT NULL, data TEXT NOT NULL);
        ''')

    def event(self, action: str, data: Any) -> None:
        self.db.execute('INSERT INTO events(at,action,data) VALUES (?,?,?)',
                        (now(), action, json.dumps(data)))
        self.db.commit()

    def source(self, sid: str) -> dict[str, Any]:
        row = self.db.execute('SELECT * FROM sources WHERE id=?', (sid,)).fetchone()
        if not row:
            raise ValueError('Unknown source ID')
        return dict(row)

    def ingest(self, data: bytes, url: str, label: str, fmt: str) -> dict[str, Any]:
        if not data or len(data) > MAX_BYTES:
            raise ValueError('Empty source or source exceeds 20MB limit')
        rows: list[dict[str, Any]] = []
        text = ''
        status = 'extracted'
        if fmt == 'pdf':
            if not data.startswith(b'%PDF-'):
                raise ValueError('Invalid PDF signature')
            p = subprocess.run(['pdftotext', '-layout', '-', '-'], input=data,
                               capture_output=True, timeout=30, check=False)
            if p.returncode:
                raise ValueError('PDF extraction failed: ' + p.stderr.decode(errors='replace')[:300])
            text = p.stdout.decode('utf-8', errors='replace')
            if not text.strip():
                status = 'needs_ocr'
        else:
            text = data.decode('utf-8-sig')
            if fmt == 'html':
                parser = Text()
                parser.feed(text)
                text = '\n'.join(parser.parts)
            elif fmt == 'csv':
                reader = csv.DictReader(io.StringIO(text))
                if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                    raise ValueError('CSV header is missing or duplicated')
                rows = list(reader)
                if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
                    raise ValueError('CSV is empty or has malformed rows')
            elif fmt == 'json':
                obj = json.loads(text)
                if isinstance(obj, dict) and ('Errors' in obj or 'error' in obj):
                    raise ValueError('Source returned an error object')
                items = obj.get('results', obj.get('records', [obj])) if isinstance(obj, dict) else obj
                if not isinstance(items, list) or not items or not all(isinstance(r, dict) for r in items):
                    raise ValueError('JSON source must contain nonempty object records')
                rows = items
        if not text.strip() and status != 'needs_ocr':
            raise ValueError('No extractable source text')
        if len(rows) > MAX_ROWS:
            raise ValueError('Source exceeds bounded 25000-row import; partition it first')
        sha = digest(data)
        sid = digest((url + '\0' + sha).encode())[:24]
        if self.db.execute('SELECT 1 FROM sources WHERE id=?', (sid,)).fetchone():
            return self.source(sid)
        path = self.originals / (sid + '.' + fmt)
        textpath = self.originals / (sid + '.extracted.txt')
        path.write_bytes(data)
        textpath.write_text(text)
        record = {'id': sid, 'sha256': sha, 'path': str(path), 'textpath': str(textpath), 'url': url,
                  'label': label, 'format': fmt, 'fetched_at': now(), 'bytes': len(data),
                  'records': len(rows), 'extraction_status': status, 'text_sha256': digest(text.encode())}
        self.db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', tuple(record.values()))
        self.db.executemany('INSERT INTO records VALUES (?,?,?)',
                            [(sid, i + 1, json.dumps(row)) for i, row in enumerate(rows)])
        self.event('source_imported', record)
        return record

    def verify(self) -> dict[str, Any]:
        errors = []
        sources = [dict(r) for r in self.db.execute('SELECT * FROM sources')]
        for row in sources:
            path = Path(row['path'])
            if not path.is_file() or digest(path.read_bytes()) != row['sha256']:
                errors.append({'id': row['id'], 'error': 'original hash mismatch or missing'})
            textpath = Path(row['textpath'])
            if not textpath.is_file() or digest(textpath.read_bytes()) != row['text_sha256']:
                errors.append({'id': row['id'], 'error': 'extracted text hash mismatch or missing'})
        return {'passed': not errors, 'sources': len(sources), 'errors': errors}


def parser() -> argparse.ArgumentParser:
    from .settings import data_home
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--home', type=Path, default=data_home())
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    sub.add_parser('sources')
    sub.add_parser('verify')
    a = sub.add_parser('web-search')
    a.add_argument('query')
    a.add_argument('--limit', type=int, default=5)
    a = sub.add_parser('web-extract')
    a.add_argument('url')
    a = sub.add_parser('ingest')
    a.add_argument('path', type=Path)
    a.add_argument('--url', required=True)
    a.add_argument('--label', required=True)
    a.add_argument('--format', choices=['csv', 'json', 'html', 'text', 'pdf'], required=True)
    a = sub.add_parser('records')
    a.add_argument('id')
    from .bulk import add_commands as add_bulk_commands
    from .cases import add_commands as add_case_commands
    from .readonly import add_commands as add_readonly_commands
    from .research import add_commands
    add_bulk_commands(sub)
    add_readonly_commands(sub)
    add_commands(sub)
    add_case_commands(sub)
    return p


def dispatch(a: argparse.Namespace, store: Store) -> dict[str, Any]:
    if a.command == 'init':
        return {'initialized': True, 'home': str(store.home), 'mode': 'on_demand', 'submission_tools': False}
    if a.command == 'ingest':
        return store.ingest(a.path.read_bytes(), a.url, a.label, a.format)
    if a.command == 'sources':
        return {'sources': [dict(r) for r in store.db.execute('SELECT * FROM sources ORDER BY fetched_at')]}
    if a.command == 'records':
        store.source(a.id)
        return {'records': [json.loads(r[0]) for r in store.db.execute(
            'SELECT data FROM records WHERE source_id=? ORDER BY ordinal LIMIT 1000', (a.id,))]}
    if a.command == 'verify':
        return store.verify()
    if a.command in ('case', 'status'):
        from .cases import dispatch as case_dispatch
        return case_dispatch(a, store)
    from .research import dispatch as research_dispatch
    return research_dispatch(a, store)


def main() -> None:
    os.umask(0o077)
    a = parser().parse_args()
    try:
        if a.command in ('web-search', 'web-extract'):
            from .local_web import extract, search
            result = search(a.query, a.limit) if a.command == 'web-search' else extract(a.url, a.home)
        elif a.command == 'bulk':
            from .bulk import dispatch as bulk_dispatch
            result = bulk_dispatch(a)
        elif a.command == 'inspect':
            from .readonly import dispatch as readonly_dispatch
            result = readonly_dispatch(a)
        else:
            result = dispatch(a, Store(a.home))
        print(json.dumps(result, indent=2))
        if result.get('passed') is False:
            raise SystemExit(1)
    except (ValueError, TypeError, OSError, sqlite3.Error, UnicodeError,
            subprocess.SubprocessError, httpx.HTTPError) as exc:
        print(json.dumps({'error': str(exc)}))
        raise SystemExit(1) from exc
