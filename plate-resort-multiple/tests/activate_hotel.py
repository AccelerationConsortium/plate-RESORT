#!/usr/bin/env python3
"""
Simple script to activate a specific hotel for testing
Usage: python activate_hotel.py B
       python activate_hotel.py A
       python activate_hotel.py C
       python activate_hotel.py D
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from plate_resort.core import PlateResort


def main():
    if len(sys.argv) != 2:
        print("Usage: python activate_hotel.py <hotel>")
        print("Available hotels: A, B, C, D")
        sys.exit(1)

    hotel = sys.argv[1].upper()

    # Validate hotel
    valid_hotels = ["A", "B", "C", "D"]
    if hotel not in valid_hotels:
        print(
            f"Error: Invalid hotel '{hotel}'. Available hotels: {', '.join(valid_hotels)}"
        )
        sys.exit(1)

    try:
        # Initialize and connect
        print(f"🏨 Activating hotel {hotel}...")
        resort = PlateResort()

        print("🔌 Connecting to hardware...")
        resort.connect()

        print(f"📍 Current position: {resort.get_current_position():.2f}°")
        print(f"🎯 Moving to hotel {hotel}...")

        # Activate the hotel
        resort.activate_hotel(hotel)

        print(f"📍 Final position: {resort.get_current_position():.2f}°")
        print(f"✅ Hotel {hotel} activated successfully!")

    except KeyboardInterrupt:
        print("\n⏹️  Movement interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Always disconnect
        if "resort" in locals() and resort.port:
            resort.disconnect()
            print("🔌 Disconnected from hardware")


if __name__ == "__main__":
    main()
