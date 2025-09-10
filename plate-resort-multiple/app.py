#!/usr/bin/env python3
"""
Plate Resort Application
Provides both web API and local GUI for controlling the plate storage system
"""
import threading
import time
from flask import Flask, render_template, jsonify, request
from plate_resort import PlateResort
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlateResortApp:
    def __init__(self):
        self.resort = PlateResort()
        self.flask_app = Flask(__name__)
        self.setup_routes()
        self.resort_connected = False
        self.current_status = {
            'active_hotel': None,
            'position': 0.0,
            'health': {},
            'connected': False,
            'error': None
        }
        
    def setup_routes(self):
        """Setup Flask routes for web API"""
        
        @self.flask_app.route('/')
        def index():
            """Main web interface"""
            return render_template('index.html', 
                                 hotels=self.resort.hotels,
                                 rooms=self.resort.rooms)
        
        @self.flask_app.route('/api/status')
        def get_status():
            """Get current system status"""
            return jsonify(self.current_status)
        
        @self.flask_app.route('/api/connect', methods=['POST'])
        def connect():
            """Connect to motor"""
            try:
                self.resort.connect()
                self.resort_connected = True
                self.current_status['connected'] = True
                self.current_status['error'] = None
                logger.info("Motor connected successfully")
                return jsonify({'success': True, 'message': 'Connected to motor'})
            except Exception as e:
                self.current_status['error'] = str(e)
                logger.error(f"Failed to connect: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.flask_app.route('/api/disconnect', methods=['POST'])
        def disconnect():
            """Disconnect from motor"""
            try:
                self.resort.disconnect()
                self.resort_connected = False
                self.current_status['connected'] = False
                logger.info("Motor disconnected")
                return jsonify({'success': True, 'message': 'Disconnected from motor'})
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.flask_app.route('/api/hotel/<hotel>/activate', methods=['POST'])
        def activate_hotel(hotel):
            """Activate specific hotel"""
            if not self.resort_connected:
                return jsonify({'success': False, 'error': 'Not connected to motor'}), 400
                
            try:
                success = self.resort.activate_hotel(hotel)
                if success:
                    self.current_status['active_hotel'] = hotel
                    return jsonify({'success': True, 'message': f'Hotel {hotel} activated'})
                else:
                    return jsonify({'success': False, 'error': f'Failed to reach hotel {hotel}'}), 500
            except Exception as e:
                logger.error(f"Error activating hotel {hotel}: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.flask_app.route('/api/health')
        def get_health():
            """Get motor health status"""
            if not self.resort_connected:
                return jsonify({'error': 'Not connected to motor'}), 400
                
            try:
                health = self.resort.get_motor_health()
                return jsonify(health)
            except Exception as e:
                logger.error(f"Error reading health: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.flask_app.route('/api/emergency_stop', methods=['POST'])
        def emergency_stop():
            """Emergency stop - disconnect motor"""
            try:
                if self.resort_connected:
                    self.resort.disconnect()
                    self.resort_connected = False
                    self.current_status['connected'] = False
                logger.info("Emergency stop executed")
                return jsonify({'success': True, 'message': 'Emergency stop executed'})
            except Exception as e:
                logger.error(f"Error during emergency stop: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.flask_app.route('/api/speed', methods=['POST'])
        def set_speed():
            """Set motor speed"""
            data = request.get_json()
            speed = data.get('speed', 50)
            
            try:
                self.resort.set_speed(speed)
                return jsonify({'success': True, 'message': f'Speed set to {speed}'})
            except Exception as e:
                logger.error(f"Error setting speed: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
    def update_status(self):
        """Background thread to update system status"""
        while True:
            if self.resort_connected:
                try:
                    # Update position
                    self.current_status['position'] = self.resort.get_current_position()
                    
                    # Update active hotel
                    self.current_status['active_hotel'] = self.resort.get_active_hotel()
                    
                    # Update health
                    self.current_status['health'] = self.resort.get_motor_health()
                    
                    self.current_status['error'] = None
                    
                except Exception as e:
                    self.current_status['error'] = str(e)
                    logger.error(f"Status update error: {e}")
            
            time.sleep(2)  # Update every 2 seconds
    
    def run_web_server(self, host='0.0.0.0', port=5000, debug=False):
        """Run the Flask web server"""
        # Start status update thread
        status_thread = threading.Thread(target=self.update_status, daemon=True)
        status_thread.start()
        
        logger.info(f"Starting web server on http://{host}:{port}")
        self.flask_app.run(host=host, port=port, debug=debug, threaded=True)

def main():
    """Main application entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Plate Resort Application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind web server')
    parser.add_argument('--port', type=int, default=5000, help='Port for web server')
    parser.add_argument('--gui', action='store_true', help='Launch touchscreen GUI')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    app = PlateResortApp()
    
    if args.gui:
        # Launch both web server and GUI
        web_thread = threading.Thread(
            target=app.run_web_server, 
            args=(args.host, args.port, args.debug),
            daemon=True
        )
        web_thread.start()
        
        # Launch GUI (this will block)
        from gui import PlateResortGUI
        gui = PlateResortGUI(app.resort)
        gui.run()
    else:
        # Run web server only
        app.run_web_server(args.host, args.port, args.debug)

if __name__ == '__main__':
    main()
