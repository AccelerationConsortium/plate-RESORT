#!/usr/bin/env python3

import random
import time
from colorsys import hsv_to_rgb
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
import busio
import board

# Initialize GPIO
GPIO.setmode(GPIO.BCM)

# Pin definitions
CS_PIN = 8      # CE0 is GPIO8
DC_PIN = 25     # GPIO25
RESET_PIN = 24  # GPIO24
BAUDRATE = 24000000

# Setup SPI
spi = board.SPI()

# Setup pins
GPIO.setup(CS_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)
GPIO.setup(RESET_PIN, GPIO.OUT)

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=CS_PIN,
    dc=DC_PIN,
    rst=RESET_PIN,
    baudrate=BAUDRATE,
)

# Button pins setup
BUTTON_PINS = {
    'A': 5,    # Front button A
    'B': 6,    # Front button B
    'L': 27,   # Joystick Left
    'R': 23,   # Joystick Right
    'U': 17,   # Joystick Up
    'D': 22,   # Joystick Down
    'C': 4     # Joystick Center
}

# Setup all buttons as inputs with pull-up
for pin in BUTTON_PINS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup backlight
BACKLIGHT_PIN = 26
GPIO.setup(BACKLIGHT_PIN, GPIO.OUT)
GPIO.output(BACKLIGHT_PIN, GPIO.HIGH)  # Turn on backlight

# Create blank image for drawing.
width = disp.width
height = disp.height
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Clear display.
draw.rectangle((0, 0, width, height), outline=0, fill=(255, 0, 0))
disp.image(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

udlr_fill = "#00FF00"
udlr_outline = "#00FFFF"
button_fill = "#FF00FF"
button_outline = "#FFFFFF"

try:
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
except:
    fnt = ImageFont.load_default()

try:
    while True:
        # Check buttons and update display
        up_fill = udlr_fill if not GPIO.input(BUTTON_PINS['U']) else 0
        draw.polygon([(40, 40), (60, 4), (80, 40)], outline=udlr_outline, fill=up_fill)

        down_fill = udlr_fill if not GPIO.input(BUTTON_PINS['D']) else 0
        draw.polygon([(60, 120), (80, 84), (40, 84)], outline=udlr_outline, fill=down_fill)

        left_fill = udlr_fill if not GPIO.input(BUTTON_PINS['L']) else 0
        draw.polygon([(0, 60), (36, 42), (36, 81)], outline=udlr_outline, fill=left_fill)

        right_fill = udlr_fill if not GPIO.input(BUTTON_PINS['R']) else 0
        draw.polygon([(120, 60), (84, 42), (84, 82)], outline=udlr_outline, fill=right_fill)

        center_fill = button_fill if not GPIO.input(BUTTON_PINS['C']) else 0
        draw.rectangle((40, 44, 80, 80), outline=button_outline, fill=center_fill)

        A_fill = button_fill if not GPIO.input(BUTTON_PINS['A']) else 0
        draw.ellipse((140, 80, 180, 120), outline=button_outline, fill=A_fill)

        B_fill = button_fill if not GPIO.input(BUTTON_PINS['B']) else 0
        draw.ellipse((190, 40, 230, 80), outline=button_outline, fill=B_fill)

        # Make random colored text
        rcolor = tuple(int(x * 255) for x in hsv_to_rgb(random.random(), 1, 1))
        draw.text((20, 150), "Hello World", font=fnt, fill=rcolor)
        rcolor = tuple(int(x * 255) for x in hsv_to_rgb(random.random(), 1, 1))
        draw.text((20, 180), "Hello World", font=fnt, fill=rcolor)
        rcolor = tuple(int(x * 255) for x in hsv_to_rgb(random.random(), 1, 1))
        draw.text((20, 210), "Hello World", font=fnt, fill=rcolor)

        # Display the Image
        disp.image(image)
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nProgram stopped by user")
finally:
    GPIO.cleanup()
    print("GPIO cleanup completed") 