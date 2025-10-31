import os
import sys
import argparse
from typing import Dict, Any
from plate_resort.core import PlateResort
from plate_resort.workflows import orchestrator


class PlateResortClient:
    """Python client for Plate Resort using Prefect workflows"""

    def __init__(self, remote: bool = False, host: str = None, port: int = None):
        """
        Initialize Plate Resort client

        Args:
            remote: If True, use remote Prefect orchestration.
                   If False, run flows locally.
            host: Prefect server host (for remote mode)
            port: Prefect server port (for remote mode)
        """
        self.remote = remote
        self.host = host or os.getenv("PREFECT_HOST", "localhost")
        self.port = port or int(os.getenv("PREFECT_PORT", "4200"))

        if remote:
            # Configure Prefect API URL for remote execution
            prefect_api_url = f"http://{self.host}:{self.port}/api"
            os.environ["PREFECT_API_URL"] = prefect_api_url
            print(f"🌐 Remote mode: Using Prefect server at {prefect_api_url}")
        else:
            # Local mode - direct flow execution
            print("🏠 Local mode: Running flows directly")
            self.resort = PlateResort()

    def connect(
        self, device: str = "/dev/ttyUSB0", baudrate: int = 57600, motor_id: int = 1
    ) -> Dict[str, Any]:
        """Connect to Dynamixel motor"""
        if self.remote:
            result = orchestrator.connect(device, baudrate, motor_id)
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                self.resort.connect(device, baudrate, motor_id)
                return {"status": "success", "message": "Connected to motor"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from motor"""
        if self.remote:
            result = orchestrator.disconnect()
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                self.resort.disconnect()
                return {"status": "success", "message": "Disconnected from motor"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def status(self) -> Dict[str, Any]:
        """Get system status"""
        if self.remote:
            result = orchestrator.get_status()
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                connected = (
                    self.resort.is_connected
                    if hasattr(self.resort, "is_connected")
                    else False
                )
                return {"status": "success", "connected": connected}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def health(self) -> Dict[str, Any]:
        """Get motor health diagnostics"""
        if self.remote:
            result = orchestrator.get_motor_health()
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                health_data = self.resort.get_motor_health()
                return {"status": "success", "health": health_data}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def activate_hotel(self, hotel: str) -> Dict[str, Any]:
        """Move to specified hotel"""
        if self.remote:
            result = orchestrator.activate_hotel(hotel)
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                self.resort.activate_hotel(hotel)
                return {"status": "success", "message": f"Activated hotel {hotel}"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def go_home(self) -> Dict[str, Any]:
        """Return to home position"""
        if self.remote:
            result = orchestrator.go_home()
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                self.resort.go_home()
                return {"status": "success", "message": "Moved to home position"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def set_speed(self, speed: int) -> Dict[str, Any]:
        """Set motor movement speed"""
        if self.remote:
            result = orchestrator.set_profile_velocity(speed)
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                self.resort.set_profile_velocity(speed)
                return {"status": "success", "message": f"Set speed to {speed}"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop motor"""
        if self.remote:
            result = orchestrator.emergency_stop()
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                self.resort.emergency_stop()
                return {"status": "success", "message": "Emergency stop executed"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def get_hotels(self) -> Dict[str, Any]:
        """Get available hotels"""
        # This is config-based, no need for remote execution
        try:
            hotels = ["A", "B", "C", "D"]  # From config
            return {"status": "success", "hotels": hotels}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def get_position(self) -> Dict[str, Any]:
        """Get current motor position"""
        if self.remote:
            result = orchestrator.get_current_position()
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                position = self.resort.get_current_position()
                return {"status": "success", "position": position}
            except Exception as e:
                return {"status": "error", "error": str(e)}

    def move_to_angle(self, angle: float) -> Dict[str, Any]:
        """Move to specific angle in degrees"""
        if self.remote:
            result = orchestrator.move_to_angle(angle)
            return {"status": "submitted", "flow_run": str(result)}
        else:
            try:
                self.resort.move_to_angle(angle)
                return {"status": "success", "message": f"Moved to {angle} degrees"}
            except Exception as e:
                return {"status": "error", "error": str(e)}


def main():
    """CLI interface with proper argument parsing"""
    parser = argparse.ArgumentParser(
        description="Plate Resort Client - Prefect Workflows"
    )
    parser.add_argument(
        "--host", default="localhost", help="Prefect server host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=4200, help="Prefect server port (default: 4200)"
    )
    parser.add_argument(
        "--remote", action="store_true", help="Use remote Prefect orchestration"
    )
    parser.add_argument(
        "command",
        choices=[
            "connect",
            "disconnect",
            "status",
            "health",
            "activate",
            "home",
            "speed",
            "stop",
            "hotels",
            "position",
            "move",
        ],
        help="Command to execute",
    )
    parser.add_argument("args", nargs="*", help="Additional arguments for command")

    args = parser.parse_args()

    # Initialize client
    client = PlateResortClient(remote=args.remote, host=args.host, port=args.port)

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

        elif command == "position":
            result = client.get_position()

        elif command == "move":
            if len(args.args) < 1:
                print("Error: Angle required (e.g., move 90)")
                return
            angle = float(args.args[0])
            result = client.move_to_angle(angle)

        print(result)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
