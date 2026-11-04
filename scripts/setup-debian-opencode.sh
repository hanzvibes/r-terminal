#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail

pkg update -y
pkg install -y proot-distro git

# Make the setup safe to run again if Debian is already installed.
if ! proot-distro login debian -- true >/dev/null 2>&1; then
  proot-distro install debian
fi

proot-distro login debian -- bash -lc '
  set -Eeuo pipefail
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl git nodejs npm python3 python3-pip
  npm install --global opencode-ai
  command -v opencode
'

mkdir -p "$PREFIX/bin"
cat > "$PREFIX/bin/r-opencode" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
set -Eeuo pipefail
exec proot-distro login debian -- opencode "$@"
EOF
chmod +x "$PREFIX/bin/r-opencode"

cat <<'EOF'
R-Terminal environment is ready.

Start OpenCode from Termux with:
  r-opencode

On first launch, connect your model provider. Keep API keys out of scripts
and source control.
EOF
