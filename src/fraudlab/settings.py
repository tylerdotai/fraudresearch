"""Portable user-owned settings; no credentials or developer service defaults."""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlsplit


def data_home() -> Path:
    override = os.environ.get('FRAUDLAB_HOME')
    if override:
        return Path(override).expanduser().resolve()
    base = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local' / 'share')))
    return (base / 'fraudresearch').expanduser().resolve()


def scratch_dir() -> Path:
    override = os.environ.get('TMPDIR')
    path = Path(override).expanduser() if override else data_home() / 'scratch'
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path.resolve()


def config_path() -> Path:
    base = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
    return base.expanduser() / 'fraudresearch' / 'services.json'


def service_url(kind: str, explicit: str | None = None) -> str:
    value = explicit
    if value is None:
        path = config_path()
        if not path.is_file():
            raise ValueError('Configure your own loopback services in ' + str(path) + '; no fallback is enabled')
        if path.stat().st_size > 16384:
            raise ValueError('Service settings exceed 16KB')
        try:
            settings = json.loads(path.read_text())
        except (ValueError, UnicodeError) as exc:
            raise ValueError('Invalid JSON service settings') from exc
        if not isinstance(settings, dict):
            raise ValueError('Service settings must be a JSON object')
        value = settings.get(kind + '_url')
    if not isinstance(value, str) or not value:
        raise ValueError('Missing configured service: ' + kind)
    parsed = urlsplit(value)
    if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1'
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ('', '/') or parsed.port is None):
        raise ValueError('Service URL must be credential-free HTTP on literal loopback with an explicit port')
    return value.rstrip('/')
