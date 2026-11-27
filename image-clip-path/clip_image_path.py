#!/usr/bin/env python3
"""When an image is copied in Chrome, save it to a file and keep BOTH the image
and the file path in the clipboard, so the paste key decides what you get:

    Ctrl+V        -> the image   (OpenCode, Slack, Gmail, anything that takes images)
    Ctrl+Shift+V  -> the path    (plain-text paste; also what terminals use)

Saved images are deleted after 24 hours."""
import os, subprocess, time

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import GLib, GObject, Gdk, Gtk

DIR = os.path.expanduser(os.environ.get("CLIP_DIR", "~/.cache/chrome-copied-images"))
MAX_AGE = 24 * 3600
ANY_SOURCE = os.environ.get("CLIP_ANY_SOURCE") == "1"  # for testing only
NOTIFY = os.environ.get("CLIP_NOTIFY", "1") == "1"

os.makedirs(DIR, exist_ok=True)
Gtk.init()
cb = Gdk.Display.get_default().get_clipboard()
busy = False
provider = None  # keep a reference to what we put in the clipboard


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


def new_path():
    path = os.path.join(DIR, time.strftime("img-%Y%m%d-%H%M%S.png"))
    n = 1
    while os.path.exists(path):
        n += 1
        path = os.path.join(DIR, time.strftime(f"img-%Y%m%d-%H%M%S-{n}.png"))
    return path


def check():
    global busy
    if busy or cb.is_local():  # nothing new, or it's our own image+path
        return False
    mimes = cb.get_formats().get_mime_types() or []
    if not any(m.startswith("image/") for m in mimes):
        return False
    from_chrome = any(m.startswith("chromium/") for m in mimes) or active_window_is_chrome()
    if not (from_chrome or ANY_SOURCE):
        return False
    busy = True
    cb.read_texture_async(None, on_texture)
    return False


def on_texture(_cb, res):
    global busy, provider
    try:
        tex = cb.read_texture_finish(res)
        if tex is None:
            return
        png = tex.save_to_png_bytes()
        path = new_path()
        with open(path, "wb") as f:
            f.write(png.get_data())
        provider = Gdk.ContentProvider.new_union([
            Gdk.ContentProvider.new_for_bytes("image/png", png),
            Gdk.ContentProvider.new_for_value(GObject.Value(GObject.TYPE_STRING, path)),
        ])
        cb.set_content(provider)
        if NOTIFY:
            subprocess.Popen(["notify-send", "-t", "3000", "-i", path, "Image copied",
                              "Ctrl+V = image   ·   Ctrl+Shift+V = path\n" + path])
        print("saved", path, flush=True)
    except GLib.Error as e:
        print("could not read image:", e.message, flush=True)
    finally:
        busy = False


def on_changed(_cb):
    GLib.timeout_add(150, check)  # let the source app finish writing


cb.connect("changed", on_changed)
cleanup()
GLib.timeout_add_seconds(3600, cleanup)
GLib.MainLoop().run()
