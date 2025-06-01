import RPi.GPIO as GPIO
import time

# Setup GPIO
GPIO.setmode(GPIO.BCM)
SERVO_PIN = 18
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create PWM instance
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz frequency

try:
    print("Starting servo test...")
    pwm.start(2.5)  # Should move to 0 degrees
    print("Setting to 0 degrees (2.5% duty cycle)")
    time.sleep(2)
    
    print("Setting to 150 degrees (7.5% duty cycle)")
    pwm.ChangeDutyCycle(7.5)
    time.sleep(2)
    
    print("Setting to 300 degrees (12.5% duty cycle)")
    pwm.ChangeDutyCycle(12.5)
    time.sleep(2)
    
except KeyboardInterrupt:
    print("\nTest stopped by user")
finally:
    pwm.stop()
    GPIO.cleanup()
    print("Cleanup completed") 