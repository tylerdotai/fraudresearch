"""Existing loopback SearXNG/Crawl4AI services; public official pages only for extraction."""
from __future__ import annotations

import ipaddress
import json
import socket
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from . import digest, now
from .settings import service_url


def public_url(url: str) -> None:
    u = urlsplit(url)
    host = u.hostname or ''
    if u.scheme != 'https' or not host.endswith('.gov') or u.username or u.password or u.port not in (None, 443):
        raise ValueError('Only credential-free public .gov HTTPS URLs at port 443 are accepted')
    addresses = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(r[4][0]).is_global for r in addresses):
        raise ValueError('Non-public destination rejected')


def local_service(url: str) -> str:
    u = urlsplit(url)
    if u.scheme != 'http' or u.hostname != '127.0.0.1' or u.username or u.password or u.query or u.fragment:
        raise ValueError('Research service must be credential-free HTTP on literal loopback 127.0.0.1')
    return url.rstrip('/')


def bounded_get(url: str, target: Path, max_bytes: int, seconds: int = 120) -> dict[str, Any]:
    """Stream to an exclusive temporary file; callers commit it only after complete success."""
    if not 0 < max_bytes <= 5_000_000_000:
        raise ValueError('max-bytes must be 1..5000000000')
    start = time.monotonic()
    requested = url
    with httpx.Client(timeout=httpx.Timeout(30, connect=15), follow_redirects=False,
                      trust_env=False, headers={'User-Agent': 'FraudResearchWorkbench/0.2 public-record-study',
                                               'Accept-Encoding': 'identity'}) as client:
        for _ in range(6):
            public_url(url)
            with client.stream('GET', url) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    url = urljoin(url, response.headers.get('location', ''))
                    continue
                response.raise_for_status()
                if int(response.headers.get('content-length', '0')) > max_bytes:
                    raise ValueError('Response exceeds byte budget')
                if response.headers.get('content-encoding', 'identity') not in ('', 'identity'):
                    raise ValueError('Unexpected HTTP content encoding; preserve unencoded original bytes')
                import hashlib
                h = hashlib.sha256()
                size = 0
                with target.open('xb') as output:
                    for chunk in response.iter_raw(chunk_size=65536):
                        size += len(chunk)
                        if size > max_bytes or time.monotonic() - start > seconds:
                            raise ValueError('Response exceeds byte/time budget; partial not acquired')
                        output.write(chunk)
                        h.update(chunk)
                if not size:
                    raise ValueError('Empty response')
                return {'requested_url': requested, 'final_url': str(response.url),
                        'status': response.status_code, 'bytes': size, 'sha256': h.hexdigest(),
                        'retrieved_at': now(), 'content_type': response.headers.get('content-type', ''),
                        'etag': response.headers.get('etag'), 'last_modified': response.headers.get('last-modified')}
    raise ValueError('Redirect budget exceeded')


def search(query: str, limit: int = 5, endpoint: str | None = None) -> dict[str, Any]:
    if not query.strip() or not 1 <= limit <= 20:
        raise ValueError('Nonempty query and limit 1..20 required')
    r = httpx.get(service_url('searxng', endpoint) + '/search',
                  params={'q': query, 'format': 'json', 'pageno': 1, 'engines': 'google,bing'},
                  timeout=30, follow_redirects=False, trust_env=False)
    r.raise_for_status()
    data = r.json()
    rows = data.get('results', [])
    if not isinstance(rows, list) or not rows:
        raise ValueError('SearXNG returned no results; engine warnings: ' + str(data.get('unresponsive_engines')))
    return {'success': True, 'backend': 'local-searxng', 'retrieved_at': now(),
            'warnings': data.get('unresponsive_engines', []), 'data': {'web': [
                {'url': row.get('url', ''), 'title': row.get('title', ''),
                 'description': row.get('content', ''), 'position': i + 1}
                for i, row in enumerate(rows[:limit])]},
            'coverage': 'bounded search results, not exhaustive public-record coverage'}


def crawl_response(url: str, endpoint: str, path: Path) -> dict[str, Any]:
    payload = {'urls': [url], 'browser_config': {'type': 'BrowserConfig', 'params': {'headless': True}},
               'crawler_config': {'type': 'CrawlerRunConfig', 'params': {
                   'page_timeout': 45000, 'check_robots_txt': True, 'delay_before_return_html': 2.0}}}
    with httpx.stream('POST', local_service(endpoint) + '/crawl', json=payload, timeout=75,
                      follow_redirects=False, trust_env=False) as response:
        size = 0
        with path.open('xb') as f:
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > 20000000:
                    raise ValueError('Crawl4AI response exceeds 20MB transformation budget')
                f.write(chunk)
        response.raise_for_status()
    result: dict[str, Any] = json.loads(path.read_bytes())
    return result


def extract(url: str, root: Path, endpoint: str | None = None) -> dict[str, Any]:
    endpoint = service_url('crawl4ai', endpoint)
    public_url(url)
    root = root / 'web-acquisitions' / str(time.time_ns())
    root.mkdir(parents=True, mode=0o700)
    receipt: dict[str, Any] = {'url': url, 'at': now(), 'state': 'attempted'}
    try:
        original = root / 'original.response'
        receipt.update(bounded_get(url, original, 10_000_000, 60))
        if original.read_bytes().startswith(b'%PDF-'):
            proc = subprocess.run(['pdftotext', '-layout', str(original), '-'],
                                  capture_output=True, timeout=30, check=False)
            response = root / 'pdftotext.response.json'
            response.write_text(json.dumps({'returncode': proc.returncode,
                                            'stderr': proc.stderr.decode('utf-8', errors='replace')}))
            receipt.update(response_path=str(response), response_sha256=digest(response.read_bytes()))
            content = proc.stdout.decode('utf-8', errors='strict')
            if proc.returncode or not content.strip():
                receipt['failure_kind'] = 'extraction_failed' if proc.returncode else 'needs_ocr'
                raise ValueError('PDF extraction failed or needs_ocr; no text fabricated')
            text = root / 'extracted.txt'
            text.write_text(content)
            receipt.update(state='extracted', backend='pdftotext', original_path=str(original),
                           text_path=str(text), text_sha256=digest(content.encode()),
                           transformation='pdftotext -layout; PDF page breaks retained; no browser required')
            (root / 'receipt.json').write_text(json.dumps(receipt, indent=2))
            return {**receipt, 'content': content}
        # Do not send an explicit access/challenge response to a rendering service.
        prefix = original.read_bytes()[:30000].decode('utf-8', errors='replace').lower()
        if any(t in prefix for t in ['<title>access denied', '<title>just a moment', '<title>sign in']):
            raise ValueError('Access/challenge page rejected; no bypass attempted')
        response = root / 'crawl4ai.response.json'
        receipt['response_path'] = str(response)
        data = crawl_response(receipt['final_url'], service_url('crawl4ai', endpoint), response)
        receipt['response_sha256'] = digest(response.read_bytes())
        results = data.get('results', [])
        if not data.get('success') or len(results) != 1:
            raise ValueError('Crawl4AI failed or returned wrong result count')
        page = results[0]
        if not page.get('success') or page.get('status_code', 0) != 200:
            raise ValueError('Page extraction failed: ' + str(page.get('error_message', page.get('status_code'))))
        final = page.get('redirected_url') or page.get('url') or url
        public_url(final)
        md = page.get('markdown')
        content = md.get('raw_markdown', '') if isinstance(md, dict) else (md or '')
        if len(content.strip()) < 100 or any(x in content[:500].lower() for x in ['access denied', 'verify you are human']):
            raise ValueError('Empty or challenge extraction; not evidence')
        text = root / 'rendered.md'
        text.write_text(content)
        receipt.update(state='extracted', backend='crawl4ai', original_path=str(original), text_path=str(text),
                       text_sha256=digest(content.encode()), rendered_url=final,
                       transformation='Crawl4AI browser-rendered markdown; not original HTTP bytes',
                       network_boundary='DNS preflight, not hardened browser/subresource egress isolation')
        (root / 'receipt.json').write_text(json.dumps(receipt, indent=2))
        return {**receipt, 'content': content}
    except (ValueError, OSError, httpx.HTTPError, subprocess.SubprocessError) as exc:
        receipt.update(state='failed', error=str(exc))
        (root / 'receipt.json').write_text(json.dumps(receipt, indent=2))
        raise ValueError(str(exc)) from exc
