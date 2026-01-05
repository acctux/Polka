list="/run/wireguard/connections.list"

lines="$(grep -c . "$list")"

choice="$(
  cat "$list" |
    fuzzel --dmenu \
      --hide-prompt \
      --lines "$lines" \
      --width 14 \
      --config=/home/nick/.config/fuzzel/timemenu.ini \
      'Select config:'
)"

[ -z "$choice" ] && exit 1

sudo -A python /home/nick/Polka/local/bin/protonvpn/protonconnect.py "$choice"
