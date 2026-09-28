# Aplisim Remote Support

Branded RustDesk client for Windows x64 and macOS (Intel and Apple Silicon).

**Status:** The Windows x64 EXE and both macOS DMG packages build successfully,
including a startup check on all three platforms. The app logo, colors, system
icons and tray icons are Aplisim. Installation and real remote sessions have not
been tested yet. This repository contains the native Flutter/Rust application;
the HTML visual prototype from the working project is not part of the native UI.

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

`deployment/` contains the Docker Compose setup for the self-hosted ID/relay
server, plus start, check and backup scripts. The **Aplisim server validation**
workflow tests startup, key persistence across restarts, and backups.

## Origin and license

Based on RustDesk 1.5.0. Exact revisions are in [source.json](aplisim/source.json).
The original license remains in [LICENCE](LICENCE); upstream documentation is in
[UPSTREAM-README.md](aplisim/UPSTREAM-README.md).

## Test packages

- [Windows x64, macOS Intel and Apple Silicon](https://github.com/stefan011v/aplisim-remote-support/actions/runs/36455813708)
