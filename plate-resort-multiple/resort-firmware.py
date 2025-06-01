#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import adafruit_ads1x15.ads1115 as ADS

# Setup GPIO
GPIO.setmode(GPIO.BCM)
SERVO_PIN = 18  # GPIO18 (PWM0)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create PWM instance
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz frequency

# Setup I2C for ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

def angle_to_duty_cycle(angle):
    """Convert angle (0-300 degrees) to duty cycle (2-12.5%)"""
    # FB5118M has 300° range, so we need to scale appropriately
    if angle < 0 or angle > 300:
        raise ValueError("Angle must be between 0 and 300 degrees")
    
    # Map angle (0-300) to duty cycle (2-12.5)
    duty_cycle = 2 + (angle / 300) * 10.5
    return duty_cycle

def set_servo_angle(angle):
    """Set servo to specified angle"""
    duty_cycle = angle_to_duty_cycle(angle)
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # Give servo time to move

def main():
    try:
        # Start PWM
        pwm.start(0)
        
        while True:
            # Test sequence: 0° -> 90° -> 180° -> 270° -> repeat
            angles = [0, 90, 180, 270]
            
            for angle in angles:
                print(f"Moving to {angle} degrees")
                set_servo_angle(angle)
                
                # Read ADC value (optional, for testing feedback)
                chan = AnalogIn(ads, ADS.P0)
                print(f"ADC Value: {chan.value}, Voltage: {chan.voltage:.2f}V")
                
                time.sleep(2)  # Wait between movements
                
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        pwm.stop()
        GPIO.cleanup()
        print("Cleanup completed")

if __name__ == "__main__":
    main()
