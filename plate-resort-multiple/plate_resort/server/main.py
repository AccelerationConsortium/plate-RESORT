from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
import os
import yaml

from plate_resort.server.wrapper import (
    PlateResortWrapper,
    require_api_key,
    load_api_key,
)


def load_config():
    """Load configuration from YAML file using same logic as PlateResort"""
    # Get the directory where this file is located
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    home_dir = os.path.expanduser("~")

    # Try user config first, then package defaults
    possible_paths = [
        os.path.join(home_dir, "plate-resort-config", "defaults.yaml"),
        os.path.join(package_dir, "config", "defaults.yaml"),
        "config/defaults.yaml",  # Relative fallback
    ]

    for config_file in possible_paths:
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
                continue

    # Return default server config if no file found
    return {"server": {"host": "0.0.0.0", "port": 8000, "api_key": "changeme"}}


config = load_config()
server_config = config.get("server", {})

app = FastAPI(
    title="Plate Resort API",
    version="2.0.0",
    description="REST API for Plate Resort Control System",
    docs_url="/docs" if server_config.get("docs_enabled", True) else None,
)
wrapper = PlateResortWrapper()


class ConnectRequest(BaseModel):
    device: str = "/dev/ttyUSB0"
    baudrate: int = 57600
    motor_id: int = 1


class ActivateRequest(BaseModel):
    hotel: str


class SpeedRequest(BaseModel):
    speed: int


class AngleRequest(BaseModel):
    angle: float


@app.get("/")
def root():
    """API status and info"""
    return {
        "name": "Plate Resort API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.post("/connect")
def connect(req: ConnectRequest, x_api_key: str = Depends(require_api_key)):
    """Connect to Dynamixel motor"""
    try:
        wrapper.connect(req.device, req.baudrate, req.motor_id)
        return {"status": "connected", "device": req.device}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/disconnect")
def disconnect(x_api_key: str = Depends(require_api_key)):
    """Disconnect from motor"""
    wrapper.disconnect()
    return {"status": "disconnected"}


@app.get("/status")
def status(x_api_key: str = Depends(require_api_key)):
    """Get system status"""
    return wrapper.status()


@app.get("/health")
def health(x_api_key: str = Depends(require_api_key)):
    """Get motor health diagnostics"""
    return wrapper.get_motor_health()


@app.post("/activate")
def activate(req: ActivateRequest, x_api_key: str = Depends(require_api_key)):
    """Move to specified hotel"""
    try:
        wrapper.activate_hotel(req.hotel)
        return {"status": "moving", "hotel": req.hotel}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/home")
def go_home(x_api_key: str = Depends(require_api_key)):
    """Return to home position"""
    try:
        wrapper.go_home()
        return {"status": "moving_home"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/move_to_angle")
def move_to_angle(req: AngleRequest, x_api_key: str = Depends(require_api_key)):
    """Move to specific angle in degrees"""
    try:
        wrapper.move_to_angle(req.angle)
        return {"status": "moving", "angle": req.angle}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/set_speed")
def set_speed(req: SpeedRequest, x_api_key: str = Depends(require_api_key)):
    """Set motor movement speed"""
    try:
        wrapper.set_speed(req.speed)
        return {"status": "speed_set", "speed": req.speed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/emergency_stop")
def emergency_stop(x_api_key: str = Depends(require_api_key)):
    """Emergency stop motor"""
    try:
        wrapper.emergency_stop()
        return {"status": "emergency_stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/hotels")
def hotels(x_api_key: str = Depends(require_api_key)):
    """Get available hotels and their angles"""
    return wrapper.get_hotels()


@app.get("/position")
def get_position(x_api_key: str = Depends(require_api_key)):
    """Get current motor position"""
    try:
        position = wrapper.get_current_position()
        return {"position": position}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_server():
    """Entry point for the plate-resort-server command"""
    import uvicorn

    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8000)
    reload = server_config.get("reload", False)  # Default False for production

    print(f"🚀 Starting Plate Resort Server")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print(f"🔑 API Key: {load_api_key()}")

    # Use import string for reload to work properly
    if reload:
        uvicorn.run("plate_resort.server.main:app", host=host, port=port, reload=reload)
    else:
        uvicorn.run(app, host=host, port=port, reload=False)


if __name__ == "__main__":
    run_server()
