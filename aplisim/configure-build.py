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


def access_password(mode, password):
    """The fixed permanent password that lets Aplisim connect unattended.

    Returned base64-encoded for safe embedding in the Rust source (no quoting or
    escaping concerns); the client decodes it back at startup. Preview builds have
    no password and no unattended access.
    """
    if mode != 'configured':
        return ''
    password = password.strip()
    if len(password) < 8:
        raise ValueError('Set APLISIM_ACCESS_PASSWORD to the unattended-access password (>= 8 chars)')
    return base64.b64encode(password.encode()).decode()


def patch(path, replacements):
    content = path.read_text()
    for pattern, value in replacements.items():
        content, count = re.subn(pattern, lambda _: value, content)
        if count != 1:
            raise ValueError('Unexpected upstream configuration; refusing to build')
    return content


# Injected into load_custom_client() so every Aplisim process (UI, service, flutter)
# forces unattended support access and seeds the fixed permanent password at startup.
# RustDesk's own custom.txt mechanism is signed with RustDesk's private key, so it is
# unusable for a self-built client; we configure the same settings in source instead.
UNATTENDED_RUST = '''pub fn load_custom_client() {
    // Aplisim: enforce unattended support access (injected at build time).
    {
        let mut ow = config::OVERWRITE_SETTINGS.write().unwrap();
        ow.insert("approve-mode".to_owned(), "password".to_owned());
        ow.insert("verification-method".to_owned(), "use-permanent-password".to_owned());
        ow.insert("allow-hide-cm".to_owned(), "Y".to_owned());
    }
    if let Ok(aplisim_pw_bytes) = decode64("__APLISIM_PW_B64__") {
        if let Ok(aplisim_pw) = String::from_utf8(aplisim_pw_bytes) {
            if !aplisim_pw.is_empty() {
                Config::set_permanent_password(&aplisim_pw);
            }
        }
    }
'''

# Injected at the end of the desktop home page's initState: a one-time consent
# dialog shown on first launch, disclosing the persistent access and autostart.
CONSENT_DART = '''    WidgetsBinding.instance.addObserver(this);
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (bind.mainGetLocalOption(key: "aplisim-consent-shown") == "Y") return;
      await bind.mainSetLocalOption(key: "aplisim-consent-shown", value: "Y");
      gFFI.dialogManager.show((setState, close, context) {
        return CustomAlertDialog(
          title: Text("Aplisim Remote Support"),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                  "By continuing you allow Aplisim support staff to connect to and control this computer at any time to provide remote assistance."),
              SizedBox(height: 10),
              Text(
                  "Aplisim starts automatically with this computer so support is always available. To revoke access, uninstall the Aplisim app."),
            ],
          ),
          actions: [dialogButton("I agree", onPressed: close)],
        );
      });
    });
  }'''


def configure(root, mode, host='', key='', password=''):
    host, key = configuration(mode, host, key)
    pw_b64 = access_password(mode, password)
    config_path = root / 'libs/hbb_common/src/config.rs'
    common_path = root / 'src/common.rs'
    home_path = root / 'flutter/lib/desktop/pages/desktop_home_page.dart'
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

    if mode == 'configured':
        # Seed the unattended-access settings and the fixed permanent password.
        common_path.write_text(patch(common_path, {
            r'pub fn load_custom_client\(\) \{\n':
                UNATTENDED_RUST.replace('__APLISIM_PW_B64__', pw_b64),
        }))
        # One-time consent dialog on first launch.
        home_path.write_text(patch(home_path, {
            r'    WidgetsBinding\.instance\.addObserver\(this\);\n  \}': CONSENT_DART,
        }))

    metadata = json.dumps({
        'app': 'Aplisim', 'mode': mode, 'server': host, 'apiServer': f'https://{host}', 'publicKey': key,
        'signed': False, 'connectionTested': False,
        'unattendedAccess': mode == 'configured', 'accessPasswordSet': bool(pw_b64),
    }, indent=2) + '\n'
    (root / 'aplisim-build.json').write_text(metadata)
    assets = root / 'flutter/assets'
    assets.mkdir(parents=True, exist_ok=True)
    (assets / 'aplisim-build.json').write_text(metadata)


if __name__ == '__main__':
    configure(Path(__file__).resolve().parents[1], os.environ.get('APLISIM_BUILD_MODE', 'preview'),
              os.environ.get('APLISIM_SERVER', ''), os.environ.get('APLISIM_PUBLIC_KEY', ''),
              os.environ.get('APLISIM_ACCESS_PASSWORD', ''))
    print('Aplisim build configuration applied. Preview builds use a reserved .invalid host.')
