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
    # Initialize resort with 5% speed
    resort = PlateResort(speed=50)
    
    try:
        # Connect to motor
        print("Connecting to motor...")
        resort.connect()
        print("Connected to PlateResort")
        print(f"Hotel angles: {resort.hotel_angles}")
        
        # Check initial position
        initial_pos = resort.get_current_position()
        print(f"Initial position: {initial_pos:.1f}°")
        
        # Test hotel activation
        for hotel in ['A', 'B', 'C', 'D']:
            print(f"\nActivating hotel {hotel}...")
            resort.activate_hotel(hotel)
            
            # Wait longer for slow movement at 5% speed
            print("Waiting for movement to complete...")
            time.sleep(8)
            current_pos = resort.get_current_position()
            target_pos = resort.hotel_angles[hotel]
            print(f"Target: {target_pos}°, Current: {current_pos:.1f}°")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        resort.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    main()
