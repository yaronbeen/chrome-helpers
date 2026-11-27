#!/usr/bin/env python3
"""Copy-on-select for chosen apps (default: the OpenCode desktop app).

Selecting text on Linux only fills the PRIMARY selection (middle-click paste).
When the focused window belongs to one of APPS, this also puts the selected
text in the normal clipboard, so Ctrl+V pastes it anywhere.

Other apps are left alone. Set SELECT_COPY_APPS to a comma-separated list of
WM_CLASS names to change which apps get this (see `xprop WM_CLASS`).
Selections are kept out of clipboard-manager history (CopyQ) unless
SELECT_COPY_HISTORY=1."""
import os, subprocess

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import GLib, GObject, Gdk, Gtk

APPS = {a.strip().lower() for a in
        os.environ.get("SELECT_COPY_APPS", "ai.opencode.desktop").split(",") if a.strip()}
KEEP_IN_HISTORY = os.environ.get("SELECT_COPY_HISTORY") == "1"  # 1 = let CopyQ record selections
# Extra clipboard format that marks a copy as "made by copy-on-select".
# (GTK4 refuses KDE's x-kde-passwordManagerHint: not a valid mime type.)
MARK = "application/x-select-to-clipboard"
DELAY_MS = 300  # wait until the mouse drag / Shift+arrow selection settles

Gtk.init()
display = Gdk.Display.get_default()
primary = display.get_primary_clipboard()
clipboard = display.get_clipboard()
timer = None


def focused_app():
    """WM_CLASS of the focused window, lower-case ('' if unknown)."""
    for cmd in (["xdotool", "getactivewindow"], ["xdotool", "getwindowfocus"]):
        try:
            wid = subprocess.run(cmd, capture_output=True, text=True, timeout=2).stdout.strip()
            if not wid:
                continue
            out = subprocess.run(["xprop", "-id", wid, "WM_CLASS"],
                                 capture_output=True, text=True, timeout=2).stdout
            if "=" in out:
                return out.split("=", 1)[1].lower()
        except Exception:
            pass
    return ""


def settle():
    global timer
    timer = None
    if primary.is_local():
        return False
    app = focused_app()
    if not any(f'"{a}"' in app for a in APPS):
        return False
    primary.read_text_async(None, on_text)
    return False


def on_text(_cb, res):
    try:
        text = primary.read_text_finish(res)
    except GLib.Error:
        return
    if not text or not text.strip():
        return
    parts = [Gdk.ContentProvider.new_for_value(GObject.Value(GObject.TYPE_STRING, text))]
    if not KEEP_IN_HISTORY:
        # A CopyQ rule ignores clipboard content carrying MARK (see README),
        # so selections don't flood the history; real Ctrl+C copies still land.
        parts.append(Gdk.ContentProvider.new_for_bytes(
            MARK, GLib.Bytes.new(b"1")))
    clipboard.set_content(Gdk.ContentProvider.new_union(parts))
    print(f"copied {len(text)} chars", flush=True)


def on_changed(_cb):
    global timer
    if timer:
        GLib.source_remove(timer)
    timer = GLib.timeout_add(DELAY_MS, settle)


primary.connect("changed", on_changed)
print("watching selections in:", ", ".join(sorted(APPS)), flush=True)
GLib.MainLoop().run()
