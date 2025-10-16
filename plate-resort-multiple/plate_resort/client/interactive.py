#!/usr/bin/env python3
"""
Interactive Plate Resort Client - Prefect Workflows
Command-line interface for controlling the Plate Resort via Prefect flows
"""

import os
import configparser
from pathlib import Path
from plate_resort.core import PlateResort
from plate_resort.workflows import orchestrator


def load_client_config():
    """Load client configuration from secrets.ini or environment variables"""
    config = {
        'host': 'localhost',
        'port': 4200,
        'prefect_api_url': 'http://localhost:4200/api'
    }
    
    # Try to load from the repository root secrets.ini
    repo_root = Path(__file__).parents[2]
    secrets_file = str(repo_root / 'secrets.ini')
    if os.path.exists(secrets_file):
        try:
            parser = configparser.ConfigParser()
            parser.read(secrets_file)
            
            if 'client' in parser:
                config['host'] = parser.get('client', 'default_host', 
                                          fallback=config['host'])
                config['port'] = parser.getint('client', 'default_port', 
                                             fallback=config['port'])
            
            if 'prefect' in parser:
                config['prefect_api_url'] = parser.get('prefect', 'server_api_url',
                                                     fallback=config['prefect_api_url'])
            if 'server' in parser:
                api_key = parser.get('server', 'api_key', fallback=None)
                if api_key:
                    config['api_key'] = api_key
                    
        except Exception as e:
            print(f"⚠️  Warning: Could not read config/secrets.ini: {e}")
    
    # Environment variables override file settings
    config['host'] = os.getenv('PREFECT_HOST', config['host'])
    config['port'] = int(os.getenv('PREFECT_PORT', config['port']))
    config['prefect_api_url'] = os.getenv('PREFECT_API_URL', config['prefect_api_url'])
    # Set Prefect API key if provided in config or environment
    api_key = os.getenv('PREFECT_API_KEY', config.get('api_key'))
    if api_key:
        os.environ['PREFECT_API_KEY'] = api_key

    return config


class InteractivePlateResort:
    """Interactive client for Plate Resort workflows"""
    
    def __init__(self, use_remote=False):
        """Initialize client in local or remote mode"""
        self.use_remote = use_remote
        self.config = load_client_config()
        
        if use_remote:
            print(f"🌐 Remote mode - Using Prefect server: {self.config['prefect_api_url']}")
            # Set Prefect API URL for remote orchestration
            os.environ['PREFECT_API_URL'] = self.config['prefect_api_url']
        else:
            print("🏠 Local mode - Running flows directly")
            self.resort = PlateResort()

    def show_help(self):
        """Display available commands"""
        print("\n📋 Available Commands:")
        print("─" * 50)
        print("🔌 Connection:")
        print("  connect              - Connect to motor")
        print("  disconnect           - Disconnect from motor")
        print("  status              - Check connection status")
        print("  health              - Get motor health")
        print("")
        print("🎯 Movement:")
        print("  activate <hotel>     - Move to hotel (A/B/C/D)")
        print("  home                - Return to home position")
        print("  angle <degrees>     - Move to specific angle")
        print("  position            - Get current position")
        print("")
        print("⚙️  Settings:")
        print("  speed <value>       - Set movement speed (1-100)")
        print("")
        print("🚨 Emergency:")
        print("  stop                - Emergency stop")
        print("")
        print("ℹ️  Info:")
        print("  help                - Show this help")
        print("  quit/exit           - Exit client")
        print("─" * 50)

    def execute_command(self, command):
        """Execute a command in local or remote mode"""
        parts = command.strip().split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        try:
            if cmd == "connect":
                if self.use_remote:
                    result = orchestrator.connect()
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    self.resort.connect()
                    print("✅ Connected to motor")
                    
            elif cmd == "disconnect":
                if self.use_remote:
                    result = orchestrator.disconnect()
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    self.resort.disconnect()
                    print("✅ Disconnected from motor")
                    
            elif cmd == "health":
                if self.use_remote:
                    result = orchestrator.get_health()
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    health = self.resort.get_motor_health()
                    print(f"🏥 Motor Health: {health}")
                    
            elif cmd == "activate":
                if not args:
                    print("❌ Usage: activate <hotel> (A/B/C/D)")
                    return
                hotel = args[0].upper()
                if self.use_remote:
                    result = orchestrator.activate_hotel(hotel)
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    self.resort.activate_hotel(hotel)
                    print(f"✅ Moved to hotel {hotel}")
                    
            elif cmd == "home":
                if self.use_remote:
                    result = orchestrator.go_home()
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    self.resort.go_home()
                    print("✅ Returned to home position")
                    
            elif cmd == "angle":
                if not args:
                    print("❌ Usage: angle <degrees>")
                    return
                angle = float(args[0])
                if self.use_remote:
                    result = orchestrator.move_to_angle(angle)
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    self.resort.move_to_angle(angle)
                    print(f"✅ Moved to {angle}°")
                    
            elif cmd == "position":
                if self.use_remote:
                    result = orchestrator.get_position()
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    pos = self.resort.get_current_position()
                    print(f"📍 Current position: {pos}°")
                    
            elif cmd == "speed":
                if not args:
                    print("❌ Usage: speed <value> (1-100)")
                    return
                speed = int(args[0])
                if self.use_remote:
                    result = orchestrator.set_speed(speed)
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    self.resort.set_speed(speed)
                    print(f"✅ Speed set to {speed}")
                    
            elif cmd == "stop":
                if self.use_remote:
                    result = orchestrator.emergency_stop()
                    print(f"📡 Remote flow submitted: {result}")
                else:
                    self.resort.emergency_stop()
                    print("🛑 Emergency stop executed")
                    
            elif cmd in ["help", "?"]:
                self.show_help()
                
            else:
                print(f"❌ Unknown command: {cmd}")
                print("💡 Type 'help' for available commands")
                
        except Exception as e:
            print(f"❌ Error: {e}")

    def run(self):
        """Main interactive loop"""
        print("🚀 Plate Resort Interactive Client")
        print("═" * 50)
        self.show_help()
        while True:
            cmd = input("› ")
            if cmd.lower() in ("quit", "exit"):  # allow user to exit
                print("👋 Bye!")
                break
            self.execute_command(cmd)

# Add CLI entrypoint

def main():
    """Command-line interface for interactive Plate Resort client"""
    import argparse
    parser = argparse.ArgumentParser(
        description="Plate Resort Interactive Client (local or remote via Prefect)")
    parser.add_argument(
        '-r', '--remote', action='store_true',
        help='Use remote Prefect server instead of local instance')
    args = parser.parse_args()
    client = InteractivePlateResort(use_remote=args.remote)
    client.run()


if __name__ == "__main__":
    main()