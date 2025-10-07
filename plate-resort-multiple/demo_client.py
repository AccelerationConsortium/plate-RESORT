#!/usr/bin/env python3
"""
Plate Resort Client Demo Script
Demonstrates all available client operations in Python
"""

import os
import sys
import time
import configparser
import requests
from plate_resort.client import PlateResortClient


def load_client_config():
    """Load client configuration from secrets.ini or environment variables"""
    config = {
        'host': '100.83.140.57',  # Default fallback
        'port': 8000,
        'api_key': None
    }
    
    # Try to load from secrets.ini
    secrets_file = 'secrets.ini'
    if os.path.exists(secrets_file):
        try:
            parser = configparser.ConfigParser()
            parser.read(secrets_file)
            
            if 'client' in parser:
                config['host'] = parser.get('client', 'default_host', 
                                          fallback=config['host'])
                config['port'] = parser.getint('client', 'default_port', 
                                             fallback=config['port'])
            
            # Get API key from server section (shared with server)
            if 'server' in parser:
                api_key = parser.get('server', 'api_key', fallback=None)
                if api_key and api_key not in ['changeme', 'change_me', 'default']:
                    config['api_key'] = api_key
                    
        except Exception as e:
            print(f"⚠️  Warning: Could not read secrets.ini: {e}")
    
    # Environment variables override file settings
    config['host'] = os.getenv('PLATE_HOST', config['host'])
    config['port'] = int(os.getenv('PLATE_PORT', config['port']))
    config['api_key'] = os.getenv('PLATE_API_KEY', config['api_key'])
    
    return config

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
    """Main demo function"""
    # Load configuration
    config = load_client_config()
    
    # Allow command line override
    if len(sys.argv) > 1:
        config['host'] = sys.argv[1]
    if len(sys.argv) > 2:
        config['api_key'] = sys.argv[2]
    
    # Validate API key
    if not config['api_key']:
        print("❌ No API key found!")
        print("� Create secrets.ini file or set PLATE_API_KEY environment variable")
        sys.exit(1)
    
    server_url = f"http://{config['host']}:{config['port']}"
    
    print("�🚀 Plate Resort Python Client Demo")
    print(f"Server: {server_url}")
    print(f"API Key: {'*' * (len(config['api_key']) - 4) + config['api_key'][-4:]}")
    
    # Initialize client
    client = PlateResortClient(server_url, config['api_key'])
    
    try:
        # 1. Test server health
        print_section("Server Health Check")
        health = client.health()
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