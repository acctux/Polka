#!/bin/bash
set -e

systemctl --user start deluged.service
for _ in {1..30}; do
  if deluge-console info >/dev/null 2>&1; then
    exec deluge-gtk "$@"
  fi
  sleep 2
done
echo "Deluge daemon did not become ready" >&2
exit 1
