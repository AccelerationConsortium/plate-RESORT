"""
Example usage of PlateResort with Prefect flows

The PlateResort class methods are decorated with @flow, so they
can be used directly as Prefect flows.
"""

from plate_resort.core import PlateResort

# Create instance
resort = PlateResort()

# Use methods directly - they are Prefect flows
resort.connect()
resort.activate_hotel("A")
position = resort.get_current_position()
print(f"Current position: {position}")
resort.go_home()
resort.disconnect()
