#!/bin/bash

declare -g DEVICE_ID="4d76022a5910415f9073cc44af2025c3"
declare -g PHONE_PATH="$HOME/Phone"
declare -g ANDROID_MOUNT_PATH="$PHONE_PATH/Internal"
declare -g SD_MOUNT_PATH="$PHONE_PATH/SD"
declare -g ANDROID_DIR="/storage/emulated/0"
declare -g SD_DIR="/storage/0000-0000"
declare -g SSH_KEY="$HOME/.config/kdeconnect/privateKey.pem"

declare -g ANDROID_USER="kdeconnect"
declare -g ANDROID_HOST
declare -g ANDROID_PORT

activate_sftp() {
  if ! qdbus org.kde.kdeconnect "/modules/kdeconnect/devices/$DEVICE_ID/sftp" org.kde.kdeconnect.device.sftp.mountAndWait; then
    exit 1
  fi
}

detect_mount() {
  sleep 3
  local mount_line
  mount_line=$(mount | grep "kdeconnect@$DEVICE_ID")
  if [[ -z "$mount_line" ]]; then
    mount_line=$(mount | grep "kdeconnect" | grep "$DEVICE_ID")
  fi

  if [[ -n "$mount_line" ]]; then
    ANDROID_HOST=$(echo "$mount_line" | sed -n 's/.*kdeconnect@\([0-9.]*\):.*/\1/p')
  else
    exit 1
  fi
}

get_ssh_port() {
  ANDROID_PORT=$(ss -tnp | grep "$ANDROID_HOST" | grep ssh | awk '{print $5}' | cut -d: -f2 | head -n 1)
  if [[ -z "$ANDROID_PORT" ]]; then
    exit 1
  fi
}

mount_storage() {
  mkdir -p "$ANDROID_MOUNT_PATH" "$SD_MOUNT_PATH"
  if ! sshfs -o rw,nosuid,nodev,IdentityFile="$SSH_KEY",port="$ANDROID_PORT",uid=$(id -u),gid=$(id -g),allow_other "$ANDROID_USER@$ANDROID_HOST:$ANDROID_DIR" "$ANDROID_MOUNT_PATH"; then
    echo "Error: Failed to mount Internal Storage." >&2
  fi

  if ! sshfs -o rw,nosuid,nodev,IdentityFile="$SSH_KEY",port="$ANDROID_PORT",uid=$(id -u),gid=$(id -g),allow_other "$ANDROID_USER@$ANDROID_HOST:$SD_DIR" "$SD_MOUNT_PATH"; then
    echo "Warning: Failed to mount SD card (it might not exist or be unshared)." >&2
  fi
}

main() {
  check_requirements
  check_kdeconnect
  activate_sftp
  create_mount_points
  detect_mount
  get_ssh_port
  mount_storage
}

main "$@"
