#!/usr/bin/env python3
"""
Simple script to get current status and position
Usage: python status.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plate_resort.core import PlateResort


def main():
    try:
        print("🔍 Checking PlateResort status...")
        resort = PlateResort()
        
        print("🔌 Connecting to hardware...")
        resort.connect()
        
        print("\n📊 Current Status:")
        print(f"   📍 Position: {resort.get_current_position():.2f}°")
        print(f"   🏨 Current hotel: {resort.current_hotel or 'Unknown'}")
        print(f"   ⚙️  Motor speed: {resort.speed}")
        print(f"   🎯 Position tolerance: {resort.config.get('position_tolerance', 'N/A')}°")
        print(f"   🔧 Two-stage move: {'Enabled' if resort.config.get('enable_precise_move') else 'Disabled'}")
        
        # Show hotel positions
        print(f"\n🏨 Hotel positions:")
        for hotel, angle in resort.hotel_angles.items():
            print(f"   Hotel {hotel}: {angle:.1f}°")
        
        print("✅ Status check complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'resort' in locals() and resort.port:
            resort.disconnect()
            print("🔌 Disconnected from hardware")


if __name__ == "__main__":
    main()