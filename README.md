# R-Terminal

R-Terminal is an Android terminal app build overlay based on the upstream Termux application. It applies R/WORKS branding and a custom Android package ID, then builds a matching ARM64 bootstrap through GitHub Actions.

## Current scope

- Termux upstream source is fetched during CI; this repository contains the branding/build overlay, not a vendored Termux fork.
- Package ID: `id.rworks.rterminal`
- App label: `R-Terminal`
- Target ABI: `arm64-v8a`
- GitHub Actions builds a debug APK artifact.
- Debian + OpenCode can be installed from the R-Terminal shell with `bash scripts/setup-debian-opencode.sh`.

## Build

Push to `main` or run **Actions → Build R-Terminal APK**. The workflow checks out Termux and termux-packages sources, applies the overlay, builds the custom bootstrap, and assembles the debug APK.

## Install Debian + OpenCode

Open R-Terminal and run:

```sh
pkg update -y
pkg install -y proot-distro git
proot-distro install debian
proot-distro login debian
```

Inside Debian, run the setup helper (or follow its commands) to install Node.js, npm, Git, and OpenCode:

```sh
apt update
apt install -y ca-certificates curl git nodejs npm
npm install -g opencode-ai
opencode
```

## Important limitations

This is an early build pipeline, not a verified release. The GitHub Actions APK build is still being validated, and the APK has not yet been installed on a physical Android device. No release signing, Play Store publishing, custom apt repository, preinstalled Debian rootfs, or first-run GUI wizard is included yet.

## License

Termux is distributed under its upstream license. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for project attribution and licensing notes.
