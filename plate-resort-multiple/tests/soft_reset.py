#!/usr/bin/env python3
"""
Soft reset script for Plate Resort Dynamixel motor
Run this on the Pi to reset the motor hardware
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plate_resort.core import PlateResort
import time


def soft_reset():
    """Perform a soft reset of the Dynamixel motor"""
    print("🔄 Starting motor soft reset...")

    try:
        # Initialize resort instance
        resort = PlateResort()
        print(f"📡 Connecting to motor (ID: {resort.motor_id}) on {resort.device}...")

        # Connect to motor
        resort.connect()
        print("✓ Connected successfully")

        # Get initial status
        try:
            pos = resort.get_current_position()
            print(f"📍 Current position: {pos:.2f}°")
        except:
            print("⚠️ Could not read initial position")

        # Perform soft reboot
        print("🔄 Performing soft reboot...")
        result = resort.reboot(wait=1.0, reapply=True)
        print(f"✓ Reboot complete: {result}")

        # Wait a bit for motor to stabilize
        time.sleep(0.5)

        # Test basic functionality
        print("🧪 Testing motor functionality...")
        pos = resort.get_current_position()
        print(f"📍 Position after reset: {pos:.2f}°")

        # Test motor health
        health = resort.get_motor_health()
        print(f"🌡️ Temperature: {health['temperature']}°C")
        print(f"⚡ Voltage: {health['voltage']:.1f}V")
        print(f"🔋 Current: {health['current']:.0f}mA")

        if health["warnings"]:
            print("⚠️ Warnings:")
            for warning in health["warnings"]:
                print(f"  • {warning}")
        else:
            print("✅ All parameters normal")

        # Disconnect cleanly
        resort.disconnect()
        print("✅ Soft reset completed successfully!")

        return True

    except Exception as e:
        print(f"❌ Soft reset failed: {e}")
        return False


if __name__ == "__main__":
    success = soft_reset()
    exit(0 if success else 1)
