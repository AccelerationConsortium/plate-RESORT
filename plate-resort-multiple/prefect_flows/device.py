"""
Prefect flows for Plate Resort device control.
These flows run on the device (Raspberry Pi) that has physical access to the motor.
"""
from plate_resort.core import PlateResort

# Create a singleton instance
resort_instance = None

def get_resort():
    """Get or create the PlateResort instance"""
    global resort_instance
    if resort_instance is None:
        resort_instance = PlateResort()
    return resort_instance

