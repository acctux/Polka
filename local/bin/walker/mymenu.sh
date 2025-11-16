#!/bin/bash
todo=$(echo "" | walker --dmenu "New todo:")
if [ -n "$todo" ]; then
  echo "!$todo" | walker --dmenu
fi
