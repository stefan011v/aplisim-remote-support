#!/usr/bin/env bash
set -euo pipefail
umask 077
cd "$(dirname "$0")/../server"
[[ -f .env && -d data ]] || { echo 'Server is not initialized.' >&2; exit 1; }
mkdir -p backups
aplisim_services="$(docker compose ps --status running --services)"
aplisim_running=()
if [[ -n "$aplisim_services" ]]; then
  mapfile -t aplisim_running <<< "$aplisim_services"
fi
aplisim_archive="backups/aplisim-$(date -u +%Y%m%dT%H%M%SZ)-${RANDOM}.tar.gz"
resume_services() {
  if (( ${#aplisim_running[@]} )); then
    docker compose start "${aplisim_running[@]}"
  fi
}
trap resume_services EXIT
if (( ${#aplisim_running[@]} )); then
  docker compose stop "${aplisim_running[@]}"
fi
tar -czf "${aplisim_archive}.partial" .env compose.yaml data
mv "${aplisim_archive}.partial" "$aplisim_archive"
echo "Backup created: $aplisim_archive (contains the private server key; keep private)."
