"""Build an allowlisted source-and-reviewed-graphics release; verify its exact ZIP contents."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from privacy_check import check, file_list

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='New ZIP outside the source checkout')
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.is_relative_to(ROOT) or output.exists():
        raise SystemExit('Choose a new output path outside the source checkout')
    files = sorted(file_list(ROOT))
    base = Path(os.environ.get('TMPDIR', str(Path.home() / '.cache' / 'fraudresearch' / 'releases')))
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix='fraudresearch-release-', dir=base) as scratch:
        stage = Path(scratch) / 'payload'
        stage.mkdir()
        hashes = {}
        for relative in files:
            source = ROOT / relative
            if not source.is_file() or source.is_symlink() or any(p.is_symlink() for p in source.parents):
                raise ValueError('Missing or symlinked release source: ' + relative)
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            hashes[relative] = hashlib.sha256(destination.read_bytes()).hexdigest()
        manifest_text = json.dumps({'schema': 1, 'files': hashes}, indent=2, sort_keys=True) + '\n'
        (stage / 'release-manifest.json').write_text(manifest_text)
        verdict = check(stage)
        if not verdict['passed']:
            raise ValueError(json.dumps(verdict))
        output.parent.mkdir(parents=True, exist_ok=True)
        # No local paths, uid/gid, original mtimes or machine metadata in the archive.
        with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(p for p in stage.rglob('*') if p.is_file()):
                entry = zipfile.ZipInfo(path.relative_to(stage).as_posix(), date_time=(2020, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.create_system = 3
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, path.read_bytes())
        unpacked = Path(scratch) / 'unpacked'
        with zipfile.ZipFile(output) as archive:
            archive.extractall(unpacked)
        verified = check(unpacked)
        if not verified['passed']:
            raise ValueError('Final archive validation failed: ' + json.dumps(verified))
        # The same manifest is checked in so the public Git tree can be compared.
        (ROOT / 'release-manifest.json').write_text(manifest_text)
        print(json.dumps({'passed': True, 'files': verified['files'],
                          'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                          'output': str(output)}, indent=2))


if __name__ == '__main__':
    main()
