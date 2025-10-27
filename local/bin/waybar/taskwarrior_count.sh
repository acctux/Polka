#!/usr/bin/env bash

DB="$HOME/.task/taskchampion.sqlite3"

TASKS=$(sqlite3 -noheader -batch $HOME/.task/taskchampion.sqlite3 \
  "SELECT json_extract(data, '\$.description'), json_extract(data, '\$.urgency') FROM tasks WHERE json_extract(data, '\$.status')='pending';" |
  sed '/^$/d')

TASK_NAMES=""
URGENT=false
COUNT=0

while IFS='|' read -r DESC URG; do
  ((COUNT++))
  TASK_NAMES+=$(printf "• %s\n" "$DESC")

  URG_NUM=$(echo "$URG" | awk '{if($1=="") print 0; else print $1}')

  if (($(awk "BEGIN {print ($URG_NUM >= 9)}"))); then
    URGENT=true
  fi
done <<<"$TASKS"

if [ "$COUNT" -eq 0 ]; then
  echo ""
  exit 0
fi

TASK_NAMES_JSON=$(echo "$TASK_NAMES" | awk '{printf "%s\\n", $0}')

if [ "$URGENT" = true ]; then
  echo "{\"text\": \"$COUNT\", \"tooltip\": \"Active tasks: $COUNT\\n$TASK_NAMES_JSON\", \"class\": \"critical\"}"
else
  echo "{\"text\": \"$COUNT\", \"tooltip\": \"Active tasks: $COUNT\\n$TASK_NAMES_JSON\"}"
fi
