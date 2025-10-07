#!/bin/bash
# Plate Resort Client Demo Script
# Demonstrates all available client commands

# Configuration
PI_HOST="100.83.140.57"
API_KEY="PZIFj85Bh2oP64yVkuaWZehG9Wc1YXiM"

echo "🚀 Plate Resort Client Demo"
echo "============================"
echo "Server: $PI_HOST"
echo "API Key: $API_KEY"
echo ""

# Helper function to run commands with consistent formatting
run_cmd() {
    echo "📋 Command: $1"
    echo "─────────────────────────────────────────"
    eval "$1"
    echo ""
    read -p "Press Enter to continue..."
    echo ""
}

# 1. Check server health (no auth required)
run_cmd "curl.exe http://$PI_HOST:8000/health"

# 2. Get server status
run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY status"

# 3. Connect to motor (only if motor is plugged in)
echo "⚠️  Next command will try to connect to motor at /dev/ttyUSB0"
read -p "Continue? (y/N): " connect_motor
if [[ $connect_motor == "y" || $connect_motor == "Y" ]]; then
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY connect"
    
    # 4. Get status after connection
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY status"
    
    # 5. Get current position
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY position"
    
    # 6. Move to specific angle
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY move 90.0"
    
    # 7. Wait and check position
    echo "⏱️  Waiting 3 seconds for movement..."
    sleep 3
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY position"
    
    # 8. Activate hotel A
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY activate A"
    
    # 9. Check which hotel is active
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY status"
    
    # 10. Activate hotel B
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY activate B"
    
    # 11. Go to home position
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY home"
    
    # 12. Emergency stop (safe to run anytime)
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY stop"
    
    # 13. Disconnect motor
    run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY disconnect"
else
    echo "Skipping motor commands (no motor connected)"
fi

# 14. Final status check
run_cmd "plate-resort-client --host $PI_HOST --api-key $API_KEY status"

echo "✅ Demo completed!"
echo ""
echo "🔗 Useful URLs:"
echo "   Server: http://$PI_HOST:8000"
echo "   API Docs: http://$PI_HOST:8000/docs"
echo ""
echo "📖 Available Commands:"
echo "   plate-resort-client --help        # Show all options"
echo "   plate-resort-client status        # Server status"
echo "   plate-resort-client connect       # Connect to motor"
echo "   plate-resort-client position      # Get position"
echo "   plate-resort-client move <angle>  # Move to angle"
echo "   plate-resort-client activate <X>  # Activate hotel (A,B,C,D)"
echo "   plate-resort-client home          # Go to home position"
echo "   plate-resort-client stop          # Emergency stop"
echo "   plate-resort-client disconnect    # Disconnect motor"