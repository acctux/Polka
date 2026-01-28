#!/usr/bin/env bash

ICON=""
TOOLTIP="AyuGram is running"

if systemctl --user is-active --quiet ayugram.service; then
  printf '{"text":"%s","tooltip":"%s"}\n' "$ICON" "$TOOLTIP"
fi
