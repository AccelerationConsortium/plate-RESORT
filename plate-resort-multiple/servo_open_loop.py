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
        servo.pwm.ChangeDutyCycle(servo.angle_to_duty_cycle(angles[angle_index]))
        print(f"Moved to angle: {angles[angle_index]}°")
        time.sleep(1)
        servo.pwm.ChangeDutyCycle(0)
        while True:
            key = get_key()
            if key == 'a':
                angle_index = (angle_index + 1) % len(angles)
                servo.pwm.ChangeDutyCycle(servo.angle_to_duty_cycle(angles[angle_index]))
                print(f"Moved to angle: {angles[angle_index]}°")
                time.sleep(1)
                servo.pwm.ChangeDutyCycle(0)
            elif key == 'q':
                print("Exiting.")
                break
    finally:
        servo.stop()
        print("\nServo test complete. GPIO cleaned up.")
