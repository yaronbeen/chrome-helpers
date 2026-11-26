#!/bin/sh
# Registers zip_host.py as a Chrome native-messaging host for this extension.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
chmod +x "$DIR/zip_host.py"
DEST="$HOME/.config/google-chrome/NativeMessagingHosts"
mkdir -p "$DEST"
cat > "$DEST/com.yaron.copy_download_path.json" <<EOF
{
  "name": "com.yaron.copy_download_path",
  "description": "Zip selected downloads",
  "path": "$DIR/zip_host.py",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://ihadcgobmpipahafkpdjnadpnpmdfkae/"]
}
EOF
echo "Installed $DEST/com.yaron.copy_download_path.json"
