#!/usr/bin/env python3
"""
Test script to verify two-stage precise movement works directly
Usage: python test_two_stage.py B
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from plate_resort.core import PlateResort


def main():
    if len(sys.argv) != 2:
        print("Usage: python test_two_stage.py <hotel>")
        print("Available hotels: A, B, C, D")
        sys.exit(1)
    
    hotel = sys.argv[1].upper()
    
    try:
        print(f"🧪 Testing TWO-STAGE movement to hotel {hotel}...")
        resort = PlateResort()
        
        print("🔌 Connecting to hardware...")
        resort.connect()
        
        print(f"📍 Current position: {resort.get_current_position():.2f}°")
        print(f"🎯 Starting PRECISE two-stage move to hotel {hotel}...")
        
        # Use the PRECISE method instead of the simple one
        result = resort.activate_hotel_precise(hotel)
        
        print(f"\n📊 Two-stage move results:")
        print(f"   ✅ Success: {result['success']}")
        print(f"   📝 Reason: {result['reason']}")
        print(f"   🔄 Pulses used: {result['pulses']}")
        print(f"   📍 Final position: {result['final_angle']:.3f}°")
        print(f"   📏 Final error: {result['final_error']:.3f}°")
        
        if result['success']:
            print(f"✅ Hotel {hotel} activated with two-stage precision!")
        else:
            print(f"❌ Two-stage move failed: {result['reason']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'resort' in locals() and resort.port:
            resort.disconnect()
            print("🔌 Disconnected from hardware")


if __name__ == "__main__":
    main()