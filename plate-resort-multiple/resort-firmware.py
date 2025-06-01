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

# Create PID controller instance with adjusted gains
pid = PIDController(kp=0.5, ki=0.005, kd=0.02)

def voltage_to_angle(voltage):
    """Convert feedback voltage to angle
    FB5118M feedback voltage mapping:
    2.60V = 900μs (60 degrees)
    1.66V = 1500μs (150 degrees)
    0.72V = 2100μs (240 degrees)
    """
    if voltage >= 2.60:
        return 60
    elif voltage <= 0.72:
        return 240
    
    # Linear interpolation between known points
    if voltage >= 1.66:
        # Between 2.60V (60°) and 1.66V (150°)
        ratio = (2.60 - voltage) / (2.60 - 1.66)
        return 60 + ratio * 90
    else:
        # Between 1.66V (150°) and 0.72V (240°)
        ratio = (1.66 - voltage) / (1.66 - 0.72)
        return 150 + ratio * 90

def angle_to_duty_cycle(angle):
    """Convert angle to duty cycle
    FB5118M pulse width range: 500-2500μs
    For 50Hz PWM, period is 20ms (20000μs)
    500μs = 2.5% duty cycle
    2500μs = 12.5% duty cycle
    """
    # Ensure angle is within 0-300 degree range
    angle = max(0, min(300, angle))
    
    # Convert angle to pulse width (500-2500μs)
    pulse_width = 500 + (angle / 300.0) * 2000
    
    # Convert pulse width to duty cycle
    duty_cycle = (pulse_width / 20000.0) * 100
    return max(2.5, min(12.5, duty_cycle))

def set_servo_angle(target_angle, max_attempts=50):
    """Set servo to specified angle using closed-loop control"""
    # Ensure target angle is within valid range
    target_angle = max(0, min(300, target_angle))
    
    chan = AnalogIn(ads, ADS.P0)
    
    # Reset PID integral term when starting new movement
    pid.integral = 0
    
    attempt = 0
    last_angles = []  # Keep track of last few angles for stability check
    
    while attempt < max_attempts:
        # Get current position from feedback
        current_voltage = chan.voltage
        current_angle = voltage_to_angle(current_voltage)
        
        # Calculate PID output
        pid_output = pid.compute(target_angle, current_angle)
        
        # Limit PID output more strictly
        pid_output = max(-20, min(20, pid_output))
        
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
        
        # Keep track of last 3 angles for stability check
        last_angles.append(current_angle)
        if len(last_angles) > 3:
            last_angles.pop(0)
        
        # Check if we've reached the target (within tolerance)
        if len(last_angles) == 3:
            # Check both position accuracy and stability
            max_diff = max(abs(a - b) for a, b in zip(last_angles[:-1], last_angles[1:]))
            if abs(target_angle - current_angle) < 5.0 and max_diff < 2.0:
                print("Target position reached and stable!")
                break
        
        time.sleep(0.1)  # 100ms control loop
        attempt += 1
    
    if attempt >= max_attempts:
        print("Warning: Maximum attempts reached without achieving target position")

def main():
    try:
        print("Initializing servo...")
        pwm.start(7.5)  # Start at center position (150 degrees)
        time.sleep(1)   # Wait for servo to initialize
        
        print("Starting movement sequence with closed-loop control...")
        while True:
            # Test sequence: 60° -> 150° -> 240° -> repeat
            # These angles correspond to the calibrated feedback voltages
            angles = [60, 150, 240]
            
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
