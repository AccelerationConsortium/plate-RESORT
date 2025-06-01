#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import threading
from digitalio import DigitalInOut, Direction, Pull

# Configuration for CS and DC pins:
cs_pin = DigitalInOut(board.CE0)    # Chip select
dc_pin = DigitalInOut(board.D25)   # GPIO25
reset_pin = DigitalInOut(board.D24) # GPIO24
BAUDRATE = 24000000  # Updated to match documentation

# Setup SPI bus using hardware SPI
spi = board.SPI()

# Create the ST7789 display:
display = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
    rotation=180,  # Adjust if display is upside down
)

# Button pins (TFT Bonnet)
BUTTON_A = 23  # Up
BUTTON_B = 24  # Down
BUTTON_L = 27  # Left
BUTTON_R = 5   # Right
BUTTON_U = 6   # Center

# Create image buffer
width = 240
height = 240
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Load a TTF font
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
except:
    font = ImageFont.load_default()

# Global variables for display
current_display_angle = 0
target_display_angle = 0
is_moving = False
angle_index = 0
angles = [68.5, 159.0, 240.0]  # Available angles

def init_display():
    """Initialize display"""
    display.fill(st7789.BLACK)
    display.init()

def update_display():
    """Update display with current angle and status"""
    global current_display_angle, target_display_angle, is_moving
    
    while True:
        # Create blank image for drawing
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
        
        # Draw current angle
        draw.text(
            (10, 10),
            f"Current: {current_display_angle:.1f}°",
            font=font,
            fill=(255, 255, 255),
        )
        
        # Draw target angle
        draw.text(
            (10, 50),
            f"Target: {target_display_angle:.1f}°",
            font=font,
            fill=(255, 255, 0),
        )
        
        # Draw status
        status = "MOVING" if is_moving else "STABLE"
        color = (255, 165, 0) if is_moving else (0, 255, 0)
        draw.text(
            (10, 90),
            f"Status: {status}",
            font=font,
            fill=color,
        )
        
        # Draw button guide
        draw.text(
            (10, 160),
            "Press A to cycle angles",
            font=font,
            fill=(128, 128, 255),
        )
        
        # Display the image
        display.image(image)
        time.sleep(0.1)

def button_callback(channel):
    """Handle button press"""
    global angle_index, target_display_angle
    
    if channel == BUTTON_A:  # Only use button A to cycle through angles
        angle_index = (angle_index + 1) % len(angles)
        target_display_angle = angles[angle_index]
        print(f"Moving to angle: {target_display_angle}")

def setup_buttons():
    """Setup button inputs"""
    GPIO.setup(BUTTON_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_A, GPIO.FALLING, callback=button_callback, bouncetime=200)

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.last_error = 0
        self.integral = 0
        self.last_time = time.time()
        self.integral_limit = 50  # Limit integral windup

    def compute(self, setpoint, measured_value):
        current_time = time.time()
        dt = current_time - self.last_time
        
        # Calculate error
        error = setpoint - measured_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term with anti-windup
        self.integral += error * dt
        self.integral = max(-self.integral_limit, min(self.integral_limit, self.integral))
        i_term = self.ki * self.integral
        
        # Derivative term
        d_term = 0
        if dt > 0:  # Avoid division by zero
            d_term = self.kd * (error - self.last_error) / dt
        
        # Save current values for next iteration
        self.last_error = error
        self.last_time = current_time
        
        # Calculate total output
        output = p_term + i_term + d_term
        return output

# Setup GPIO
GPIO.setmode(GPIO.BCM)
SERVO_PIN = 18  # GPIO18 (PWM0)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create PWM instance
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz frequency

# Setup I2C for ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Create PID controller instance with adjusted gains
pid = PIDController(kp=0.3, ki=0.001, kd=0.01)

def voltage_to_angle(voltage):
    """Convert feedback voltage to angle based on observed readings:
    2.51V ≈ 68.5° (minimum angle)
    1.56V ≈ 159° (middle position)
    0.58V ≈ 240° (maximum angle)
    """
    # Handle limits
    if voltage >= 2.51:
        return 68.5
    elif voltage <= 0.58:
        return 240.0
    
    # Linear interpolation between known points
    if voltage >= 1.56:
        # Between 2.51V (68.5°) and 1.56V (159°)
        ratio = (2.51 - voltage) / (2.51 - 1.56)
        return 68.5 + ratio * (159.0 - 68.5)
    else:
        # Between 1.56V (159°) and 0.58V (240°)
        ratio = (1.56 - voltage) / (1.56 - 0.58)
        return 159.0 + ratio * (240.0 - 159.0)

def angle_to_duty_cycle(angle):
    """Convert angle to duty cycle based on observed working ranges
    68.5° = 4.3% duty cycle
    159° = 7.4% duty cycle
    240° = 10.5% duty cycle
    """
    # Ensure angle is within physical limits
    angle = max(68.5, min(240.0, angle))
    
    # Linear interpolation for duty cycle
    if angle <= 159.0:
        ratio = (angle - 68.5) / (159.0 - 68.5)
        return 4.3 + ratio * (7.4 - 4.3)
    else:
        ratio = (angle - 159.0) / (240.0 - 159.0)
        return 7.4 + ratio * (10.5 - 7.4)

def set_servo_angle(target_angle, max_attempts=50):
    """Set servo to specified angle using closed-loop control"""
    global current_display_angle, target_display_angle, is_moving
    
    # Update display variables
    target_display_angle = target_angle
    is_moving = True
    
    # Ensure target angle is within physical limits
    target_angle = max(68.5, min(240.0, target_angle))
    
    chan = AnalogIn(ads, ADS.P0)
    
    # Reset PID integral term when starting new movement
    pid.integral = 0
    
    attempt = 0
    last_angles = []  # Keep track of last few angles for stability check
    
    while attempt < max_attempts:
        # Get current position from feedback
        current_voltage = chan.voltage
        current_angle = voltage_to_angle(current_voltage)
        current_display_angle = current_angle
        
        # Calculate PID output
        pid_output = pid.compute(target_angle, current_angle)
        
        # Limit PID output more strictly
        pid_output = max(-15, min(15, pid_output))
        
        # Calculate new angle with PID adjustment
        adjusted_angle = target_angle + pid_output
        adjusted_angle = max(68.5, min(240.0, adjusted_angle))
        
        # Convert to duty cycle
        current_duty = angle_to_duty_cycle(adjusted_angle)
        
        # Apply the control signal
        pwm.ChangeDutyCycle(current_duty)
        
        # Print diagnostic information
        print(f"Target: {target_angle:.1f}°, Current: {current_angle:.1f}°, Adjusted: {adjusted_angle:.1f}°")
        print(f"Voltage: {current_voltage:.2f}V, PID Output: {pid_output:.1f}, Duty: {current_duty:.1f}%, I-term: {pid.integral:.1f}")
        
        # Keep track of last 3 angles for stability check
        last_angles.append(current_angle)
        if len(last_angles) > 3:
            last_angles.pop(0)
        
        # Check if we've reached the target (within tolerance)
        if len(last_angles) == 3:
            # Check both position accuracy and stability
            max_diff = max(abs(a - b) for a, b in zip(last_angles[:-1], last_angles[1:]))
            if abs(target_angle - current_angle) < 3.0 and max_diff < 1.0:
                print("Target position reached and stable!")
                is_moving = False
                break
        
        time.sleep(0.1)  # 100ms control loop
        attempt += 1
    
    if attempt >= max_attempts:
        print("Warning: Maximum attempts reached without achieving target position")
        is_moving = False

def main():
    try:
        # Initialize display
        init_display()
        
        # Setup buttons
        setup_buttons()
        
        # Start display update thread
        display_thread = threading.Thread(target=update_display, daemon=True)
        display_thread.start()
        
        print("Initializing servo...")
        pwm.start(7.4)  # Start at middle position (159 degrees)
        time.sleep(1)   # Wait for servo to initialize
        
        print("Starting servo control (Press A to cycle angles, Ctrl+C to exit)...")
        while True:
            # Wait for button press to change angle
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        pwm.stop()
        GPIO.cleanup()
        print("Cleanup completed")

if __name__ == "__main__":
    main()
