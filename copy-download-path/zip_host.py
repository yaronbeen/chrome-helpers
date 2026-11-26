#!/usr/bin/env python3
"""Chrome native-messaging host: zips the given files next to the first one."""
import json, os, struct, sys, time, zipfile


def read_msg():
    raw = sys.stdin.buffer.read(4)
    if len(raw) < 4:
        sys.exit(0)
    return json.loads(sys.stdin.buffer.read(struct.unpack("<I", raw)[0]))


def send(obj):
    data = json.dumps(obj).encode()
    sys.stdout.buffer.write(struct.pack("<I", len(data)) + data)
    sys.stdout.buffer.flush()


def zip_files(paths):
    files = [p for p in paths if os.path.isfile(p)]
    if not files:
        return {"ok": False, "error": "None of the selected files exist anymore."}
    out_dir = os.path.dirname(files[0])
    if not os.access(out_dir, os.W_OK):
        out_dir = os.path.expanduser("~/Downloads")
    out = os.path.join(out_dir, time.strftime("downloads-%Y%m%d-%H%M%S.zip"))
    used = set()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            base, ext = os.path.splitext(os.path.basename(p))
            name, n = base + ext, 1
            while name in used:  # same file name from different folders
                n += 1
                name = f"{base} ({n}){ext}"
            used.add(name)
            z.write(p, name)
    return {"ok": True, "zip": out, "count": len(files), "missing": len(paths) - len(files)}


msg = read_msg()
try:
    if msg.get("action") == "zip":
        send(zip_files(msg.get("paths", [])))
    else:
        send({"ok": False, "error": "unknown action"})
except Exception as e:
    send({"ok": False, "error": str(e)})
