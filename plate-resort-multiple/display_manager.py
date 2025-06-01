#!/usr/bin/env python3

import board
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import threading
import time

class DisplayManager:
    def __init__(self, adc_manager):
        # Store ADC manager for live readings
        self.adc = adc_manager
        
        # Initialize display
        self.cs_pin = DigitalInOut(board.CE0)
        self.dc_pin = DigitalInOut(board.D25)
        self.reset_pin = DigitalInOut(board.D24)
        self.BAUDRATE = 24000000

        self.spi = board.SPI()
        self.disp = st7789.ST7789(
            self.spi,
            height=240,
            y_offset=80,
            rotation=180,
            cs=self.cs_pin,
            dc=self.dc_pin,
            rst=self.reset_pin,
            baudrate=self.BAUDRATE,
        )

        # Turn on the Backlight
        self.backlight = DigitalInOut(board.D26)
        self.backlight.switch_to_output()
        self.backlight.value = True

        # Create blank image for drawing
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new("RGB", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        # Load a TTF font
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            self.font = ImageFont.load_default()

        # Display state
        self.target_angle = 0
        self.is_moving = False
        self.update_thread = None
        self.running = True

    def init_display(self):
        """Initialize display"""
        self.clear_display()

    def clear_display(self):
        """Clear the display"""
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))
        self.disp.image(self.image)

    def update_servo_display(self):
        """Update display with current angle and status"""
        while self.running:
            # Create blank image for drawing
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=(0, 0, 0))
            
            # Get live current angle reading
            current_voltage = self.adc.get_voltage()
            current_angle = self.adc.voltage_to_angle(current_voltage)
            
            # Draw current angle (live)
            self.draw.text(
                (10, 10),
                f"Current: {current_angle:.1f}°",
                font=self.font,
                fill=(255, 255, 255),
            )
            
            # Draw target angle
            self.draw.text(
                (10, 50),
                f"Target: {self.target_angle:.1f}°",
                font=self.font,
                fill=(255, 255, 0),
            )
            
            # Draw status
            status = "MOVING" if self.is_moving else "STABLE"
            color = (255, 165, 0) if self.is_moving else (0, 255, 0)
            self.draw.text(
                (10, 90),
                f"Status: {status}",
                font=self.font,
                fill=color,
            )
            
            # Draw voltage reading
            self.draw.text(
                (10, 130),
                f"Voltage: {current_voltage:.2f}V",
                font=self.font,
                fill=(128, 128, 255),
            )
            
            # Draw button guide
            self.draw.text(
                (10, 180),
                "A: Cycle angles | B: Snake Game",
                font=self.font,
                fill=(128, 128, 255),
            )
            
            # Display the image
            self.disp.image(self.image)
            time.sleep(0.1)  # Update 10 times per second

    def start_display_thread(self):
        """Start the display update thread"""
        self.running = True
        self.update_thread = threading.Thread(target=self.update_servo_display, daemon=True)
        self.update_thread.start()

    def stop_display_thread(self):
        """Stop the display update thread"""
        self.running = False
        if self.update_thread:
            self.update_thread.join()

    def update_state(self, target_angle, is_moving):
        """Update the display state"""
        self.target_angle = target_angle
        self.is_moving = is_moving 