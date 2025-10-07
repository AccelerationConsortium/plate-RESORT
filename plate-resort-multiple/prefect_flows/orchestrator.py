"""
Orchestrator for executing Plate Resort flows remotely.
This runs on a remote machine (e.g., laptop) and submits jobs to the Prefect work pool.
"""
from prefect.deployments import run_deployment


def connect(device: str = "/dev/ttyUSB0", baudrate: int = 57600, motor_id: int = 1):
    """Connect to the motor"""
    return run_deployment(
        name="connect/plate-resort-connect",
        parameters={"device": device, "baudrate": baudrate, "motor_id": motor_id},
    )


def disconnect():
    """Disconnect from the motor"""
    return run_deployment(name="disconnect/plate-resort-disconnect")


def get_status():
    """Get system status"""
    return run_deployment(name="status/plate-resort-status")


def get_health():
    """Get motor health"""
    return run_deployment(name="health/plate-resort-health")


def activate_hotel(hotel: str):
    """Activate a hotel"""
    return run_deployment(
        name="activate-hotel/plate-resort-activate-hotel",
        parameters={"hotel": hotel},
    )


def go_home():
    """Go to home position"""
    return run_deployment(name="go-home/plate-resort-go-home")


def move_to_angle(angle: float):
    """Move to specific angle"""
    return run_deployment(
        name="move-to-angle/plate-resort-move-to-angle",
        parameters={"angle": angle},
    )


def set_speed(speed: int):
    """Set motor speed"""
    return run_deployment(
        name="set-speed/plate-resort-set-speed",
        parameters={"speed": speed},
    )


def emergency_stop():
    """Emergency stop"""
    return run_deployment(name="emergency-stop/plate-resort-emergency-stop")


def get_hotels():
    """Get available hotels"""
    return run_deployment(name="get-hotels/plate-resort-get-hotels")


def get_position():
    """Get current position"""
    return run_deployment(name="get-position/plate-resort-get-position")


if __name__ == "__main__":
    print("Example usage:")
    print("\n# Connect to motor")
    print("from orchestrator import connect, activate_hotel, get_status")
    print('connect(device="/dev/ttyUSB0")')
    print("\n# Activate hotel A")
    print('activate_hotel("A")')
    print("\n# Get status")
    print("get_status()")
