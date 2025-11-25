#!/bin/bash
systemctl --user start protonmail-bridge.service
sleep 5
betterbird &
BBIRD_PID=$!
wait "$BBIRD_PID"
systemctl --user stop protonmail-bridge.service
