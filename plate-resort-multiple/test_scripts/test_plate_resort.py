#!/usr/bin/env python3
"""
Test script for PlateResort class
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plate_resort import PlateResort
import time

def main():
    # Initialize resort from YAML config with speed override
    resort = PlateResort(speed=50)
    
    try:
        # Connect to motor
        print("Connecting to motor...")
        resort.connect()
        print("Connected to PlateResort")
        print(f"Config: {len(resort.hotels)} hotels, {resort.rooms} rooms each")
        print(f"Hotel angles: {resort.hotel_angles}")
        print(f"Rotation direction: {'CW' if resort.rotation_direction == 1 else 'CCW'}")
        
        # Check initial position
        initial_pos = resort.get_current_position()
        print(f"Initial position: {initial_pos:.1f}°")
        
        # Check what hotel is currently active
        active_hotel = resort.get_active_hotel()
        if active_hotel:
            print(f"Currently active hotel: {active_hotel}")
        else:
            print("No hotel is currently active (position not aligned)")
        
        # Test hotel activation with config defaults
        for hotel in resort.hotels:
            print(f"\nActivating hotel {hotel}...")
            success = resort.activate_hotel(hotel)  # Uses config tolerance/timeout
            if success:
                active = resort.get_active_hotel()
                print(f"Active hotel confirmed: {active}")
            else:
                print(f"Failed to reach hotel {hotel}")
                break
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        resort.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    main()
