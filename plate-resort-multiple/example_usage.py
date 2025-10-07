#!/usr/bin/env python3
"""
Example usage of Plate Resort System
Run this after successful installation to test basic functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from plate_resort import PlateResort
    import yaml
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure dependencies are installed:")
    print("pip3 install -r requirements.txt")
    sys.exit(1)


def main():
    print("🔧 Plate Resort System - Basic Example")
    print("=====================================")
    
    # Check if config file exists
    config_file = "resort_config.yaml"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return
    
    try:
        # Load and validate configuration
        with open(config_file, 'r') as f:
            yaml.safe_load(f)  # Just validate the YAML format
        print(f"✅ Configuration loaded from {config_file}")
        
        # Initialize PlateResort (this will test motor connection)
        resort = PlateResort(config_file)
        print("✅ PlateResort initialized successfully")
        
        # Test basic motor health
        health = resort.get_motor_health()
        print(f"🏥 Motor Health: {health}")
        
        # Show current position
        current_pos = resort.get_current_position()
        print(f"📍 Current Position: {current_pos}")
        
        print("\n🎉 Basic functionality test completed!")
        print("\nNext steps:")
        print("- Use resort.move_to_hotel('A') to move to hotel position A")
        print("- Use resort.emergency_stop() for emergency stop")
        print("- Check test_scripts/ for more examples")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check motor power and USB connection")
        print("2. Run: python3 test_scripts/test_dxl_ping.py")
        print("3. Verify device permissions: ls -la /dev/ttyUSB*")


if __name__ == "__main__":
    main()