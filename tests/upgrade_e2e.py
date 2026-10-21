"""Pre-implementation subprocess acceptance. Fixtures are synthetic and scratch-only."""
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from fraudlab.settings import scratch_dir

ROOT = Path(__file__).resolve().parents[1]
STAMP = str(time.time_ns())
SCRATCH = scratch_dir() / ('fraudlab-upgrade-' + STAMP)
SCRATCH.mkdir(parents=True)
HOME = SCRATCH / 'store'
EVENTS = []


def cli(*args, ok=True):
    proc = subprocess.run([sys.executable, '-m', 'fraudlab', '--home', str(HOME), *args],
                          env=dict(os.environ, PYTHONPATH=str(ROOT / 'src')),
                          capture_output=True, text=True, timeout=180, check=False)
    EVENTS.append({'args': list(args), 'exit_code': proc.returncode,
                   'stdout': proc.stdout, 'stderr': proc.stderr})
    assert (proc.returncode == 0) == ok, EVENTS[-1]
    result = json.loads(proc.stdout)
    if not ok:
        assert 'error' in result or result.get('passed') is False, result
    return result


def hashes():
    return {str(p.relative_to(HOME)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in HOME.rglob('*') if p.is_file()}


def ingest(path, **extra):
    args = ['bulk', 'ingest', str(path), '--url', 'https://example.gov/SYNTHETIC',
            '--max-bytes', '2000000']
    return cli(*args, **extra)


def convert(sid, *args, ok=True):
    return cli('bulk', 'convert', sid, '--required', 'npi', '--required', 'amount',
               '--max-rows', '100', '--max-expanded-bytes', '2000000', *args, ok=ok)


def deterministic():
    missing = HOME
    cli('inspect', 'status', ok=False)
    assert not missing.exists(), 'Read-only inspection initialized a missing store'
    cli('init')
    fixture = SCRATCH / 'SYNTHETIC.csv'
    fixture.write_text('npi,amount\n0012345678,10.25\n0098765432,20.50\n0012345678,0.25\n')
    old = cli('ingest', str(fixture), '--url', 'https://example.gov/SYNTHETIC',
              '--label', 'SYNTHETIC ONLY', '--format', 'csv')
    before = hashes()
    assert cli('inspect', 'status')['sources'] == 1
    assert cli('inspect', 'verify')['passed']
    assert len(cli('inspect', 'sources')['sources']) == 1
    assert len(cli('inspect', 'records', old['id'])['records']) == 3
    assert hashes() == before, 'Inspection wrote to store'
    raw = ingest(fixture)
    assert raw['state'] == 'acquired'
    assert ingest(fixture)['id'] == raw['id']
    ds = convert(raw['id'])
    assert ds['state'] == 'schema-verified' and ds['rows'] == 3
    assert convert(raw['id'])['id'] == ds['id']
    before = hashes()
    result = cli('bulk', 'query', ds['id'], '--column', 'npi', '--equals', '0012345678', '--limit', '1')
    assert result['total_matching'] == 2 and result['truncated']
    assert result['rows'][0]['npi'] == '0012345678' and result['rows'][0]['__source_row'] == 1
    assert cli('bulk', 'verify')['passed']
    joined = cli('bulk', 'join', ds['id'], ds['id'], '--left-key', 'npi', '--right-key', 'npi', '--limit', '1')
    assert joined['total_matches'] == 5 and joined['truncated'] and len(joined['matches']) == 1
    assert joined['matches'][0]['key'] == '0012345678'
    cli('bulk', 'join', ds['id'], ds['id'], '--left-key', 'missing', '--right-key', 'npi', ok=False)
    cli('bulk', 'query', ds['id'], '--column', 'not_a_column', '--equals', 'x', ok=False)
    cli('bulk', 'query', ds['id'], '--limit', '0', ok=False)
    assert hashes() == before, 'Bulk read-only query/verify wrote to store'
    convert(raw['id'], '--max-rows', '1', ok=False)
    convert(raw['id'], '--max-expanded-bytes', '1', ok=False)
    cli('bulk', 'convert', raw['id'], '--required', 'absent', ok=False)
    for content in ['npi,npi,amount\na,b,1\n', 'npi,amount\na,1,extra\n',
                    'npi,amount\na\n', 'npi,amount\n', 'npi,amount,__source_row\na,1,99\n',
                    'npi,amount\na,"1\n']:
        p = SCRATCH / 'bad.csv'
        p.write_text(content)
        bad = ingest(p)
        convert(bad['id'], ok=False)
    latin = SCRATCH / 'latin.csv'
    latin.write_bytes('npi,amount,name\n0012345678,1,CAFÉ\n'.encode('cp1252'))
    lat = ingest(latin)
    convert(lat['id'], ok=False)
    assert convert(lat['id'], '--encoding', 'cp1252')['rows'] == 1
    archive = SCRATCH / 'valid.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr('SYNTHETIC.csv', fixture.read_bytes())
    arc = ingest(archive)
    assert convert(arc['id'], '--member', 'SYNTHETIC.csv')['rows'] == 3
    convert(arc['id'], '--member', 'missing.csv', ok=False)
    unsafe = SCRATCH / 'unsafe.zip'
    with zipfile.ZipFile(unsafe, 'w') as z:
        z.writestr('../escape.csv', fixture.read_bytes())
    un = ingest(unsafe)
    convert(un['id'], '--member', '../escape.csv', ok=False)
    cli('bulk', 'query', '../escape', ok=False)
    for url in ['http://127.0.0.1/private', 'https://127.0.0.1/', 'https://example.com/',
                'https://user:password@example.gov/']:
        cli('bulk', 'acquire', url, '--max-bytes', '1000', ok=False)
    cli('bulk', 'acquire', 'https://www.cms.gov/', '--max-bytes', '0', ok=False)
    Path(ds['parquet_path']).write_bytes(b'TAMPERED SYNTHETIC PARQUET')
    cli('bulk', 'query', ds['id'], ok=False)
    assert not cli('bulk', 'verify', ok=False)['passed']
    # Separate original-tampering contract: a raw original mutation blocks conversion.
    Path(raw['path']).write_bytes(b'TAMPERED SYNTHETIC ORIGINAL')
    convert(raw['id'], ok=False)


def live_web():
    result = cli('web-search', 'Medicare hospice')
    assert result['success'] and result['data']['web']
    assert result['backend'] == 'local-searxng'
    for url in ['https://www.justice.gov/fraud/whistleblower',
                'https://opendata.hhs.gov/datasets/medicaid-provider-spending/',
                'https://www.cms.gov/files/document/mm13333-medicare-program-integrity-manual-cy-2024-home-health-prospective-payment-system-updates.pdf']:
        result = cli('web-extract', url)
        assert result['state'] == 'extracted' and len(result['content']) > 200
        for key in ['original_path', 'response_path', 'text_path']:
            assert Path(result[key]).is_file()
        if 'opendata' in url:
            assert 'TOTAL_CLAIM_LINES' in result['content'], 'JavaScript documentation was not rendered'
    cli('web-extract', 'http://127.0.0.1/private', ok=False)


def live_connectors():
    for name in ['cms-hospice-chow', 'cms-hospice-owners', 'cms-hospice-enrollments',
                 'oig-leie', 'oig-reinstatements']:
        result = cli('bulk', 'connector', name, '--max-bytes', '20000000', '--max-rows', '200000')
        assert result['state'] == 'exercised' and result['datasets']
        assert result['catalog_id'] and result['coverage']
        for ds in result['datasets']:
            assert ds['rows'] > 0 and ds['state'] == 'schema-verified'
    assert cli('bulk', 'verify')['passed']


if __name__ == '__main__':
    phase = sys.argv[1] if len(sys.argv) > 1 else 'deterministic'
    passed = False
    try:
        {'deterministic': deterministic, 'web': live_web, 'connectors': live_connectors}[phase]()
        passed = True
    finally:
        dest = ROOT / 'artifacts' / ('upgrade-' + phase + '-' + STAMP + '.json')
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(json.dumps({'phase': phase, 'passed': passed, 'scratch': str(SCRATCH),
                                    'events': EVENTS}, indent=2))
        print(json.dumps({'passed': passed, 'artifact': str(dest)}))
