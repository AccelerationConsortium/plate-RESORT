#!/usr/bin/env python3

from servo_controller import ServoController
from button_manager import ButtonManager
import time

def main():
    servo = ServoController(None)  # No ADC needed for open loop
    buttons = ButtonManager()
    angles = [0, 180]  # Change these to your desired angles
    idx = 0

    servo.start()
    print("Open-loop servo control: Press Button A to toggle angle. Ctrl+C to exit.")

    try:
        while True:
            if buttons.check_button_a():
                idx = 1 - idx  # Toggle between 0 and 1
                print(f"Setting servo to {angles[idx]} degrees")
                servo.set_angle(angles[idx])
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
