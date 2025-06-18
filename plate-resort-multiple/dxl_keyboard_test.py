#!/usr/bin/env python3
"""
dxl_keyboard_test.py

Test script for Robotis XC330 Dynamixel motor.
- Press 'a' to move 90° clockwise
- Press 'z' to move 90° counterclockwise
- Position is polled and printed every 2 seconds
"""
import sys
import time
import threading
import termios
import tty
from dynamixel_sdk import PortHandler, PacketHandler

ADDR_TORQUE_ENABLE    = 64
ADDR_GOAL_POSITION    = 116
ADDR_PRESENT_POSITION = 132
MAX_POSITION = 4095
MAX_ANGLE = 360.0

# --- Keyboard input helper ---
def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# --- Polling thread ---
def poll_position(pkt, port, dxl_id, stop_event):
    while not stop_event.is_set():
        pos, result, error = pkt.read4ByteTxRx(port, dxl_id, ADDR_PRESENT_POSITION)
        if result == 0 and error == 0:
            actual_deg = pos * MAX_ANGLE / MAX_POSITION
            print(f"[POLL] Present pos: {pos} (~{actual_deg:.1f}°)")
        else:
            print("[POLL] Read error.")
        stop_event.wait(2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="/dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=57600)
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

    # Enable torque
    pkt.write1ByteTxRx(port, args.id, ADDR_TORQUE_ENABLE, 1)

    # Get initial position
    pos, result, error = pkt.read4ByteTxRx(port, args.id, ADDR_PRESENT_POSITION)
    if result == 0 and error == 0:
        current_angle = pos * MAX_ANGLE / MAX_POSITION
    else:
        print("[ERROR] Could not read initial position. Defaulting to 0°.")
        current_angle = 0.0

    stop_event = threading.Event()
    poll_thread = threading.Thread(target=poll_position, args=(pkt, port, args.id, stop_event), daemon=True)
    poll_thread.start()

    print("\nPress 'a' to move +90°, 'z' to move -90°, 'q' to quit.")
    try:
        while True:
            key = get_key()
            if key == 'a':
                current_angle = min(current_angle + 90, 360)
                goal_pos = int(current_angle * MAX_POSITION / MAX_ANGLE)
                pkt.write4ByteTxRx(port, args.id, ADDR_GOAL_POSITION, goal_pos)
                print(f"[CMD] Move to {current_angle:.1f}° (pos {goal_pos})")
            elif key == 'z':
                current_angle = max(current_angle - 90, 0)
                goal_pos = int(current_angle * MAX_POSITION / MAX_ANGLE)
                pkt.write4ByteTxRx(port, args.id, ADDR_GOAL_POSITION, goal_pos)
                print(f"[CMD] Move to {current_angle:.1f}° (pos {goal_pos})")
            elif key == 'q':
                print("Exiting.")
                break
    finally:
        stop_event.set()
        poll_thread.join(timeout=2)
        pkt.write1ByteTxRx(port, args.id, ADDR_TORQUE_ENABLE, 0)
        port.closePort()
        print("\nDynamixel test complete. Port closed.")
