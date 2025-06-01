#!/usr/bin/env python3

import time
import random
import board
from digitalio import DigitalInOut, Direction, Pull
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from collections import deque

# Initialize display
cs_pin = DigitalInOut(board.CE0)
dc_pin = DigitalInOut(board.D25)
reset_pin = DigitalInOut(board.D24)
BAUDRATE = 24000000

spi = board.SPI()
disp = st7789.ST7789(
    spi,
    height=240,
    y_offset=80,
    rotation=180,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

# Initialize buttons with pull-ups
button_A = DigitalInOut(board.D5)  # Front button A
button_A.direction = Direction.INPUT
button_A.pull = Pull.UP

button_B = DigitalInOut(board.D6)  # Front button B
button_B.direction = Direction.INPUT
button_B.pull = Pull.UP

button_L = DigitalInOut(board.D27) # Left
button_L.direction = Direction.INPUT
button_L.pull = Pull.UP

button_R = DigitalInOut(board.D23) # Right
button_R.direction = Direction.INPUT
button_R.pull = Pull.UP

button_U = DigitalInOut(board.D17) # Up
button_U.direction = Direction.INPUT
button_U.pull = Pull.UP

button_D = DigitalInOut(board.D22) # Down
button_D.direction = Direction.INPUT
button_D.pull = Pull.UP

# Turn on the Backlight
backlight = DigitalInOut(board.D26)
backlight.switch_to_output()
backlight.value = True

# Create blank image for drawing
width = disp.width   # 240
height = disp.height # 240
image = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(image)

# Load font
try:
    font = ImageFont.load_default()
except:
    font = ImageFont.load_default()

# Game constants
GRID_SIZE = 10
GRID_WIDTH = width // GRID_SIZE
GRID_HEIGHT = height // GRID_SIZE
SNAKE_COLOR = (0, 255, 0)  # Green
FOOD_COLOR = (255, 0, 0)   # Red
BG_COLOR = (0, 0, 0)       # Black
TEXT_COLOR = (255, 255, 255)  # White

class SnakeGame:
    def __init__(self, display, draw):
        self.display = display
        self.draw = draw
        self.width = display.width
        self.height = display.height
        
        # Game constants
        self.GRID_SIZE = 10
        self.GRID_WIDTH = self.width // self.GRID_SIZE
        self.GRID_HEIGHT = self.height // self.GRID_SIZE
        self.SNAKE_COLOR = (0, 255, 0)  # Green
        self.FOOD_COLOR = (255, 0, 0)   # Red
        self.BG_COLOR = (0, 0, 0)       # Black
        self.TEXT_COLOR = (255, 255, 255)  # White
        
        # Load font
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            self.font = ImageFont.load_default()
        
        # Initialize game state
        self.reset_game()

    def reset_game(self):
        """Reset the game state"""
        # Start with snake in the middle
        self.snake = deque([(self.GRID_WIDTH//2, self.GRID_HEIGHT//2)])
        self.direction = (1, 0)  # Start moving right
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        
    def spawn_food(self):
        """Spawn food in a random location not occupied by snake"""
        while True:
            food = (random.randint(0, self.GRID_WIDTH-1), 
                   random.randint(0, self.GRID_HEIGHT-1))
            if food not in self.snake:
                return food

    def update(self, controls):
        """Update game state based on controls"""
        if self.game_over:
            return

        # Update direction based on controls
        if controls['up'] and self.direction != (0, 1):
            self.direction = (0, -1)
        elif controls['down'] and self.direction != (0, -1):
            self.direction = (0, 1)
        elif controls['left'] and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif controls['right'] and self.direction != (-1, 0):
            self.direction = (1, 0)

        # Get new head position
        new_head = (
            (self.snake[0][0] + self.direction[0]) % self.GRID_WIDTH,
            (self.snake[0][1] + self.direction[1]) % self.GRID_HEIGHT
        )
        
        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            return
            
        self.snake.appendleft(new_head)
        
        # Check if food eaten
        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()

    def draw_game(self):
        """Draw the current game state"""
        # Clear screen
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.BG_COLOR)
        
        # Draw snake
        for segment in self.snake:
            x, y = segment
            self.draw.rectangle(
                (x * self.GRID_SIZE, y * self.GRID_SIZE,
                 (x + 1) * self.GRID_SIZE - 1, (y + 1) * self.GRID_SIZE - 1),
                fill=self.SNAKE_COLOR
            )
        
        # Draw food
        x, y = self.food
        self.draw.rectangle(
            (x * self.GRID_SIZE, y * self.GRID_SIZE,
             (x + 1) * self.GRID_SIZE - 1, (y + 1) * self.GRID_SIZE - 1),
            fill=self.FOOD_COLOR
        )
        
        # Draw score
        self.draw.text((5, 5), f"Score: {self.score}", font=self.font, fill=self.TEXT_COLOR)
        
        # Draw game over message
        if self.game_over:
            msg = "Game Over! Press B to exit"
            text_bbox = self.draw.textbbox((0, 0), msg, font=self.font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (self.width - text_width) // 2
            y = (self.height - text_height) // 2
            self.draw.text((x, y), msg, font=self.font, fill=self.TEXT_COLOR)
        
        # Update display
        self.display.image(self.draw._image)

def main():
    game = SnakeGame(disp, draw)
    last_update = time.monotonic()
    update_interval = 0.2  # Speed of snake movement
    
    while True:
        # Handle input
        if not button_A.value:  # Right front button pressed
            if game.game_over:
                game.reset_game()
                time.sleep(0.2)  # Debounce
                
        if not button_B.value:  # Left front button pressed
            game.game_over = True
            time.sleep(0.2)  # Debounce
            
        if not game.game_over:
            if not button_U.value:  # Up pressed
                game.update({'up': True})
            elif not button_D.value:  # Down pressed
                game.update({'down': True})
            elif not button_L.value:  # Left pressed
                game.update({'left': True})
            elif not button_R.value:  # Right pressed
                game.update({'right': True})
        
        # Update game state
        current_time = time.monotonic()
        if current_time - last_update > update_interval:
            game.update({'up': False, 'down': False, 'left': False, 'right': False})
            last_update = current_time
        
        # Draw everything
        game.draw_game()
        
        # Small delay to prevent too much CPU usage
        time.sleep(0.01)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGame terminated by user")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Clear display before exit
        draw.rectangle((0, 0, width, height), fill=(0, 0, 0))
        disp.image(image)
        print("Game cleaned up") 