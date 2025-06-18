#!/usr/bin/env python3

from adc_manager import ADCManager
from servo_controller import ServoController
import time

def set_angle_pid(servo, adc, target_angle, kp=0.7, ki=0.01, kd=0.15, dt=0.08, max_output_step=3.0, deadband=1.5, max_attempts=200):
    """
    Move servo to target_angle using PID control with feedback.
    - kp, ki, kd: PID gains (tune these to reduce oscillation)
    - dt: time between updates (seconds)
    - max_output_step: max angle change per update (deg)
    - deadband: error threshold to consider 'close enough'
    """
    servo.MIN_ANGLE = 0.0
    servo.MAX_ANGLE = 270.0  # or 300.0 if your feedback supports it
    target_angle = max(servo.MIN_ANGLE, min(servo.MAX_ANGLE, target_angle))
    integral = 0
    last_error = 0
    attempt = 0

    try:
        current_voltage = adc.get_voltage()
        current_angle = adc.voltage_to_angle(current_voltage)
    except Exception as e:
        print(f"[PID] ADC read error at start: {e}")
        return

    while attempt < max_attempts:
        error = target_angle - current_angle
        if abs(error) < deadband:
            print(f"[PID] Target reached: {current_angle:.1f}° (error {error:.2f})")
            break
        integral += error * dt
        derivative = (error - last_error) / dt
        output = kp * error + ki * integral + kd * derivative
        # Limit output step size for smoothness
        output = max(-max_output_step, min(max_output_step, output))
        next_angle = current_angle + output
        next_angle = max(servo.MIN_ANGLE, min(servo.MAX_ANGLE, next_angle))
        duty = servo.angle_to_duty_cycle(next_angle)
        servo.pwm.ChangeDutyCycle(duty)
        time.sleep(dt)
        servo.pwm.ChangeDutyCycle(0)
        try:
            current_voltage = adc.get_voltage()
            current_angle = adc.voltage_to_angle(current_voltage)
        except Exception as e:
            print(f"[PID] ADC read error: {e}")
            break
        print(f"[PID] Target: {target_angle:.1f}°, Current: {current_angle:.1f}°, Error: {error:.2f}, Output: {output:.2f}")
        last_error = error
        attempt += 1
    # Final correction
    duty = servo.angle_to_duty_cycle(target_angle)
    servo.pwm.ChangeDutyCycle(duty)
    time.sleep(0.15)
    servo.pwm.ChangeDutyCycle(0)
    print("[PID] Done.")

if __name__ == "__main__":
    adc = ADCManager()
    servo = ServoController(adc)
    try:
        print("\n--- PID Servo Test ---")
        for angle in [0, 90, 180, 270]:
            print(f"\nMoving to {angle}° with PID...")
            set_angle_pid(servo, adc, angle)
            time.sleep(1.5)
    finally:
        servo.stop()
        print("\nPID test complete. GPIO cleaned up.")
