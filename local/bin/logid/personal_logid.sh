#!/usr/bin/env bash

LOGID_CACHE_D="$HOME/.cache"
LOG="$LOGID_CACHE_D/logid_check.log"

DEVICE="MX Master 3S"
ATTEMPTS=5
START_DELAY=3
LOGID_DELAY=3

restart_logid() {
    sudo logid restart >"$LOG" 2>&1 &
    sleep "$LOGID_DELAY"
}

run_attempts() {
  sleep "$START_DELAY"
  for i in $(seq 1 "$ATTEMPTS"); do
	restart_logid
    if ! rg "Failed" "${LOG}"; then
      if pgrep -x "logid"; then
        return 0
      fi
    fi
  done
}

main() {
  mkdir -p $LOGID_CACHE_D
  run_attempts
  START_DELAY=15
  LOGID_DELAY=10
  restart_logid
  run_attempts
}

main
