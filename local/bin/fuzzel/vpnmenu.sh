list="/run/wireguard/connections.list"

lines="$(grep -c . "$list")"

choice="$(
  cat "$list" |
    fuzzel --dmenu \
      --hide-prompt \
      --lines "$lines" \
      --config=/home/nick/.config/fuzzel/vpnmenu.ini \
      'Select config:'
)"

[ -z "$choice" ] && exit 1

alacritty -e sudo python /home/nick/Polka/local/bin/protonvpn/protonconnect.py "$choice"
