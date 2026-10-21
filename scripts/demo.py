"""Offline synthetic workflow; no network, genuine subjects or submissions."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', required=True, type=Path, help='New private directory for synthetic data')
    args = parser.parse_args()
    home = args.home.expanduser().resolve()
    if home.exists() and any(home.iterdir()):
        raise SystemExit('Use a new empty directory; the demo must not mix with real evidence')
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    source = Path(__file__).resolve().parents[1] / 'examples' / 'synthetic-payments.csv'
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')

    def cli(*words: str) -> dict:
        proc = subprocess.run([sys.executable, '-m', 'fraudlab', '--home', str(home), *words],
                              env=env, capture_output=True, text=True, timeout=60, check=False)
        if proc.returncode:
            raise RuntimeError(proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    cli('init')
    record = cli('ingest', str(source), '--url', 'https://example.org/SYNTHETIC-ONLY',
                 '--label', 'SYNTHETIC DEMONSTRATION — NOT REAL PAYMENTS', '--format', 'csv')
    result = cli('analyze', record['id'], '--group', 'category', '--amount', 'amount')
    case = {'title': 'SYNTHETIC demonstration — not an allegation', 'sector': 'other-review-required',
            'claims': [{'text': 'The synthetic fixture contains this illustrative record.',
                        'classification': 'fact', 'source_id': record['id'], 'locator': 'row:1',
                        'quote': 'SYNTHETIC-001'}],
            'federal_nexus': {'status': 'unverified', 'explanation': 'No real funding evidence.'},
            'originality': {'status': 'unverified', 'explanation': 'Invented example, not a discovery.'},
            'alternative_explanations': ['This is a deliberately fictional dataset.'],
            'unanswered_questions': ['All real-world facts remain unestablished.']}
    input_path = home / 'synthetic-input.json'
    input_path.write_text(json.dumps(case))
    cid = cli('case', 'create', str(input_path))['id']
    exported = cli('case', 'export', cid, '--draft')
    output = Path(exported['directory'])
    report = json.loads((output / 'report.json').read_text())
    manifest = json.loads((output / 'manifest.json').read_text())
    assert all(hashlib.sha256((output / p).read_bytes()).hexdigest() == sha for p, sha in manifest.items())
    assert cli('verify')['passed']
    print(json.dumps({'synthetic': True, 'total': result['groups']['SYNTHETIC']['total'],
                      'draft': report['draft'], 'submitted': False,
                      'reward_eligibility': report['reward_eligibility'],
                      'export_directory': str(output), 'manifest_verified': True}, indent=2))


if __name__ == '__main__':
    main()
