"""Prefect Interface for Plate Resort

Modern cloud-native workflow orchestration using Prefect v3.
Suitable for distributed execution, monitoring, and scheduling.
"""

from . import flows
from . import orchestrator
from . import deploy
from . import worker_service

# Convenience imports for direct access to orchestrator functions
from .orchestrator import (
    activate_hotel,
    connect,
    disconnect,
    emergency_stop,
    get_health,
    get_position,
    go_home,
    move_to_angle,
    set_speed,
)

__all__ = [
    "flows",
    "orchestrator",
    "deploy",
    "worker_service",
    # Orchestrator functions
    "activate_hotel",
    "connect",
    "disconnect",
    "emergency_stop",
    "get_health",
    "get_position",
    "go_home",
    "move_to_angle",
    "set_speed",
]
