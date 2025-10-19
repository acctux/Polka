#!/bin/bash

# CSS file for Wofi styling
STYLE_FILE="$HOME/Lit/scripts/hyprland/power_menu.css"

# Power menu options
OPTIONS=(
    " Power Off"
    " Reboot"
    " Lock"
    " Logout"
    " Cancel"
)

# Show the main menu with styling
choice=$(printf "%s\n" "${OPTIONS[@]}" | wofi --dmenu --style "$STYLE_FILE" --prompt "System Menu" --insensitive --width 400 --height 300 --location center --hide-scroll)

# Exit if no choice made
[[ -z "$choice" ]] && exit 0

# Handle user selection
case "$choice" in
    *Power\ Off*)
        confirm=$(printf "Yes\nNo" | wofi --dmenu --style "$STYLE_FILE" --prompt "Confirm Power Off?" --width 200 --height 100)
        [[ "$confirm" == "Yes" ]] && exec systemctl poweroff
        ;;
    *Reboot*)
        confirm=$(printf "Yes\nNo" | wofi --dmenu --style "$STYLE_FILE" --prompt "Confirm Reboot?" --width 200 --height 100)
        [[ "$confirm" == "Yes" ]] && exec systemctl reboot
        ;;
    *Suspend*)
        exec systemctl suspend
        ;;
    *Lock*)
        exec hyprlock
        ;;
    *Logout*)
        confirm=$(printf "Yes\nNo" | wofi --dmenu --style "$STYLE_FILE" --prompt "Confirm Logout?" --width 200 --height 100)
        [[ "$confirm" == "Yes" ]] && exec hyprctl dispatch exit
        ;;
    *Cancel*)
        exit 0
        ;;
    *)
        exit 1
        ;;
esac
