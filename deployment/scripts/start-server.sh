#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../server"
if [[ ! -f .env ]]; then
  echo 'First copy server/.env.example to server/.env and fill in the VPS address.' >&2
  exit 1
fi
command -v docker >/dev/null || { echo 'Docker with the Compose plugin is required.' >&2; exit 1; }
docker compose config --quiet
docker compose up -d
docker compose ps
echo 'Public key after initialization: server/data/id_ed25519.pub'
echo 'Keep the private key id_ed25519 only on the server and in backups.'
