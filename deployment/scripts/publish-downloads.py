#!/usr/bin/env python3
"""Copy configured client packages into server/download/files for remote.aplisim.com/download."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
FILES = ROOT / 'server/download/files'
PACKAGES = {
    'windows': ('aplisim-windows-x64-configured/Aplisim-windows-x64.exe', 'Aplisim-Windows-x64.exe'),
    'mac-arm': ('aplisim-macos-aarch64-configured/Aplisim-macos-aarch64.dmg', 'Aplisim-macOS-AppleSilicon.dmg'),
    'mac-intel': ('aplisim-macos-x86_64-configured/Aplisim-macos-x86_64.dmg', 'Aplisim-macOS-Intel.dmg'),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('packages', type=Path, help='directory with the downloaded configured build artifacts')
    args = parser.parse_args()
    version = json.loads((ROOT / 'client/UPSTREAM.json').read_text())['tag']
    FILES.mkdir(parents=True, exist_ok=True)
    listing, sums = {}, []
    for key, (source, name) in PACKAGES.items():
        source = args.packages / source
        build = json.loads((source.parent / 'aplisim-build.json').read_text())
        # Only packages built for the Aplisim server may be offered to customers.
        if build.get('mode') != 'configured' or build.get('server') != 'remote.aplisim.com':
            raise SystemExit(f'{source} is not a configured remote.aplisim.com build')
        target = FILES / name
        shutil.copyfile(source, target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        listing[key] = {'file': name, 'size': f'{target.stat().st_size / 1e6:.0f} MB',
                        'sha256': digest, 'version': version}
        sums.append(f'{digest}  {name}')
    (FILES / 'SHA256SUMS').write_text('\n'.join(sums) + '\n')
    (FILES / 'downloads.json').write_text(json.dumps(listing, indent=2) + '\n')
    print(f'Prepared {len(listing)} packages in {FILES}')


if __name__ == '__main__':
    main()
