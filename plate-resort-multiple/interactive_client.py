#!/usr/bin/env python3
"""
Interactive Plate Resort Client
Command-line interface for controlling the P            elif cmd == "position":
                if not self.connected:
                    print("⚠️  Motor not connected. Use 'connect' first.")
                else:
                    result = self.client.get_position()
                    print(f"📍 Current Position: {result}")
                    
            elif cmd == "move":
                if len(args) < 1:
                    print("❌ Please specify an angle (e.g., move 90)")
                elif not self.connected:
                    print("⚠️  Motor not connected. Use 'connect' first.")
                else:
                    try:
                        angle = float(args[0])
                        print(f"🔄 Moving to {angle}°...")
                        result = self.client.move_to_angle(angle)
                        print(f"   Result: {result}")
                    except ValueError:
                        print("❌ Invalid angle. Please provide a number.")
                        
            elif cmd == "stop":ver
"""

import sys
import requests
from plate_resort.client import PlateResortClient


class InteractivePlateResort:
    def __init__(self, host, api_key):
        self.host = host
        self.api_key = api_key
        self.server_url = f"http://{host}:8000"
        self.client = PlateResortClient(self.server_url, api_key)
        self.connected = False
        
    def print_banner(self):
        """Print welcome banner"""
        print("🚀 Interactive Plate Resort Client")
        print("=" * 50)
        print(f"Server: {self.server_url}")
        print(f"API Key: {self.api_key}")
        print("=" * 50)
        print("Type 'help' for available commands, 'quit' to exit")
        print()
    
    def print_help(self):
        """Print available commands"""
        commands = {
            "Server Commands": [
                "status - Get server status",
                "health - Get motor health diagnostics",
                "docs - Show API documentation URL"
            ],
            "Motor Commands": [
                "connect - Connect to motor",
                "disconnect - Disconnect motor", 
                "position - Get current motor position",
                "move <angle> - Move to specific angle (e.g., move 90)",
                "stop - Emergency stop motor"
            ],
            "Hotel Commands": [
                "activate <hotel> - Activate hotel (e.g., activate A)",
                "home - Return to home position",
                "hotels - List available hotels"
            ],
            "Utility Commands": [
                "clear - Clear screen",
                "help - Show this help",
                "quit/exit - Exit the program"
            ]
        }
        
        print("\n📚 Available Commands:")
        print("=" * 30)
        for category, cmd_list in commands.items():
            print(f"\n🔹 {category}:")
            for cmd in cmd_list:
                print(f"   {cmd}")
        print()
    
    def handle_command(self, command):
        """Process user commands"""
        parts = command.strip().split()
        if not parts:
            return True
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        try:
            # Server commands
            if cmd == "status":
                result = self.client.status()
                print(f"📊 Status: {result}")
                self.connected = result.get('connected', False)
                
            elif cmd == "health":
                result = self.client.health()
                print(f"❤️  Health: {result}")
                
            elif cmd == "docs":
                print(f"📖 API Documentation: {self.server_url}/docs")
                
            # Motor commands
            elif cmd == "connect":
                print("🔌 Connecting to motor...")
                result = self.client.connect()
                print(f"   Result: {result}")
                self.connected = True
                
            elif cmd == "disconnect":
                print("🔌 Disconnecting motor...")
                result = self.client.disconnect()
                print(f"   Result: {result}")
                self.connected = False
                
            elif cmd == "position":
                if not self.connected:
                    print("⚠️  Motor not connected. Use 'connect' first.")
                else:
                    position = self.client.get_position()
                    print(f"📍 Current position: {position}°")
                    
            elif cmd == "move":
                if not args:
                    print("❌ Usage: move <angle> (e.g., move 90)")
                elif not self.connected:
                    print("⚠️  Motor not connected. Use 'connect' first.")
                else:
                    try:
                        angle = float(args[0])
                        print(f"🔄 Moving to {angle}°...")
                        result = self.client.move_to_position(angle)
                        print(f"   Result: {result}")
                    except ValueError:
                        print("❌ Invalid angle. Please provide a number.")
                        
            elif cmd == "stop":
                print("🛑 Emergency stop!")
                result = self.client.emergency_stop()
                print(f"   Result: {result}")
                
            # Hotel commands
            elif cmd == "activate":
                if not args:
                    print("❌ Usage: activate <hotel> (e.g., activate A)")
                elif not self.connected:
                    print("⚠️  Motor not connected. Use 'connect' first.")
                else:
                    hotel = args[0].upper()
                    if hotel not in ['A', 'B', 'C', 'D']:
                        print("❌ Invalid hotel. Use A, B, C, or D.")
                    else:
                        print(f"🏨 Activating hotel {hotel}...")
                        result = self.client.activate_hotel(hotel)
                        print(f"   Result: {result}")
                        
            elif cmd == "home":
                if not self.connected:
                    print("⚠️  Motor not connected. Use 'connect' first.")
                else:
                    print("🏠 Returning to home position...")
                    result = self.client.go_home()
                    print(f"   Result: {result}")
                    
            elif cmd == "hotels":
                print("🏨 Available hotels: A, B, C, D")
                
            # Utility commands
            elif cmd == "clear":
                import os
                os.system('cls' if os.name == 'nt' else 'clear')
                self.print_banner()
                
            elif cmd == "help":
                self.print_help()
                
            elif cmd in ["quit", "exit"]:
                print("👋 Goodbye!")
                return False
                
            else:
                print(f"❌ Unknown command: {cmd}")
                print("Type 'help' for available commands.")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Could not connect to server at {self.server_url}")
            print("   Make sure the server is running and accessible.")
        except Exception as e:
            print(f"❌ Error: {e}")
            
        return True
    
    def run(self):
        """Main interactive loop"""
        self.print_banner()
        
        # Test connection
        try:
            health = self.client.health()
            print(f"✅ Server is healthy: {health}")
        except:
            print("⚠️  Could not reach server or authenticate. Commands may fail.")
        
        print("\nReady for commands!")
        
        while True:
            try:
                # Show connection status in prompt
                status_indicator = "🟢" if self.connected else "🔴"
                command = input(f"\n{status_indicator} plate-resort> ").strip()
                
                if not self.handle_command(command):
                    break
                    
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break


def main():
    # Configuration
    PI_HOST = "100.83.140.57"
    API_KEY = "PZIFj85Bh2oP64yVkuaWZehG9Wc1YXiM"
    
    # Allow command line override
    if len(sys.argv) > 1:
        PI_HOST = sys.argv[1]
    if len(sys.argv) > 2:
        API_KEY = sys.argv[2]
    
    # Start interactive session
    interactive = InteractivePlateResort(PI_HOST, API_KEY)
    interactive.run()


if __name__ == "__main__":
    main()