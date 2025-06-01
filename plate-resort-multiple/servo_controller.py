#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
from adc_manager import ADCManager
from collections import deque
import math

class ServoController:
    def __init__(self, adc_manager):
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        self.SERVO_PIN = 18  # GPIO18 (PWM0)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        
        # Create PWM instance
        self.pwm = GPIO.PWM(self.SERVO_PIN, 50)  # 50Hz frequency
        
        # Store ADC manager
        self.adc = adc_manager
        
        # Servo angle constants
        self.MIN_ANGLE = 68.5   # 2.51V
        self.MID_ANGLE = 159.0  # 1.56V
        self.MAX_ANGLE = 240.0  # 0.58V
        self.angles = [self.MIN_ANGLE, self.MID_ANGLE, self.MAX_ANGLE]
        
        # Control parameters
        self.ANGLE_DEADBAND = 2.0  # Ignore changes smaller than this
        self.VOLTAGE_WINDOW = 10    # Number of voltage readings to average
        self.voltage_history = deque(maxlen=self.VOLTAGE_WINDOW)
        self.last_duty_cycle = None
        self.duty_cycle_change_limit = 0.05  # Reduced from 0.1 for more gradual changes
        
        # Initialize state
        self.current_angle = self.MID_ANGLE
        self.target_angle = self.MID_ANGLE
        self.angle_index = 0
        self.is_moving = False
        self.last_movement_time = 0

    def start(self):
        """Start the servo at middle position"""
        # Very gradual power-up sequence
        self.pwm.start(0)  # Start with no power
        time.sleep(1.0)    # Let the servo initialize
        
        # Gradually increase to middle position in smaller steps
        for dc in range(0, 75, 2):  # Smaller 0.2 increments
            self.pwm.ChangeDutyCycle(dc/10.0)
            time.sleep(0.2)  # Longer delay between steps
        
        self.pwm.ChangeDutyCycle(7.4)  # Final middle position
        time.sleep(2)   # Longer wait for initial stabilization
        self.last_duty_cycle = 7.4
        self.last_movement_time = time.time()

    def stop(self):
        """Stop the servo"""
        # Gradual power down
        current_duty = self.last_duty_cycle
        for dc in range(int(current_duty * 10), -1, -2):  # Decrease in 0.2 increments
            self.pwm.ChangeDutyCycle(dc/10.0)
            time.sleep(0.1)
        time.sleep(0.5)  # Let the servo settle
        self.pwm.stop()
        GPIO.cleanup()

    def get_smoothed_voltage(self):
        """Get smoothed voltage reading using moving average"""
        current_voltage = self.adc.get_voltage()
        self.voltage_history.append(current_voltage)
        return sum(self.voltage_history) / len(self.voltage_history)

    def angle_to_duty_cycle(self, angle):
        """Convert angle to duty cycle based on observed working ranges"""
        angle = max(self.MIN_ANGLE, min(self.MAX_ANGLE, angle))
        
        if angle <= self.MID_ANGLE:
            ratio = (angle - self.MIN_ANGLE) / (self.MID_ANGLE - self.MIN_ANGLE)
            return 4.3 + ratio * (7.4 - 4.3)
        else:
            ratio = (angle - self.MID_ANGLE) / (self.MAX_ANGLE - self.MID_ANGLE)
            return 7.4 + ratio * (10.5 - 7.4)

    def smooth_duty_cycle(self, target_duty):
        """Smooth duty cycle changes to prevent jerky movements"""
        if self.last_duty_cycle is None:
            self.last_duty_cycle = target_duty
            return target_duty
            
        change = target_duty - self.last_duty_cycle
        if abs(change) > self.duty_cycle_change_limit:
            # Limit the change to our maximum allowed change
            if change > 0:
                target_duty = self.last_duty_cycle + self.duty_cycle_change_limit
            else:
                target_duty = self.last_duty_cycle - self.duty_cycle_change_limit
        
        self.last_duty_cycle = target_duty
        return target_duty

    def set_angle(self, target_angle, max_attempts=100):  # Increased max attempts for slower movement
        """Set servo to specified angle using closed-loop control"""
        # Enforce minimum delay between any movements
        current_time = time.time()
        time_since_last_move = current_time - self.last_movement_time
        
        # Minimum 1.5 second delay between any movements
        if time_since_last_move < 1.5:
            time.sleep(1.5 - time_since_last_move)
        
        self.target_angle = target_angle
        self.is_moving = True
        
        # Ensure target angle is within physical limits
        target_angle = max(self.MIN_ANGLE, min(self.MAX_ANGLE, target_angle))
        
        # Calculate final target duty cycle
        final_duty = self.angle_to_duty_cycle(target_angle)
        current_duty = self.angle_to_duty_cycle(self.current_angle)
        
        # Calculate number of steps based on angle difference
        angle_diff = abs(target_angle - self.current_angle)
        num_steps = max(10, int(angle_diff / 2))  # At least 10 steps, or more for larger movements
        
        # Generate intermediate positions
        for i in range(num_steps):
            # Calculate intermediate duty cycle with easing
            progress = (i + 1) / num_steps
            # Use easing function to make movement smoother at start and end
            eased_progress = 0.5 - 0.5 * math.cos(progress * math.pi)
            intermediate_duty = current_duty + (final_duty - current_duty) * eased_progress
            
            self.pwm.ChangeDutyCycle(intermediate_duty)
            time.sleep(0.2)  # Longer delay between steps
            
            # Check current position
            try:
                current_voltage = self.adc.get_voltage()
                self.current_angle = self.adc.voltage_to_angle(current_voltage)
                print(f"Step {i+1}/{num_steps}: {self.current_angle:.1f}°")
                
                # If we're getting close to target, move even more carefully
                if abs(target_angle - self.current_angle) < 10:
                    time.sleep(0.3)  # Extra delay when near target
                    
            except IOError as e:
                print(f"Recovered from IOError: {str(e)}")
                time.sleep(0.5)
                continue
        
        # Final approach and stabilization
        attempt = 0
        stable_count = 0
        
        while attempt < max_attempts:
            try:
                current_voltage = self.adc.get_voltage()
                self.current_angle = self.adc.voltage_to_angle(current_voltage)
                
                print(f"Target: {target_angle:.1f}°, Current: {self.current_angle:.1f}°")
                print(f"Voltage: {current_voltage:.2f}V, Duty: {final_duty:.1f}%")
                
                # More stringent stability check
                if abs(target_angle - self.current_angle) < 2.0:  # Tighter tolerance
                    stable_count += 1
                    if stable_count >= 5:  # Require more stable readings
                        print("Target position reached and stable!")
                        self.is_moving = False
                        self.pwm.ChangeDutyCycle(0)  # Stop sending PWM signals
                        self.last_movement_time = time.time()
                        break
                else:
                    stable_count = 0
                    # Small correction if needed
                    if abs(target_angle - self.current_angle) < 5.0:
                        correction = (target_angle - self.current_angle) * 0.02  # Very small correction
                        corrected_duty = final_duty + correction
                        self.pwm.ChangeDutyCycle(corrected_duty)
                
                time.sleep(0.2)  # Slower control loop
                attempt += 1
                
            except IOError as e:
                print(f"Recovered from IOError: {str(e)}")
                time.sleep(0.5)
                continue
        
        if attempt >= max_attempts:
            print("Warning: Maximum attempts reached without achieving target position")
            self.is_moving = False
            self.pwm.ChangeDutyCycle(0)
            self.last_movement_time = time.time()

    def cycle_angle(self):
        """Cycle through preset angles"""
        self.angle_index = (self.angle_index + 1) % len(self.angles)
        self.set_angle(self.angles[self.angle_index])

    def get_state(self):
        """Get current servo state"""
        return {
            'current_angle': self.current_angle,
            'target_angle': self.target_angle,
            'is_moving': self.is_moving
        } 