#!/usr/bin/env python3
"""
Modern GUI for Plate Resort System
7" Touchscreen Interface with Live Debug Data
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
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
        
        # Configure main window
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.load_config()
        
    def setup_window(self):
        """Configure the main window for 7" touchscreen"""
        self.root.title("Plate Resort Control")
        
        # Fullscreen for 7" display (800x480)
        self.root.geometry("800x480")
        self.root.configure(bg='#2c3e50')
        
        # Remove window decorations for kiosk mode
        self.root.overrideredirect(True)
        
        # Bind escape key to exit fullscreen
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
    def setup_styles(self):
        """Configure modern styling"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Modern color scheme
        self.colors = {
            'bg': '#2c3e50',
            'fg': '#ecf0f1',
            'primary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'secondary': '#95a5a6'
        }
        
        # Configure ttk styles
        self.style.configure('Title.TLabel', 
                           font=('Arial', 16, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['fg'])
        
        self.style.configure('Header.TLabel',
                           font=('Arial', 12, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['primary'])
        
        self.style.configure('Status.TLabel',
                           font=('Arial', 10),
                           background=self.colors['bg'],
                           foreground=self.colors['fg'])
        
        self.style.configure('Success.TLabel',
                           font=('Arial', 10, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['success'])
        
        self.style.configure('Warning.TLabel',
                           font=('Arial', 10, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['warning'])
        
        self.style.configure('Danger.TLabel',
                           font=('Arial', 10, 'bold'),
                           background=self.colors['bg'],
                           foreground=self.colors['danger'])
        
        # Configure button styles
        self.style.configure('Action.TButton',
                           font=('Arial', 12, 'bold'),
                           padding=(20, 10))
        
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
        
        # Title
        title_label = ttk.Label(control_frame, text="🍽️ Plate Resort Control", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Status display
        status_frame = ttk.LabelFrame(control_frame, text="System Status", padding=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Disconnected", style='Warning.TLabel')
        self.status_label.pack()
        
        self.position_label = ttk.Label(status_frame, text="Position: Unknown", style='Status.TLabel')
        self.position_label.pack()
        
        # Visual position indicator
        self.position_canvas = tk.Canvas(status_frame, height=60, bg=self.colors['bg'])
        self.position_canvas.pack(fill='x', pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=20)
        
        # Connect/Disconnect
        self.connect_btn = ttk.Button(button_frame, text="Connect", 
                                    command=self.toggle_connection, style='Action.TButton')
        self.connect_btn.grid(row=0, column=0, padx=10, pady=5)
        
        # Position buttons
        ttk.Button(button_frame, text="Go to Position 1", 
                  command=lambda: self.move_to_position(1), style='Action.TButton').grid(row=1, column=0, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Go to Position 2", 
                  command=lambda: self.move_to_position(2), style='Action.TButton').grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Go to Position 3", 
                  command=lambda: self.move_to_position(3), style='Action.TButton').grid(row=1, column=2, padx=10, pady=5)
        
        # Home and emergency buttons
        ttk.Button(button_frame, text="🏠 Home", 
                  command=self.go_home, style='Action.TButton').grid(row=2, column=0, padx=10, pady=5)
        
        ttk.Button(button_frame, text="⚠️ Emergency Stop", 
                  command=self.emergency_stop, style='Action.TButton').grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Button(button_frame, text="❌ Exit", 
                  command=self.quit_app, style='Action.TButton').grid(row=2, column=2, padx=10, pady=5)
        
    def create_debug_tab(self):
        """Live debug data interface"""
        debug_frame = ttk.Frame(self.notebook)
        self.notebook.add(debug_frame, text="Debug")
        
        # Title
        ttk.Label(debug_frame, text="🔧 Live Debug Data", style='Title.TLabel').pack(pady=10)
        
        # Motor health display
        health_frame = ttk.LabelFrame(debug_frame, text="Motor Health", padding=10)
        health_frame.pack(fill='x', padx=20, pady=10)
        
        health_grid = ttk.Frame(health_frame)
        health_grid.pack()
        
        # Health indicators
        ttk.Label(health_grid, text="Temperature:", style='Header.TLabel').grid(row=0, column=0, sticky='w', padx=5)
        self.temp_label = ttk.Label(health_grid, text="-- °C", style='Status.TLabel')
        self.temp_label.grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(health_grid, text="Voltage:", style='Header.TLabel').grid(row=1, column=0, sticky='w', padx=5)
        self.voltage_label = ttk.Label(health_grid, text="-- V", style='Status.TLabel')
        self.voltage_label.grid(row=1, column=1, sticky='w', padx=5)
        
        ttk.Label(health_grid, text="Current:", style='Header.TLabel').grid(row=2, column=0, sticky='w', padx=5)
        self.current_label = ttk.Label(health_grid, text="-- mA", style='Status.TLabel')
        self.current_label.grid(row=2, column=1, sticky='w', padx=5)
        
        ttk.Label(health_grid, text="Position:", style='Header.TLabel').grid(row=0, column=2, sticky='w', padx=5)
        self.debug_position_label = ttk.Label(health_grid, text="-- steps", style='Status.TLabel')
        self.debug_position_label.grid(row=0, column=3, sticky='w', padx=5)
        
        ttk.Label(health_grid, text="Velocity:", style='Header.TLabel').grid(row=1, column=2, sticky='w', padx=5)
        self.velocity_label = ttk.Label(health_grid, text="-- rpm", style='Status.TLabel')
        self.velocity_label.grid(row=1, column=3, sticky='w', padx=5)
        
        ttk.Label(health_grid, text="Load:", style='Header.TLabel').grid(row=2, column=2, sticky='w', padx=5)
        self.load_label = ttk.Label(health_grid, text="-- %", style='Status.TLabel')
        self.load_label.grid(row=2, column=3, sticky='w', padx=5)
        
        # Raw data display
        data_frame = ttk.LabelFrame(debug_frame, text="Raw Motor Data", padding=10)
        data_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.debug_text = tk.Text(data_frame, height=10, font=('Courier', 9),
                                bg='#34495e', fg='#ecf0f1', insertbackground='#ecf0f1')
        self.debug_text.pack(fill='both', expand=True)
        
        # Scrollbar for debug text
        scrollbar = ttk.Scrollbar(data_frame, orient='vertical', command=self.debug_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.debug_text.configure(yscrollcommand=scrollbar.set)
        
        # Control buttons
        debug_controls = ttk.Frame(debug_frame)
        debug_controls.pack(pady=10)
        
        self.debug_toggle_btn = ttk.Button(debug_controls, text="Start Debug", 
                                         command=self.toggle_debug, style='Action.TButton')
        self.debug_toggle_btn.pack(side='left', padx=10)
        
        ttk.Button(debug_controls, text="Clear Log", 
                  command=self.clear_debug, style='Action.TButton').pack(side='left', padx=10)
        
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
                
    def move_to_position(self, position):
        """Move to specified position"""
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
        """Return to home position"""
        if self.resort is None:
            messagebox.showwarning("Not Connected", "Please connect to motor first")
            return
            
        try:
            self.log_debug("🏠 Returning to home...")
            self.resort.go_home()
            self.log_debug("✅ Returned to home")
            self.update_position_display()
            
        except Exception as e:
            messagebox.showerror("Home Error", f"Failed to go home: {e}")
            self.log_debug(f"❌ Home failed: {e}")
            
    def emergency_stop(self):
        """Emergency stop"""
        if self.resort is None:
            return
            
        try:
            self.log_debug("⚠️ EMERGENCY STOP")
            self.resort.emergency_stop()
            self.log_debug("🛑 Motor stopped")
            
        except Exception as e:
            self.log_debug(f"❌ Emergency stop failed: {e}")
            
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
        
        # Draw scale
        for i in range(1, 4):
            x = (width - 40) * (i / 3) + 20
            self.position_canvas.create_line(x, 20, x, 40, fill=self.colors['secondary'], width=2)
            self.position_canvas.create_text(x, 50, text=f"Pos {i}", fill=self.colors['fg'], font=('Arial', 8))
        
        # Draw current position indicator
        if self.resort and hasattr(self.resort, 'config'):
            try:
                positions = [self.resort.config['positions'][f'position_{i}'] for i in range(1, 4)]
                if position in positions:
                    pos_index = positions.index(position) + 1
                    x = (width - 40) * (pos_index / 3) + 20
                    self.position_canvas.create_oval(x-8, 22, x+8, 38, fill=self.colors['success'], outline=self.colors['fg'])
            except KeyError as e:
                print(f"Position config missing: {e}")  # Debug log
                
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
