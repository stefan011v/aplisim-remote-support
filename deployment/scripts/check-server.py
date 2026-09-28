#!/usr/bin/env python3
"""Check local Compose services and export public client settings only."""
import argparse
import base64
import json
from pathlib import Path
import socket
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / 'server'


def docker(*args):
    return subprocess.check_output(['docker', 'compose', *args], cwd=SERVER, text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    config = json.loads(docker('config', '--format', 'json'))
    for service in ['hbbs', 'hbbr']:
        container = docker('ps', '--status', 'running', '-q', service)
        if not container:
            raise SystemExit(f'{service} is not running')
    key = docker('exec', '-T', 'hbbs', 'cat', '/root/id_ed25519.pub')
    raw = base64.b64decode(key, validate=True)
    if len(raw) != 32 or base64.b64encode(raw).decode() != key:
        raise SystemExit('Invalid server public key')
    for port in [21115, 21116, 21117]:
        with socket.create_connection(('127.0.0.1', port), timeout=5):
            pass
    command = config['services']['hbbs']['command']
    relay = command[command.index('-r') + 1]
    host = relay.rsplit(':', 1)[0]
    print('hbbs/hbbr running; TCP ports responding; public key valid.')
    print('UDP and real desktop sessions require external client tests.')
    if args.export:
        output = SERVER / 'client-config.json'
        with output.open('x') as handle:
            json.dump({'schemaVersion': 1, 'app': 'Aplisim', 'host': host, 'key': key}, handle, indent=2)
            handle.write('\n')
        print(f'Public settings exported to {output}')


if __name__ == '__main__':
    main()
