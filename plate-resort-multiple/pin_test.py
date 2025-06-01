#!/usr/bin/env python3
import platform
import os

print("System Information:")
print(f"Platform: {platform.platform()}")
print(f"Machine: {platform.machine()}")
print(f"Python version: {platform.python_version()}")

# Check if running on Raspberry Pi
def is_raspberry_pi():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Model'):
                    return '[Raspberry Pi]' in line
        return False
    except:
        return False

print(f"\nIs this a Raspberry Pi? {is_raspberry_pi()}")

print("\nTrying to import board module:")
try:
    import board
    print("\nAvailable board pins:")
    for pin in dir(board):
        if not pin.startswith('__'):  # Skip internal attributes
            print(pin)
except Exception as e:
    print(f"Error importing board module: {str(e)}")

print("\nChecking if Blinka is installed:")
try:
    import pkg_resources
    blinka_version = pkg_resources.get_distribution('Adafruit-Blinka').version
    print(f"Adafruit-Blinka version: {blinka_version}")
except Exception as e:
    print(f"Error checking Blinka: {str(e)}") 