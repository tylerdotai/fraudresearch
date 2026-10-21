"""Strict evidence-store read-only CLI routes: no Store constructor or directory creation."""
from __future__ import annotations

import argparse
import json
import sqlite3
from typing import Any

from .bulk import file_hash


def add_commands(sub: Any) -> None:
    p = sub.add_parser('inspect')
    s = p.add_subparsers(dest='inspect_action', required=True)
    for name in ('status', 'sources', 'verify'):
        s.add_parser(name)
    a = s.add_parser('records')
    a.add_argument('id')


def dispatch(a: argparse.Namespace) -> dict[str, Any]:
    path = (a.home / 'evidence.sqlite3').resolve()
    if not path.is_file():
        raise ValueError('Existing evidence database required; no initialization performed')
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA query_only=ON')
        sources = [dict(r) for r in db.execute('SELECT * FROM sources ORDER BY fetched_at')]
        if a.inspect_action == 'sources':
            return {'sources': sources}
        if a.inspect_action == 'records':
            if not any(s['id'] == a.id for s in sources):
                raise ValueError('Unknown source ID')
            total = db.execute('SELECT count(*) FROM records WHERE source_id=?', (a.id,)).fetchone()[0]
            return {'records': [json.loads(r[0]) for r in db.execute(
                'SELECT data FROM records WHERE source_id=? ORDER BY ordinal LIMIT 1000', (a.id,))],
                'total': total, 'truncated': total > 1000}
        errors = []
        from pathlib import Path
        for r in sources:
            for field, sha in [('path', 'sha256'), ('textpath', 'text_sha256')]:
                try:
                    if file_hash(Path(r[field])) != r[sha]:
                        errors.append({'id': r['id'], 'field': field, 'error': 'hash mismatch'})
                except OSError as exc:
                    errors.append({'id': r['id'], 'field': field, 'error': str(exc)})
        integrity = {'passed': not errors, 'sources': len(sources), 'errors': errors}
        if a.inspect_action == 'verify':
            return integrity
        return {'sources': len(sources), 'records': db.execute('SELECT count(*) FROM records').fetchone()[0],
                'cases': len(list((a.home / 'cases').glob('*.json'))), 'integrity': integrity,
                'mode': 'strict_read_only', 'writes': False, 'scope': 'case SQLite/originals; bulk verify separate'}
