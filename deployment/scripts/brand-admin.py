#!/usr/bin/env python3
"""Rebrand the rustdesk-api admin panel as Aplisim; rerun after changing RUSTDESK_API_IMAGE."""
import base64
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / 'server'
OUTPUT = SERVER / 'admin-branding'
LOGO = SERVER / 'branding/icon-128.png'
FAVICON = SERVER / 'branding/app.ico'


def image():
    for line in (SERVER / '.env').read_text().splitlines():
        if line.startswith('RUSTDESK_API_IMAGE='):
            return line.split('=', 1)[1].strip()
    raise SystemExit('Set RUSTDESK_API_IMAGE in server/.env')


def replace_once(path, pattern, value):
    content, count = re.subn(pattern, lambda _: value, path.read_text())
    if count != 1:
        raise SystemExit(f'Unexpected admin panel layout in {path.name}; refusing to rebrand')
    path.write_text(content)


def main():
    with tempfile.TemporaryDirectory() as directory:
        admin = Path(directory) / 'admin'
        container = subprocess.check_output(['docker', 'create', image()], text=True).strip()
        try:
            subprocess.run(['docker', 'cp', f'{container}:/app/resources/admin', str(admin)], check=True)
        finally:
            subprocess.run(['docker', 'rm', container], check=True, stdout=subprocess.DEVNULL)
        [entry] = (admin / 'static/entry').glob('index-*.js')
        logo = 'data:image/png;base64,' + base64.b64encode(LOGO.read_bytes()).decode()
        # The upstream sidebar logo is the only inline 128x128 PNG in the bundle.
        replace_once(entry, r'"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIAAAACA[A-Za-z0-9+/=]+"', f'"{logo}"')
        replace_once(entry, r'title:"Rustdesk API Admin"', 'title:"Aplisim Admin"')
        replace_once(admin / 'index.html', r'<title>Rustdesk API Admin</title>', '<title>Aplisim Admin</title>')
        # "Open in client" must launch the Aplisim app, which registers its own URL scheme.
        [peer] = [p for p in (admin / 'static/chunk').glob('*.js') if 'rustdesk://${' in p.read_text()]
        replace_once(peer, r'`rustdesk://\$\{', '`aplisim://${')
        # Show the active language code (EN, FR, ...) instead of the static CJK translate glyph.
        [header] = [p for p in (admin / 'static/chunk').glob('*.js') if 'm18.5 10l4.4 11h' in p.read_text()]
        replace_once(
            header,
            r'm\[(\d+)\]\|\|\(m\[\1\]=h\("div",\{class:"title"\},\[h\("i",\{class:"el-icon el-tooltip__trigger"'
            r'[^\]]*\[h\("svg",\{[^}]*\},\[h\("path",\{fill:"currentColor",d:"m18\.5 10l4\.4 11h[^"]*"\}\)\]\)\]\)\],-1\)\)',
            'h("div",{class:"title",style:{"font-size":"14px","font-weight":"600","letter-spacing":"0.5px"}},'
            'v(g(c).setting.lang.split("-")[0].toUpperCase()),1)')
        shutil.copyfile(FAVICON, admin / 'favicon.ico')
        if OUTPUT.exists():
            shutil.rmtree(OUTPUT)
        shutil.copytree(admin, OUTPUT)
    print(f'Aplisim admin panel prepared in {OUTPUT}. Apply with: docker compose up -d api')


if __name__ == '__main__':
    main()
