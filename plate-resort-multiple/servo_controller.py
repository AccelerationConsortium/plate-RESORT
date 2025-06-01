#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
from adc_manager import ADCManager
from collections import deque

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
        self.duty_cycle_change_limit = 0.1  # Maximum allowed change in duty cycle per update
        
        # Initialize state
        self.current_angle = self.MID_ANGLE
        self.target_angle = self.MID_ANGLE
        self.angle_index = 0
        self.is_moving = False

    def start(self):
        """Start the servo at middle position"""
        self.pwm.start(7.4)  # Start at middle position (159 degrees)
        time.sleep(1)   # Wait for servo to initialize
        self.last_duty_cycle = 7.4

    def stop(self):
        """Stop the servo"""
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

    def set_angle(self, target_angle, max_attempts=50):
        """Set servo to specified angle using closed-loop control"""
        self.target_angle = target_angle
        self.is_moving = True
        
        # Ensure target angle is within physical limits
        target_angle = max(self.MIN_ANGLE, min(self.MAX_ANGLE, target_angle))
        
        # Calculate target duty cycle
        duty = self.angle_to_duty_cycle(target_angle)
        
        # Apply the control signal
        self.pwm.ChangeDutyCycle(duty)
        
        attempt = 0
        stable_count = 0
        
        while attempt < max_attempts:
            # Get current position from feedback
            current_voltage = self.adc.get_voltage()
            self.current_angle = self.adc.voltage_to_angle(current_voltage)
            
            # Print diagnostic information
            print(f"Target: {target_angle:.1f}°, Current: {self.current_angle:.1f}°")
            print(f"Voltage: {current_voltage:.2f}V, Duty: {duty:.1f}%")
            
            # Check if we've reached the target (within tolerance)
            if abs(target_angle - self.current_angle) < 3.0:
                stable_count += 1
                if stable_count >= 3:  # Require 3 consecutive stable readings
                    print("Target position reached and stable!")
                    self.is_moving = False
                    self.pwm.ChangeDutyCycle(0)  # Stop sending PWM signals
                    break
            else:
                stable_count = 0
            
            time.sleep(0.1)  # 100ms control loop
            attempt += 1
        
        if attempt >= max_attempts:
            print("Warning: Maximum attempts reached without achieving target position")
            self.is_moving = False
            self.pwm.ChangeDutyCycle(0)  # Stop sending PWM signals even if we didn't reach target

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