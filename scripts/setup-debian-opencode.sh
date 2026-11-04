#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

pkg update -y
pkg install -y proot-distro git
proot-distro install debian

cat <<'EOF'
Debian has been installed.

Enter it with:
  proot-distro login debian

Then inside Debian run:
  apt update
  apt install -y ca-certificates curl git nodejs npm python3 python3-pip
  npm install -g opencode-ai
  opencode

OpenCode will ask you to connect/configure a model provider. Keep API keys out of scripts and source control.
EOF
