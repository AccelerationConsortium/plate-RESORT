#!/usr/bin/env python3
"""
dxl_ping.py

Pings a Dynamixel servo and checks the Hardware Error Status register.
Usage:
  python dxl_ping.py --device /dev/ttyUSB0 --baud 1000000 --id 1
"""
import sys
import argparse
from dynamixel_sdk import PortHandler, PacketHandler

ADDR_HARDWARE_ERROR_STATUS = 70
ERROR_BITS = [
    (0, "Input Voltage Error"),
    (1, "Overheating Error"),
    (2, "Motor Encoder Error"),
    (3, "Electrical Shock Error"),
    (4, "Overload Error"),
    (5, "Motor Hall Sensor Error"),
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=1000000)
    parser.add_argument("--protocol", type=float, default=2.0)
    parser.add_argument("--id", type=int, default=1)
    args = parser.parse_args()

    port = PortHandler(args.device)
    pkt = PacketHandler(args.protocol)
    if not port.openPort():
        print(f"[ERROR] Failed to open port {args.device}")
        sys.exit(1)
    if not port.setBaudRate(args.baud):
        print(f"[ERROR] Failed to set baudrate {args.baud}")
        port.closePort(); sys.exit(1)

    # Ping the servo
    dxl_model, result, error = pkt.ping(port, args.id)
    if result == 0 and error == 0:
        print(f"[OK] Ping successful. Model number: {dxl_model}")
    else:
        print(f"[ERROR] Ping failed. Check ID, wiring, and power.")
        port.closePort(); sys.exit(1)

    # Read hardware error status
    error_status, result, error = pkt.read1ByteTxRx(port, args.id, ADDR_HARDWARE_ERROR_STATUS)
    if result == 0 and error == 0:
        print(f"Hardware Error Status: 0x{error_status:02X}")
        if error_status == 0:
            print("No hardware errors detected.")
        else:
            print("Active errors:")
            for bit, desc in ERROR_BITS:
                if error_status & (1 << bit):
                    print(f"  - {desc}")
    else:
        print("Failed to read Hardware Error Status.")
    port.closePort()

if __name__ == "__main__":
    main()
