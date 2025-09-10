#!/usr/bin/env python3
"""
Diagnostic script for XM430-210 Dynamixel motor
Checks operating mode and key settings
"""
from dynamixel_sdk import PortHandler, PacketHandler

def main():
    port = PortHandler('/dev/ttyUSB0')
    pkt = PacketHandler(2.0)
    
    if not port.openPort():
        print("Failed to open port")
        return
    
    if not port.setBaudRate(57600):
        print("Failed to set baudrate")
        return
    
    dxl_id = 1
    
    print("=== XM430-210 Diagnostic ===")
    
    # Check operating mode (Address 11)
    mode, result, error = pkt.read1ByteTxRx(port, dxl_id, 11)
    if result == 0:
        mode_names = {
            0: "Current Control",
            1: "Velocity Control", 
            3: "Position Control",
            4: "Extended Position Control",
            5: "Current-based Position Control",
            16: "PWM Control"
        }
        print(f"Operating Mode: {mode} ({mode_names.get(mode, 'Unknown')})")
    else:
        print(f"Failed to read operating mode")
    
    # Check torque enable
    torque, result, error = pkt.read1ByteTxRx(port, dxl_id, 64)
    if result == 0:
        print(f"Torque Enable: {torque} ({'ON' if torque else 'OFF'})")
    
    # Check positions
    pos, result, error = pkt.read4ByteTxRx(port, dxl_id, 132)
    if result == 0:
        angle = pos * 360.0 / 4095
        print(f"Current Position: {pos} ({angle:.1f}°)")
    
    goal, result, error = pkt.read4ByteTxRx(port, dxl_id, 116)
    if result == 0:
        goal_angle = goal * 360.0 / 4095
        print(f"Goal Position: {goal} ({goal_angle:.1f}°)")
    
    # Check profile velocity
    vel, result, error = pkt.read4ByteTxRx(port, dxl_id, 112)
    if result == 0:
        print(f"Profile Velocity: {vel}")
    
    # If not in position control mode, set it
    if mode != 3:
        print(f"\n>>> Setting to Position Control Mode (3)")
        # Disable torque first
        pkt.write1ByteTxRx(port, dxl_id, 64, 0)
        # Set position control mode
        pkt.write1ByteTxRx(port, dxl_id, 11, 3)
        # Re-enable torque
        pkt.write1ByteTxRx(port, dxl_id, 64, 1)
        print(">>> Mode changed and torque re-enabled")
    
    port.closePort()

if __name__ == "__main__":
    main()
