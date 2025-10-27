#!/bin/bash

DEVICE_ID="4d76022a5910415f9073cc44af2025c3"
PHONE_PATH="$HOME/Phone"
ANDROID_MOUNT_PATH="$PHONE_PATH/Internal"
SD_MOUNT_PATH="$PHONE_PATH/SD"
ANDROID_DIR="/storage/emulated/0"
SD_DIR="/storage/0000-0000"
SSH_KEY="$HOME/.config/kdeconnect/privateKey.pem"
ANDROID_USER="kdeconnect"

# --- Check for required utilities ---
for cmd in kdeconnect-cli sshfs qdbus mount ss; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: Required utility '$cmd' is not installed or not available in PATH." >&2
    exit 1
  fi
done

# --- Check KDE Connect availability ---
if ! qdbus org.kde.kdeconnect &> /dev/null; then
  echo "Error: kdeconnect service is not running or not available." >&2
  exit 1
fi

# --- Activate SFTP service ---
echo "Activating SFTP service for device ID: $DEVICE_ID"
if ! qdbus org.kde.kdeconnect "/modules/kdeconnect/devices/$DEVICE_ID/sftp" org.kde.kdeconnect.device.sftp.mountAndWait; then
  echo "Error: Failed to activate SFTP service for device $DEVICE_ID." >&2
  exit 1
fi

# --- Create local mount points ---
mkdir -p "$ANDROID_MOUNT_PATH" "$SD_MOUNT_PATH"

# --- Detect existing KDE Connect mount ---
sleep 3
mount_line=$(mount | grep "kdeconnect@$DEVICE_ID")
if [[ -z "$mount_line" ]]; then
  mount_line=$(mount | grep "kdeconnect" | grep "$DEVICE_ID")
fi

if [[ -n "$mount_line" ]]; then
  ANDROID_HOST=$(echo "$mount_line" | sed -n 's/.*kdeconnect@\([0-9.]*\):.*/\1/p')
else
  echo "Error: No mount entry found for DEVICE_ID=$DEVICE_ID (SFTP may not be active)." >&2
  exit 1
fi

# --- Get SSH port ---
ANDROID_PORT=$(ss -tnp | grep "$ANDROID_HOST" | grep ssh | awk '{print $5}' | cut -d: -f2 | head -n 1)
if [[ -z "$ANDROID_PORT" ]]; then
  echo "Error: Could not detect SFTP port for $ANDROID_HOST" >&2
  exit 1
fi

# --- Mount internal and SD storage manually ---
echo "Mounting Internal Storage to: $ANDROID_MOUNT_PATH"
if ! sshfs -o rw,nosuid,nodev,IdentityFile="$SSH_KEY",port="$ANDROID_PORT",uid=$(id -u),gid=$(id -g),allow_other "$ANDROID_USER@$ANDROID_HOST:$ANDROID_DIR" "$ANDROID_MOUNT_PATH"; then
  echo "Error: Failed to mount Internal Storage." >&2
fi

echo "Mounting SD Card to: $SD_MOUNT_PATH"
if ! sshfs -o rw,nosuid,nodev,IdentityFile="$SSH_KEY",port="$ANDROID_PORT",uid=$(id -u),gid=$(id -g),allow_other "$ANDROID_USER@$ANDROID_HOST:$SD_DIR" "$SD_MOUNT_PATH"; then
  echo "Warning: Failed to mount SD card (it might not exist or be unshared)." >&2
fi

echo "✅ Android device mounted successfully at:"
echo "  Internal → $ANDROID_MOUNT_PATH"
echo "  SD card  → $SD_MOUNT_PATH"

