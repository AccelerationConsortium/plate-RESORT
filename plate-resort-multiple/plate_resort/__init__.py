"""
Plate Resort Control System

A complete server-client architecture for laboratory plate management
using Dynamixel motors and FastAPI.
"""

__version__ = "2.0.0"
__author__ = "Acceleration Consortium"
__email__ = "info@acceleration.utoronto.ca"

from .core import PlateResort

__all__ = ["PlateResort"]
