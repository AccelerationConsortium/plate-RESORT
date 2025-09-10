#!/usr/bin/env python3
"""
PlateResort class for controlling Dynamixel-based plate storage system
"""
from dynamixel_sdk import PortHandler, PacketHandler
import yaml
import os

class PlateResort:
    def __init__(self, config_file="resort_config.yaml", **overrides):
        """
        Initialize plate resort system from YAML config
        
        Args:
            config_file: Path to YAML configuration file
            **overrides: Override any config values (e.g., speed=30, offset_angle=15)
        """
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Apply any overrides
        for key, value in overrides.items():
            if key in self.config:
                self.config[key] = value
        
        # Set attributes from config
        self.device = self.config['device']
        self.baud = self.config['baudrate']
        self.motor_id = self.config['motor_id']
        self.hotels = self.config['hotels']
        self.rooms = self.config['rooms_per_hotel']
        self.speed = self.config['default_speed']
        self.offset_angle = self.config['offset_angle']
        self.rotation_direction = self.config['rotation_direction']
        
        # Calculate hotel angles automatically
        delta_angle = 360.0 / len(self.hotels) * self.rotation_direction
        self.hotel_angles = {}
        for i, hotel in enumerate(self.hotels):
            self.hotel_angles[hotel] = self.offset_angle + (i * delta_angle)
            
        self.current_hotel = None
        self.port = None
        self.packet_handler = None
        
        # Dynamixel constants
        self.ADDR_TORQUE_ENABLE = 64
        self.ADDR_GOAL_POSITION = 116
        self.ADDR_PRESENT_POSITION = 132
        self.ADDR_GOAL_TORQUE = 102
        self.ADDR_TORQUE_LIMIT = 32
        self.ADDR_PRESENT_TEMPERATURE = 146
        self.ADDR_PRESENT_CURRENT = 144
        self.ADDR_PRESENT_VOLTAGE = 144
        self.ADDR_HARDWARE_ERROR = 70
        self.MAX_POSITION = 4095
        self.MAX_ANGLE = 360.0
        
    def _load_config(self, config_file):
        """Load configuration from YAML file"""
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file not found: {config_file}")
            
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            
        return config['resort']
        
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
        
        # Set torque settings
        self.packet_handler.write2ByteTxRx(self.port, self.motor_id, self.ADDR_TORQUE_LIMIT, self.config['torque_limit'])
        self.packet_handler.write2ByteTxRx(self.port, self.motor_id, self.ADDR_GOAL_TORQUE, self.config['goal_torque'])
        
        self.packet_handler.write1ByteTxRx(self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 1)
        
        # Set profile velocity (speed)
        self.packet_handler.write4ByteTxRx(self.port, self.motor_id, 112, self.speed)
        
    def activate_hotel(self, hotel, tolerance=None, timeout=None):
        """
        Rotate resort to activate specified hotel
        
        Args:
            hotel: Hotel identifier (e.g., from hotels list)
            tolerance: Position tolerance in degrees (uses config default if None)
            timeout: Maximum wait time in seconds (uses config default if None)
            
        Returns:
            bool: True if position reached within tolerance, False if timeout
        """
        if tolerance is None:
            tolerance = self.config['position_tolerance']
        if timeout is None:
            timeout = self.config['movement_timeout']
        if hotel not in self.hotels:
            raise ValueError(f"Hotel {hotel} not found. Available: {self.hotels}")
            
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
            
        target_angle = self.hotel_angles[hotel]
        goal_pos = int(target_angle * self.MAX_POSITION / self.MAX_ANGLE)
        
        self.packet_handler.write4ByteTxRx(self.port, self.motor_id, self.ADDR_GOAL_POSITION, goal_pos)
        print(f"Moving to hotel {hotel} at {target_angle}° (position {goal_pos})")
        
        # Wait for position to be reached
        import time
        start_time = time.time()
        min_error = float('inf')
        
        while time.time() - start_time < timeout:
            current_pos = self.get_current_position()
            error = abs(current_pos - target_angle)
            min_error = min(min_error, error)
            
            if error <= tolerance:
                self.current_hotel = hotel
                print(f"✓ Hotel {hotel} activated! Position: {current_pos:.1f}° (error: {error:.2f}°)")
                return True
                
            time.sleep(0.1)
            
        print(f"✗ Timeout waiting for hotel {hotel}. Current: {self.get_current_position():.1f}°, Min error achieved: {min_error:.2f}°")
        return False
        
    def go_home(self):
        """Go to home position (0 degrees)"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
            
        print("Moving to home position (0°)")
        self.packet_handler.write4ByteTxRx(self.port, self.motor_id, self.ADDR_GOAL_POSITION, 0)
        
        # Wait for position to be reached
        import time
        start_time = time.time()
        timeout = self.config.get('movement_timeout', 20)
        tolerance = self.config.get('position_tolerance', 0.5)
        
        while time.time() - start_time < timeout:
            current_pos = self.get_current_position()
            error = abs(current_pos)
            
            if error <= tolerance:
                self.current_hotel = None
                print(f"✓ Home position reached! Position: {current_pos:.1f}°")
                return True
                
            time.sleep(0.1)
            
        print(f"✗ Timeout waiting for home position. Current: {self.get_current_position():.1f}°")
        return False
        
    def emergency_stop(self):
        """Emergency stop - disable torque immediately"""
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
            
        print("🛑 EMERGENCY STOP - Disabling torque")
        self.packet_handler.write1ByteTxRx(self.port, self.motor_id, self.ADDR_TORQUE_ENABLE, 0)
        return True
        
    def get_active_hotel(self):
        """
        Get the currently active hotel based on motor position
        
        Returns:
            str: Hotel identifier from hotels list, or None if position doesn't match any hotel
        """
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
            
        current_pos = self.get_current_position()
        
        # Find closest hotel within tolerance
        min_error = float('inf')
        active_hotel = None
        
        for hotel, angle in self.hotel_angles.items():
            error = abs(current_pos - angle)
            if error < min_error:
                min_error = error
                active_hotel = hotel
                
        # Return hotel if within reasonable tolerance (5 degrees)
        if min_error <= 5.0:
            return active_hotel
        else:
            return None
            
    def get_motor_health(self):
        """
        Get comprehensive motor health status
        
        Returns:
            dict: Motor health data including temperature, current, voltage, errors
        """
        if self.port is None:
            raise Exception("Not connected. Call connect() first.")
            
        health = {}
        
        # Temperature (1 byte)
        temp, result, error = self.packet_handler.read1ByteTxRx(self.port, self.motor_id, self.ADDR_PRESENT_TEMPERATURE)
        health['temperature'] = temp if result == 0 else None
        
        # Current (2 bytes, signed)
        current, result, error = self.packet_handler.read2ByteTxRx(self.port, self.motor_id, self.ADDR_PRESENT_CURRENT)
        if result == 0:
            # Convert to signed and mA
            if current > 32767:
                current = current - 65536
            health['current'] = current * 2.69  # Convert to mA
        else:
            health['current'] = None
            
        # Voltage (2 bytes)
        voltage, result, error = self.packet_handler.read2ByteTxRx(self.port, self.motor_id, self.ADDR_PRESENT_VOLTAGE)
        health['voltage'] = voltage * 0.1 if result == 0 else None  # Convert to volts
        
        # Hardware error status
        hw_error, result, error = self.packet_handler.read1ByteTxRx(self.port, self.motor_id, self.ADDR_HARDWARE_ERROR)
        health['hardware_error'] = hw_error if result == 0 else None
        
        # Position feedback
        health['position'] = self.get_current_position()
        
        # Health warnings
        health['warnings'] = []
        if health['temperature'] and health['temperature'] > self.config['temperature_limit']:
            health['warnings'].append(f"High temperature: {health['temperature']}°C")
        if health['current'] and abs(health['current']) > self.config['current_limit']:
            health['warnings'].append(f"High current: {health['current']:.0f}mA")
        if health['voltage']:
            if health['voltage'] < self.config['voltage_min']:
                health['warnings'].append(f"Low voltage: {health['voltage']:.1f}V")
            elif health['voltage'] > self.config['voltage_max']:
                health['warnings'].append(f"High voltage: {health['voltage']:.1f}V")
        if health['hardware_error'] and health['hardware_error'] > 0:
            health['warnings'].append(f"Hardware error: 0x{health['hardware_error']:02X}")
            
        return health
        
    def print_motor_health(self):
        """Print formatted motor health status"""
        health = self.get_motor_health()
        
        print("\n=== Motor Health Status ===")
        print(f"Temperature: {health['temperature']}°C" if health['temperature'] else "Temperature: N/A")
        print(f"Current: {health['current']:.0f}mA" if health['current'] else "Current: N/A")
        print(f"Voltage: {health['voltage']:.1f}V" if health['voltage'] else "Voltage: N/A")
        print(f"Position: {health['position']:.2f}°")
        print(f"Hardware Error: 0x{health['hardware_error']:02X}" if health['hardware_error'] else "Hardware Error: None")
        
        if health['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in health['warnings']:
                print(f"  • {warning}")
        else:
            print("✓ All parameters within normal range")
            
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
