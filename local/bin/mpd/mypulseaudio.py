#!/usr/bin/env python3
import subprocess
import json
import re
import time
from pathlib import Path

CACHE_FILE = Path.home() / ".cache" / "nowplaying_scroll.json"
SLEEP = 0.3
SPEED = 2
SEP = ""
MIN_VISIBLE = 8
VISIBLE_DIVISOR = 6
IGNORE_TEXT_PLAYERS = ["JBL_Go_4"]


# Player helper functions
def run(args):
    return subprocess.run(
        ["playerctl"] + args, capture_output=True, text=True
    ).stdout.strip()


def list_players():
    out = subprocess.run(["playerctl", "-l"], capture_output=True, text=True).stdout
    return out.strip().splitlines()


def get_playing_player(players):
    for p in players:
        if run(["--player", p, "status"]) == "Playing":
            return p
    return None


def get_track_metadata(player):
    artist = run(["--player", player, "metadata", "xesam:artist"]).strip()
    title = run(["--player", player, "metadata", "xesam:title"]).strip()
    if not artist and not title:
        return ""
    return f"{artist} – {title}" if artist else title


def load_state():
    if not CACHE_FILE.exists():
        return None, 0.0, time.time()

    try:
        data = json.loads(CACHE_FILE.read_text())
        return (
            data.get("track"),
            float(data.get("pos", 0.0)),
            float(data.get("ts", time.time())),
        )
    except Exception:
        return None, 0.0, time.time()


def save_state(track, pos):
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"track": track, "pos": pos, "ts": time.time()}))


def scroll_text(track: str, pos: float, dt: float):
    pos += dt * SPEED
    visible = max(len(track) // VISIBLE_DIVISOR, MIN_VISIBLE)
    # No need to scroll
    if len(track) <= visible:
        return pos, track
    loop = track + SEP + track
    start = int(pos) % len(track)
    display = loop[start : start + visible]
    return pos, display


def get_nowplaying(players):
    track_player = None
    for p in players:
        if run(["--player", p, "status"]) == "Playing" and p not in IGNORE_TEXT_PLAYERS:
            track_player = p
            break
    if not track_player:
        track_player = get_playing_player(players)
    if not track_player:
        return "", "stopped", "stopped", ""
    full_track = (
        "" if track_player in IGNORE_TEXT_PLAYERS else get_track_metadata(track_player)
    )
    last_track, pos, last_ts = load_state()
    now = time.time()
    if full_track != last_track:
        save_state(full_track, 0.0)
        return full_track or "", "playing", "playing", full_track or ""
    pos, display = scroll_text(full_track, pos, now - last_ts)
    save_state(full_track, pos)
    return display or "", "playing", "playing", full_track or ""


def volume_icon(vol: int) -> str:
    if vol == 0:
        return "󰖁"
    elif vol <= 33:
        return "󰕿"
    elif vol <= 66:
        return "󰖀"
    else:
        return "󰕾"


def get_volume() -> int:
    try:
        out = subprocess.check_output(
            ["pactl", "get-sink-volume", "@DEFAULT_SINK@"], stderr=subprocess.DEVNULL
        ).decode()
        matches = re.findall(r"(\d+)%", out)
        if matches:
            return sum(int(m) for m in matches) // len(matches)
    except subprocess.CalledProcessError:
        pass
    return 0


# ────────────────────────────────────────────
# Main loop
# ────────────────────────────────────────────
def main():
    while True:
        players = list_players()
        text, status, css_class, full_track = get_nowplaying(players)
        vol = get_volume()
        tooltip = f"{vol}%\n{full_track}" if full_track else f"{vol}%"
        display_text = (
            f"{volume_icon(vol)}<span size='8.5pt'> {text}</span>"
            if text
            else volume_icon(vol)
        )
        print(
            json.dumps(
                {
                    "text": display_text,
                    "status": status,
                    "class": css_class,
                    "tooltip": tooltip,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        time.sleep(SLEEP)


if __name__ == "__main__":
    main()
