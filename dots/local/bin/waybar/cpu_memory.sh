#!/bin/bash

# Log output to a file for debugging
LOGFILE="/tmp/waybar_cpu_memory.log"
echo "---- $(date) ----" >>"$LOGFILE"

# Get CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | awk '{printf "%d", $1}')
if [ -z "$CPU_USAGE" ] || ! [[ "$CPU_USAGE" =~ ^[0-9]+$ ]]; then
  CPU_USAGE=0
  echo "Warning: CPU_USAGE invalid or empty, defaulting to 0" >>"$LOGFILE"
fi

# Get memory usage
MEMORY=$(free -m | awk '/Mem:/ {printf "%.1f %.1f", $3/1024, $2/1024}')
USED=$(echo "$MEMORY" | awk '{print $1}')
TOTAL=$(echo "$MEMORY" | awk '{print $2}')
if [ -z "$USED" ] || [ -z "$TOTAL" ]; then
  USED=0.0
  TOTAL=0.0
  echo "Warning: Memory values invalid or empty, defaulting to 0.0/0.0" >>"$LOGFILE"
fi

# Calculate memory percentage
if (($(echo "$TOTAL > 0" | bc -l))); then
  MEMORY_PERCENT=$(echo "$USED / $TOTAL * 100" | bc -l | awk '{printf "%.0f", $1}')
else
  MEMORY_PERCENT=0.0
  echo "Warning: Total memory is 0, setting MEMORY_PERCENT to 0.0" >>"$LOGFILE"
fi

# Output JSON with memory in percentage
JSON="{\"text\": \"${CPU_USAGE}󰻠 ${MEMORY_PERCENT}󰍛\", \"tooltip\": \"CPU: $CPU_USAGE% | Memory: ${MEMORY_PERCENT}%\", \"class\": \"cpu-memory\"}"
echo "$JSON" >>"$LOGFILE"
echo "$JSON"
