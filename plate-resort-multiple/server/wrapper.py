import os
import threading
from typing import Dict, Any, Optional
from fastapi import Header, HTTPException


def require_api_key(x_api_key: str = Header(None)):
    """Validate API key from header"""
    expected = os.getenv("PLATE_API_KEY", "changeme")
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


class PlateResortWrapper:
    """Thread-safe wrapper around PlateResort for API access"""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.resort = None
        self.connected = False
        self._load_resort_class()
    
    def _load_resort_class(self):
        """Lazy load PlateResort class"""
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from plate_resort import PlateResort
            self.resort = PlateResort()
        except ImportError as e:
            raise RuntimeError(f"Failed to import PlateResort: {e}")

    def connect(self, device="/dev/ttyUSB0", baudrate=57600, motor_id=1):
        """Connect to motor with thread safety"""
        with self.lock:
            if not self.connected and self.resort:
                # Update config if different from defaults
                if (device != "/dev/ttyUSB0" or 
                    baudrate != 57600 or 
                    motor_id != 1):
                    self.resort.device = device
                    self.resort.baud = baudrate
                    self.resort.motor_id = motor_id
                
                self.resort.connect()
                self.connected = True

    def disconnect(self):
        """Disconnect from motor"""
        with self.lock:
            if self.connected and self.resort:
                self.resort.disconnect()
                self.connected = False

    def status(self) -> Dict[str, Any]:
        """Get current system status"""
        with self.lock:
            if not self.resort:
                return {"error": "resort not initialized"}
            
            status = {
                "connected": self.connected,
                "position": None,
                "active_hotel": None,
            }
            
            if self.connected:
                try:
                    status["position"] = self.resort.get_current_position()
                    status["active_hotel"] = getattr(self.resort, "current_hotel", None)
                except Exception as e:
                    status["error"] = str(e)
            
            return status

    def get_motor_health(self) -> Dict[str, Any]:
        """Get motor health diagnostics"""
        with self.lock:
            if not self.connected:
                return {"error": "not connected"}
            
            if not self.resort:
                return {"error": "resort not initialized"}
            
            try:
                return self.resort.get_motor_health()
            except Exception as e:
                return {"error": str(e)}

    def activate_hotel(self, hotel: str):
        """Move to specified hotel"""
        with self.lock:
            if not self.connected:
                raise RuntimeError("Not connected to motor")
            
            if not self.resort:
                raise RuntimeError("Resort not initialized")
            
            return self.resort.activate_hotel(hotel)

    def go_home(self):
        """Return to home position"""
        with self.lock:
            if not self.connected:
                raise RuntimeError("Not connected to motor")
            
            if not self.resort:
                raise RuntimeError("Resort not initialized")
            
            return self.resort.go_home()

    def set_speed(self, speed: int):
        """Set motor movement speed"""
        with self.lock:
            if not self.resort:
                raise RuntimeError("Resort not initialized")
            
            return self.resort.set_speed(speed)

    def emergency_stop(self):
        """Emergency stop motor"""
        with self.lock:
            if not self.resort:
                raise RuntimeError("Resort not initialized")
            
            return self.resort.emergency_stop()

    def get_hotels(self) -> Dict[str, Any]:
        """Get available hotels and their angles"""
        if not self.resort:
            return {"error": "resort not initialized"}
        
        return {
            "hotels": list(self.resort.hotels),
            "hotel_angles": dict(self.resort.hotel_angles),
            "rooms_per_hotel": self.resort.rooms
        }