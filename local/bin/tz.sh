#!/bin/sh

TZONE=$(find /usr/share/zoneinfo \
  -type f \
  ! -path '*/posix/*' \
  ! -path '*/right/*' \
  ! -name 'localtime' \
  ! -name 'posixrules' \
  | sed 's|/usr/share/zoneinfo/||' \
  | sort \
  | fuzzel --dmenu --prompt="Timezone: ")

[ -n "$TZONE" ] && sudo timedatectl set-timezone "$TZONE"

