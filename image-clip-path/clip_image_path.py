#!/usr/bin/env python3
"""When an image is copied in Chrome, save it to a file and put the file path
in the clipboard instead of the image. Saved images are deleted after 24 hours."""
import os, subprocess, time

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import GLib, Gdk, Gtk

DIR = os.path.expanduser("~/.cache/chrome-copied-images")
MAX_AGE = 24 * 3600
ANY_SOURCE = os.environ.get("CLIP_ANY_SOURCE") == "1"  # for testing only

os.makedirs(DIR, exist_ok=True)
cb = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
last_path = None


def active_window_is_chrome():
    try:
        pid = subprocess.run(["xdotool", "getactivewindow", "getwindowpid"],
                             capture_output=True, text=True, timeout=2).stdout.strip()
        exe = os.path.basename(os.readlink(f"/proc/{pid}/exe"))
        return exe in ("chrome", "chromium", "chromium-browser")
    except Exception:
        return False


def cleanup():
    now = time.time()
    for f in os.listdir(DIR):
        p = os.path.join(DIR, f)
        try:
            if now - os.path.getmtime(p) > MAX_AGE:
                os.remove(p)
        except OSError:
            pass
    return True  # keep the GLib timer running


def check():
    global last_path
    ok, targets = cb.wait_for_targets()
    if not ok:
        return False
    names = [t.name() for t in targets]
    if not any(n.startswith("image/") for n in names):
        return False
    from_chrome = any(n.startswith("chromium/") for n in names) or active_window_is_chrome()
    if not (from_chrome or ANY_SOURCE):
        return False
    pix = cb.wait_for_image()
    if pix is None:
        return False
    path = os.path.join(DIR, time.strftime("img-%Y%m%d-%H%M%S.png"))
    n = 1
    while os.path.exists(path):
        n += 1
        path = os.path.join(DIR, time.strftime(f"img-%Y%m%d-%H%M%S-{n}.png"))
    pix.savev(path, "png", [], [])
    last_path = path
    cb.set_text(path, -1)
    cb.store()
    subprocess.Popen(["notify-send", "-t", "2500", "-i", path, "Image saved - path copied", path])
    print("saved", path, flush=True)
    return False


def on_owner_change(_cb, _event):
    GLib.timeout_add(150, check)  # let the source app finish writing


cb.connect("owner-change", on_owner_change)
cleanup()
GLib.timeout_add_seconds(3600, cleanup)
Gtk.main()
