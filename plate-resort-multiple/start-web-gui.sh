#!/bin/bash
# Simple launcher for Plate Resort Web GUI

echo "Starting Plate Resort Web GUI"
echo "Optimized for 7 inch touchscreen"

# Install dependencies if needed
echo "Checking Python dependencies..."
pip3 install -r requirements.txt --quiet

# Start the web GUI directly with Python
echo "Starting web interface..."
python3 web_gui.py &

# Store the process ID
WEB_PID=$!
echo $WEB_PID > web_gui.pid

# Wait a moment for startup
sleep 3

# Get the Pi's IP address
PI_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "Plate Resort Web GUI is running!"
echo "Process ID: $WEB_PID"
echo "Access the interface at:"
echo "  Local: http://localhost:5000"
echo "  Network: http://${PI_IP}:5000"
echo ""
echo "For fullscreen on the Pi touchscreen:"
echo "  1. Open Chromium browser"
echo "  2. Navigate to http://localhost:5000"
echo "  3. Press F11 for fullscreen"
echo ""
echo "To stop: kill $WEB_PID or pkill -f web_gui.py"
