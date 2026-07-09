#!/usr/bin/env python3
"""
Simple script to get current status and position
Usage: python status.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
        print(
            f"   🎯 Position tolerance: {resort.config.get('position_tolerance', 'N/A')}°"
        )
        print(
            f"   🔧 Control: mode {resort.config.get('operating_mode', 5)}, "
            f"gains P={resort.config.get('position_p_gain', 800)} "
            f"I={resort.config.get('position_i_gain', 300)} "
            f"D={resort.config.get('position_d_gain', 0)}"
        )

        # Show hotel positions
        print(f"\n🏨 Hotel positions:")
        for hotel, angle in resort.hotel_angles.items():
            print(f"   Hotel {hotel}: {angle:.1f}°")

        print("✅ Status check complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if "resort" in locals() and resort.port:
            resort.disconnect()
            print("🔌 Disconnected from hardware")


if __name__ == "__main__":
    main()
