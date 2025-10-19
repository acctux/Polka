#!/usr/bin/env bash

CONF="/boot/loader/entries/arch.conf"
PARAMS="modprobe.blacklist=nvidia,nvidia_drm,nvidia_modeset,nvidia_uvm,nouveau vfio-pci.ids=10de:28a1,10de:22be"

# Backup first
sudo cp "$CONF" "$CONF.bak"

# Remove existing occurrences of the parameters
sudo sed -i "/^options / s/\bmodprobe\.blacklist=nvidia,nvidia_drm,nvidia_modeset,nvidia_uvm,nouveau\b//g" "$CONF"
sudo sed -i "/^options / s/\bvfio-pci\.ids=10de:28a1,10de:22be\b//g" "$CONF"

# Clean up multiple spaces
sudo sed -i '/^options / s/  / /g' "$CONF"

# Append the parameters at the end
sudo sed -i "/^options / s|$| $PARAMS|" "$CONF"
