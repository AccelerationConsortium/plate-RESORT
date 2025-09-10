#!/usr/bin/env python3
"""
Touchscreen Application Launcher
Starts the web service and launches the GUI for touchscreen use
"""
import threading
import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import PlateResortApp
from gui import PlateResortGUI

def main():
    print("🔄 Starting Plate Resort Touchscreen Application")
    
    # Create app instance
    app = PlateResortApp()
    
    print("📡 Starting web service...")
    # Start web service in background thread
    web_thread = threading.Thread(
        target=app.run_web_server,
        args=('0.0.0.0', 5000, False),  # host, port, debug
        daemon=True
    )
    web_thread.start()
    
    # Wait a moment for web service to start
    time.sleep(2)
    
    print("🖥️  Launching touchscreen GUI...")
    # Launch GUI (this blocks until GUI is closed)
    try:
        gui = PlateResortGUI(app.resort)
        gui.run()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ GUI Error: {e}")
    
    print("✅ Application stopped")

if __name__ == '__main__':
    main()
