#!/bin/bash
#
# Simple Docker startup script for Plate Resort GUI
# Use this for autostart or desktop shortcuts
#

cd "$(dirname "$0")"

# Set up X11 access for GUI
export DISPLAY=:0
xhost +local:docker >/dev/null 2>&1

# Start the GUI in Docker
echo "🐳 Starting Plate Resort GUI in Docker..."
docker-compose up --build plate-resort-gui
