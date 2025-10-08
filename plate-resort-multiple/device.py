from prefect import flow
from plate_resort.core import PlateResort

_resort = None

def get_resort():
    """Get or create PlateResort instance"""
    global _resort
    if _resort is None:
        _resort = PlateResort()
    return _resort

@flow
def connect(device: str = "/dev/ttyUSB0", baudrate: int = 57600, motor_id: int = 1):
    """Connect to Dynamixel motor"""
    resort = get_resort()
    resort.device = device
    resort.baud = baudrate
    resort.motor_id = motor_id
    resort.connect()
    return {"status": "connected", "device": device}

@flow
def disconnect():
    """Disconnect from motor"""
    resort = get_resort()
    resort.disconnect()
    return {"status": "disconnected"}

@flow
def status():
    """Get current system status"""
    resort = get_resort()
    return {
        "connected": resort.is_connected(),
        "current_hotel": resort.current_hotel,
        "hotels": list(resort.hotels)
    }

@flow
def health():
    """Get motor health diagnostics"""
    resort = get_resort()
    return resort.get_motor_health()

@flow
def activate_hotel(hotel: str):
    """Move to specified hotel"""
    resort = get_resort()
    resort.activate_hotel(hotel)
    return {"status": "moving", "hotel": hotel}

@flow
def go_home():
    """Return to home position"""
    resort = get_resort()
    resort.go_home()
    return {"status": "moving_home"}

@flow
def move_to_angle(angle: float):
    """Move to specific angle in degrees"""
    resort = get_resort()
    resort.move_to_angle(angle)
    return {"status": "moving", "angle": angle}

@flow
def get_position():
    """Get current motor position"""
    resort = get_resort()
    position = resort.get_current_position()
    return {"position": position}

@flow
def set_speed(speed: int):
    """Set motor movement speed"""
    resort = get_resort()
    resort.set_speed(speed)
    return {"status": "speed_set", "speed": speed}

@flow
def emergency_stop():
    """Emergency stop motor"""
    resort = get_resort()
    resort.emergency_stop()
    return {"status": "emergency_stopped"}

@flow
def get_hotels():
    """Get available hotels and their angles"""
    resort = get_resort()
    return {
        "hotels": resort.hotels,
        "angles": resort.hotel_angles
    }

if __name__ == "__main__":
    print("To start the worker, run: prefect worker start --pool plate-resort-pool --type process")
