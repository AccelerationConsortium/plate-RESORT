#!/bin/bash
#
# Auto-startup script for Plate Resort System
# Place this in /etc/systemd/system/ for automatic startup
#

# This is a systemd service file
# To install:
# sudo cp plate-resort-autostart.service /etc/systemd/system/
# sudo systemctl enable plate-resort-autostart.service
# sudo systemctl start plate-resort-autostart.service

cat > plate-resort-autostart.service << 'EOF'
[Unit]
Description=Plate Resort Control System
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/plate-RESORT/plate-resort-multiple
ExecStart=/home/pi/plate-RESORT/plate-resort-multiple/start-gui-docker.sh
Restart=always
RestartSec=5
Environment=DISPLAY=:0
Environment=PYTHONPATH=/home/pi/plate-RESORT/plate-resort-multiple

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created: plate-resort-autostart.service"
echo ""
echo "To install for auto-startup on boot:"
echo "sudo cp plate-resort-autostart.service /etc/systemd/system/"
echo "sudo systemctl enable plate-resort-autostart.service"
echo "sudo systemctl start plate-resort-autostart.service"
echo ""
echo "To check status:"
echo "sudo systemctl status plate-resort-autostart.service"
echo ""
echo "To stop auto-startup:"
echo "sudo systemctl disable plate-resort-autostart.service"
