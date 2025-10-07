"""
Prefect flows for Plate Resort control.
"""
from .device import (
    connect_flow,
    disconnect_flow,
    status_flow,
    health_flow,
    activate_hotel_flow,
    go_home_flow,
    move_to_angle_flow,
    set_speed_flow,
    emergency_stop_flow,
    get_hotels_flow,
    get_position_flow,
)

__all__ = [
    "connect_flow",
    "disconnect_flow",
    "status_flow",
    "health_flow",
    "activate_hotel_flow",
    "go_home_flow",
    "move_to_angle_flow",
    "set_speed_flow",
    "emergency_stop_flow",
    "get_hotels_flow",
    "get_position_flow",
]
