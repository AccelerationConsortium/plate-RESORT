#!/usr/bin/env python3
"""
Test the GUI locally without hardware
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the PlateResort class for testing
class MockPlateResort:
    def __init__(self):
        self.connected = True
        self.current_position = 0
        self.portHandler = True  # Mock port handler
        self.motor_id = 1
        self.packetHandler = self  # Mock packet handler
        
    def connect(self):
        return True
        
    def disconnect(self):
        pass
        
    def go_home(self):
        self.current_position = 0
        return True
        
    def activate_hotel(self, hotel_num):
        self.current_position = hotel_num * 45  # Mock positions
        return True
        
    def emergency_stop(self):
        return True
        
    def get_current_position(self):
        return self.current_position
        
    def get_motor_health(self):
        import random
        return {
            'temperature': random.randint(25, 45),
            'voltage': round(random.uniform(11.8, 12.2), 1),
            'current': random.randint(50, 200),
            'load': random.randint(0, 30)
        }
    
    def read2ByteTxRx(self, port, motor_id, address):
        """Mock packet handler method"""
        import random
        return (random.randint(0, 100), 0)  # Mock velocity and error

# Mock the entire plate_resort module to avoid import errors
class MockModule:
    PlateResort = MockPlateResort

sys.modules['plate_resort'] = MockModule()

# Now import our GUI
from gui import PlateResortGUI

if __name__ == "__main__":
    print("Starting GUI test with mock hardware...")
    app = PlateResortGUI()
    app.run()
