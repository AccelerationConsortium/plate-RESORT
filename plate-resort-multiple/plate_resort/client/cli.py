import os
import sys
import requests
import argparse
from typing import Dict, Any


class PlateResortClient:
    """Python client for Plate Resort API"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or os.getenv("PLATE_API_URL", "http://plate-resort.local:8000")
        self.api_key = api_key or os.getenv("PLATE_API_KEY", "changeme")
        self.headers = {"x-api-key": self.api_key}
    
    def _request(self, method: str, endpoint: str, json_data: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=json_data, headers=self.headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def connect(self, device="/dev/ttyUSB0", baudrate=57600, motor_id=1) -> Dict[str, Any]:
        """Connect to Dynamixel motor"""
        return self._request("POST", "/connect", {
            "device": device,
            "baudrate": baudrate,
            "motor_id": motor_id
        })
    
    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from motor"""
        return self._request("POST", "/disconnect")
    
    def status(self) -> Dict[str, Any]:
        """Get system status"""
        return self._request("GET", "/status")
    
    def health(self) -> Dict[str, Any]:
        """Get motor health diagnostics"""
        return self._request("GET", "/health")
    
    def activate_hotel(self, hotel: str) -> Dict[str, Any]:
        """Move to specified hotel"""
        return self._request("POST", "/activate", {"hotel": hotel})
    
    def go_home(self) -> Dict[str, Any]:
        """Return to home position"""
        return self._request("POST", "/home")
    
    def set_speed(self, speed: int) -> Dict[str, Any]:
        """Set motor movement speed"""
        return self._request("POST", "/set_speed", {"speed": speed})
    
    def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop motor"""
        return self._request("POST", "/emergency_stop")
    
    def get_hotels(self) -> Dict[str, Any]:
        """Get available hotels"""
        return self._request("GET", "/hotels")


def main():
    """CLI interface with proper argument parsing"""
    parser = argparse.ArgumentParser(description="Plate Resort Client")
    parser.add_argument("--host", default="localhost",
                        help="Server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8000,
                        help="Server port (default: 8000)")
    parser.add_argument("--api-key", 
                        help="API key for authentication")
    parser.add_argument("command", 
                        choices=["connect", "disconnect", "status", "health", 
                                "activate", "home", "speed", "stop", "hotels"],
                        help="Command to execute")
    parser.add_argument("args", nargs="*", 
                        help="Additional arguments for command")
    
    args = parser.parse_args()
    
    # Build API URL
    api_url = f"http://{args.host}:{args.port}"
    
    # Initialize client
    client = PlateResortClient(api_url=api_url, api_key=args.api_key)
    
    command = args.command.lower()
    
    try:
        if command == "connect":
            device = args.args[0] if len(args.args) > 0 else "/dev/ttyUSB0"
            baudrate = int(args.args[1]) if len(args.args) > 1 else 57600
            motor_id = int(args.args[2]) if len(args.args) > 2 else 1
            result = client.connect(device, baudrate, motor_id)
        
        elif command == "disconnect":
            result = client.disconnect()
        
        elif command == "status":
            result = client.status()
        
        elif command == "health":
            result = client.health()
        
        elif command == "activate":
            if len(args.args) < 1:
                print("Error: Hotel required (A, B, C, D)")
                return
            hotel = args.args[0].upper()
            result = client.activate_hotel(hotel)
        
        elif command == "home":
            result = client.go_home()
        
        elif command == "speed":
            if len(args.args) < 1:
                print("Error: Speed value required")
                return
            speed = int(args.args[0])
            result = client.set_speed(speed)
        
        elif command == "stop":
            result = client.emergency_stop()
        
        elif command == "hotels":
            result = client.get_hotels()
        
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()