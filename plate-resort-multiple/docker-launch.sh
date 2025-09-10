#!/bin/bash
#
# Docker-Only Plate Resort Launcher
# Everything runs inside containers for clean dependency management
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🐳 Plate Resort System - Docker Mode${NC}"
echo -e "${BLUE}====================================${NC}"
echo ""

# Check for updates
echo -e "${YELLOW}📥 Checking for updates...${NC}"
git pull origin main

echo ""
echo "Select mode:"
echo "1) 🖥️  GUI Mode (Touchscreen Interface)"
echo "2) 🌐 Web Service Mode"
echo "3) 🔧 Debug/Testing Mode"
echo "4) 🛠️  Build/Rebuild Containers"
echo "5) 🧹 Clean Containers"
echo "6) 📊 Container Status"
echo "0) Exit"
echo ""

read -p "Enter your choice [0-6]: " choice

case $choice in
    1)
        echo -e "${GREEN}🖥️  Starting GUI in Docker...${NC}"
        echo "Setting up X11 for GUI..."
        xhost +local:docker >/dev/null 2>&1
        echo "Starting touchscreen interface..."
        echo "Debug logs will appear below. Press Ctrl+C to stop."
        docker-compose up --build plate-resort-gui
        ;;
    2)
        echo -e "${GREEN}🌐 Starting Web Service in Docker...${NC}"
        echo "Web interface will be available at:"
        echo "  Local: http://localhost:5000"
        echo "  Network: http://$(hostname -I | awk '{print $1}'):5000"
        echo "Press Ctrl+C to stop"
        docker-compose up --build plate-resort-app
        ;;
    3)
        echo -e "${GREEN}🔧 Debug/Testing Mode${NC}"
        echo "Running debug container with shell access..."
        docker-compose build plate-resort-app
        docker run -it --rm \
            --privileged \
            -v /dev:/dev \
            -v $(pwd):/app \
            -w /app \
            --user 1000:1000 \
            plate-resort-multiple_plate-resort-app /bin/bash
        ;;
    4)
        echo -e "${GREEN}🛠️  Building/Rebuilding Containers...${NC}"
        echo "Stopping any running containers..."
        docker-compose down
        echo "Removing old images..."
        docker-compose build --no-cache
        echo "✅ Containers rebuilt successfully!"
        ;;
    5)
        echo -e "${YELLOW}🧹 Cleaning up containers and images...${NC}"
        docker-compose down --volumes --remove-orphans
        docker system prune -f
        echo "✅ Cleanup completed!"
        ;;
    6)
        echo -e "${BLUE}📊 Container Status${NC}"
        echo ""
        echo "=== Running Containers ==="
        docker-compose ps
        echo ""
        echo "=== Docker Images ==="
        docker images | grep plate-resort
        echo ""
        echo "=== Docker System Info ==="
        docker system df
        ;;
    0)
        echo -e "${GREEN}👋 Goodbye!${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Invalid choice. Please try again.${NC}"
        ;;
esac

echo ""
echo -e "${BLUE}🔄 Launcher finished. Run './docker-launch.sh' again to restart.${NC}"
