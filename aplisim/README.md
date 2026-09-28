# Aplisim desktop build

This project produces unsigned test packages for Windows x64, macOS Intel and
macOS Apple Silicon. All three build and pass a startup check. The in-app logo,
colors, name, system icons (ICO/ICNS) and tray icons are Aplisim.

## Preparing the source locally

```sh
git -C upstream/rustdesk submodule update --init --recursive
python3 scripts/export-build-project.py
```

This produces a standalone source project in `dist/aplisim-build-source`, with the
vendored submodule, the license and the workflow files. It contains no private
keys, VPS data or automatic publishing. The export refuses to overwrite an
existing directory; pass a new `--output` path for the next export.

## Building on GitHub Actions

The exported directory must be the root of a separate GitHub repository.
Private repository: https://github.com/stefan011v/aplisim-remote-support. After
pushing the source, manually run the **Aplisim desktop builds** workflow from the
Actions tab.

- `preview`: uses the reserved domain `aplisim-preview.invalid`; it never connects
  to public RustDesk servers. Use it to check the look and startup of the app.
- `configured`: requires the repository variables `APLISIM_SERVER` (domain or IPv4)
  and `APLISIM_PUBLIC_KEY` (contents of `id_ed25519.pub`). The build stops if the
  values are malformed. Server reachability and ownership are not checked.

The `aplisim/configure-build.py` script sets the server and public key in the
vendored `libs/hbb_common/src/config.rs` before compiling. Setting only the
`RENDEZVOUS_SERVER`/`RS_PUB_KEY` environment variables is not enough in this
upstream revision.

The workflow keeps the upstream preparation of the Flutter/Rust bridge, libraries
and build tools. The Windows output is a self-extracting EXE; the macOS outputs
are separate DMG packages. Results are stored as Actions artifacts together with
SHA256SUMS and public build metadata. No GitHub Release is created and no package
is sent to a signing service. Future builds depend on upstream dependency services
being available. Running the workflow uses Actions minutes.

## Before distribution

Verify installation, process and service names, macOS Screen Recording and
Accessibility permissions, startup after reboot, and direct and relay connections.
Add Windows code signing and macOS signing/notarization. MSI is not included yet.
Keep the RustDesk license and make the corresponding source code available.

## Change surface

Besides the logo, icons, Flutter colors, desktop name and Windows metadata, macOS
changes AppInfo.xcconfig (name and bundle ID), project.pbxproj (bundle ID and
product), Runner.xcscheme (product name), MainMenu.xib (Swift module), and one
path in build.py that copies the helper service into Aplisim.app. All of these
keep the product consistent after renaming. The legacy Sciter build path is
unchanged. The exported hbb_common changes only the default server and public
key for the selected build.
