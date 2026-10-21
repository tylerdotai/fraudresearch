"""Check an exact release payload: allowlist, content patterns and SHA256.

This is a release gate, not a comprehensive PII detector. Review all source text.
Do not run against a used checkout: build and inspect the clean ZIP payload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath

FORBIDDEN = {'data', 'artifacts', 'sessions', 'memories', 'logs', 'cache', '.git', '.venv',
             '__pycache__', 'cron', 'vault', 'mcp-tokens', 'node_modules', 'backups'}
BINARY_GRAPHICS = {'site/public/eagle-mascot.webp', 'site/public/nous-mascot.webp',
                   'site/public/community-duo.webp', 'site/public/patriotic-banner.webp',
                   'site/public/brand-logo.webp', 'site/public/social-card.webp',
                   'site/public/repo-banner.webp'}
PATTERNS = {
    'personal-home-path': r'/(?:home|Users)/[A-Za-z0-9_.-]+',
    'windows-home-path': r'[A-Za-z]:\\(?:Users|Documents and Settings)\\[^\\\s]+',
    'internal-ip': r'(?<![\d.])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![\d.])',
    'private-key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'github-token': r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}',
    'aws-access-key': r'AKIA[A-Z0-9]{16}',
    'provider-key': r'\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}',
}
# These exact negative fixtures are code examples, not real private data.
# Exemption applies only to this named test, not to README or other payloads.
SYNTHETIC_TEST_LITERALS = (
    '/home/example-private-user/private-case', 'http://192.168.99.7:4567',
    '-----BEGIN PRIVATE KEY-----',
)


def clean_webp(raw: bytes) -> bool:
    """Accept only a single WebP image bitstream with no EXIF, XMP, ICC or animation chunks."""
    if (len(raw) < 20 or raw[:4] != b'RIFF' or raw[8:12] != b'WEBP'
            or int.from_bytes(raw[4:8], 'little') != len(raw) - 8):
        return False
    offset = 12
    images = 0
    while offset < len(raw):
        if len(raw) - offset < 8:
            return False
        tag = raw[offset:offset + 4]
        size = int.from_bytes(raw[offset + 4:offset + 8], 'little')
        end = offset + 8 + size
        if tag not in (b'VP8 ', b'VP8L', b'VP8X', b'ALPH') or end > len(raw):
            return False
        if tag in (b'VP8 ', b'VP8L'):
            images += 1
        if tag == b'VP8X' and (size != 10 or raw[offset + 8] & 0x2e):
            return False
        offset = end + size % 2
    return offset == len(raw) and images == 1


def file_list(root: Path) -> list[str]:
    items = json.loads((root / 'release-files.json').read_text())
    if not isinstance(items, list) or not items or len(items) != len(set(items)):
        raise ValueError('Invalid or duplicated release file list')
    for item in items:
        path = PurePosixPath(item)
        if path.is_absolute() or '..' in path.parts or '\\' in item or item != path.as_posix():
            raise ValueError('Unsafe release path')
        if any(part in FORBIDDEN for part in path.parts):
            raise ValueError('Runtime/private path in release list')
        if not (root / item).resolve().is_relative_to(root.resolve()):
            raise ValueError('Release path escapes root')
    return items


def check(root: Path) -> dict:
    root = root.resolve()
    allowed = set(file_list(root))
    expected = allowed | {'release-manifest.json'}
    errors = []
    actual = set()
    for path in root.rglob('*'):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append(relative + ': symlink rejected')
        if path.is_file():
            actual.add(relative)
        if any(part in FORBIDDEN for part in path.relative_to(root).parts):
            errors.append(relative + ': runtime/private path rejected')
    if actual != expected:
        errors.append('Unexpected or missing files: ' + repr(sorted(actual ^ expected)))
    manifest = json.loads((root / 'release-manifest.json').read_text())
    hashes = manifest.get('files', {})
    if set(hashes) != allowed:
        errors.append('Manifest does not exactly match the reviewed file list')
    markers = json.loads(os.environ.get('FRAUDRESEARCH_PRIVATE_MARKERS', '[]'))
    account = os.environ.get('FRAUDRESEARCH_PUBLIC_ACCOUNT', '')
    for relative in sorted(actual & expected):
        path = root / relative
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            continue
        if path.stat().st_size > 4_000_000:
            errors.append(relative + ': text-size budget exceeded')
            continue
        raw = path.read_bytes()
        if relative in allowed and hashlib.sha256(raw).hexdigest() != hashes.get(relative):
            errors.append(relative + ': checksum mismatch')
        if relative in BINARY_GRAPHICS:
            if not clean_webp(raw):
                errors.append(relative + ': graphic metadata or invalid WebP rejected')
            continue
        try:
            text = raw.decode('utf-8')
        except UnicodeError:
            errors.append(relative + ': non-text payload rejected')
            continue
        # Test source explicitly documents negative fixtures; copied data elsewhere does not get this exemption.
        if relative in ('tests/release_e2e.py', 'scripts/privacy_check.py'):
            for literal in SYNTHETIC_TEST_LITERALS:
                text = text.replace(literal, '[SYNTHETIC NEGATIVE FIXTURE]')
        for label, pattern in PATTERNS.items():
            if re.search(pattern, text):
                errors.append(relative + ': ' + label)
        if account:
            text = re.sub(r'(?:https://(?:github\.com|raw\.githubusercontent\.com)|github\.com)/'
                          + re.escape(account) + '/', '[APPROVED PUBLIC REPOSITORY]/', text)
            text = text.replace('https://' + account + '.github.io/', '[APPROVED PUBLIC WEBSITE]/')
        if any(str(marker).casefold() in text.casefold() for marker in markers):
            errors.append(relative + ': private review marker')
    return {'passed': not errors, 'files': len(actual), 'errors': errors,
            'scope': 'exact allowlist, text patterns, reviewed metadata-free graphics and SHA256; manual review required'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(args.root)
    except (OSError, ValueError, TypeError) as exc:
        result = {'passed': False, 'errors': [str(exc)]}
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
