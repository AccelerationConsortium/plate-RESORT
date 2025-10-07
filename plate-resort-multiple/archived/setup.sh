#!/bin/bash
"""
First-time setup script for Plate Resort System on Raspberry Pi
"""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Plate Resort System - First Time Setup${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    echo -e "${YELLOW}⚠️  Warning: This script is designed to run as the 'pi' user${NC}"
    echo "Current user: $USER"
    read -p "Continue anyway? [y/N]: " continue_setup
    if [ "$continue_setup" != "y" ] && [ "$continue_setup" != "Y" ]; then
        exit 1
    fi
fi

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
sudo apt update
sudo apt upgrade -y

# Install required system packages
echo -e "${YELLOW}📦 Installing required packages...${NC}"
sudo apt install -y python3-pip python3-tk python3-dev python3-yaml \
    python3-flask git build-essential \
    udev x11-xserver-utils
sudo usermod -aG dialout $USER

# Install Python packages
echo -e "${YELLOW}🐍 Installing Python packages...${NC}"
pip3 install --user dynamixel-sdk pyyaml flask

# Make scripts executable
echo -e "${YELLOW}🔧 Setting up scripts...${NC}"
chmod +x launch.sh
chmod +x setup-autostart.sh

# Copy desktop launcher
if [ -d "$HOME/Desktop" ]; then
    echo -e "${YELLOW}🖥️  Installing desktop launcher...${NC}"
    cp plate-resort.desktop "$HOME/Desktop/"
    chmod +x "$HOME/Desktop/plate-resort.desktop"
fi

# Set up USB permissions
echo -e "${YELLOW}🔌 Setting up USB device permissions...${NC}"
sudo tee /etc/udev/rules.d/99-dynamixel.rules > /dev/null << 'EOF'
# Dynamixel USB devices
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6014", MODE="0666", GROUP="dialout"
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout"
# Generic USB-to-serial adapters
SUBSYSTEM=="tty", KERNEL=="ttyUSB*", MODE="0666", GROUP="dialout"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger

# Test configuration
echo -e "${YELLOW}🧪 Testing configuration...${NC}"
echo ""
echo "=== Python Dependencies ==="
python3 -c "
import sys
modules = ['dynamixel_sdk', 'yaml', 'flask', 'tkinter']
success = True
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module} - FAILED')
        success = False

if success:
    print('\\n✅ All Python dependencies installed successfully!')
else:
    print('\\n❌ Some dependencies failed to install')
"

echo ""
echo "=== USB Device Check ==="
if ls /dev/ttyUSB* >/dev/null 2>&1; then
    echo "✅ USB serial devices found:"
    ls -la /dev/ttyUSB*
else
    echo "ℹ️  No USB devices currently connected"
    echo "Connect your Dynamixel USB adapter and run:"
    echo "ls /dev/ttyUSB*"
fi

echo ""
echo -e "${GREEN}🎉 Setup completed!${NC}"
echo ""
echo "Next steps:"
echo "1. 🔌 Connect your Dynamixel motor and USB adapter"
echo "2. 🔄 Reboot to apply group membership changes: sudo reboot"
echo "3. 🚀 After reboot, run: ./launch.sh"
echo ""
echo "Optional:"
echo "- To enable auto-startup on boot: ./setup-autostart.sh"
echo "- Desktop launcher created (if Desktop folder exists)"
echo ""
echo -e "${BLUE}📖 For help and documentation, see README.md${NC}"

# Ask about reboot
echo ""
read -p "Reboot now to apply changes? [y/N]: " reboot_now
if [ "$reboot_now" = "y" ] || [ "$reboot_now" = "Y" ]; then
    echo "Rebooting in 5 seconds... (Ctrl+C to cancel)"
    sleep 5
    sudo reboot
fi
