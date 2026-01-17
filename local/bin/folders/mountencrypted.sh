#!/usr/bin/env bash

CIPHER="$HOME/Documents/Encrypted"
PLAIN="$HOME/Documents/Decrypted"

initialize_gocrypt() {
  PASSFILE=$(mktemp)
  PASSWORD=$(zenity --password --title="Enter init password")
  echo "$PASSWORD" >"$PASSFILE"
  gocryptfs -init --passfile "$PASSFILE" "$CIPHER"
  shred -u "$PASSFILE"
}

mount_fs() {
  mkdir -p "$CIPHER" "$PLAIN"
  PASSFILE=$(mktemp)
  PASSWORD=$(zenity --password --title="Enter gocryptfs password")
  echo "$PASSWORD" >"$PASSFILE"
  gocryptfs --passfile "$PASSFILE" "$CIPHER" "$PLAIN"
  shred -u "$PASSFILE"
  xdg-open "$PLAIN"
}

unmount_fs() {
  fusermount3 -u "$PLAIN"
  rmdir "$PLAIN"
}

main() {
  if [ ! -f "$CIPHER/gocryptfs.conf" ]; then
    initialize_gocrypt
  fi
  if mountpoint -q "$PLAIN"; then
    # xdg-open "$PLAIN"
    unmount_fs
  else
    mount_fs
  fi
}
main
