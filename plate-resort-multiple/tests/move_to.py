#!/usr/bin/env python3
"""
Simple script to move to a specific position in degrees
Usage: python move_to.py 45.5
       python move_to.py 90
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plate_resort.core import PlateResort


def main():
    if len(sys.argv) != 2:
        print("Usage: python move_to.py <angle>")
        print("Example: python move_to.py 45.5")
        sys.exit(1)

    try:
        angle = float(sys.argv[1])
    except ValueError:
        print("Error: Angle must be a number")
        sys.exit(1)

    try:
        print(f"🎯 Moving to {angle}°...")
        resort = PlateResort()

        print("🔌 Connecting to hardware...")
        resort.connect()

        print(f"📍 Current position: {resort.get_current_position():.2f}°")
        print(f"➡️  Moving to {angle}°...")

        # Move to position
        resort.move_to_angle(angle)

        print(f"📍 Final position: {resort.get_current_position():.2f}°")
        print(f"✅ Moved to {angle}° successfully!")

    except KeyboardInterrupt:
        print("\n⏹️  Movement interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if "resort" in locals() and resort.port:
            resort.disconnect()
            print("🔌 Disconnected from hardware")


if __name__ == "__main__":
    main()
