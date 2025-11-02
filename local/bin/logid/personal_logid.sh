#!/usr/bin/env bash

DEVICE="MX Master 3S"
LOG="$HOME/.cache/logid_check.log"
ATTEMPTS=5
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
      if ! grep -Eq "disconnected|Failed|Error|Failure" "${LOG}"; then
        return 0
      fi
    else
      restart_logid
    fi
  done
}

main() {
  sleep $LOGID_DELAY
  rm "${LOG}"
  run_attempts
  sleep $START_DELAY
  if grep -Eq "disconnected|Failed|Error|Failure" "${LOG}"; then
    restart_logid
  fi
}
main
