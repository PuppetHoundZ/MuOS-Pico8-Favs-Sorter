#!/bin/sh

# HELP: Sort and organise your PICO-8 favourites list into categories
# ICON: pico8
# GRID: P8 Favourites

. /opt/muos/script/var/func.sh

APP_BIN="python3"
SETUP_APP "$APP_BIN" ""

# -----------------------------------------------------------------------------
APP_DIR="/run/muos/storage/application/Pico8FavsSorter"
$APP_BIN "$APP_DIR/main.py"
