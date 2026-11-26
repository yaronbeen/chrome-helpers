#!/bin/sh
# Installs both helpers from wherever this repo is cloned.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

# 1. Zip helper for the Copy Download Path extension
"$ROOT/copy-download-path/install-zip-helper.sh"

# 2. Image-copy service (systemd user unit)
chmod +x "$ROOT/image-clip-path/clip_image_path.py"
mkdir -p "$HOME/.config/systemd/user"
sed "s#@DIR@#$ROOT/image-clip-path#" "$ROOT/image-clip-path/chrome-image-clip-path.service" \
  > "$HOME/.config/systemd/user/chrome-image-clip-path.service"
systemctl --user daemon-reload
systemctl --user enable chrome-image-clip-path.service
systemctl --user restart chrome-image-clip-path.service
echo "Image-copy service: $(systemctl --user is-active chrome-image-clip-path.service)"

echo
echo "Last step (once): chrome://extensions -> Developer mode -> Load unpacked -> $ROOT/copy-download-path"
