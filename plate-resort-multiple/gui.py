#!/usr/bin/env python3
"""
Touchscreen GUI for Plate Resort System
Optimized for 7" touchscreen interface
"""
import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
from plate_resort import PlateResort

class PlateResortGUI:
    def __init__(self, resort=None):
        self.resort = resort if resort else PlateResort()
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_widgets()
        self.connected = False
        self.monitoring = False
        
        # Start monitoring thread
        self.start_monitoring()
        
    def setup_window(self):
        """Configure main window for 7\" touchscreen"""
        self.root.title("Plate Resort Control")
        self.root.geometry("800x480")  # 7" touchscreen resolution
        self.root.configure(bg='#2c3e50')
        
        # Make fullscreen for touchscreen
        # self.root.attributes('-fullscreen', True)
        
    def setup_styles(self):
        """Setup UI styles for touchscreen use"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Large fonts for touchscreen
        self.title_font = font.Font(family="Arial", size=20, weight="bold")
        self.button_font = font.Font(family="Arial", size=16, weight="bold")
        self.status_font = font.Font(family="Arial", size=12)
        
        # Custom button style
        style.configure('Big.TButton', 
                       font=self.button_font,
                       padding=(20, 15))
        
        style.configure('Hotel.TButton',
                       font=self.button_font,
                       padding=(30, 20))
        
    def setup_widgets(self):
        """Create GUI widgets"""
        # Main title
        title_label = tk.Label(self.root, 
                              text="PLATE RESORT CONTROL", 
                              font=self.title_font,
                              bg='#2c3e50', 
                              fg='white')
        title_label.pack(pady=20)
        
        # Connection frame
        conn_frame = tk.Frame(self.root, bg='#2c3e50')
        conn_frame.pack(pady=10)
        
        self.connect_btn = ttk.Button(conn_frame, 
                                     text="CONNECT", 
                                     style='Big.TButton',
                                     command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=10)
        
        self.emergency_btn = ttk.Button(conn_frame, 
                                       text="EMERGENCY STOP", 
                                       style='Big.TButton',
                                       command=self.emergency_stop)
        self.emergency_btn.pack(side=tk.LEFT, padx=10)
        
        # Status display
        status_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, bd=2)
        status_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(status_frame, text="STATUS", font=self.button_font, 
                bg='#34495e', fg='white').pack(pady=5)
        
        self.status_text = tk.Text(status_frame, height=6, width=60, 
                                  font=self.status_font, state=tk.DISABLED)
        self.status_text.pack(padx=10, pady=5)
        
        # Hotel selection
        hotel_frame = tk.Frame(self.root, bg='#2c3e50')
        hotel_frame.pack(pady=20)
        
        tk.Label(hotel_frame, text="SELECT HOTEL", font=self.button_font,
                bg='#2c3e50', fg='white').pack(pady=(0, 10))
        
        # Hotel buttons in a grid
        button_grid = tk.Frame(hotel_frame, bg='#2c3e50')
        button_grid.pack()
        
        self.hotel_buttons = {}
        hotels = self.resort.hotels
        
        # Arrange hotels in 2x2 grid
        for i, hotel in enumerate(hotels):
            row = i // 2
            col = i % 2
            
            btn = ttk.Button(button_grid, 
                           text=f"HOTEL {hotel}", 
                           style='Hotel.TButton',
                           command=lambda h=hotel: self.activate_hotel(h))
            btn.grid(row=row, column=col, padx=20, pady=10, sticky='ew')
            self.hotel_buttons[hotel] = btn
        
        # Speed control
        speed_frame = tk.Frame(self.root, bg='#2c3e50')
        speed_frame.pack(pady=10)
        
        tk.Label(speed_frame, text="SPEED:", font=self.status_font,
                bg='#2c3e50', fg='white').pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=50)
        self.speed_scale = tk.Scale(speed_frame, from_=10, to=200, 
                                   orient=tk.HORIZONTAL, variable=self.speed_var,
                                   command=self.set_speed, length=200,
                                   font=self.status_font)
        self.speed_scale.pack(side=tk.LEFT, padx=10)
        
        # Current hotel display
        self.current_hotel_label = tk.Label(self.root, 
                                           text="CURRENT: None", 
                                           font=self.button_font,
                                           bg='#2c3e50', 
                                           fg='#e74c3c')
        self.current_hotel_label.pack(pady=10)
        
    def toggle_connection(self):
        """Connect or disconnect from motor"""
        if not self.connected:
            try:
                self.resort.connect()
                self.connected = True
                self.connect_btn.configure(text="DISCONNECT")
                self.update_status("Connected to motor")
                
                # Enable hotel buttons
                for btn in self.hotel_buttons.values():
                    btn.configure(state='normal')
                    
            except Exception as e:
                messagebox.showerror("Connection Error", str(e))
                self.update_status(f"Connection failed: {e}")
        else:
            try:
                self.resort.disconnect()
                self.connected = False
                self.connect_btn.configure(text="CONNECT")
                self.update_status("Disconnected from motor")
                
                # Disable hotel buttons
                for btn in self.hotel_buttons.values():
                    btn.configure(state='disabled')
                    
            except Exception as e:
                messagebox.showerror("Disconnect Error", str(e))
    
    def activate_hotel(self, hotel):
        """Activate selected hotel"""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to motor first")
            return
            
        try:
            self.update_status(f"Moving to hotel {hotel}...")
            
            # Disable buttons during movement
            for btn in self.hotel_buttons.values():
                btn.configure(state='disabled')
            
            # Run in thread to prevent GUI freezing
            def move_thread():
                try:
                    success = self.resort.activate_hotel(hotel)
                    if success:
                        self.update_status(f"Hotel {hotel} activated successfully")
                        self.root.after(0, lambda: self.current_hotel_label.configure(
                            text=f"CURRENT: Hotel {hotel}", fg='#27ae60'))
                    else:
                        self.update_status(f"Failed to reach hotel {hotel}")
                        
                except Exception as e:
                    self.update_status(f"Error activating hotel {hotel}: {e}")
                finally:
                    # Re-enable buttons
                    self.root.after(0, lambda: [btn.configure(state='normal') 
                                               for btn in self.hotel_buttons.values()])
            
            threading.Thread(target=move_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Movement Error", str(e))
            # Re-enable buttons
            for btn in self.hotel_buttons.values():
                btn.configure(state='normal')
    
    def set_speed(self, value):
        """Set motor speed"""
        if self.connected:
            try:
                speed = int(value)
                self.resort.set_speed(speed)
                self.update_status(f"Speed set to {speed}")
            except Exception as e:
                self.update_status(f"Error setting speed: {e}")
    
    def emergency_stop(self):
        """Emergency stop"""
        try:
            if self.connected:
                self.resort.disconnect()
                self.connected = False
                self.connect_btn.configure(text="CONNECT")
                
                # Disable hotel buttons
                for btn in self.hotel_buttons.values():
                    btn.configure(state='disabled')
            
            self.update_status("EMERGENCY STOP EXECUTED")
            self.current_hotel_label.configure(text="CURRENT: STOPPED", fg='#e74c3c')
            
        except Exception as e:
            messagebox.showerror("Emergency Stop Error", str(e))
    
    def update_status(self, message):
        """Update status display"""
        self.status_text.configure(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state=tk.DISABLED)
    
    def start_monitoring(self):
        """Start background monitoring"""
        def monitor():
            while self.monitoring:
                if self.connected:
                    try:
                        # Check health
                        health = self.resort.get_motor_health()
                        if health.get('warnings'):
                            for warning in health['warnings']:
                                self.root.after(0, lambda w=warning: 
                                               self.update_status(f"⚠️ {w}"))
                        
                        # Update current hotel
                        active_hotel = self.resort.get_active_hotel()
                        if active_hotel:
                            self.root.after(0, lambda h=active_hotel: 
                                           self.current_hotel_label.configure(
                                               text=f"CURRENT: Hotel {h}", fg='#27ae60'))
                        
                    except Exception as e:
                        self.root.after(0, lambda: 
                                       self.update_status(f"Monitoring error: {e}"))
                
                time.sleep(5)  # Check every 5 seconds
        
        self.monitoring = True
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def on_closing(self):
        """Handle window closing"""
        self.monitoring = False
        if self.connected:
            try:
                self.resort.disconnect()
            except:
                pass
        self.root.destroy()
    
    def run(self):
        """Run the GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial status
        self.update_status("GUI started")
        self.update_status(f"Configuration: {len(self.resort.hotels)} hotels, {self.resort.rooms} rooms each")
        
        # Disable hotel buttons initially
        for btn in self.hotel_buttons.values():
            btn.configure(state='disabled')
        
        self.root.mainloop()

def main():
    """Run GUI standalone"""
    gui = PlateResortGUI()
    gui.run()

if __name__ == '__main__':
    main()
