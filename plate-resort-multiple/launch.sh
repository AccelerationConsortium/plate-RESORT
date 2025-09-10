#!/bin/bash
"""
Plate Resort Application Launcher for Raspberry Pi
Provides easy startup options for different modes
"""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$HOME/plate-RESORT/plate-resort-multiple"

echo -e "${BLUE}🔄 Plate Resort System Launcher${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_DIR${NC}"
    echo "Please ensure the repository is cloned to ~/plate-RESORT/"
    exit 1
fi

cd "$PROJECT_DIR"

# Check if git repo is up to date
echo -e "${YELLOW}📥 Checking for updates...${NC}"
git fetch origin main
if [ $(git rev-list HEAD...origin/main --count) != 0 ]; then
    echo -e "${YELLOW}📦 Updates available! Pulling latest changes...${NC}"
    git pull origin main
else
    echo -e "${GREEN}✅ Already up to date${NC}"
fi

echo ""
echo "Select launch mode:"
echo "1) 🖥️  Touchscreen GUI (Fullscreen)"
echo "2) 🌐 Web Service Only"
echo "3) 🔧 Debug/Testing Mode"
echo "4) 🐳 Docker Mode"
echo "5) ⚙️  Configuration Check"
echo "6) 🔍 Hardware Test"
echo "0) Exit"
echo ""

read -p "Enter your choice [0-6]: " choice

case $choice in
    1)
        echo -e "${GREEN}🖥️  Starting Touchscreen GUI...${NC}"
        echo "Press Ctrl+C to stop, or ESC key to toggle fullscreen"
        export DISPLAY=:0
        python3 touchscreen_app.py
        ;;
    2)
        echo -e "${GREEN}🌐 Starting Web Service...${NC}"
        echo "Web interface will be available at:"
        echo "  Local: http://localhost:5000"
        echo "  Network: http://$(hostname -I | awk '{print $1}'):5000"
        echo "Press Ctrl+C to stop"
        python3 app.py --host 0.0.0.0 --port 5000
        ;;
    3)
        echo -e "${GREEN}🔧 Debug/Testing Mode${NC}"
        echo "Available test scripts:"
        echo "  1) Motor health check"
        echo "  2) Basic functionality test"
        echo "  3) Motor ping test"
        echo "  4) Manual keyboard control"
        echo ""
        read -p "Select test [1-4]: " test_choice
        case $test_choice in
            1) python3 test_scripts/test_motor_health.py ;;
            2) python3 test_scripts/test_plate_resort.py ;;
            3) python3 test_scripts/test_dxl_ping.py ;;
            4) python3 dxl_keyboard_test.py ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
    4)
        echo -e "${GREEN}🐳 Docker Mode${NC}"
        echo "Select Docker option:"
        echo "  1) Web service in Docker"
        echo "  2) GUI in Docker (requires X11)"
        echo "  3) Build containers"
        echo ""
        read -p "Select option [1-3]: " docker_choice
        case $docker_choice in
            1)
                echo "Starting web service in Docker..."
                docker-compose up plate-resort-app
                ;;
            2)
                echo "Setting up X11 for GUI..."
                export DISPLAY=:0
                xhost +local:docker
                echo "Starting GUI in Docker..."
                docker-compose up plate-resort-gui
                ;;
            3)
                echo "Building Docker containers..."
                docker-compose build
                ;;
            *)
                echo "Invalid choice"
                ;;
        esac
        ;;
    5)
        echo -e "${GREEN}⚙️  Configuration Check${NC}"
        echo ""
        echo "=== System Configuration ==="
        echo "Python version: $(python3 --version)"
        echo "Project directory: $PROJECT_DIR"
        echo "Git status:"
        git status --porcelain
        echo ""
        echo "=== Hardware Check ==="
        echo "USB devices:"
        ls -la /dev/ttyUSB* 2>/dev/null || echo "No USB serial devices found"
        echo ""
        echo "=== Configuration File ==="
        if [ -f "resort_config.yaml" ]; then
            echo "✅ Configuration file found"
            echo "Hotels configured: $(grep -A1 'hotels:' resort_config.yaml | tail -1)"
        else
            echo "❌ Configuration file missing"
        fi
        echo ""
        echo "=== Python Dependencies ==="
        python3 -c "
import sys
modules = ['dynamixel_sdk', 'yaml', 'flask', 'tkinter']
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        print(f'❌ {module} - NOT INSTALLED')
"
        ;;
    6)
        echo -e "${GREEN}🔍 Hardware Test${NC}"
        echo "Testing hardware connection..."
        echo ""
        if [ -e /dev/ttyUSB0 ]; then
            echo "✅ USB device found: /dev/ttyUSB0"
            echo "Device permissions:"
            ls -la /dev/ttyUSB0
            echo ""
            echo "Testing motor communication..."
            python3 test_scripts/test_dxl_ping.py --device /dev/ttyUSB0 --baud 57600 --id 1
        else
            echo "❌ No USB device found at /dev/ttyUSB0"
            echo "Available USB devices:"
            ls -la /dev/ttyUSB* 2>/dev/null || echo "No USB serial devices detected"
            echo ""
            echo "To fix this issue:"
            echo "1. Check USB cable connection"
            echo "2. Check device permissions: sudo chmod 666 /dev/ttyUSB0"
            echo "3. Add user to dialout group: sudo usermod -a -G dialout $USER"
        fi
        ;;
    0)
        echo -e "${BLUE}👋 Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}🔄 Launcher finished. Run './launch.sh' again to restart.${NC}"
