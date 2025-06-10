#!/usr/bin/env python3

from adc_manager import ADCManager
from servo_controller import ServoController
import time

if __name__ == "__main__":
    adc = ADCManager()
    servo = ServoController(adc)
    try:
        print("\n--- PWM Endpoint Sweep ---")
        servo.test_pwm_endpoints()
        time.sleep(2)
        print("\n--- PWM Intermediate Points Sweep ---")
        servo.test_pwm_intermediate_points()
    finally:
        servo.stop()
        print("\nServo test complete. GPIO cleaned up.")
