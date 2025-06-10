#!/usr/bin/env python3

from servo_controller import ServoController
from button_manager import ButtonManager
import time

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

if __name__ == "__main__":
    main()
