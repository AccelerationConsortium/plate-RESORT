"""
Example orchestrator for running multiple PlateResort operations

This demonstrates how to use PlateResort methods as Prefect flows
for orchestration and monitoring.
"""

from plate_resort.core import PlateResort

# Create instance
resort = PlateResort()

# Connect to motor
resort.connect()

# Move to hotel A
resort.activate_hotel("A")

# Get current position
position = resort.get_current_position()
print(f"Position after moving to A: {position}")

# Go home
resort.go_home()

# Disconnect
resort.disconnect()

