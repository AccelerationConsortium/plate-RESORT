#!/usr/bin/env python3

from adc_manager import ADCManager
from servo_controller import ServoController
from button_manager import ButtonManager
import time
import sys
import termios
import tty

# Open-loop version: direct PWM, no feedback, no servo.start()
def main():
    servo = ServoController(None)  # No ADC needed for open loop
    buttons = ButtonManager()
    angles = [0, 150, 300]  # Test full range: 0°, 150°, 300°
    idx = 0

    print("Open-loop servo control: Press Button A to cycle through 0°, 150°, 300°. Ctrl+C to exit.")

    try:
        while True:
            if buttons.check_button_a():
                idx = (idx + 1) % len(angles)  # Cycle through all angles
                print(f"Setting servo to {angles[idx]} degrees")
                duty = servo.angle_to_duty_cycle(angles[idx])
                servo.pwm.ChangeDutyCycle(duty)
                time.sleep(0.5)
                servo.pwm.ChangeDutyCycle(0)
                # Debounce: wait for button release
                while buttons.check_button_a():
                    time.sleep(0.05)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("\nExiting open-loop control.")
    finally:
        servo.stop()

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
    try:
        print("\nPress 'a' to cycle to the next angle, 'q' to quit.")
        while True:
            key = get_key()
            if key == 'a':
                servo.cycle_angle()
                print(f"Moved to angle: {servo.angles[servo.angle_index]}°")
            elif key == 'q':
                print("Exiting.")
                break
    finally:
        servo.stop()
        print("\nServo test complete. GPIO cleaned up.")
