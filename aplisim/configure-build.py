#!/usr/bin/env python3
"""Configure an exported source tree before compilation; never include private keys."""
import base64
import json
import os
from pathlib import Path
import re


def configuration(mode, host, key):
    if mode == 'preview':
        return 'aplisim-preview.invalid', base64.b64encode(bytes(32)).decode()
    if mode != 'configured':
        raise ValueError('Unknown build mode')
    host, key = host.strip().lower(), key.strip()
    parts = host.split('.')
    ipv4 = len(parts) == 4 and all(re.fullmatch(r'0|[1-9][0-9]{0,2}', p) and int(p) <= 255 for p in parts)
    domain = len(parts) >= 2 and re.fullmatch(r'[a-z]{2,63}', parts[-1]) and all(
        re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', p) for p in parts)
    if len(host) > 253 or not (ipv4 or domain):
        raise ValueError('Set APLISIM_SERVER to a domain or IPv4 without protocol or port')
    try:
        decoded = base64.b64decode(key, validate=True)
    except ValueError as exc:
        raise ValueError('Invalid APLISIM_PUBLIC_KEY') from exc
    if len(decoded) != 32 or base64.b64encode(decoded).decode() != key:
        raise ValueError('APLISIM_PUBLIC_KEY must be a canonical 32-byte Ed25519 public key')
    return host, key


def patch(path, replacements):
    content = path.read_text()
    for pattern, value in replacements.items():
        content, count = re.subn(pattern, lambda _: value, content)
        if count != 1:
            raise ValueError('Unexpected upstream configuration; refusing to build')
    return content


def configure(root, mode, host='', key=''):
    host, key = configuration(mode, host, key)
    config_path = root / 'libs/hbb_common/src/config.rs'
    common_path = root / 'src/common.rs'
    config_content = patch(config_path, {
        r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[[^\n]+\];':
            f'pub const RENDEZVOUS_SERVERS: &[&str] = &[{json.dumps(host)}];',
        r'pub const RS_PUB_KEY: &str = "[^"\n]+";':
            f'pub const RS_PUB_KEY: &str = {json.dumps(key)};',
    })
    # Without this, clients with a built-in server report to admin.rustdesk.com instead of
    # the Aplisim admin API, which nginx serves over HTTPS on the same host.
    common_content = patch(common_path, {
        r'(?m)^    "https://[^"\n]+"\.to_owned\(\)\n\}\n\n#\[inline\]\npub fn is_public':
            f'    "https://{host}".to_owned()\n}}\n\n#[inline]\npub fn is_public',
        # The built-in server is Aplisim's own, not RustDesk's public one: no "set up your own
        # server" tip and no public-server limits on image quality or registration backoff.
        r'(?m)^pub fn using_public_server\(\) -> bool \{\n    [^\n]+\n\}':
            'pub fn using_public_server() -> bool {\n    false\n}',
    })
    config_path.write_text(config_content)
    common_path.write_text(common_content)
    metadata = json.dumps({
        'app': 'Aplisim', 'mode': mode, 'server': host, 'apiServer': f'https://{host}', 'publicKey': key,
        'signed': False, 'connectionTested': False,
    }, indent=2) + '\n'
    (root / 'aplisim-build.json').write_text(metadata)
    assets = root / 'flutter/assets'
    assets.mkdir(parents=True, exist_ok=True)
    (assets / 'aplisim-build.json').write_text(metadata)


if __name__ == '__main__':
    configure(Path(__file__).resolve().parents[1], os.environ.get('APLISIM_BUILD_MODE', 'preview'),
              os.environ.get('APLISIM_SERVER', ''), os.environ.get('APLISIM_PUBLIC_KEY', ''))
    print('Aplisim build configuration applied. Preview builds use a reserved .invalid host.')
