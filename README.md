# Aplisim Remote Support

Branded RustDesk client for Windows x64 and macOS (Intel and Apple Silicon).

**Status:** In use. Configured builds connect to `remote.aplisim.com` and report to
the Aplisim admin panel. Customers download the app from
https://remote.aplisim.com/download/. Packages are unsigned.

## Running a build

Actions → **Aplisim desktop builds** → **Run workflow**:

- `preview`: tests the look and startup without connecting to public RustDesk servers.
- `configured`: uses the repository variables `APLISIM_SERVER` and `APLISIM_PUBLIC_KEY`.
  Enter only the public key from `id_ed25519.pub`.

A successful build attaches the unsigned Windows EXE and macOS DMG packages as
Actions artifacts, together with SHA256SUMS. It does not create a public Release
and does not send packages to external signing services. Before distribution,
complete code signing, notarization, and installation/remote session tests.

Details: [build guide](aplisim/README.md).

## Server

`deployment/` contains the Docker Compose stack run on the Aplisim VPS: the RustDesk
ID/relay server, the `rustdesk-api` admin panel (rebranded by
`scripts/brand-admin.py`), the download page, nightly backups and the one-time
nginx/HTTPS scripts. It never contains the server's private key.

## Origin and license

Based on RustDesk 1.5.0. Exact revisions are in [source.json](aplisim/source.json).
The original license remains in [LICENCE](LICENCE); upstream documentation is in
[UPSTREAM-README.md](aplisim/UPSTREAM-README.md).

## Releases

Run **Aplisim desktop builds** in `configured` mode, then publish the packages to the
download page (see the operations section of the working project's README).
