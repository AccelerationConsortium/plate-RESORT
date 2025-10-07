#!/usr/bin/env python3
"""
Test the optimized Pi GUI locally
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock PlateResort for testing
class MockPlateResort:
    def __init__(self):
        self.connected = True
        self.current_position = 0
        self.portHandler = True
        self.motor_id = 1
        
    def connect(self):
        return True
        
    def disconnect(self):
        pass
        
    def go_home(self):
        self.current_position = 0
        return True
        
    def activate_hotel(self, hotel_num):
        self.current_position = hotel_num * 45
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

# Mock the module
class MockModule:
    PlateResort = MockPlateResort

sys.modules['plate_resort'] = MockModule()

# Import and run the web GUI
from web_gui import app

if __name__ == "__main__":
    print("Testing Web GUI locally...")
    print("Optimized for 7 inch touchscreen (800x480)")
    print("Open browser to http://localhost:5000")
    print("The interface is designed to fit perfectly on the Pi display")
    
    app.run(host='127.0.0.1', port=5000, debug=True)
