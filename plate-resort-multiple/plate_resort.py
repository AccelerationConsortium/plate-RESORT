#!/usr/bin/env python3
"""
PlateResort class for controlling Dynamixel-based plate storage system
"""
from dynamixel_sdk import PortHandler, PacketHandler

class PlateResort:
    def __init__(self, device="/dev/ttyUSB0", baud=57600, motor_id=1, 
                 hotels=['A', 'B', 'C', 'D'], rooms=20, hotel_angles=None, speed=50):
        """
        Initialize plate resort system
        
        Args:
            device: Serial device path
            baud: Baudrate
            motor_id: Dynamixel motor ID
            hotels: List of hotel names (default ['A','B','C','D'])
            rooms: Number of rooms per hotel (1-20)
            hotel_angles: Dict mapping hotel to angle (default A:22.5, B:112.5, C:202.5, D:292.5)
            speed: Profile velocity (50 = ~5% speed)
        """
        self.device = device
        self.baud = baud
        self.motor_id = motor_id
        self.hotels = hotels
        self.rooms = rooms
        self.speed = speed
        
        # Default hotel positions with 22.5° offset
        if hotel_angles is None:
            self.hotel_angles = {
                'A': 22.5,
                'B': 112.5, 
                'C': 202.5,
                'D': 292.5
            }
        else:
            self.hotel_angles = hotel_angles
            
        self.current_hotel = None
        self.port = None
        self.packet_handler = None
        
        # Dynamixel constants
        self.ADDR_TORQUE_ENABLE = 64
        self.ADDR_GOAL_POSITION = 116
        self.ADDR_PRESENT_POSITION = 132
        self.MAX_POSITION = 4095
        self.MAX_ANGLE = 360.0
        
    def connect(self):
        """Connect to Dynamixel motor"""
        self.port = PortHandler(self.device)
        self.packet_handler = PacketHandler(2.0)
        
        if not self.port.openPort():
            raise Exception(f"Failed to open port {self.device}")
        if not self.port.setBaudRate(self.baud):
            raise Exception(f"Failed to set baudrate {self.baud}")
            
        # Set position control mode and enable torque
        self.packet_handler.write1ByteTxRx(self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 0)
        self.packet_handler.write1ByteTxRx(self.port, self.motor_id, 11, 3)  # Position control mode
        self.packet_handler.write1ByteTxRx(self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 1)
        
        # Set profile velocity (speed)
        self.packet_handler.write4ByteTxRx(self.port, self.motor_id, 112, self.speed)
        
    def activate_hotel(self, hotel):
        """
        Rotate resort to activate specified hotel
        
        Args:
            hotel: Hotel letter ('A', 'B', 'C', 'D')
        """
        if hotel not in self.hotels:
            raise ValueError(f"Hotel {hotel} not found. Available: {self.hotels}")
            
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
            
        target_angle = self.hotel_angles[hotel]
        goal_pos = int(target_angle * self.MAX_POSITION / self.MAX_ANGLE)
        
        self.packet_handler.write4ByteTxRx(self.port, self.motor_id, self.ADDR_GOAL_POSITION, goal_pos)
        self.current_hotel = hotel
        
        print(f"Activating hotel {hotel} at {target_angle}° (position {goal_pos})")
        
    def set_speed(self, speed):
        """Set motor speed (profile velocity)"""
        self.speed = speed
        if self.port:
            self.packet_handler.write4ByteTxRx(self.port, self.motor_id, 112, speed)
            
    def get_current_position(self):
        """Get current motor position in degrees"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
            
        pos, result, error = self.packet_handler.read4ByteTxRx(self.port, self.motor_id, self.ADDR_PRESENT_POSITION)
        if result == 0 and error == 0:
            angle = pos * self.MAX_ANGLE / self.MAX_POSITION
            return angle
        else:
            raise Exception("Failed to read position")
            
    def disconnect(self):
        """Disconnect from motor"""
        if self.port:
            self.packet_handler.write1ByteTxRx(self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 0)
            self.port.closePort()
            self.port = None
