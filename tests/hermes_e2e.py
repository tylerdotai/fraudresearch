"""Install the exact release in a disposable Hermes home; no model calls.

Run with an existing Hermes source installation:
uv run python tests/hermes_e2e.py --hermes-source /path/to/hermes-agent
Native runtime loading is installation-specific; no packages are installed into Hermes.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hermes-source', type=Path, required=True)
    parser.add_argument('--services-file', type=Path, help='Optional private loopback settings for live acceptance')
    args = parser.parse_args()
    source = args.hermes_source.resolve()
    if not (source / 'hermes_cli/_launchers.py').is_file():
        raise SystemExit('An installed Hermes source checkout is required')
    sys.path.insert(0, str(source))
    from hermes_cli._launchers import runtime_command

    base = Path(os.environ.get('TMPDIR', str(Path.home() / '.cache' / 'fraudresearch' / 'acceptance')))
    base.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix='fraudresearch-hermes-', dir=base))
    private_home = scratch / 'user'
    hermes_home = scratch / 'isolated-hermes'
    env = {k: v for k, v in os.environ.items() if k in ('PATH', 'LANG', 'LC_ALL', 'UV_CACHE_DIR')}
    env.update(HOME=str(private_home), HERMES_HOME=str(hermes_home), TMPDIR=str(scratch),
               XDG_DATA_HOME=str(scratch / 'user-data'), XDG_CONFIG_HOME=str(scratch / 'user-config'),
               PYTHONDONTWRITEBYTECODE='1')
    events = []

    def run(label, command, selected_env=None):
        proc = subprocess.run(command, env=selected_env or env, capture_output=True, text=True,
                              timeout=240, check=False)
        events.append({'label': label, 'exit_code': proc.returncode,
                       'stdout': proc.stdout, 'stderr': proc.stderr})
        assert proc.returncode == 0, events[-1]
        return proc

    passed = False
    try:
        boundary = ("from pathlib import Path; from hermes_constants import get_default_hermes_root; "
                    f"assert get_default_hermes_root() == Path({str(hermes_home)!r}); "
                    "print('isolated-home-boundary-verified')")
        run('verify-isolation-before-install', runtime_command(source, code=boundary, home=hermes_home))
        archive = scratch / 'candidate.zip'
        # Build subprocess inherits only a clean environment, never another profile's secrets.
        run('build-exact-candidate', [sys.executable, str(ROOT / 'scripts/release.py'), '--output', str(archive)])
        candidate = scratch / 'candidate'
        shutil.unpack_archive(archive, candidate)
        run('install-distribution', runtime_command(source, args=['profile', 'install', str(candidate), '-y'],
                                                   home=hermes_home))
        installed = hermes_home / 'profiles' / 'fraudresearch-starter'
        assert (installed / 'src/fraudlab/settings.py').is_file()
        assert (installed / 'plugins/web/research_local/__init__.py').is_file()
        assert len(list((installed / 'skills').glob('*/SKILL.md'))) == 13
        assert not (installed / 'data').exists()
        assert not list((installed / 'cron').glob('*.json'))
        run('sync-installed-workbench', ['uv', 'sync', '--frozen', '--project', str(installed)])
        selected = dict(env, HERMES_HOME=str(installed))
        code = '''import json
from pathlib import Path
from hermes_constants import get_hermes_home
from tools.skill_manager_tool import _validate_content_size, _validate_frontmatter
from tools.web_tools import _get_extract_backend, _get_search_backend, web_search_tool
home = get_hermes_home()
assert _get_search_backend() == _get_extract_backend() == 'research-local'
for path in (home / 'skills').glob('*/SKILL.md'):
    text = path.read_text()
    assert not _validate_frontmatter(text, new_skill=True), path.name
    assert not _validate_content_size(text), path.name
result = json.loads(web_search_tool('SYNTHETIC provider check', limit=1))
assert not result.get('success'), result
assert 'Configure your own loopback services' in result.get('error', ''), result
print(json.dumps({'passed': True, 'skills': 13, 'provider': 'research-local',
                  'unconfigured_service_rejected': True, 'model_calls': 0}))
'''
        run('native-skills-and-provider', runtime_command(source, code=code, home=installed), selected)
        if args.services_file:
            service_settings = Path(env['XDG_CONFIG_HOME']) / 'fraudresearch' / 'services.json'
            service_settings.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(args.services_file, service_settings)
            live_code = '''import asyncio, json
from tools.web_tools import web_extract_tool, web_search_tool
search = json.loads(web_search_tool('Medicare hospice', limit=2))
assert search.get('success') and search['data']['web'], search
assert not search.get('rescued_from'), search
extracted = json.loads(asyncio.run(web_extract_tool(
    ['https://opendata.hhs.gov/datasets/medicaid-provider-spending/'], char_limit=20000)))
assert 'TOTAL_CLAIM_LINES' in extracted['results'][0]['content'], extracted
assert not extracted['results'][0].get('error'), extracted
print(json.dumps({'passed': True, 'native_live_search': True, 'native_live_extract': True, 'model_calls': 0}))
'''
            run('native-live-web', runtime_command(source, code=live_code, home=installed), selected)
        run('installed-offline-demo', ['uv', 'run', '--frozen', '--project', str(installed),
                                      'python', str(installed / 'scripts/demo.py'),
                                      '--home', str(scratch / 'synthetic-demo')], selected)
        passed = True
    finally:
        artifact = ROOT / 'artifacts' / (scratch.name + '.json')
        artifact.parent.mkdir(exist_ok=True)
        artifact.write_text(json.dumps({'passed': passed, 'events': events, 'scratch': str(scratch)}, indent=2))
        print(json.dumps({'passed': passed, 'commands': len(events), 'artifact': str(artifact)}))


if __name__ == '__main__':
    main()
