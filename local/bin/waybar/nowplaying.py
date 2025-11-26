#!/usr/bin/env python3
import json
import subprocess
import time
from pathlib import Path

# ── Config ───────────────────────
PLAYERS = ["mpv", "vivaldi", "mpd"]
CACHE_FILE = Path.home() / ".cache" / "nowplaying_scroll.json"
VISIBLE = 10
SPEED = 1.5
SEP = " "


# ── Helpers ──────────────────────
def run(cmd):
    try:
        return subprocess.check_output(["playerctl"] + cmd, text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def playing_player():
    for p in PLAYERS:
        if run(["--player", p, "status"]) == "Playing":
            return p
    return None


def metadata(player):
    artist = run(["--player", player, "metadata", "xesam:artist"]) or ""
    title = run(["--player", player, "metadata", "xesam:title"]) or ""
    return artist.strip(), title.strip()


# ── Persistent state ─────────────
def load_state():
    if CACHE_FILE.exists():
        try:
            data = json.loads(CACHE_FILE.read_text())
            return data["track"], float(data["pos"]), data.get("ts", time.time())
        except:
            pass
    return None, 0.0, time.time()


def save_state(track, pos):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"track": track, "pos": pos, "ts": time.time()}))


# ── Main logic ───────────────────
def main():
    player = playing_player()
    if not player:
        CACHE_FILE.unlink(missing_ok=True)
        print(json.dumps({"text": "", "class": "stopped"}))
        return
    artist, title = metadata(player)
    track = f"{artist} – {title}" if artist else title
    if not track:
        print(json.dumps({"text": "", "class": "stopped"}))
        return
    last_track, pos, last_ts = load_state()
    now = time.time()
    if track != last_track:
        save_state(track, 0.0)
        print(json.dumps({"text": "", "class": "playing"}))
        return
    pos += (now - last_ts) * SPEED
    if len(track) <= VISIBLE:
        display = track
    else:
        infinite = track + SEP + track
        start = int(pos) % len(track)
        display = infinite[start : start + VISIBLE]
    save_state(track, pos)
    print(json.dumps({"text": display, "class": "playing"}))


if __name__ == "__main__":
    main()
