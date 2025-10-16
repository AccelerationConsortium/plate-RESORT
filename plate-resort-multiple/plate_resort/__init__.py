"""Plate Resort Control System

Prefect-orchestrated laboratory plate management using Dynamixel motors.
Legacy REST/FastAPI layer removed in favor of function-based Prefect flows.
"""

__version__ = "2.0.7"
__author__ = "Acceleration Consortium"
__email__ = "info@acceleration.utoronto.ca"

from .core import PlateResort

__all__ = ["PlateResort"]
