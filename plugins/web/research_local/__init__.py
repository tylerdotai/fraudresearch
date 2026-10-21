"""Portable Hermes adapter; workbench dependencies stay in their own uv environment."""
import json
import shutil
import subprocess
from pathlib import Path

from agent.web_search_provider import WebSearchProvider

ROOT = Path(__file__).resolve().parents[3]


class ResearchLocalProvider(WebSearchProvider):
    @property
    def name(self):
        return 'research-local'

    @property
    def display_name(self):
        return 'FraudResearch: configured local search and public .gov extraction'

    def is_available(self):
        return (ROOT / 'pyproject.toml').is_file() and shutil.which('uv') is not None

    def supports_extract(self):
        return True

    def call(self, *args):
        executable = shutil.which('uv')
        if not executable:
            raise ValueError('Install uv and sync the workbench before using this provider')
        proc = subprocess.run([executable, 'run', '--frozen', '--project', str(ROOT), 'fraudlab', *args],
                              capture_output=True, text=True, timeout=240, check=False)
        try:
            value = json.loads(proc.stdout)
        except ValueError as exc:
            raise ValueError('Workbench did not return JSON; check your local installation') from exc
        if proc.returncode or 'error' in value:
            raise ValueError(value.get('error', 'Workbench command failed'))
        return value

    def search(self, query, limit=5):
        try:
            return self.call('web-search', query, '--limit', str(limit))
        except (ValueError, OSError, subprocess.SubprocessError) as exc:
            return {'success': False, 'error': str(exc)}

    def extract(self, urls, **kwargs):
        if isinstance(urls, str):
            urls = [urls]
        if not 1 <= len(urls) <= 5:
            return [{'url': '', 'title': '', 'content': '', 'error': 'Supply one to five public official URLs'}]
        results = []
        for url in urls:
            try:
                receipt = self.call('web-extract', url)
                results.append({'url': url, 'title': url, 'content': receipt['content'],
                                'raw_content': receipt['content'],
                                'metadata': {k: v for k, v in receipt.items() if k != 'content'}})
            except (ValueError, OSError, subprocess.SubprocessError) as exc:
                results.append({'url': url, 'title': '', 'content': '', 'error': str(exc)})
        return results


def register(ctx):
    ctx.register_web_search_provider(ResearchLocalProvider())
