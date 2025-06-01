#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import adafruit_ads1x15.ads1115 as ADS

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

# Create PID controller instance with gentler gains
pid = PIDController(kp=1.0, ki=0.01, kd=0.05)

def voltage_to_angle(voltage):
    """Convert feedback voltage to angle based on observed readings:
    ~3.22V = 0 degrees
    ~2.27V = 90 degrees
    ~1.27V = 180 degrees
    ~0.28V = 270 degrees
    """
    # Linear interpolation
    voltage_range = 3.22 - 0.28
    angle = (3.22 - voltage) * (270.0 / voltage_range)
    return max(0, min(300, angle))  # Clamp to valid range

def angle_to_duty_cycle(angle):
    """Convert angle (0-300 degrees) to duty cycle"""
    # Clamp angle to valid range
    angle = max(0, min(300, angle))
    
    # Convert angle to duty cycle (2.5-12.5%)
    duty_cycle = 2.5 + (angle / 300.0) * 10.0
    return max(2.5, min(12.5, duty_cycle))

def set_servo_angle(target_angle, max_attempts=50):
    """Set servo to specified angle using closed-loop control"""
    # Ensure target angle is within valid range
    target_angle = max(0, min(270, target_angle))  # Limit to 270 degrees as per your setup
    
    chan = AnalogIn(ads, ADS.P0)
    
    # Reset PID integral term when starting new movement
    pid.integral = 0
    
    attempt = 0
    while attempt < max_attempts:
        # Get current position from feedback
        current_voltage = chan.voltage
        current_angle = voltage_to_angle(current_voltage)
        
        # Calculate PID output
        pid_output = pid.compute(target_angle, current_angle)
        
        # Limit PID output more strictly
        pid_output = max(-30, min(30, pid_output))
        
        # Calculate new angle with PID adjustment
        adjusted_angle = target_angle + pid_output
        adjusted_angle = max(0, min(300, adjusted_angle))
        
        # Convert to duty cycle
        current_duty = angle_to_duty_cycle(adjusted_angle)
        
        # Apply the control signal
        pwm.ChangeDutyCycle(current_duty)
        
        # Print diagnostic information
        print(f"Target: {target_angle:.1f}°, Current: {current_angle:.1f}°, Adjusted: {adjusted_angle:.1f}°")
        print(f"Voltage: {current_voltage:.2f}V, PID Output: {pid_output:.1f}, Duty: {current_duty:.1f}%, I-term: {pid.integral:.1f}")
        
        # Check if we've reached the target (within tolerance)
        if abs(target_angle - current_angle) < 8.0:  # Increased tolerance
            print("Target position reached!")
            break
            
        time.sleep(0.2)  # Slower control loop (200ms)
        attempt += 1
    
    if attempt >= max_attempts:
        print("Warning: Maximum attempts reached without achieving target position")

def main():
    try:
        print("Initializing servo...")
        pwm.start(2.5)  # Start at 0 degrees
        time.sleep(1)   # Wait for servo to initialize
        
        print("Starting movement sequence with closed-loop control...")
        while True:
            # Test sequence: 0° -> 90° -> 180° -> 270° -> repeat
            angles = [0, 90, 180, 270]
            
            for angle in angles:
                print(f"\nMoving to {angle} degrees")
                set_servo_angle(angle)
                time.sleep(1)  # Wait between movements
                
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        pwm.stop()
        GPIO.cleanup()
        print("Cleanup completed")

if __name__ == "__main__":
    main()
