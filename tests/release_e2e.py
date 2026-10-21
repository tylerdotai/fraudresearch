"""Release acceptance specified before portability/privacy implementation.

Run: uv run python tests/release_e2e.py
Receipts stay under artifacts/ (not part of a public release).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(os.environ.get('TMPDIR', str(Path.home() / '.cache' / 'fraudresearch' / 'acceptance')))
BASE.mkdir(parents=True, exist_ok=True)
SCRATCH = Path(tempfile.mkdtemp(prefix='release-e2e-', dir=BASE))
EVENTS = []
ENV = {k: v for k, v in os.environ.items()
       if k in ('PATH', 'LANG', 'LC_ALL', 'VIRTUAL_ENV', 'UV_CACHE_DIR', 'SYSTEMROOT')}
ENV.update(HOME=str(SCRATCH / 'user'), XDG_DATA_HOME=str(SCRATCH / 'user-data'),
           XDG_CONFIG_HOME=str(SCRATCH / 'user-config'), PYTHONPATH=str(ROOT / 'src'),
           PYTHONDONTWRITEBYTECODE='1')


def run(label, args, *, env=None, cwd=None, ok=True):
    proc = subprocess.run(args, env=env or ENV, cwd=cwd or SCRATCH,
                          text=True, capture_output=True, timeout=120, check=False)
    EVENTS.append({'label': label, 'exit_code': proc.returncode,
                   'stdout': proc.stdout, 'stderr': proc.stderr})
    assert (proc.returncode == 0) == ok, EVENTS[-1]
    return proc


def cli(label, *args, **kwargs):
    return run(label, [sys.executable, '-m', 'fraudlab', *args], **kwargs)


def acceptance():
    # No shell variables, paths or services from the developer's live profile.
    init = json.loads(cli('default-private-home', 'init').stdout)
    expected = Path(ENV['XDG_DATA_HOME']) / 'fraudresearch'
    assert Path(init['home']) == expected and not (ROOT / 'data').exists()
    assert not (expected / 'scratch').exists()
    cli('empty-store-integrity', 'verify')
    cli('unconfigured-search-fails-closed', 'web-search', 'SYNTHETIC', ok=False)
    cli('unconfigured-renderer-fails-closed', 'web-extract', 'https://example.gov/', ok=False)
    config = Path(ENV['XDG_CONFIG_HOME']) / 'fraudresearch' / 'services.json'
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({'searxng_url': 'http://192.0.2.1:8080',
                                  'crawl4ai_url': 'http://192.0.2.1:8081'}))
    cli('non-loopback-service-rejected', 'web-search', 'SYNTHETIC', ok=False)
    config.write_text(json.dumps({'searxng_url': 'http://user:password@127.0.0.1:8080'}))
    cli('credential-in-service-rejected', 'web-search', 'SYNTHETIC', ok=False)
    config.write_text('{broken')
    cli('invalid-settings-fail-clearly', 'web-search', 'SYNTHETIC', ok=False)
    config.unlink()
    # A bulk operation must work when TMPDIR is not inherited.
    fixture = SCRATCH / 'SYNTHETIC.csv'
    fixture.write_text('id,amount\nSYNTHETIC-001,10.25\nSYNTHETIC-002,20.50\n')
    raw = json.loads(cli('bulk-without-tmpdir', 'bulk', 'ingest', str(fixture),
                         '--url', 'https://example.gov/SYNTHETIC', '--max-bytes', '1000').stdout)
    ds = json.loads(cli('convert-with-private-scratch', 'bulk', 'convert', raw['id'],
                        '--required', 'id', '--max-rows', '10', '--max-expanded-bytes', '1000').stdout)
    query = json.loads(cli('exact-synthetic-query', 'bulk', 'query', ds['id'],
                           '--column', 'id', '--equals', 'SYNTHETIC-001').stdout)
    assert query['total_matching'] == 1 and query['rows'][0]['amount'] == '10.25'
    cli('bulk-integrity', 'bulk', 'verify')
    demo = json.loads(run('offline-demo', [sys.executable, str(ROOT / 'scripts/demo.py'),
                                         '--home', str(SCRATCH / 'demo')]).stdout)
    assert demo['synthetic'] and demo['draft'] and not demo['submitted']
    assert demo['total'] == '30.75'
    # Release round-trip: inspect the exact distributable, not the used workspace.
    archive = SCRATCH / 'fraudresearch.zip'
    run('build-release', [sys.executable, str(ROOT / 'scripts/release.py'),
                          '--output', str(archive)])
    candidate = SCRATCH / 'candidate'
    shutil.unpack_archive(archive, candidate)
    check = ROOT / 'scripts/privacy_check.py'
    run('clean-payload', [sys.executable, str(check), '--root', str(candidate)])
    manifest = json.loads((candidate / 'release-manifest.json').read_text())
    assert manifest['files'] and all(not Path(p).is_absolute() for p in manifest['files'])
    assert len(list((candidate / 'skills').glob('*/SKILL.md'))) == 13
    # Explicitly approved generated graphics must be stripped of hidden metadata.
    for filename in ('eagle-mascot.webp', 'brand-logo.webp', 'social-card.webp'):
        relative = 'site/public/' + filename
        graphic = candidate / relative
        graphic_bytes = graphic.read_bytes()
        assert graphic_bytes[:4] == b'RIFF' and graphic_bytes[8:12] == b'WEBP'
        metadata = b'SYNTHETIC PRIVATE METADATA'
        chunk = b'EXIF' + len(metadata).to_bytes(4, 'little') + metadata
        if len(metadata) % 2:
            chunk += b'\0'
        injected = graphic_bytes + chunk
        injected = injected[:4] + (len(injected) - 8).to_bytes(4, 'little') + injected[8:]
        graphic.write_bytes(injected)
        manifest['files'][relative] = hashlib.sha256(injected).hexdigest()
        (candidate / 'release-manifest.json').write_text(json.dumps(manifest))
        run('graphic-metadata-rejected-' + filename,
            [sys.executable, str(check), '--root', str(candidate)], ok=False)
        graphic.write_bytes(graphic_bytes)
        manifest['files'][relative] = hashlib.sha256(graphic_bytes).hexdigest()
        (candidate / 'release-manifest.json').write_text(json.dumps(manifest))
    # Every injection is removed before the next, so each rejection is independent.
    for label, relative, content in [
        ('unexpected-file', 'notes.txt', 'private internal notes'),
        ('evidence-store', 'data/evidence.sqlite3', 'SYNTHETIC forbidden store'),
        ('credential-file', '.env', 'SYNTHETIC_KEY=not-a-real-key'),
        ('runtime-history', 'sessions/session.json', '{}'),
    ]:
        path = candidate / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        run(label, [sys.executable, str(check), '--root', str(candidate)], ok=False)
        path.unlink()
        while path.parent != candidate and not any(path.parent.iterdir()):
            parent = path.parent
            parent.rmdir()
            path = parent
    target = candidate / 'README.md'
    original = target.read_bytes()
    for label, addition in [
        ('personal-path', '\n/home/example-private-user/private-case\n'),
        ('private-address', '\nhttp://192.168.99.7:4567\n'),
        ('secret-marker', '\n-----BEGIN PRIVATE KEY-----\n'),
    ]:
        target.write_bytes(original + addition.encode())
        # Refresh only the checksum to prove content scanning, not just hash checking.
        manifest['files']['README.md'] = hashlib.sha256(target.read_bytes()).hexdigest()
        (candidate / 'release-manifest.json').write_text(json.dumps(manifest))
        run(label, [sys.executable, str(check), '--root', str(candidate)], ok=False)
    target.write_bytes(original)
    manifest['files']['README.md'] = hashlib.sha256(original).hexdigest()
    (candidate / 'release-manifest.json').write_text(json.dumps(manifest))
    target.write_bytes(original + b'\nSYNTHETIC unmanifested edit\n')
    run('checksum-tamper', [sys.executable, str(check), '--root', str(candidate)], ok=False)
    target.write_bytes(original)
    link = candidate / 'unexpected-link'
    link.symlink_to(SCRATCH / 'SYNTHETIC.csv')
    run('symlink-rejected', [sys.executable, str(check), '--root', str(candidate)], ok=False)
    link.unlink()
    run('restored-clean-payload', [sys.executable, str(check), '--root', str(candidate)])
    # Execute the code from the extracted release, not the developer source tree.
    clean_env = dict(ENV, PYTHONPATH=str(candidate / 'src'),
                     XDG_DATA_HOME=str(SCRATCH / 'installed-user-data'))
    run('extracted-cli', [sys.executable, '-m', 'fraudlab', 'init'], env=clean_env, cwd=candidate)
    run('extracted-demo', [sys.executable, str(candidate / 'scripts/demo.py'),
                            '--home', str(SCRATCH / 'extracted-demo')], env=clean_env, cwd=candidate)


if __name__ == '__main__':
    passed = False
    try:
        acceptance()
        passed = True
    finally:
        artifacts = ROOT / 'artifacts'
        artifacts.mkdir(exist_ok=True)
        receipt = artifacts / ('release-e2e-' + SCRATCH.name + '.json')
        receipt.write_text(json.dumps({'passed': passed, 'scratch': str(SCRATCH), 'events': EVENTS}, indent=2))
        print(json.dumps({'passed': passed, 'artifact': str(receipt), 'commands': len(EVENTS)}))
