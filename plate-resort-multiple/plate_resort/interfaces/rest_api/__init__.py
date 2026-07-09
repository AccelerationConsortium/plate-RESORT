"""REST API Interface for Plate Resort

Traditional HTTP-based control interface using FastAPI.
Suitable for direct REST API access and legacy integrations.
"""

from .main import app, run_server
from .wrapper import PlateResortWrapper

__all__ = ["app", "run_server", "PlateResortWrapper"]
