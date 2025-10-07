#!/usr/bin/env python3
"""
Integrated Web GUI for Plate Resort System on Raspberry Pi
Optimized for 7" touchscreen (800x480) with real hardware integration
"""

from flask import Flask, render_template, jsonify, request
import threading
import time
import json
from datetime import datetime
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from plate_resort import PlateResort
    HARDWARE_AVAILABLE = True
except ImportError:
    print("⚠️  Hardware not available, using mock mode")
    HARDWARE_AVAILABLE = False
    
    # Mock PlateResort for testing without hardware
    class PlateResort:
        def __init__(self):
            self.connected = True
            self.current_position = 11.0  # Start at Hotel A position
            self.portHandler = True
            self.motor_id = 1
            # Hotel positions from config (offset_angle + 90° intervals)
            self.hotel_angles = {
                'A': 11.0,   # offset_angle
                'B': 101.0,  # offset_angle + 90°
                'C': 191.0,  # offset_angle + 180°
                'D': 281.0   # offset_angle + 270°
            }
            
        def connect(self):
            return True
            
        def disconnect(self):
            pass
            
        def go_home(self):
            self.current_position = 0.0  # Home is 0°
            time.sleep(0.5)
            return True
            
        def activate_hotel(self, hotel):
            if hotel in self.hotel_angles:
                old_pos = self.current_position
                new_pos = self.hotel_angles[hotel]
                # Simulate movement time based on distance
                distance = abs(new_pos - old_pos)
                time.sleep(distance / 360.0)  # Simulate realistic movement time
                
                self.current_position = new_pos
                return True
            return False
            
        def emergency_stop(self):
            return True
            
        def get_current_position(self):
            return self.current_position
            
        def get_active_hotel(self):
            """Determine which hotel is currently active based on position"""
            for hotel, angle in self.hotel_angles.items():
                if abs(self.current_position - angle) < 10:  # Within 10° tolerance
                    return hotel
            return None
            
        def get_motor_health(self):
            import random
            return {
                'temperature': random.randint(25, 45),
                'voltage': round(random.uniform(11.8, 12.2), 1),
                'current': random.randint(50, 200),
                'load': random.randint(0, 30)
            }

app = Flask(__name__)
resort = None

def initialize_resort():
    """Initialize the PlateResort with error handling"""
    global resort
    try:
        resort = PlateResort()
        if resort.connect():
            print("✅ PlateResort connected successfully")
            return True
        else:
            print("❌ Failed to connect to PlateResort")
            return False
    except Exception as e:
        print(f"❌ Error initializing PlateResort: {e}")
        return False

@app.route('/')
def index():
    """Serve the web GUI"""
    return render_template('web_gui.html')

@app.route('/api/status')
def get_status():
    """Get current motor status and health data"""
    try:
        if resort:
            position = resort.get_current_position()
            health = resort.get_motor_health()
            
            # Try to get active hotel if method exists
            active_hotel = None
            try:
                active_hotel = resort.get_active_hotel()
            except AttributeError:
                # Calculate active hotel manually if method doesn't exist
                hotel_angles = {'A': 11.0, 'B': 101.0, 'C': 191.0, 'D': 281.0}
                for hotel, angle in hotel_angles.items():
                    if abs(position - angle) < 10:  # Within 10° tolerance
                        active_hotel = hotel
                        break
            
            connected = True
        else:
            position = 0
            health = {'temperature': 0, 'voltage': 0, 'current': 0, 'load': 0}
            active_hotel = None
            connected = False
        
        return jsonify({
            'position': round(position, 1),
            'active_hotel': active_hotel,
            'health': health,
            'connected': connected,
            'hardware_available': HARDWARE_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'position': 0,
            'active_hotel': None,
            'health': {'temperature': 0, 'voltage': 0, 'current': 0, 'load': 0},
            'connected': False,
            'hardware_available': HARDWARE_AVAILABLE,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/move', methods=['POST'])
def move_motor():
    """Execute motor movement commands"""
    if not resort:
        return jsonify({
            'success': False, 
            'error': 'PlateResort not initialized'
        }), 500
    
    try:
        data = request.json
        action = data.get('action')
        
        print(f"Executing command: {action}")
        
        if action == 'emergency_stop':
            result = resort.emergency_stop()
            print(f"Emergency stop result: {result}")
        elif action == 'disconnect':
            resort.disconnect()
            print("Disconnected from motor")
            return jsonify({
                'success': True,
                'action': 'disconnect',
                'message': 'Disconnected successfully',
                'timestamp': datetime.now().isoformat()
            })
        elif action == 'reconnect':
            result = resort.connect()
            print(f"Reconnect result: {result}")
            if result:
                return jsonify({
                    'success': True,
                    'action': 'reconnect', 
                    'message': 'Reconnected successfully',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to reconnect',
                    'timestamp': datetime.now().isoformat()
                })
        elif action.startswith('hotel_'):
            hotel_letter = action.split('_')[1]  # Extract A, B, C, or D
            if hotel_letter in ['A', 'B', 'C', 'D']:
                result = resort.activate_hotel(hotel_letter)
                print(f"Hotel {hotel_letter} command result: {result}")
            else:
                return jsonify({
                    'success': False, 
                    'error': f'Invalid hotel: {hotel_letter}. Valid hotels: A, B, C, D'
                }), 400
        else:
            return jsonify({
                'success': False, 
                'error': f'Invalid action: {action}'
            }), 400
        
        # Get updated position
        new_position = resort.get_current_position()
        
        return jsonify({
            'success': result,
            'position': round(new_position, 1),
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/health')
def get_detailed_health():
    """Get detailed motor health information"""
    try:
        if resort:
            health = resort.get_motor_health()
            position = resort.get_current_position()
            
            # Add additional diagnostics
            health_status = "healthy"
            if health.get('temperature', 0) > 60:
                health_status = "overheating"
            elif health.get('voltage', 12) < 11.0:
                health_status = "low_voltage"
            elif health.get('load', 0) > 80:
                health_status = "overloaded"
            
            return jsonify({
                'health': health,
                'position': round(position, 1),
                'status': health_status,
                'connected': True,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'health': {'temperature': 0, 'voltage': 0, 'current': 0, 'load': 0},
                'position': 0,
                'status': 'disconnected',
                'connected': False,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'connected': False,
            'timestamp': datetime.now().isoformat()
        }), 500

def cleanup():
    """Cleanup function to properly disconnect hardware"""
    global resort
    if resort:
        try:
            resort.disconnect()
            print("🔌 PlateResort disconnected")
        except:
            pass

if __name__ == '__main__':
    import atexit
    atexit.register(cleanup)
    
    print("Starting Plate Resort Web GUI for Raspberry Pi")
    print("Optimized for 7 inch touchscreen (800x480)")
    
    # Initialize hardware
    if not initialize_resort():
        print("Warning: Running in mock mode - no hardware detected")
    
    print("Starting web server...")
    print("Access the GUI at:")
    print("  Local: http://localhost:5000")
    print("  Network: http://<pi-ip>:5000")
    print("For fullscreen: Open in browser and press F11")
    
    try:
        # Run on all interfaces so it's accessible from network
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        cleanup()
    except Exception as e:
        print(f"❌ Server error: {e}")
        cleanup()
