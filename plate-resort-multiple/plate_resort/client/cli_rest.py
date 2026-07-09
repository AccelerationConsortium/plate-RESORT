#!/usr/bin/env python3
"""REST client for Plate Resort API"""

import os
import sys
import requests
import argparse
from typing import Dict, Any


class PlateResortClient:
    """Python client for Plate Resort API"""

    def __init__(self, api_url: str = None, api_key: str = None):
        self.api_url = api_url or os.getenv(
            "PLATE_RESORT_BASE_URL", "http://localhost:8000"
        )
        self.api_key = api_key or os.getenv("PLATE_RESORT_API_KEY")
        self.headers = {"X-API-Key": self.api_key}

    def _request(
        self, method: str, endpoint: str, json_data: Dict = None
    ) -> Dict[str, Any]:
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

    def connect(
        self, device="/dev/ttyUSB0", baudrate=57600, motor_id=1
    ) -> Dict[str, Any]:
        """Connect to Dynamixel motor"""
        return self._request(
            "POST",
            "/connect",
            {"device": device, "baudrate": baudrate, "motor_id": motor_id},
        )

    def disconnect(self) -> Dict[str, Any]:
        """Disconnect from motor"""
        return self._request("POST", "/disconnect")

    def status(self) -> Dict[str, Any]:
        """Get system status"""
        return self._request("GET", "/status")

    def position(self) -> Dict[str, Any]:
        """Get current motor position"""
        return self._request("GET", "/position")

    def activate(self, hotel: str) -> Dict[str, Any]:
        """Move to specified hotel"""
        return self._request("POST", "/activate", {"hotel": hotel})


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description="Plate Resort Client")
    parser.add_argument(
        "command",
        choices=["connect", "disconnect", "status", "position", "activate"],
        help="Command to execute",
    )
    parser.add_argument("args", nargs="*", help="Additional arguments for command")

    args = parser.parse_args()

    client = PlateResortClient()

    command = args.command.lower()

    try:
        if command == "connect":
            result = client.connect()
        elif command == "disconnect":
            result = client.disconnect()
        elif command == "status":
            result = client.status()
        elif command == "position":
            result = client.position()
        elif command == "activate":
            if len(args.args) < 1:
                print("Error: Hotel required (A, B, C, D)")
                return
            hotel = args.args[0].upper()
            result = client.activate(hotel)

        print(result)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
