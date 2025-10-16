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
    """Get motor health"""
    resort = PlateResort()
    resort.connect()
    try:
        health = resort.get_motor_health()
        return health
    finally:
        resort.disconnect()


@flow
def activate_hotel(hotel: str):
    """Activate a hotel"""
    resort = PlateResort()
    resort.connect()
    try:
        resort.activate_hotel(hotel)
    finally:
        resort.disconnect()


@flow
def go_home():
    """Go to home position"""
    resort = PlateResort()
    resort.connect()
    try:
        resort.go_home()
    finally:
        resort.disconnect()


@flow
def move_to_angle(angle: float):
    """Move to specific angle"""
    resort = PlateResort()
    resort.connect()
    try:
        resort.move_to_angle(angle)
    finally:
        resort.disconnect()


@flow
def set_speed(speed: int):
    """Set movement speed"""
    resort = PlateResort()
    resort.connect()
    try:
        resort.set_speed(speed)
    finally:
        resort.disconnect()


@flow
def emergency_stop():
    """Emergency stop"""
    resort = PlateResort()
    resort.connect()
    try:
        resort.emergency_stop()
    finally:
        resort.disconnect()


@flow
def get_current_position():
    """Get current position"""
    resort = PlateResort()
    resort.connect()
    try:
        position = resort.get_current_position()
        return position
    finally:
        resort.disconnect()
