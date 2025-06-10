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
        self.MIN_ANGLE = 0.0
        self.MID_ANGLE = 120.0  # midpoint for 0-240
        self.MAX_ANGLE = 240.0
        self.angles = [0, 60, 120, 180, 240]
        
        # Initialize state
        self.current_angle = self.MID_ANGLE
        self.target_angle = self.MID_ANGLE
        self.angle_index = 0
        self.is_moving = False
        self.last_movement_time = 0
        self.stable_count = 0  # Track stability across cycles

    def start(self):
        """Start the servo at middle position"""
        self.pwm.start(7.4)  # Start at middle position
        time.sleep(2)   # Wait longer for servo to initialize
        self.pwm.ChangeDutyCycle(0)  # Stop active signal

    def stop(self):
        """Stop the servo"""
        self.pwm.stop()
        GPIO.cleanup()

    def angle_to_duty_cycle(self, angle):
        """Convert angle to duty cycle based on observed working ranges"""
        angle = max(self.MIN_ANGLE, min(self.MAX_ANGLE, angle))
        
        if angle <= self.MID_ANGLE:
            ratio = (angle - self.MIN_ANGLE) / (self.MID_ANGLE - self.MIN_ANGLE)
            return 4.3 + ratio * (7.4 - 4.3)
        else:
            ratio = (angle - self.MID_ANGLE) / (self.MAX_ANGLE - self.MID_ANGLE)
            return 7.4 + ratio * (10.5 - 7.4)

    def update_movement_status(self):
        """Update movement status based on current conditions"""
        # Check if we're at target position
        if abs(self.target_angle - self.current_angle) < 2.0:
            self.stable_count += 1
            if self.stable_count >= 3:
                self.is_moving = False
                return True  # Indicates stability achieved
        else:
            self.stable_count = 0
            self.is_moving = True
        return False  # Not stable yet

    def set_angle(self, target_angle, max_attempts=50):
        """Set servo to specified angle using minimal PWM signals"""
        # Ensure minimum delay between movements
        current_time = time.time()
        time_since_last_move = current_time - self.last_movement_time
        if time_since_last_move < 3.0:
            time.sleep(3.0 - time_since_last_move)

        self.target_angle = target_angle
        self.is_moving = True
        self.stable_count = 0

        # Ensure target angle is within physical limits
        target_angle = max(self.MIN_ANGLE, min(self.MAX_ANGLE, target_angle))
        duty = self.angle_to_duty_cycle(target_angle)

        attempt = 0
        last_correction_time = time.time()
        while attempt < max_attempts:
            current_voltage = self.adc.get_voltage()
            self.current_angle = self.adc.voltage_to_angle(current_voltage)
            error = self.target_angle - self.current_angle
            print(f"[Closed Loop] Target: {self.target_angle:.1f}°, Current: {self.current_angle:.1f}°, Error: {error:.2f}")
            if abs(error) < 2.0:
                self.stable_count += 1
                if self.stable_count >= 3:
                    print("[Closed Loop] Target position reached and stable!")
                    self.pwm.ChangeDutyCycle(0)
                    self.last_movement_time = time.time()
                    self.is_moving = False
                    break
            else:
                self.stable_count = 0
                self.is_moving = True
                # Apply correction pulse every 1.5 seconds
                current_time = time.time()
                if current_time - last_correction_time >= 1.5:
                    self.pwm.ChangeDutyCycle(duty)
                    time.sleep(0.2)
                    self.pwm.ChangeDutyCycle(0)
                    last_correction_time = current_time
            time.sleep(0.2)
            attempt += 1
        if attempt >= max_attempts:
            print("[Closed Loop] Warning: Maximum attempts reached without achieving target position")
            self.is_moving = False
            self.pwm.ChangeDutyCycle(0)
            self.last_movement_time = time.time()

    def get_next_angle(self):
        """Get the next angle in the sequence without moving"""
        next_index = (self.angle_index + 1) % len(self.angles)
        return self.angles[next_index]

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