#!/usr/bin/env bash

DEVICE="MX Master 3S"
LOG="$HOME/.cache/logid_check.log"
ATTEMPTS=10
LOGID_DELAY=3

LOGID_PID=0
restart_logid() {
  sudo logid restart >"$LOG" 2>&1 &
  LOGID_PID=$!
  echo "$LOGID_PID" >>"$LOG"
  sleep "$LOGID_DELAY"
}

run_attempts() {
  for i in $(seq 1 "$ATTEMPTS"); do
    if grep -q "${DEVICE}" "${LOG}"; then
      if ! grep -Eq "disconnected|Failed|Error" "${LOG}"; then
        return 0
      fi
    else
      restart_logid
    fi
  done
}

main() {
  rm "${LOG}"
  if run_attempts; then
    echo "Connected with $LOGID_PID" >>"$LOG"
  else
    LOGID_DELAY=10
    ATTEMPTS=20
    run_attempts
  fi
}
main
