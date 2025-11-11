#!/usr/bin/env python3
import gi
import json
import time

gi.require_version("Gtk", "4.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gtk, GLib


class CountdownApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.nick.timer")
        self.end_time = None
        self.timeout_id = None

    def do_activate(self):
        # Create a standalone window not strictly tied to the app
        self.win = Gtk.Window(title="Countdown Timer")
        self.win.set_default_size(200, 50)
        self.win.connect("destroy", self.on_window_destroy)  # optional cleanup

        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Enter seconds")
        self.entry.connect("activate", self.start_countdown)

        self.win.set_child(self.entry)
        self.win.present()

    def on_window_destroy(self, widget):
        # Optional: just stop the timeout if window is closed
        if self.timeout_id:
            GLib.source_remove(self.timeout_id)
            self.timeout_id = None

    def start_countdown(self, widget):
        try:
            secs = int(widget.get_text())
        except ValueError:
            secs = 60
        self.end_time = time.time() + secs
        self.entry.set_sensitive(False)  # prevent re-entry

        # GLib timeout every 1 second
        self.timeout_id = GLib.timeout_add_seconds(1, self.update_countdown)

    def update_countdown(self):
        rem = int(self.end_time - time.time())
        if rem < 0:
            rem = 0

        mins, secs_rem = divmod(rem, 60)
        out = {"text": f"{mins:02d}:{secs_rem:02d}", "tooltip": "Countdown remaining"}
        if rem <= 10:
            out["class"] = "critical"

        print(json.dumps(out), flush=True)

        if rem == 0:
            print(json.dumps({"text": "Done!"}))
            self.timeout_id = None  # timeout done
            return False
        return True


app = CountdownApp()
app.run()
