#!/bin/sh

choice="$(
  cat /run/wireguard/connections.list |
    fuzzel --dmenu 'Select config:'
)"

[ -z "$choice" ] && exit 1

alacritty -e sudo python /home/nick/Polka/local/bin/protonvpn/protonconnect.py "$choice"
