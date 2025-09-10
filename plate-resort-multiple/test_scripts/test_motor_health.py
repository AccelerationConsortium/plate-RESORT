#!/usr/bin/env python3
"""
Motor health monitoring test for PlateResort
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plate_resort import PlateResort
import time

def main():
    resort = PlateResort()
    
    try:
        print("Connecting to motor...")
        resort.connect()
        print("Connected!")
        
        # Initial health check
        resort.print_motor_health()
        
        # Test movement with health monitoring
        print("\n" + "="*50)
        print("Testing movement with health monitoring...")
        
        for hotel in resort.hotels:
            print(f"\nMoving to hotel {hotel}...")
            
            # Health before movement
            health_before = resort.get_motor_health()
            
            # Move
            success = resort.activate_hotel(hotel)
            
            # Health after movement
            time.sleep(1)  # Let readings settle
            health_after = resort.get_motor_health()
            
            if success:
                print(f"✓ Reached hotel {hotel}")
                print(f"  Temp: {health_before['temperature']}°C → {health_after['temperature']}°C")
                print(f"  Current: {health_before['current']:.0f}mA → {health_after['current']:.0f}mA")
                print(f"  Position: {health_before['position']:.1f}° → {health_after['position']:.1f}°")
                
                if health_after['warnings']:
                    print("  ⚠️  Warnings:", ", ".join(health_after['warnings']))
            else:
                print(f"✗ Failed to reach hotel {hotel}")
                resort.print_motor_health()
                break
                
        # Final comprehensive health check
        print("\n" + "="*50)
        print("Final Health Report:")
        resort.print_motor_health()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if resort.port:
            resort.disconnect()
        print("\nDisconnected")

if __name__ == "__main__":
    main()
