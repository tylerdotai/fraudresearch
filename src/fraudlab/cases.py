"""Case provenance checks and private local exports, never government submissions."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from . import Store

SECTORS = ['hospice', 'home-health', 'day-care', 'special-services', 'agriculture', 'labor',
           'housing', 'education', 'veterans', 'small-business', 'healthcare', 'other-review-required']


def add_commands(sub: Any) -> None:
    p = sub.add_parser('case')
    actions = p.add_subparsers(dest='case_action', required=True)
    a = actions.add_parser('create')
    a.add_argument('path', type=Path)
    for name in ('check', 'export'):
        a = actions.add_parser(name)
        a.add_argument('id')
        if name == 'export':
            a.add_argument('--draft', action='store_true', help='Export clearly marked incomplete research')
    actions.add_parser('list')
    sub.add_parser('status')


def case_path(store: Store, cid: str) -> Path:
    if not re.fullmatch(r'[a-f0-9]{24}', cid):
        raise ValueError('Invalid case ID')
    return store.home / 'cases' / (cid + '.json')


def citation(store: Store, item: dict[str, Any]) -> bool:
    try:
        source = store.source(item['source_id'])
        locator = item['locator']
        quote = item['quote']
        if not isinstance(quote, str) or not quote.strip():
            return False
        if re.fullmatch(r'row:[1-9][0-9]*', locator):
            row = store.db.execute('SELECT data FROM records WHERE source_id=? AND ordinal=?',
                                   (source['id'], int(locator.split(':')[1]))).fetchone()
            return row is not None and quote in row[0]
        text = Path(source['textpath']).read_text()
        if re.fullmatch(r'page:[1-9][0-9]*', locator) and source['format'] == 'pdf':
            pages = text.split('\f')
            index = int(locator.split(':')[1]) - 1
            return index < len(pages) and quote in pages[index]
        if re.fullmatch(r'line:[1-9][0-9]*', locator):
            lines = text.splitlines()
            index = int(locator.split(':')[1]) - 1
            return index < len(lines) and quote in lines[index]
        return False
    except (KeyError, TypeError, ValueError, OSError):
        return False


def check(store: Store, case: dict[str, Any]) -> dict[str, Any]:
    blockers = []
    if not store.verify()['passed']:
        blockers.append('source_integrity_failure')
    if case.get('sector') not in SECTORS or case.get('sector') == 'other-review-required':
        blockers.append('program_scope_unverified')
    claims = case.get('claims')
    if not isinstance(claims, list) or not claims:
        blockers.append('no_claims')
    else:
        for claim in claims:
            if not isinstance(claim, dict) or not citation(store, claim):
                blockers.append('unverified_citation')
            if not isinstance(claim, dict) or claim.get('classification') not in ('fact', 'anomaly', 'allegation', 'adjudicated'):
                blockers.append('unclassified_claim')
            if not isinstance(claim, dict) or not isinstance(claim.get('text'), str) or not claim.get('text', '').strip():
                blockers.append('missing_claim_text')
    nexus = case.get('federal_nexus', {})
    if nexus.get('status') != 'documented' or not nexus.get('explanation') or not citation(store, nexus):
        blockers.append('federal_nexus_unverified')
    originality = case.get('originality', {})
    if originality.get('status') != 'independent_analysis' or not originality.get('explanation'):
        blockers.append('not_original_analysis')
    if not case.get('alternative_explanations'):
        blockers.append('alternative_explanations_missing')
    if not case.get('unanswered_questions'):
        blockers.append('limitations_missing')
    return {'passed': not blockers, 'blockers': sorted(set(blockers)),
            'meaning': 'Structural evidence completeness only, not proof of crime or reward eligibility',
            'reward_eligibility': 'unknown', 'government_prior_knowledge': 'unknown',
            'submission_authorized': False}


def dispatch(a: argparse.Namespace, store: Store) -> dict[str, Any]:
    folder = store.home / 'cases'
    folder.mkdir(exist_ok=True)
    if a.command == 'status':
        return {'mode': 'on_demand', 'submission_tools': False, 'scheduler_enabled_by_this_project': False,
                'sources': store.db.execute('SELECT count(*) FROM sources').fetchone()[0],
                'records': store.db.execute('SELECT count(*) FROM records').fetchone()[0],
                'cases': len(list(folder.glob('*.json'))), 'integrity': store.verify(),
                'connectors': {'nppes': 'bounded live registry queries', 'agencies': 'federal agency reference',
                               'cms-hospice': 'catalog-backed nationwide published snapshot',
                               'cms-home-health': 'catalog-backed nationwide published snapshot'},
                'bulk_connectors': ['cms-hospice-chow', 'cms-hospice-owners', 'cms-hospice-enrollments',
                                    'oig-leie', 'oig-reinstatements'],
                'bulk_note': 'Separate immutable/Parquet store; run bulk verify for its integrity and coverage.',
                'scope_note': 'Other sources require documented discovery and import; not all-sector automated coverage.'}
    if a.case_action == 'create':
        if a.path.stat().st_size > 2_000_000:
            raise ValueError('Case input exceeds size limit')
        case = json.loads(a.path.read_text())
        if not isinstance(case, dict) or not isinstance(case.get('title'), str) or not case['title'].strip():
            raise ValueError('Case requires a nonempty title')
        for key in ('federal_nexus', 'originality'):
            if not isinstance(case.get(key, {}), dict):
                raise TypeError(key + ' must be an object')
        data = json.dumps(case, sort_keys=True, ensure_ascii=False).encode()
        cid = hashlib.sha256(data).hexdigest()[:24]
        case_path(store, cid).write_bytes(data)
        store.event('case_created', {'id': cid})
        return {'id': cid, 'path': str(case_path(store, cid)), 'submitted': False}
    if a.case_action == 'list':
        return {'cases': [{'id': p.stem, 'title': json.loads(p.read_text())['title']}
                          for p in sorted(folder.glob('*.json'))]}
    path = case_path(store, a.id)
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest()[:24] != a.id:
        raise ValueError('Case content hash mismatch')
    case = json.loads(data)
    verdict = check(store, case)
    if a.case_action == 'check':
        return verdict
    if not verdict['passed'] and not a.draft:
        raise ValueError('Export blocked by incomplete evidence; use --draft for labelled private research: ' + ', '.join(verdict['blockers']))
    ids = {claim['source_id'] for claim in case.get('claims', []) if isinstance(claim, dict) and 'source_id' in claim}
    if 'source_id' in case.get('federal_nexus', {}):
        ids.add(case['federal_nexus']['source_id'])
    sources = []
    for sid in sorted(ids):
        sources.append(store.source(sid))
    if not store.verify()['passed']:
        raise ValueError('Cannot export tampered or missing source files, even as draft')
    report = {'case_id': a.id, 'draft': bool(a.draft), 'case': case, 'assessment': verdict,
              'sources': sources, 'reward_eligibility': 'unknown', 'submission_authorized': False,
              'synthetic_fixture': any('SYNTHETIC' in s['label'].upper() for s in sources),
              'notice': 'PRIVATE RESEARCH — NOT A FRAUD DETERMINATION — NOT SUBMITTED'}
    out = store.home / 'exports' / (a.id + '-' + str(time.time_ns()))
    out.mkdir(parents=True)
    attachments = out / 'attachments'
    attachments.mkdir()
    for source in sources:
        shutil.copyfile(source['path'], attachments / (source['id'] + '.' + source['format'] + '.source'))
    content = json.dumps(report, indent=2, ensure_ascii=False)
    (out / 'report.json').write_text(content)
    (out / 'report.md').write_text('# ' + case['title'] + '\n\n' + report['notice'] + '\n\n```json\n' + content + '\n```\n')
    (out / 'report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width"><title>Private research report</title>'
        '<style>body{background:#111827;color:#e5e7eb;font:16px/1.6 system-ui;max-width:1000px;margin:32px auto;padding:24px}'
        'h1{color:#93c5fd}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>' + html.escape(case['title']) +
        '</h1><strong>' + report['notice'] + '</strong><pre>' + html.escape(content) + '</pre></html>')
    manifests = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(out.rglob('*')) if p.is_file()}
    (out / 'manifest.json').write_text(json.dumps(manifests, indent=2))
    store.event('case_exported', {'id': a.id, 'directory': str(out), 'draft': bool(a.draft), 'manifest': manifests})
    return {'directory': str(out), 'draft': bool(a.draft), 'submitted': False, 'files': len(manifests) + 1}
