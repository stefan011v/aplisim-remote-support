#!/usr/bin/env bash
# Run once with sudo: publishes the admin panel on https://remote.aplisim.com via the host nginx.
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'Run with sudo.' >&2; exit 1; }
cd "$(dirname "$0")/.."
domain=remote.aplisim.com
site=/etc/nginx/sites-available/aplisim-remote
[[ -e $site ]] && { echo "$site already exists; not overwriting." >&2; exit 1; }
install -m 644 server/nginx/aplisim-remote.conf "$site"
ln -s "$site" /etc/nginx/sites-enabled/aplisim-remote
if ! nginx -t; then
  rm -f /etc/nginx/sites-enabled/aplisim-remote "$site"
  echo 'nginx configuration test failed; changes removed.' >&2
  exit 1
fi
systemctl reload nginx
certbot --nginx -d "$domain" --non-interactive --redirect --keep-until-expiring
nginx -t
systemctl reload nginx
echo "Admin panel: https://$domain/_admin/"
