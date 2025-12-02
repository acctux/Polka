#!/bin/sh

choice="$(printf "%s\n" \
  ES2 \
  ES \
  GA2 \
  GA \
  MA \
  SK2 \
  SK \
  TN \
  UA45 \
  UA49 \
  UA \
  UK \
  USCO \
  USFL \
  USGA \
  USMA \
  USNY \
  USTX |
  fuzzel --dmenu 'Select config:')"

[ -z "$choice" ] && exit 1

kitty sudo python /home/nick/Polka/local/bin/protonvpn/protonconnect.py "$choice"
