#!/usr/bin/env python3
"""
Prefect flows for Plate Resort operations.
Each flow instantiates a PlateResort instance and performs the operation.
"""
from prefect import flow
from plate_resort.core import PlateResort


@flow
def connect(
    device: str = "/dev/ttyUSB0",
    baudrate: int = 57600,
    motor_id: int = 1,
):
    """Connect to the motor"""
    resort = PlateResort()
    resort.connect(device, baudrate, motor_id)


@flow
def disconnect():
    """Disconnect from the motor"""
    resort = PlateResort()
    resort.disconnect()


@flow
def get_motor_health():
    """Get motor health.

    Connection is established if needed and left active (torque enabled)
    after completion. Use disconnect() flow explicitly to release torque.
    """
    resort = PlateResort()
    resort.connect()
    health = resort.get_motor_health()
    return health


@flow
def activate_hotel(hotel: str, precise: bool = True, **overrides):
    """Activate a hotel (precise two-stage by default).

    Args:
        hotel: Hotel identifier (e.g. "A").
        precise: When True (default), uses two-stage coarse+PWM refinement
            via `activate_hotel_precise`; when False, uses legacy blind
            `activate_hotel` (immediate goal position write, no verification).
        **overrides: Optional precise movement parameter overrides passed to
            `activate_hotel_precise` (e.g., switch_error=5.0,
            pulse_pwm_start=150).

    Returns:
        dict | None: Precise result dict when precise=True, else None.

    Leaves connection/torque enabled for motor locking after move so that
    subsequent flow invocations operate on an already-engaged motor.
    """
    resort = PlateResort()
    resort.connect()
    if precise:
        return resort.activate_hotel_precise(hotel, **overrides)
    else:
        resort.activate_hotel(hotel)
        return None


@flow
def go_home():
    """Go to home position and keep connection active."""
    resort = PlateResort()
    resort.connect()
    resort.go_home()


@flow
def move_to_angle(angle: float):
    """Move to specific angle; connection left active."""
    resort = PlateResort()
    resort.connect()
    resort.move_to_angle(angle)


@flow
def set_speed(speed: int):
    """Set movement speed; keep connection active."""
    resort = PlateResort()
    resort.connect()
    resort.set_speed(speed)


@flow
def emergency_stop():
    """Emergency stop.

    Leaves torque disabled (stop) but keeps port connection active.
    """
    resort = PlateResort()
    resort.connect()
    resort.emergency_stop()


@flow
def get_current_position():
    """Get current position; keep connection active."""
    resort = PlateResort()
    resort.connect()
    position = resort.get_current_position()
    return position


@flow
def reboot(wait: float = 0.8, reapply: bool = True):
    """Soft reboot the Dynamixel and reapply settings.

    Args:
        wait: Seconds to wait after reboot before reapplying settings.
        reapply: When True, reapply operating mode, limits, speed, accel.

    Returns:
        dict: Result from `PlateResort.reboot` plus a post-health snapshot.
    """
    resort = PlateResort()
    resort.connect()
    result = resort.reboot(wait=wait, reapply=reapply)
    try:
        health = resort.get_motor_health()
    except Exception as e:  # noqa: BLE001
        health = {"error": str(e)}
    result["health"] = health
    return result
