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
  and the clipboard gets the file path instead.
- Files older than 24 hours are deleted (checked hourly).
- Runs as the systemd user service `chrome-image-clip-path.service`.

## Install
```sh
git clone git@github.com:yaronbeen/chrome-helpers.git ~/code/chrome-helpers
~/code/chrome-helpers/install.sh
```
Then in Chrome: `chrome://extensions` -> Developer mode -> **Load unpacked** -> `~/code/chrome-helpers/copy-download-path`.
