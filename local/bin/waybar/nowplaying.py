#!/usr/bin/env python3
import json
import subprocess
import time
from pathlib import Path


# ────────────────────────────────────────────
# Config
# ────────────────────────────────────────────
CACHE_FILE = Path.home() / ".cache" / "nowplaying_scroll.json"
VISIBLE = 10
SPEED = 2
SEP = ""


# ────────────────────────────────────────────
# Functions
# ────────────────────────────────────────────
def run(args):
    """Run playerctl command and return stdout."""
    result = subprocess.run(["playerctl"] + args, capture_output=True, text=True)
    return result.stdout.strip()


def list_players():
    """Return active MPRIS players."""
    out = subprocess.run(["playerctl", "-l"], capture_output=True, text=True).stdout
    return out.strip().splitlines()


def get_playing_player(players):
    """Return the first active 'Playing' player."""
    for p in players:
        if run(["--player", p, "status"]) == "Playing":
            return p
    return None


def get_track_metadata(player):
    """Return full track string or '' if no metadata."""
    artist = run(["--player", player, "metadata", "xesam:artist"])
    title = run(["--player", player, "metadata", "xesam:title"])
    artist, title = artist.strip(), title.strip()
    if not artist and not title:
        return ""
    return f"{artist} – {title}" if artist else title


def load_state():
    """Load track scroll state from disk."""
    if not CACHE_FILE.exists():
        return None, 0.0, time.time()
    try:
        data = json.loads(CACHE_FILE.read_text())
        return (
            data.get("track"),
            float(data.get("pos", 0.0)),
            data.get("ts", time.time()),
        )
    except Exception:
        return None, 0.0, time.time()


def save_state(track, pos):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"track": track, "pos": pos, "ts": time.time()}))


def reset_output():
    """Reset and output empty status."""
    CACHE_FILE.unlink(missing_ok=True)
    return json.dumps({"text": "", "class": "stopped"})


def scroll_text(track, pos, dt):
    """Return updated (pos, display_text)."""
    pos += dt * SPEED
    if len(track) <= VISIBLE:
        return pos, track
    loop = track + SEP + track
    start = int(pos) % len(track)
    display = loop[start : start + VISIBLE]
    return pos, display


# ────────────────────────────────────────────
# Main logic (clean, minimal)
# ────────────────────────────────────────────
def main():
    players = list_players()
    player = get_playing_player(players)
    if not player:
        print(reset_output())
        return
    track = get_track_metadata(player)
    if not track:
        print(reset_output())
        return
    last_track, pos, last_ts = load_state()
    now = time.time()
    if track != last_track:
        save_state(track, 0.0)
        print(json.dumps({"text": "", "class": "playing"}))
        return
    pos, display = scroll_text(track, pos, now - last_ts)
    save_state(track, pos)
    print(json.dumps({"text": display, "class": "playing"}))


if __name__ == "__main__":
    main()
