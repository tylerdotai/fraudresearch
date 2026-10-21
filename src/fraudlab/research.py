"""Bounded public-source acquisition and reproducible exploratory analysis."""
from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import time
from decimal import Decimal, InvalidOperation
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode, urljoin, urlsplit

import httpx
from rapidfuzz.fuzz import ratio

if TYPE_CHECKING:
    from . import Store

RULE_URLS = {
    'portal': 'https://america.gov/fraud',
    'overview': 'https://www.justice.gov/fraud/whistleblower',
    'terms': 'https://www.justice.gov/fraud/national-fraud-enforcement-division-criminal-tip-rewards-pilot-program',
    'faq': 'https://www.justice.gov/fraud/criminal-tip-rewards-pilot-program-faqs',
}


def public_url(url: str) -> None:
    u = urlsplit(url)
    host = u.hostname or ''
    if u.scheme != 'https' or not host.endswith('.gov') or u.username or u.password or u.port not in (None, 443):
        raise ValueError('Only credential-free HTTPS URLs on official .gov hosts at port 443 are accepted')
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(r[4][0]).is_global for r in addresses):
        raise ValueError('Non-public destination rejected')


def fetch(store: Store, url: str, label: str, fmt: str, max_bytes: int = 20_000_000) -> dict[str, Any]:
    if not 0 < max_bytes <= 20_000_000:
        raise ValueError('max-bytes must be between 1 and 20000000')
    requested = url
    start = time.monotonic()
    last = store.db.execute('SELECT at FROM events WHERE action=? ORDER BY sequence DESC LIMIT 1',
                            ('fetch_attempt',)).fetchone()
    if last:
        from datetime import UTC, datetime
        elapsed = (datetime.now(UTC) - datetime.fromisoformat(last[0])).total_seconds()
        time.sleep(max(0, 1 - elapsed))
    with httpx.Client(timeout=httpx.Timeout(15, connect=10), follow_redirects=False,
                      trust_env=False, headers={'User-Agent': 'FraudResearchWorkbench/0.1 public-data-study',
                                               'Accept': 'application/json,text/csv,text/html,application/pdf'}) as client:
        for attempt in range(6):
            public_url(url)
            store.event('fetch_attempt', {'url': url})
            try:
                with client.stream('GET', url) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        url = urljoin(url, response.headers.get('location', ''))
                        continue
                    if response.status_code in (429, 502, 503, 504) and attempt < 2:
                        time.sleep(attempt + 1)
                        continue
                    response.raise_for_status()
                    if int(response.headers.get('content-length', '0')) > max_bytes:
                        raise ValueError('Response exceeds configured size limit')
                    chunks = []
                    size = 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > max_bytes or time.monotonic() - start > 45:
                            raise ValueError('Response exceeds size or elapsed-time limit')
                        chunks.append(chunk)
                    result = store.ingest(b''.join(chunks), requested, label, fmt)
                    store.event('fetch_completed', {'id': result['id'], 'final_url': str(response.url),
                                                   'http_status': response.status_code,
                                                   'content_type': response.headers.get('content-type', '')})
                    return result
            except httpx.HTTPError as exc:
                store.event('fetch_failed', {'url': url, 'error': str(exc)})
                if isinstance(exc, httpx.TransportError) and attempt < 2:
                    time.sleep(attempt + 1)
                    continue
                raise ValueError('Source unavailable: ' + str(exc)) from exc
    raise ValueError('Redirect or retry limit reached')


def add_commands(sub: Any) -> None:
    p = sub.add_parser('fetch')
    p.add_argument('url')
    p.add_argument('--label', required=True)
    p.add_argument('--format', choices=['csv', 'json', 'html', 'text', 'pdf'], required=True)
    p.add_argument('--max-bytes', type=int, default=20_000_000)
    p = sub.add_parser('analyze')
    p.add_argument('id')
    p.add_argument('--group', required=True)
    p.add_argument('--amount', required=True)
    p = sub.add_parser('match')
    p.add_argument('query')
    p = sub.add_parser('connector')
    p.add_argument('name', choices=['nppes', 'agencies', 'cms-hospice', 'cms-home-health'])
    p.add_argument('--state', default='')
    p.add_argument('--taxonomy', choices=['hospice', 'home-health'], default='hospice')
    p.add_argument('--limit', type=int, default=10)
    p.add_argument('--skip', type=int, default=0)
    sub.add_parser('refresh-rules')
    p = sub.add_parser('profile-data')
    p.add_argument('id')
    p.add_argument('--group', required=True)
    p = sub.add_parser('join')
    p.add_argument('left')
    p.add_argument('right')
    p.add_argument('--left-key', required=True)
    p.add_argument('--right-key', required=True)


def dispatch(a: argparse.Namespace, store: Store) -> dict[str, Any]:
    if a.command == 'fetch':
        return fetch(store, a.url, a.label, a.format, a.max_bytes)
    if a.command == 'refresh-rules':
        results = {}
        for name, url in RULE_URLS.items():
            try:
                results[name] = fetch(store, url, 'Program rules: ' + name, 'html')
            except ValueError as exc:
                results[name] = {'error': str(exc)}
        return {'passed': all('error' not in r for r in results.values()), 'snapshots': results,
                'notice': 'Read current text and reconcile scope differences; snapshots are not eligibility decisions.'}
    if a.command == 'connector':
        if a.name.startswith('cms-'):
            catalog = fetch(store, 'https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items',
                            'CMS Provider Data public dataset catalog', 'json')
            title = 'Hospice - General Information' if a.name == 'cms-hospice' else 'Home Health Care Agencies'
            items = [json.loads(row[0]) for row in store.db.execute(
                'SELECT data FROM records WHERE source_id=?', (catalog['id'],))]
            found = [item for item in items if item.get('title') == title and item.get('accessLevel') == 'public']
            if len(found) != 1:
                raise ValueError('Expected unique public CMS dataset title not found; review catalog drift')
            distributions = [d for d in found[0].get('distribution', []) if d.get('mediaType') == 'text/csv']
            if len(distributions) != 1 or not distributions[0].get('downloadURL'):
                raise ValueError('Expected unique CMS CSV distribution not found')
            source = fetch(store, distributions[0]['downloadURL'], 'CMS public snapshot: ' + title, 'csv')
            fields = json.loads(store.db.execute('SELECT data FROM records WHERE source_id=? LIMIT 1',
                                                (source['id'],)).fetchone()[0])
            if not any('state' in key.lower() for key in fields) or not any('ccn' in key.lower() for key in fields):
                raise ValueError('CMS provider schema lacks state or CCN; review dataset drift')
            store.event('connector_verified', {'connector': a.name, 'source_id': source['id'],
                                               'catalog_source_id': catalog['id'], 'dataset': found[0]['identifier']})
            return {**source, 'catalog_source_id': catalog['id'], 'dataset': found[0]['identifier'],
                    'coverage': 'full published CSV snapshot; not all providers or all periods',
                    'fraud_inference': False}
        if a.name == 'nppes':
            if not 1 <= a.limit <= 200 or not 0 <= a.skip <= 1000:
                raise ValueError('NPPES limit must be 1..200 and skip 0..1000')
            if a.state and (len(a.state) != 2 or not a.state.isalpha()):
                raise ValueError('State must be a two-letter code or omitted for a nationwide query')
            query = {'version': '2.1', 'enumeration_type': 'NPI-2', 'limit': a.limit,
                     'skip': a.skip, 'taxonomy_description': 'Hospice' if a.taxonomy == 'hospice' else 'Home Health'}
            if a.state:
                query['state'] = a.state.upper()
            url = 'https://npiregistry.cms.hhs.gov/api/?' + urlencode(query)
            result = fetch(store, url, 'NPPES provider registry sample — not a fraud finding', 'json')
            records = [json.loads(r[0]) for r in store.db.execute('SELECT data FROM records WHERE source_id=?', (result['id'],))]
            if not all('number' in r and 'basic' in r and r.get('enumeration_type') == 'NPI-2' for r in records):
                raise ValueError('NPPES schema mismatch')
            return {**result, 'coverage': 'bounded registry sample, not a census', 'fraud_inference': False}
        result = fetch(store, 'https://api.usaspending.gov/api/v2/references/toptier_agencies/',
                       'USAspending federal agency reference — not award-level evidence', 'json')
        records = [json.loads(r[0]) for r in store.db.execute('SELECT data FROM records WHERE source_id=?', (result['id'],))]
        if not all('agency_id' in r and 'agency_name' in r for r in records):
            raise ValueError('USAspending schema mismatch')
        return {**result, 'coverage': 'agency reference, not recipient payments'}
    if a.command == 'analyze':
        store.source(a.id)
        groups: dict[str, Any] = {}
        for row in store.db.execute('SELECT ordinal,data FROM records WHERE source_id=?', (a.id,)):
            item = json.loads(row['data'])
            if a.group not in item or a.amount not in item:
                raise ValueError('Required grouping or amount column missing at row ' + str(row['ordinal']))
            try:
                amount = Decimal(str(item[a.amount]))
                if not amount.is_finite():
                    raise ValueError('Non-finite amount')
            except InvalidOperation as exc:
                raise ValueError('Invalid decimal at row ' + str(row['ordinal'])) from exc
            group = str(item[a.group])
            current = groups.setdefault(group, {'count': 0, 'total': Decimal(0)})
            current['count'] += 1
            current['total'] += amount
        if not groups:
            raise ValueError('No records to analyze')
        for value in groups.values():
            value['total'] = str(value['total'])
        result = {'source_id': a.id, 'groups': groups, 'method': 'Decimal sum; no fraud inference',
                  'group_column': a.group, 'amount_column': a.amount}
        store.event('analysis', result)
        return result
    if a.command == 'profile-data':
        store.source(a.id)
        counts: dict[str, int] = {}
        for row in store.db.execute('SELECT data FROM records WHERE source_id=?', (a.id,)):
            record = json.loads(row[0])
            if a.group not in record:
                raise ValueError('Grouping column missing')
            value = str(record[a.group])
            counts[value] = counts.get(value, 0) + 1
        result = {'source_id': a.id, 'group_column': a.group, 'counts': counts,
                  'method': 'Published row counts, not payment or fraud counts'}
        store.event('dataset_profile', result)
        return result
    if a.command == 'join':
        store.source(a.left)
        store.source(a.right)
        right: dict[str, list[int]] = {}
        for row in store.db.execute('SELECT ordinal,data FROM records WHERE source_id=?', (a.right,)):
            record = json.loads(row['data'])
            if a.right_key not in record:
                raise ValueError('Right join column missing')
            key = str(record[a.right_key])
            if key.strip():
                right.setdefault(key, []).append(row['ordinal'])
        matches: list[dict[str, Any]] = []
        truncated = False
        for row in store.db.execute('SELECT ordinal,data FROM records WHERE source_id=?', (a.left,)):
            record = json.loads(row['data'])
            if a.left_key not in record:
                raise ValueError('Left join column missing')
            key = str(record[a.left_key])
            for ordinal in right.get(key, []):
                if len(matches) >= 10000:
                    truncated = True
                    break
                matches.append({'key': key, 'left_row': row['ordinal'], 'right_row': ordinal})
        result = {'left_source': a.left, 'right_source': a.right, 'left_key': a.left_key,
                  'right_key': a.right_key, 'matches': matches, 'truncated': truncated,
                  'relationship': 'exact_identifier_value_match_only',
                  'notice': 'Verify identifier semantics and periods; matching values do not prove identity or misconduct.'}
        store.event('source_join', result)
        return result
    if a.command == 'match':
        candidates = []
        for row in store.db.execute('SELECT source_id,ordinal,data FROM records LIMIT 25000'):
            record = json.loads(row['data'])
            name = record.get('name') or record.get('basic', {}).get('organization_name') or record.get('agency_name')
            if name:
                score = ratio(a.query.casefold(), str(name).casefold())
                candidates.append({'source_id': row['source_id'], 'row': row['ordinal'], 'record': record,
                                   'score': score, 'relationship': 'candidate_only'})
        return {'candidates': sorted(candidates, key=lambda r: r['score'], reverse=True)[:10],
                'notice': 'Name similarity is not identity, ownership, misconduct, or fraud evidence.'}
    raise ValueError('Unknown research command')
