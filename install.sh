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

# 3. Copy-on-select for OpenCode desktop (systemd user unit)
chmod +x "$ROOT/select-to-clipboard/select_to_clipboard.py"
sed "s#@DIR@#$ROOT/select-to-clipboard#" "$ROOT/select-to-clipboard/select-to-clipboard.service" \
  > "$HOME/.config/systemd/user/select-to-clipboard.service"
systemctl --user daemon-reload
systemctl --user enable select-to-clipboard.service
systemctl --user restart select-to-clipboard.service
echo "Copy-on-select service: $(systemctl --user is-active select-to-clipboard.service)"

# 4. Keep those selections out of CopyQ history (only if CopyQ is running)
if command -v copyq >/dev/null && copyq count >/dev/null 2>&1; then
  copyq eval -- 'var f="application/x-select-to-clipboard"; var c=commands();
    if (!c.some(function(x){return x.input==f})) {
      setCommands([{name:"Ignore copy-on-select (OpenCode selections)", automatic:true,
        input:f, remove:true, cmd:"copyq ignore"}].concat(c)); print("added") }
    else print("already there")' && echo " (CopyQ rule; restart CopyQ once if it was just added)"
fi

echo
echo "Last step (once): chrome://extensions -> Developer mode -> Load unpacked -> $ROOT/copy-download-path"
