#!/usr/bin/env python3
"""
Test script for PlateResort class
"""
from plate_resort import PlateResort
import time

def main():
    # Initialize resort
    resort = PlateResort()
    
    try:
        # Connect to motor
        resort.connect()
        print("Connected to PlateResort")
        
        # Test hotel activation
        for hotel in ['A', 'B', 'C', 'D']:
            print(f"\nActivating hotel {hotel}...")
            resort.activate_hotel(hotel)
            
            # Wait for movement and check position
            time.sleep(2)
            current_pos = resort.get_current_position()
            print(f"Current position: {current_pos:.1f}°")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        resort.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    main()
