#!/usr/bin/env python3

from adc_manager import ADCManager
from servo_controller import ServoController
import sys
import termios
import tty
import time

def get_key():
    """Get a single character from stdin without enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

if __name__ == "__main__":
    adc = ADCManager()
    servo = ServoController(adc)
    # Define the four positions
    angles = [0.0, 90.0, 180.0, 270.0]
    angle_index = 0
    try:
        print("\nPress 'a' to cycle to the next angle, 'q' to quit.")
        # Move to the initial position
        duty = servo.angle_to_duty_cycle(angles[angle_index])
        servo.pwm.ChangeDutyCycle(duty)
        print(f"Moved to angle: {angles[angle_index]}° (duty {duty:.2f}%)")
        while True:
            key = get_key()
            if key == 'a':
                angle_index = (angle_index + 1) % len(angles)
                duty = servo.angle_to_duty_cycle(angles[angle_index])
                # Hold PWM for longer to help with load
                servo.pwm.ChangeDutyCycle(duty)
                print(f"Moved to angle: {angles[angle_index]}° (duty {duty:.2f}%) - holding PWM for 2.5s")
                time.sleep(2.5)
                # Optionally keep PWM active, or set to 0 after move
                servo.pwm.ChangeDutyCycle(0)
            elif key == 'q':
                print("Exiting.")
                break
    finally:
        servo.pwm.ChangeDutyCycle(0)
        servo.stop()
        print("\nServo test complete. GPIO cleaned up.")
