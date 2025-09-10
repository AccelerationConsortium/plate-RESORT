#!/bin/bash
# Simple launcher for Plate Resort Web GUI

echo "Starting Plate Resort Web GUI"
echo "Optimized for 7 inch touchscreen"

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null

# Start the web GUI
echo "Starting web interface..."
docker-compose up --build -d plate-resort-web

# Wait a moment for startup
sleep 3

# Get the Pi's IP address
PI_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "Plate Resort Web GUI is running!"
echo "Access the interface at:"
echo "  Local: http://localhost:5000"
echo "  Network: http://${PI_IP}:5000"
echo ""
echo "For fullscreen on the Pi touchscreen:"
echo "  1. Open Chromium browser"
echo "  2. Navigate to http://localhost:5000"
echo "  3. Press F11 for fullscreen"
echo ""
echo "To view logs: docker-compose logs -f plate-resort-web"
echo "To stop: docker-compose down"
