#!/usr/bin/env python3
"""
Prefect flows for Plate Resort operations.
Each flow instantiates a PlateResort instance and performs the operation.
"""
from prefect import flow
from plate_resort.core import PlateResort


@flow
def connect(device: str = "/dev/ttyUSB0", baudrate: int = 57600, motor_id: int = 1):
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
def activate_hotel(hotel: str):
    """Activate a hotel.

    Leaves connection/torque enabled for motor locking after move.
    """
    resort = PlateResort()
    resort.connect()
    resort.activate_hotel(hotel)


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
