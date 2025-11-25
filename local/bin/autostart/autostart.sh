#!/usr/bin/env bash
#############################################
#############################################
RUNTIME=15
START_SERVICES=(
  # "solaar.service"
  "nm-applet.service"
)
STOP_SERVICES=(
  # "solaar.service"
  "nm-applet.service"
)

############################################
start_svcs() {
  for svc in "${START_SERVICES[@]}"; do
    if ! systemctl --user is-active --quiet "$svc"; then
      systemctl --user start "$svc"
    fi
  done
}
stop_svcs() {
  for svc in "${START_SERVICES[@]}"; do
    if systemctl --user is-active --quiet "$svc"; then
      systemctl --user stop "$svc"
    fi
  done
}

############################################
main() {
  start_svcs
  sleep $RUNTIME
  stop_svcs
  systemctl --user restart swww-daemon.service
}
