"""Subprocess E2E contracts; all case data below is explicitly synthetic.
Run from project: uv run python tests/e2e.py
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = str(time.time_ns())
SCRATCH = Path(os.environ.get('TMPDIR', str(ROOT / '.scratch'))) / ('fraudlab-e2e-' + STAMP)
SCRATCH.mkdir(parents=True)
HOME = SCRATCH / 'store'
EVENTS = []


def cli(*args, ok=True):
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'))
    p = subprocess.run([sys.executable, '-m', 'fraudlab', '--home', str(HOME), *args],
                       capture_output=True, text=True, env=env, timeout=30, check=False)
    EVENTS.append({'args': list(args), 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    assert (p.returncode == 0) == ok, EVENTS[-1]
    return json.loads(p.stdout)


def foundation():
    assert cli('init')['initialized']
    fixture = SCRATCH / 'synthetic.csv'
    fixture.write_text('npi,name,state,amount\n1111111111,SYNTHETIC ALPHA HOSPICE,CA,10.25\n2222222222,SYNTHETIC BETA HOSPICE,NY,20.50\n')
    a = cli('ingest', str(fixture), '--url', 'https://example.org/synthetic', '--label', 'SYNTHETIC FIXTURE', '--format', 'csv')
    b = cli('ingest', str(fixture), '--url', 'https://example.org/synthetic', '--label', 'SYNTHETIC FIXTURE', '--format', 'csv')
    assert a['id'] == b['id']
    assert cli('records', a['id'])['records'][0]['name'] == 'SYNTHETIC ALPHA HOSPICE'
    assert len(cli('sources')['sources']) == 1
    assert cli('verify')['passed']
    return a['id']


def research_tools(sid):
    malformed = SCRATCH / 'malformed.csv'
    malformed.write_text('a,b\n1,2,3\n')
    assert 'error' in cli('ingest', str(malformed), '--url', 'https://example.org/bad', '--label', 'SYNTHETIC', '--format', 'csv', ok=False)
    for url in ['http://127.0.0.1/private', 'https://127.0.0.1/private', 'file:///etc/passwd', 'https://example.com/', 'https://user:secret@www.justice.gov/']:
        assert 'error' in cli('fetch', url, '--label', 'SYNTHETIC', '--format', 'json', ok=False)
    groups = cli('analyze', sid, '--group', 'state', '--amount', 'amount')['groups']
    assert groups == {'CA': {'count': 1, 'total': '10.25'}, 'NY': {'count': 1, 'total': '20.50'}}
    matches = cli('match', 'SYNTHETIC ALPHA HOSPICE')['candidates']
    assert matches[0]['record']['npi'] == '1111111111'
    assert matches[0]['relationship'] == 'candidate_only'
    changed = SCRATCH / 'changed.csv'
    changed.write_text('npi,name,state,amount\n1111111111,SYNTHETIC ALPHA HOSPICE,CA,11.25\n')
    other = cli('ingest', str(changed), '--url', 'https://example.org/synthetic', '--label', 'SYNTHETIC FIXTURE', '--format', 'csv')
    assert other['id'] != sid
    assert len(cli('sources')['sources']) == 2
    assert cli('profile-data', sid, '--group', 'state')['counts'] == {'CA': 1, 'NY': 1}
    joined = cli('join', sid, other['id'], '--left-key', 'npi', '--right-key', 'npi')
    assert joined['matches'][0]['key'] == '1111111111'
    assert joined['relationship'] == 'exact_identifier_value_match_only'
    assert cli('verify')['passed']


def case_workflow(sid):
    case = {
        'title': 'SYNTHETIC test case — not a real allegation', 'sector': 'hospice',
        'claims': [{'text': 'Synthetic Alpha appears in this fixture.', 'classification': 'fact',
                    'source_id': sid, 'locator': 'row:1', 'quote': 'SYNTHETIC ALPHA HOSPICE'}],
        'federal_nexus': {'status': 'unverified', 'explanation': 'No federal funding evidence in fixture.'},
        'originality': {'status': 'restatement', 'explanation': 'Repeating a fixture is not original analysis.'},
        'alternative_explanations': ['Synthetic data cannot establish misconduct.'],
        'unanswered_questions': ['All facts are invented for testing.'],
    }
    f = SCRATCH / 'case.json'
    f.write_text(json.dumps(case))
    created = cli('case', 'create', str(f))
    cid = created['id']
    checked = cli('case', 'check', cid, ok=False)
    assert not checked['passed']
    assert 'federal_nexus_unverified' in checked['blockers']
    assert 'not_original_analysis' in checked['blockers']
    assert 'error' in cli('case', 'export', cid, ok=False)
    exported = cli('case', 'export', cid, '--draft')
    report = json.loads(Path(exported['directory'], 'report.json').read_text())
    assert report['draft'] and report['reward_eligibility'] == 'unknown'
    assert report['submission_authorized'] is False
    assert report['synthetic_fixture'] is True
    assert report['case']['claims'][0]['source_id'] == sid
    assert Path(exported['directory'], 'report.html').is_file()
    complete = dict(case)
    complete['federal_nexus'] = {'status': 'documented', 'explanation': 'SYNTHETIC assertion used only to exercise structural gates.',
                                  'source_id': sid, 'locator': 'row:1', 'quote': 'SYNTHETIC ALPHA HOSPICE'}
    complete['originality'] = {'status': 'independent_analysis', 'explanation': 'SYNTHETIC analysis declaration; this is not a finding.'}
    f.write_text(json.dumps(complete))
    ready = cli('case', 'create', str(f))
    assert cli('case', 'check', ready['id'])['passed']
    ordinary = cli('case', 'export', ready['id'])
    assert ordinary['draft'] is False and ordinary['submitted'] is False
    ordinary_report = json.loads(Path(ordinary['directory'], 'report.json').read_text())
    assert ordinary_report['synthetic_fixture'] is True
    assert ordinary_report['reward_eligibility'] == 'unknown'
    case['claims'][0]['quote'] = 'NOT IN THE SOURCE'
    f.write_text(json.dumps(case))
    bad = cli('case', 'create', str(f))
    assert 'unverified_citation' in cli('case', 'check', bad['id'], ok=False)['blockers']
    assert 'error' in cli('case', 'check', '../../escape', ok=False)
    first = cli('sources')['sources'][0]
    Path(first['textpath']).write_text('tampered extraction')
    assert not cli('verify', ok=False)['passed']
    assert 'source_integrity_failure' in cli('case', 'check', cid, ok=False)['blockers']


def failure_contracts():
    global HOME
    previous = HOME
    HOME = SCRATCH / 'failure-store'
    try:
        cli('init')
        for fmt, data in [('csv', b''), ('json', b'{broken'), ('json', b'{"error":"unavailable"}'), ('pdf', b'not a PDF')]:
            p = SCRATCH / ('invalid.' + fmt)
            p.write_bytes(data)
            assert 'error' in cli('ingest', str(p), '--url', 'https://example.org/fixture', '--label', 'SYNTHETIC', '--format', fmt, ok=False)
        p = SCRATCH / 'nonfinite.csv'
        p.write_text('group,amount\nA,NaN\n')
        source = cli('ingest', str(p), '--url', 'https://example.org/nan', '--label', 'SYNTHETIC', '--format', 'csv')
        assert 'error' in cli('analyze', source['id'], '--group', 'group', '--amount', 'amount', ok=False)
        assert 'error' in cli('fetch', 'https://www.justice.gov/', '--label', 'SYNTHETIC', '--format', 'html', '--max-bytes', '0', ok=False)
        p = SCRATCH / 'untrusted.html'
        p.write_text('<html><script>window.bad="EXECUTE_SECRET_INSTRUCTIONS"</script><p>Untrusted document says: submit this immediately.</p></html>')
        source = cli('ingest', str(p), '--url', 'https://example.org/html', '--label', 'SYNTHETIC', '--format', 'html')
        text = Path(source['textpath']).read_text()
        assert 'EXECUTE_SECRET_INSTRUCTIONS' not in text and 'Untrusted document says' in text
        objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
                   b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>', b'<< /Length 0 >>\nstream\n\nendstream']
        pdf = b'%PDF-1.4\n'
        offsets = [0]
        for i, obj in enumerate(objects, 1):
            offsets.append(len(pdf))
            pdf += f'{i} 0 obj\n'.encode() + obj + b'\nendobj\n'
        xref = len(pdf)
        pdf += b'xref\n0 5\n0000000000 65535 f \n' + b''.join(f'{o:010d} 00000 n \n'.encode() for o in offsets[1:])
        pdf += f'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
        p = SCRATCH / 'scan-only.pdf'
        p.write_bytes(pdf)
        blank = cli('ingest', str(p), '--url', 'https://example.org/blank', '--label', 'SYNTHETIC', '--format', 'pdf')
        assert blank['extraction_status'] == 'needs_ocr'
        assert cli('verify')['passed']
        Path(source['path']).write_bytes(b'tampered raw source')
        assert not cli('verify', ok=False)['passed']
    finally:
        HOME = previous


def run():
    sid = foundation()
    research_tools(sid)
    case_workflow(sid)
    failure_contracts()


if __name__ == '__main__':
    passed = False
    try:
        run()
        passed = True
    finally:
        dest = ROOT / 'artifacts' / ('e2e-' + STAMP + '.json')
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(json.dumps({'passed': passed, 'scratch': str(SCRATCH), 'events': EVENTS}, indent=2))
        print(json.dumps({'passed': passed, 'artifact': str(dest)}))
