# R-Terminal

R-Terminal is an Android terminal app build overlay based on the upstream Termux application. It applies R/WORKS branding and a custom Android package ID, then builds a matching ARM64 bootstrap through GitHub Actions.

## Current scope

- Termux upstream source is fetched during CI; this repository contains the branding/build overlay, not a vendored Termux fork.
- Package ID: `id.rworks.rterminal`
- App label: `R-Terminal`
- Target ABI: `arm64-v8a`
- GitHub Actions builds a debug APK artifact.
- Debian + OpenCode setup helper is available in this repository and can be run from the R-Terminal shell after cloning it.

## Build

Push to `main` or run **Actions → Build R-Terminal APK**. The workflow checks out Termux and termux-packages sources, applies the overlay, builds the custom bootstrap, and assembles the debug APK.

## Install Debian + OpenCode

Open R-Terminal and run:

```sh
pkg install -y git
git clone --depth 1 https://github.com/hanzvibes/r-terminal.git
cd r-terminal
bash scripts/setup-debian-opencode.sh
```

The helper installs Debian through `proot-distro`, then installs Node.js, npm, Git, and OpenCode inside Debian. Start OpenCode later with:

```sh
r-opencode
```

## Important limitations

This is an early build pipeline, not a verified release. The GitHub Actions APK build is still being validated, and the APK has not yet been installed on a physical Android device. No release signing, Play Store publishing, custom apt repository, preinstalled Debian rootfs, or first-run GUI wizard is included yet.

## License

Termux is distributed under its upstream license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for project attribution and licensing notes.
