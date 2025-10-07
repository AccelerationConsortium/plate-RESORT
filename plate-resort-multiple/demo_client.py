#!/usr/bin/env python3
"""
Plate Resort Client Demo Script
Demonstrates all available client operations in Python
"""

import time
import requests
from plate_resort.client import PlateResortClient

# Configuration
PI_HOST = "100.83.140.57"
API_KEY = "PZIFj85Bh2oP64yVkuaWZehG9Wc1YXiM"
SERVER_URL = f"http://{PI_HOST}:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f"🚀 {title}")
    print('='*50)

def print_result(operation, result):
    """Print operation result with formatting"""
    print(f"📋 {operation}:")
    print(f"   Result: {result}")
    print()

def wait_for_input(message="Press Enter to continue..."):
    """Wait for user input"""
    input(f"⏸️  {message}")

def main():
    print("🚀 Plate Resort Python Client Demo")
    print(f"Server: {SERVER_URL}")
    print(f"API Key: {API_KEY}")
    
    # Initialize client
    client = PlateResortClient(SERVER_URL, API_KEY)
    
    try:
        # 1. Test server health (no auth required)
        print_section("Server Health Check")
        health = requests.get(f"{SERVER_URL}/health").json()
        print_result("Health Check", health)
        wait_for_input()
        
        # 2. Get server status
        print_section("Server Status")
        status = client.status()
        print_result("Server Status", status)
        wait_for_input()
        
        # 3. Ask about motor connection
        print_section("Motor Connection")
        connect_motor = input("🤖 Do you want to connect to the motor? (y/N): ").lower()
        
        if connect_motor in ['y', 'yes']:
            # Connect to motor
            try:
                print("🔌 Connecting to motor...")
                result = client.connect()
                print_result("Motor Connection", result)
                wait_for_input()
                
                # Get status after connection
                print_section("Post-Connection Status")
                status = client.status()
                print_result("Status After Connect", status)
                wait_for_input()
                
                # Get current position
                print_section("Position Reading")
                position = client.get_position()
                print_result("Current Position", f"{position}°")
                wait_for_input()
                
                # Demonstrate movement
                print_section("Motor Movement Demo")
                angles = [90.0, 180.0, 270.0, 0.0]
                
                for angle in angles:
                    print(f"🔄 Moving to {angle}°...")
                    result = client.move_to_position(angle)
                    print_result(f"Move to {angle}°", result)
                    
                    # Wait for movement and check position
                    time.sleep(2)
                    current_pos = client.get_position()
                    print(f"   Current position: {current_pos}°")
                    wait_for_input("Continue to next position?")
                
                # Demonstrate hotel activation
                print_section("Hotel Activation Demo")
                hotels = ['A', 'B', 'C', 'D']
                
                for hotel in hotels:
                    print(f"🏨 Activating Hotel {hotel}...")
                    result = client.activate_hotel(hotel)
                    print_result(f"Activate Hotel {hotel}", result)
                    
                    # Check status
                    status = client.status()
                    active_hotel = status.get('active_hotel')
                    print(f"   Active hotel: {active_hotel}")
                    wait_for_input("Continue to next hotel?")
                
                # Go home
                print_section("Return Home")
                print("🏠 Returning to home position...")
                result = client.go_home()
                print_result("Go Home", result)
                wait_for_input()
                
                # Test emergency stop
                print_section("Emergency Stop Test")
                print("🛑 Testing emergency stop...")
                result = client.emergency_stop()
                print_result("Emergency Stop", result)
                wait_for_input()
                
                # Disconnect motor
                print_section("Motor Disconnection")
                print("🔌 Disconnecting motor...")
                result = client.disconnect()
                print_result("Motor Disconnect", result)
                wait_for_input()
                
            except Exception as e:
                print(f"❌ Motor operation failed: {e}")
                print("This is normal if no motor is connected.")
        
        else:
            print("⏭️  Skipping motor operations (no motor connection requested)")
        
        # Final status check
        print_section("Final Status Check")
        final_status = client.status()
        print_result("Final Status", final_status)
        
        # Show available methods
        print_section("Available Client Methods")
        methods = [
            "client.status()",
            "client.health()", 
            "client.connect(device='/dev/ttyUSB0', baudrate=57600, motor_id=1)",
            "client.disconnect()",
            "client.get_position()",
            "client.move_to_position(angle)",
            "client.activate_hotel('A')",  # or B, C, D
            "client.go_home()",
            "client.emergency_stop()",
        ]
        
        print("📚 Available methods:")
        for method in methods:
            print(f"   {method}")
        
        print(f"\n🔗 Useful URLs:")
        print(f"   Server: {SERVER_URL}")
        print(f"   API Docs: {SERVER_URL}/docs")
        
        print(f"\n✅ Demo completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {SERVER_URL}")
        print("   Make sure the server is running and accessible.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()