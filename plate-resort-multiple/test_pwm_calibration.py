#!/usr/bin/env python3

from adc_manager import ADCManager
from servo_controller import ServoController
import time

if __name__ == "__main__":
    adc = ADCManager()
    servo = ServoController(adc)
    try:
        print("\n--- PWM Endpoint Sweep ---")
        for duty in [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5]:
            servo.pwm.ChangeDutyCycle(duty)
            time.sleep(0.7)
            try:
                voltage = adc.get_voltage()
            except Exception as e:
                voltage = None
            print(f"Duty cycle: {duty:.2f}% | ADC voltage: {voltage if voltage is not None else 'ERROR'} V")
            time.sleep(0.3)
        servo.pwm.ChangeDutyCycle(0)
        time.sleep(2)
        print("\n--- PWM Intermediate Points Sweep ---")
        min_duty = 2.5
        max_duty = 12.5
        steps = 10
        for i in range(steps + 1):
            duty = min_duty + (max_duty - min_duty) * i / steps
            expected_angle = 300 * (duty - min_duty) / (max_duty - min_duty)
            servo.pwm.ChangeDutyCycle(duty)
            time.sleep(0.7)
            try:
                voltage = adc.get_voltage()
            except Exception as e:
                voltage = None
            print(f"Step {i}: Duty cycle = {duty:.2f}%, Expected angle = {expected_angle:.1f}°, ADC voltage: {voltage if voltage is not None else 'ERROR'} V")
            time.sleep(0.3)
        servo.pwm.ChangeDutyCycle(0)
    finally:
        servo.stop()
        print("\nServo test complete. GPIO cleaned up.")
