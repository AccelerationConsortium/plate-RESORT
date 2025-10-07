"""
Prefect flows for Plate Resort device control.
These flows run on the device (Raspberry Pi) that has physical access to the motor.
"""
import sys
import os
from prefect import flow, task

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from plate_resort.core import PlateResort


resort_instance = None


def get_resort():
    """Get or create the PlateResort instance"""
    global resort_instance
    if resort_instance is None:
        resort_instance = PlateResort()
    return resort_instance


@task
def connect_motor(device: str = "/dev/ttyUSB0", baudrate: int = 57600, motor_id: int = 1):
    """Connect to the Dynamixel motor"""
    resort = get_resort()
    resort.device = device
    resort.baud = baudrate
    resort.motor_id = motor_id
    resort.connect()
    return {"status": "connected", "device": device}


@task
def disconnect_motor():
    """Disconnect from the motor"""
    resort = get_resort()
    resort.disconnect()
    return {"status": "disconnected"}


@task
def get_status():
    """Get current system status"""
    resort = get_resort()
    return {
        "connected": resort.is_connected(),
        "current_hotel": resort.current_hotel,
        "position": resort.get_current_position() if resort.is_connected() else None,
    }


@task
def get_motor_health():
    """Get motor health diagnostics"""
    resort = get_resort()
    return resort.get_motor_health()


@task
def activate_hotel_task(hotel: str):
    """Move to specified hotel"""
    resort = get_resort()
    resort.activate_hotel(hotel)
    return {"status": "completed", "hotel": hotel}


@task
def go_home_task():
    """Return to home position"""
    resort = get_resort()
    resort.go_home()
    return {"status": "home"}


@task
def move_to_angle_task(angle: float):
    """Move to specific angle"""
    resort = get_resort()
    resort.move_to_angle(angle)
    return {"status": "moved", "angle": angle}


@task
def set_speed_task(speed: int):
    """Set motor speed"""
    resort = get_resort()
    resort.set_speed(speed)
    return {"status": "speed_set", "speed": speed}


@task
def emergency_stop_task():
    """Emergency stop the motor"""
    resort = get_resort()
    resort.emergency_stop()
    return {"status": "emergency_stopped"}


@task
def get_hotels_task():
    """Get available hotels"""
    resort = get_resort()
    return {
        "hotels": list(resort.hotels),
        "hotel_angles": dict(resort.hotel_angles),
        "rooms_per_hotel": resort.rooms
    }


@task
def get_position_task():
    """Get current motor position"""
    resort = get_resort()
    position = resort.get_current_position()
    return {"position": position}


@flow(name="connect")
def connect_flow(device: str = "/dev/ttyUSB0", baudrate: int = 57600, motor_id: int = 1):
    """Connect to motor flow"""
    return connect_motor(device, baudrate, motor_id)


@flow(name="disconnect")
def disconnect_flow():
    """Disconnect from motor flow"""
    return disconnect_motor()


@flow(name="status")
def status_flow():
    """Get status flow"""
    return get_status()


@flow(name="health")
def health_flow():
    """Get health flow"""
    return get_motor_health()


@flow(name="activate-hotel")
def activate_hotel_flow(hotel: str):
    """Activate hotel flow"""
    return activate_hotel_task(hotel)


@flow(name="go-home")
def go_home_flow():
    """Go home flow"""
    return go_home_task()


@flow(name="move-to-angle")
def move_to_angle_flow(angle: float):
    """Move to angle flow"""
    return move_to_angle_task(angle)


@flow(name="set-speed")
def set_speed_flow(speed: int):
    """Set speed flow"""
    return set_speed_task(speed)


@flow(name="emergency-stop")
def emergency_stop_flow():
    """Emergency stop flow"""
    return emergency_stop_task()


@flow(name="get-hotels")
def get_hotels_flow():
    """Get hotels flow"""
    return get_hotels_task()


@flow(name="get-position")
def get_position_flow():
    """Get position flow"""
    return get_position_task()


if __name__ == "__main__":
    print("Plate Resort Prefect Flows")
    print("To start the worker, run:")
    print("  prefect worker start --pool plate-resort-pool --type process")
