#!/bin/sh
export __NV_PRIME_RENDER_OFFLOAD=0
export LIBVA_DRIVER_NAME=radeonsi
exec /usr/bin/onlyoffice-desktopeditors "$@"
