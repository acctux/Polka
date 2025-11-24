#!/usr/bin/env bash

# Duration to keep the services running (in seconds)
RUNTIME=8

# List of user services to start/stop
SERVICES=(
  "solaar.service"
  "nm-applet.service"
)

# Start services
for svc in "${SERVICES[@]}"; do
  systemctl --user start "$svc"
done

# Sleep for the desired runtime
sleep "$RUNTIME"

# Stop services
for svc in "${SERVICES[@]}"; do
  systemctl --user stop "$svc"
done
