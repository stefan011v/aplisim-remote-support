#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../server"
if [[ ! -f .env ]]; then
  echo 'Prvo kopiraj server/.env.example u server/.env i popuni adresu VPS-a.' >&2
  exit 1
fi
command -v docker >/dev/null || { echo 'Potreban je Docker sa Compose dodatkom.' >&2; exit 1; }
docker compose config --quiet
docker compose up -d
docker compose ps
echo 'Javni ključ nakon inicijalizacije: server/data/id_ed25519.pub'
echo 'Privatni ključ id_ed25519 sačuvati samo na serveru i u rezervnoj kopiji.'
