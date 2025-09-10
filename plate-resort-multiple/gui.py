#!/usr/bin/env python3
"""
Modern GUI for Plate Resort System
7" Touchscreen Interface with Live Debug Data
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import yaml
from plate_resort import PlateResort
import os
import sys

class PlateResortGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.resort = None
        self.running = False
        self.debug_thread = None
        self.debug_running = False
        
        # Motor status labels for live updates
        self.temp_label = None
        self.voltage_label = None
        self.current_label = None
        self.load_label = None
        self.debug_position_label = None
        self.velocity_label = None
        self.debug_toggle_btn = None
        
        # Configure main window
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.load_config()
        
    def setup_window(self):
        """Configure the main window for 7" touchscreen"""
        self.root.title("Plate Resort Control")
        
        # True fullscreen for 7" display
        self.root.attributes('-fullscreen', True)
        self.root.state('zoomed')  # Maximize window
        self.root.configure(bg='#ffffff')  # Clean white background
        
        # Bind escape key to exit fullscreen
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
        # Handle window closing properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Configure modern Bootstrap-style styling"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Modern Bootstrap-inspired color scheme
        self.colors = {
            'bg': '#ffffff',          # Clean white background
            'fg': '#212529',          # Dark text
            'primary': '#007bff',     # Bootstrap blue
            'success': '#28a745',     # Bootstrap green
            'warning': '#ffc107',     # Bootstrap yellow
            'danger': '#dc3545',      # Bootstrap red
            'secondary': '#6c757d',   # Bootstrap gray
            'light': '#f8f9fa',       # Light gray
            'border': '#dee2e6'       # Light border
        }
        
        # Configure ttk styles with modern look
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 18, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['fg'])
        
        self.style.configure('Header.TLabel',
                           font=('Segoe UI', 12, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['primary'])
        
        self.style.configure('Status.TLabel',
                           font=('Segoe UI', 10),
                           background=self.colors['bg'],
                           foreground=self.colors['fg'])
        
        self.style.configure('Success.TLabel',
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['success'])
        
        self.style.configure('Warning.TLabel',
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['warning'])
        
        self.style.configure('Danger.TLabel',
                           font=('Segoe UI', 10, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['danger'])
        
        # Modern button styles
        self.style.configure('Primary.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(20, 12),
                           relief='flat')
        
        self.style.map('Primary.TButton',
                      background=[('active', '#0056b3'), ('!active', self.colors['primary'])],
                      foreground=[('active', 'white'), ('!active', 'white')])
        
        self.style.configure('Success.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(20, 12),
                           relief='flat')
        
        self.style.map('Success.TButton',
                      background=[('active', '#1e7e34'), ('!active', self.colors['success'])],
                      foreground=[('active', 'white'), ('!active', 'white')])
        
        self.style.configure('Danger.TButton',
                           font=('Segoe UI', 11, 'bold'),
                           padding=(20, 12),
                           relief='flat')
        
        self.style.map('Danger.TButton',
                      background=[('active', '#bd2130'), ('!active', self.colors['danger'])],
                      foreground=[('active', 'white'), ('!active', 'white')])
        
    def create_widgets(self):
        """Create the main interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_control_tab()
        self.create_debug_tab()
        self.create_config_tab()
        
    def create_control_tab(self):
        """Main control interface"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="Control")
        control_frame.configure(style='White.TFrame')
        
        # Add padding and structure
        main_container = ttk.Frame(control_frame, padding="20")
        main_container.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(main_container, text="Plate Resort Control", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Status display with modern card-like design
        status_frame = ttk.LabelFrame(main_container, text="System Status", padding="15")
        status_frame.pack(fill='x', pady=(0, 20))
        
        status_grid = ttk.Frame(status_frame)
        status_grid.pack()
        
        ttk.Label(status_grid, text="Connection:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.status_label = ttk.Label(status_grid, text="Disconnected", style='Warning.TLabel')
        self.status_label.grid(row=0, column=1, sticky='w')
        
        ttk.Label(status_grid, text="Position:", style='Header.TLabel').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(5, 0))
        self.position_label = ttk.Label(status_grid, text="Unknown", style='Status.TLabel')
        self.position_label.grid(row=1, column=1, sticky='w', pady=(5, 0))
        
        # Visual position indicator
        self.position_canvas = tk.Canvas(status_frame, height=60, bg=self.colors['light'], highlightthickness=1, highlightbackground=self.colors['border'])
        self.position_canvas.pack(fill='x', pady=(10, 0))
        
        # Control buttons in organized grid
        button_frame = ttk.LabelFrame(main_container, text="Controls", padding="15")
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Connection control
        ttk.Label(button_frame, text="Connection", style='Header.TLabel').grid(row=0, column=0, columnspan=4, sticky='w', pady=(0, 10))
        
        self.connect_btn = ttk.Button(button_frame, text="Connect", 
                                    command=self.toggle_connection, style='Primary.TButton')
        self.connect_btn.grid(row=1, column=0, padx=(0, 10), pady=(0, 15), sticky='ew')
        
        # Hotel navigation
        ttk.Label(button_frame, text="Hotel Selection", style='Header.TLabel').grid(row=2, column=0, columnspan=4, sticky='w', pady=(0, 10))
        
        ttk.Button(button_frame, text="Hotel A", 
                  command=lambda: self.move_to_hotel("A"), style='Success.TButton').grid(row=3, column=0, padx=(0, 10), pady=(0, 10), sticky='ew')
        
        ttk.Button(button_frame, text="Hotel B", 
                  command=lambda: self.move_to_hotel("B"), style='Success.TButton').grid(row=3, column=1, padx=(0, 10), pady=(0, 10), sticky='ew')
        
        ttk.Button(button_frame, text="Hotel C", 
                  command=lambda: self.move_to_hotel("C"), style='Success.TButton').grid(row=3, column=2, padx=(0, 10), pady=(0, 10), sticky='ew')
        
        ttk.Button(button_frame, text="Hotel D", 
                  command=lambda: self.move_to_hotel("D"), style='Success.TButton').grid(row=3, column=3, pady=(0, 10), sticky='ew')
        
        # System controls
        ttk.Label(button_frame, text="System Controls", style='Header.TLabel').grid(row=4, column=0, columnspan=4, sticky='w', pady=(15, 10))
        
        ttk.Button(button_frame, text="Home", 
                  command=self.go_home, style='Primary.TButton').grid(row=5, column=0, padx=(0, 10), pady=(0, 10), sticky='ew')
        
        ttk.Button(button_frame, text="Emergency Stop", 
                  command=self.emergency_stop, style='Danger.TButton').grid(row=5, column=1, padx=(0, 10), pady=(0, 10), sticky='ew')
        
        ttk.Button(button_frame, text="Exit", 
                  command=self.quit_app, style='Danger.TButton').grid(row=5, column=2, pady=(0, 10), sticky='ew')
        
        # Configure grid weights for responsive design
        for i in range(4):
            button_frame.columnconfigure(i, weight=1)
        
    def create_debug_tab(self):
        """Live debug data interface"""
        debug_frame = ttk.Frame(self.notebook)
        self.notebook.add(debug_frame, text="Debug")
        
        # Add padding and structure
        main_container = ttk.Frame(debug_frame, padding="20")
        main_container.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_container, text="Live Debug Data", style='Title.TLabel').pack(pady=(0, 20))
        
        # Motor health display with modern card design
        health_frame = ttk.LabelFrame(main_container, text="Motor Health Monitor", padding="15")
        health_frame.pack(fill='x', pady=(0, 20))
        
        health_grid = ttk.Frame(health_frame)
        health_grid.pack()
        
        # Health indicators in organized grid
        # Row 1
        ttk.Label(health_grid, text="Temperature:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.temp_label = ttk.Label(health_grid, text="-- C", style='Status.TLabel')
        self.temp_label.grid(row=0, column=1, sticky='w', padx=(0, 30))
        
        ttk.Label(health_grid, text="Voltage:", style='Header.TLabel').grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.voltage_label = ttk.Label(health_grid, text="-- V", style='Status.TLabel')
        self.voltage_label.grid(row=0, column=3, sticky='w')
        
        # Row 2
        ttk.Label(health_grid, text="Current:", style='Header.TLabel').grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.current_label = ttk.Label(health_grid, text="-- mA", style='Status.TLabel')
        self.current_label.grid(row=1, column=1, sticky='w', padx=(0, 30), pady=(10, 0))
        
        ttk.Label(health_grid, text="Load:", style='Header.TLabel').grid(row=1, column=2, sticky='w', padx=(0, 10), pady=(10, 0))
        self.load_label = ttk.Label(health_grid, text="-- %", style='Status.TLabel')
        self.load_label.grid(row=1, column=3, sticky='w', pady=(10, 0))
        
        # Row 3
        ttk.Label(health_grid, text="Position:", style='Header.TLabel').grid(row=2, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.debug_position_label = ttk.Label(health_grid, text="-- deg", style='Status.TLabel')
        self.debug_position_label.grid(row=2, column=1, sticky='w', padx=(0, 30), pady=(10, 0))
        
        ttk.Label(health_grid, text="Velocity:", style='Header.TLabel').grid(row=2, column=2, sticky='w', padx=(0, 10), pady=(10, 0))
        self.velocity_label = ttk.Label(health_grid, text="-- rpm", style='Status.TLabel')
        self.velocity_label.grid(row=2, column=3, sticky='w', pady=(10, 0))
        
        # Control buttons
        debug_controls = ttk.Frame(health_frame)
        debug_controls.pack(pady=(15, 0))
        
        self.debug_toggle_btn = ttk.Button(debug_controls, text="Start Monitoring", 
                                         command=self.toggle_debug, style='Primary.TButton')
        self.debug_toggle_btn.pack(side='left', padx=(0, 10))
        
        ttk.Button(debug_controls, text="Clear Log", 
                  command=self.clear_debug, style='Primary.TButton').pack(side='left')
        
        # Raw data display
        data_frame = ttk.LabelFrame(main_container, text="Debug Log", padding="15")
        data_frame.pack(fill='both', expand=True)
        
        # Text widget with scrollbar
        text_container = ttk.Frame(data_frame)
        text_container.pack(fill='both', expand=True)
        
        self.debug_text = tk.Text(text_container, height=15, font=('Courier New', 9),
                                bg='#f8f9fa', fg='#212529', insertbackground='#212529',
                                relief='solid', borderwidth=1)
        self.debug_text.pack(side='left', fill='both', expand=True)
        
        # Scrollbar for debug text
        scrollbar = ttk.Scrollbar(text_container, orient='vertical', command=self.debug_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.debug_text.configure(yscrollcommand=scrollbar.set)
        
    def create_config_tab(self):
        """Configuration interface"""
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Config")
        
        ttk.Label(config_frame, text="⚙️ Configuration", style='Title.TLabel').pack(pady=10)
        
        # Config display
        config_text_frame = ttk.LabelFrame(config_frame, text="Current Configuration", padding=10)
        config_text_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.config_text = tk.Text(config_text_frame, font=('Courier', 9),
                                 bg='#34495e', fg='#ecf0f1', insertbackground='#ecf0f1')
        self.config_text.pack(fill='both', expand=True)
        
        # Control buttons
        config_controls = ttk.Frame(config_frame)
        config_controls.pack(pady=10)
        
        ttk.Button(config_controls, text="Reload Config", 
                  command=self.load_config, style='Action.TButton').pack(side='left', padx=10)
        
        ttk.Button(config_controls, text="Test Hardware", 
                  command=self.test_hardware, style='Action.TButton').pack(side='left', padx=10)
        
    def load_config(self):
        """Load and display configuration"""
        try:
            config_path = 'resort_config.yaml'
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                self.config_text.delete(1.0, tk.END)
                self.config_text.insert(1.0, yaml.dump(config, default_flow_style=False, indent=2))
                
                self.log_debug("✅ Configuration loaded successfully")
            else:
                self.log_debug("❌ Configuration file not found")
                
        except Exception as e:
            self.log_debug(f"❌ Error loading config: {e}")
            
    def toggle_connection(self):
        """Connect/disconnect from motor"""
        if self.resort is None:
            try:
                self.resort = PlateResort()
                self.resort.connect()
                self.status_label.configure(text="Connected", style='Success.TLabel')
                self.connect_btn.configure(text="Disconnect")
                self.log_debug("✅ Connected to motor")
                self.update_position_display()
                
            except Exception as e:
                messagebox.showerror("Connection Error", f"Failed to connect: {e}")
                self.log_debug(f"❌ Connection failed: {e}")
        else:
            try:
                self.resort.disconnect()
                self.resort = None
                self.status_label.configure(text="Disconnected", style='Warning.TLabel')
                self.connect_btn.configure(text="Connect")
                self.position_label.configure(text="Position: Unknown")
                self.log_debug("🔌 Disconnected from motor")
                
            except Exception as e:
                self.log_debug(f"⚠️ Disconnect error: {e}")
                
    def move_to_hotel(self, hotel):
        """Move to specified hotel in background thread"""
        if self.resort is None:
            messagebox.showwarning("Not Connected", "Please connect to motor first")
            return
            
        def move_thread():
            try:
                self.log_debug(f"🔄 Moving to hotel {hotel}...")
                print(f"DEBUG: Starting movement to hotel {hotel}")  # Terminal debug
                print(f"DEBUG: Available methods: {[m for m in dir(self.resort) if not m.startswith('_')]}")
                
                # Use the correct method name: activate_hotel
                success = self.resort.activate_hotel(hotel)
                
                if success:
                    self.log_debug(f"✅ Successfully moved to hotel {hotel}")
                    print(f"✅ Successfully moved to hotel {hotel}")  # Terminal debug
                else:
                    self.log_debug(f"⚠️ Movement to hotel {hotel} timed out or failed")
                    print(f"⚠️ Movement to hotel {hotel} timed out or failed")  # Terminal debug
                
                # Update position display on main thread
                self.root.after(0, self.update_position_display)
                
            except AttributeError as e:
                error_msg = f"❌ Method error: {e} - Available methods: {[m for m in dir(self.resort) if 'hotel' in m.lower()]}"
                self.root.after(0, lambda: messagebox.showerror("Method Error", error_msg))
                self.root.after(0, lambda: self.log_debug(error_msg))
                print(error_msg)  # Terminal debug
            except Exception as e:
                error_msg = f"❌ Movement to hotel {hotel} failed: {e}"
                self.root.after(0, lambda: messagebox.showerror("Movement Error", f"Failed to move to hotel {hotel}: {e}"))
                self.root.after(0, lambda: self.log_debug(error_msg))
                print(error_msg)  # Terminal debug
        
        # Start movement in background thread to prevent GUI freezing
        threading.Thread(target=move_thread, daemon=True).start()
            
    def move_to_position(self, position):
        """Move to specified position (deprecated - use move_to_hotel)"""
        if self.resort is None:
            messagebox.showwarning("Not Connected", "Please connect to motor first")
            return
            
        try:
            self.log_debug(f"🔄 Moving to position {position}...")
            self.resort.go_to_position(position)
            self.log_debug(f"✅ Moved to position {position}")
            self.update_position_display()
            
        except Exception as e:
            messagebox.showerror("Movement Error", f"Failed to move: {e}")
            self.log_debug(f"❌ Movement failed: {e}")
            
    def go_home(self):
        """Return to home position in background thread"""
        if self.resort is None:
            messagebox.showwarning("Not Connected", "Please connect to motor first")
            return
            
        def home_thread():
            try:
                self.log_debug("🏠 Returning to home...")
                print("🏠 DEBUG: Starting home movement...")  # Terminal debug
                
                # Use the correct method name: go_home (now added to PlateResort)
                success = self.resort.go_home()
                
                if success:
                    self.log_debug("✅ Returned to home")
                    print("✅ Successfully returned to home")  # Terminal debug
                else:
                    self.log_debug("⚠️ Home movement timed out or failed")
                    print("⚠️ Home movement timed out or failed")  # Terminal debug
                    
                # Update position display on main thread
                self.root.after(0, self.update_position_display)
                
            except Exception as e:
                error_msg = f"❌ Home failed: {e}"
                self.root.after(0, lambda: messagebox.showerror("Home Error", f"Failed to go home: {e}"))
                self.root.after(0, lambda: self.log_debug(error_msg))
                print(error_msg)  # Terminal debug
        
        # Start movement in background thread
        threading.Thread(target=home_thread, daemon=True).start()
            
    def emergency_stop(self):
        """Emergency stop"""
        if self.resort is None:
            return
            
        try:
            self.log_debug("⚠️ EMERGENCY STOP")
            print("🛑 DEBUG: Emergency stop activated")  # Terminal debug
            success = self.resort.emergency_stop()
            if success:
                self.log_debug("🛑 Motor stopped")
                print("🛑 Motor torque disabled")  # Terminal debug
            else:
                self.log_debug("⚠️ Emergency stop may have failed")
                print("⚠️ Emergency stop may have failed")  # Terminal debug
            
        except Exception as e:
            error_msg = f"❌ Emergency stop failed: {e}"
            self.log_debug(error_msg)
            print(error_msg)  # Terminal debug
            
    def update_position_display(self):
        """Update position information"""
        if self.resort is None:
            return
            
        try:
            current_pos = self.resort.get_current_position()
            self.position_label.configure(text=f"Position: {current_pos}")
            
            # Update visual position indicator
            self.draw_position_indicator(current_pos)
            print(f"Position updated: {current_pos}")  # Debug log to terminal
            
        except Exception as e:
            error_msg = f"⚠️ Position update failed: {e}"
            self.log_debug(error_msg)
            print(error_msg)  # Also log to terminal
            
    def draw_position_indicator(self, position):
        """Draw visual position indicator"""
        self.position_canvas.delete("all")
        
        # Draw position scale
        width = self.position_canvas.winfo_width()
        if width <= 1:  # Canvas not yet initialized
            self.root.after(100, lambda: self.draw_position_indicator(position))
            return
            
        height = 60
        
        # Draw scale for hotels
        hotels = ["A", "B", "C", "D"]
        for i, hotel in enumerate(hotels):
            x = (width - 40) * ((i + 1) / (len(hotels) + 1)) + 20
            self.position_canvas.create_line(x, 20, x, 40, fill=self.colors['secondary'], width=2)
            self.position_canvas.create_text(x, 50, text=f"Hotel {hotel}", fill=self.colors['fg'], font=('Arial', 8))
        
        # Draw current position indicator
        if self.resort and hasattr(self.resort, 'current_hotel') and self.resort.current_hotel:
            try:
                hotel_index = hotels.index(self.resort.current_hotel)
                x = (width - 40) * ((hotel_index + 1) / (len(hotels) + 1)) + 20
                self.position_canvas.create_oval(x-8, 22, x+8, 38, fill=self.colors['success'], outline=self.colors['fg'])
            except (ValueError, AttributeError) as e:
                print(f"Hotel indicator error: {e}")  # Debug log
                
    def toggle_debug(self):
        """Start/stop debug data collection"""
        if not self.running:
            self.running = True
            self.debug_toggle_btn.configure(text="Stop Debug")
            self.debug_thread = threading.Thread(target=self.debug_loop, daemon=True)
            self.debug_thread.start()
            self.log_debug("🔍 Debug monitoring started")
        else:
            self.running = False
            self.debug_toggle_btn.configure(text="Start Debug")
            self.log_debug("⏹️ Debug monitoring stopped")
            
    def debug_loop(self):
        """Continuous debug data collection"""
        while self.running:
            if self.resort is not None:
                try:
                    # Get motor health data
                    health = self.resort.get_motor_health()
                    
                    # Update health labels
                    self.root.after(0, self.update_health_display, health)
                    
                    # Log detailed data
                    self.root.after(0, self.log_debug, 
                                  f"Health: T={health.get('temperature', 'N/A')}°C "
                                  f"V={health.get('voltage', 'N/A')}V "
                                  f"I={health.get('current', 'N/A')}mA "
                                  f"Load={health.get('load', 'N/A')}%")
                    
                except Exception as e:
                    self.root.after(0, self.log_debug, f"❌ Debug error: {e}")
                    
            time.sleep(1)
            
    def update_health_display(self, health):
        """Update health indicator labels"""
        def get_style(value, warning_threshold, danger_threshold, higher_is_worse=True):
            if value == 'N/A':
                return 'Status.TLabel'
            try:
                val = float(value)
                if higher_is_worse:
                    if val >= danger_threshold:
                        return 'Danger.TLabel'
                    elif val >= warning_threshold:
                        return 'Warning.TLabel'
                else:
                    if val <= danger_threshold:
                        return 'Danger.TLabel'
                    elif val <= warning_threshold:
                        return 'Warning.TLabel'
                return 'Success.TLabel'
            except:
                return 'Status.TLabel'
        
        # Temperature
        temp = health.get('temperature', 'N/A')
        temp_style = get_style(temp, 60, 80)
        self.temp_label.configure(text=f"{temp} °C", style=temp_style)
        
        # Voltage
        voltage = health.get('voltage', 'N/A')
        voltage_style = get_style(voltage, 10, 8, False)  # Lower voltage is worse
        self.voltage_label.configure(text=f"{voltage} V", style=voltage_style)
        
        # Current
        current = health.get('current', 'N/A')
        current_style = get_style(current, 800, 1200)
        self.current_label.configure(text=f"{current} mA", style=current_style)
        
        # Position
        position = health.get('position', 'N/A')
        self.debug_position_label.configure(text=f"{position} steps")
        
        # Velocity
        velocity = health.get('velocity', 'N/A')
        self.velocity_label.configure(text=f"{velocity} rpm")
        
        # Load
        load = health.get('load', 'N/A')
        load_style = get_style(load, 70, 90)
        self.load_label.configure(text=f"{load} %", style=load_style)
        
    def log_debug(self, message):
        """Add message to debug log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.debug_text.insert(tk.END, log_entry)
        self.debug_text.see(tk.END)
        
        # Keep log size manageable
        if self.debug_text.get("1.0", tk.END).count('\n') > 100:
            self.debug_text.delete("1.0", "10.0")
            
    def clear_debug(self):
        """Clear debug log"""
        self.debug_text.delete(1.0, tk.END)
        self.log_debug("🧹 Debug log cleared")
        
    def test_hardware(self):
        """Test hardware connectivity"""
        self.log_debug("🧪 Starting hardware test...")
        
        try:
            # Test USB connection
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            usb_ports = [port for port in ports if 'USB' in port.description or 'USB' in str(port.hwid)]
            
            if usb_ports:
                self.log_debug(f"✅ Found USB serial ports: {[port.device for port in usb_ports]}")
            else:
                self.log_debug("⚠️ No USB serial ports found")
            
            # Test motor connection if not connected
            if self.resort is None:
                self.log_debug("🔌 Testing motor connection...")
                test_resort = PlateResort()
                test_resort.connect()
                health = test_resort.get_motor_health()
                test_resort.disconnect()
                self.log_debug(f"✅ Motor test successful: {health}")
            else:
                self.log_debug("ℹ️ Motor already connected")
                
        except Exception as e:
            self.log_debug(f"❌ Hardware test failed: {e}")
            
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        current = self.root.overrideredirect()
        self.root.overrideredirect(not current)
        if not current:
            self.root.geometry("800x480")
    
    def toggle_debug(self):
        """Toggle debug monitoring"""
        if self.debug_running:
            self.stop_debug()
        else:
            self.start_debug()
    
    def start_debug(self):
        """Start live debug monitoring"""
        if not self.resort:
            self.log_debug("Error: PlateResort not initialized")
            return
            
        self.debug_running = True
        self.debug_toggle_btn.configure(text="Stop Monitoring")
        
        def debug_worker():
            while self.debug_running:
                try:
                    if self.resort and self.resort.portHandler:
                        # Read motor parameters
                        health_data = self.resort.get_motor_health()
                        
                        # Update GUI on main thread
                        self.root.after(0, self.update_debug_display, health_data)
                        
                        # Log raw data
                        position = self.resort.get_current_position()
                        velocity = self.resort.packetHandler.read2ByteTxRx(
                            self.resort.portHandler, self.resort.motor_id, 128)[0] if self.resort.portHandler else 0
                        
                        debug_info = f"Position: {position}°, Temp: {health_data.get('temperature', 'N/A')}°C, " \
                                   f"Voltage: {health_data.get('voltage', 'N/A')}V, " \
                                   f"Current: {health_data.get('current', 'N/A')}mA"
                        
                        self.root.after(0, self.log_debug, debug_info)
                        
                except Exception as e:
                    self.root.after(0, self.log_debug, f"Debug error: {e}")
                
                time.sleep(1)  # Update every second
        
        self.debug_thread = threading.Thread(target=debug_worker, daemon=True)
        self.debug_thread.start()
        self.log_debug("Debug monitoring started")
    
    def stop_debug(self):
        """Stop debug monitoring"""
        self.debug_running = False
        if self.debug_toggle_btn:
            self.debug_toggle_btn.configure(text="Start Monitoring")
        self.log_debug("Debug monitoring stopped")
    
    def update_debug_display(self, health_data):
        """Update the debug display with motor health data"""
        if self.temp_label:
            temp = health_data.get('temperature', '--')
            self.temp_label.configure(text=f"{temp}°C" if temp != '--' else "-- °C")
        
        if self.voltage_label:
            voltage = health_data.get('voltage', '--')
            self.voltage_label.configure(text=f"{voltage:.1f}V" if voltage != '--' else "-- V")
        
        if self.current_label:
            current = health_data.get('current', '--')
            self.current_label.configure(text=f"{current}mA" if current != '--' else "-- mA")
        
        if self.load_label:
            load = health_data.get('load', '--')
            self.load_label.configure(text=f"{load}%" if load != '--' else "-- %")
        
        if self.debug_position_label:
            position = self.resort.get_current_position() if self.resort else '--'
            self.debug_position_label.configure(text=f"{position:.1f}°" if position != '--' else "-- °")
        
        if self.velocity_label:
            try:
                velocity = self.resort.packetHandler.read2ByteTxRx(
                    self.resort.portHandler, self.resort.motor_id, 128)[0] if self.resort and self.resort.portHandler else '--'
                self.velocity_label.configure(text=f"{velocity} rpm" if velocity != '--' else "-- rpm")
            except:
                self.velocity_label.configure(text="-- rpm")
    
    def clear_debug(self):
        """Clear debug log"""
        if self.debug_text:
            self.debug_text.delete(1.0, tk.END)
            self.log_debug("Debug log cleared")
    
    def log_debug(self, message):
        """Log debug message with timestamp"""
        if self.debug_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.debug_text.see(tk.END)
        
        # Also log to console
        print(f"DEBUG: {message}")
    
    def on_closing(self):
        """Handle window closing"""
        self.stop_debug()
        self.quit_app()
        
    def quit_app(self):
        """Quit application"""
        self.running = False
        if self.resort:
            try:
                self.resort.disconnect()
            except:
                pass
        self.root.quit()
        
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = PlateResortGUI()
    app.run()

if __name__ == "__main__":
    main()
