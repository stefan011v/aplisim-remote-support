#!/usr/bin/env bash
# Run once with sudo after setup-https.sh: serves the download page at https://remote.aplisim.com/download/
# and sends visitors of the bare domain there. The admin panel stays at /_admin/.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run with sudo.' >&2; exit 1; }
site=/etc/nginx/sites-available/aplisim-remote
grep -q 'location /download/' "$site" && { echo 'Download page is already configured.'; exit 0; }
backup="$site.bak-$(date +%Y%m%d%H%M%S)"
cp -p "$site" "$backup"
python3 - "$site" <<'PY'
import sys
path = sys.argv[1]
content = open(path).read()
anchor = '    location / {\n'
if content.count(anchor) != 1:
    raise SystemExit('Unexpected nginx site layout; nothing changed.')
block = '''    location = / {
        return 302 /download/;
    }

    location = /download {
        return 301 /download/;
    }

    location /download/ {
        proxy_pass http://127.0.0.1:21118/;
        proxy_set_header Host $host;
        proxy_max_temp_file_size 0;
    }

'''
open(path, 'w').write(content.replace(anchor, block + anchor))
PY
if ! nginx -t; then
  cp -p "$backup" "$site"
  echo 'nginx configuration test failed; previous configuration restored.' >&2
  exit 1
fi
systemctl reload nginx
echo 'Download page: https://remote.aplisim.com/download/'
