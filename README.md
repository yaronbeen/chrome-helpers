# chrome-helpers

Two small helpers for Chrome on Ubuntu (GNOME, X11).

## copy-download-path (Chrome extension)
- Notification when a download finishes, with **Copy path** / **Show in folder**.
- Toolbar popup: last 30 downloads with checkboxes. **Copy paths**, **Open**, **Zip** the selected ones.
- `Ctrl+Shift+Y` copies the latest download's path.
- Zip goes through a native-messaging helper (`zip_host.py`), registered by `install-zip-helper.sh`.
- The extension ID is fixed by the `key` in `manifest.json`: `ihadcgobmpipahafkpdjnadpnpmdfkae`.
  `key.pem` (private key) is intentionally not in git.

## image-clip-path (background service)
- When you copy an image in Chrome, it is saved to `~/.cache/chrome-copied-images/`
  and the clipboard keeps **both** the image and the file path. The paste key picks:
  - `Ctrl+V` pastes the **image** (OpenCode attaches it; Slack, Gmail, etc. too)
  - `Ctrl+Shift+V` pastes the **path** (plain-text paste; terminals already use this key)
  - Right-click -> "Paste as plain text" also gives the path.
- Tested in Chrome 146 and the OpenCode desktop app: a normal paste carries the image
  file (OpenCode prefers files), and a plain-text paste carries only the path.
- Files older than 24 hours are deleted (checked hourly).
- Runs as the systemd user service `chrome-image-clip-path.service`.

## Install
```sh
git clone git@github.com:yaronbeen/chrome-helpers.git ~/code/chrome-helpers
~/code/chrome-helpers/install.sh
```
Then in Chrome: `chrome://extensions` -> Developer mode -> **Load unpacked** -> `~/code/chrome-helpers/copy-download-path`.

## If the extension disappears after a Chrome restart
Chrome skips an unpacked folder silently when two registered extensions point at it
with different IDs (e.g. loaded once without `key`, then reloaded after adding it).
After changing `key` in `manifest.json`: click **Remove** on the old card, then **Load unpacked**
(not **Reload**). Fix: **Load unpacked** again, then check `Ctrl+Shift+Y` at `chrome://extensions/shortcuts`.
