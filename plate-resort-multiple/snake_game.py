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
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        # Start with snake in the middle
        self.snake = deque([(GRID_WIDTH//2, GRID_HEIGHT//2)])
        self.direction = (1, 0)  # Start moving right
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.paused = False
        
    def spawn_food(self):
        while True:
            food = (random.randint(0, GRID_WIDTH-1), 
                   random.randint(0, GRID_HEIGHT-1))
            if food not in self.snake:
                return food
    
    def update(self):
        if self.game_over or self.paused:
            return

        # Get new head position
        new_head = (
            (self.snake[0][0] + self.direction[0]) % GRID_WIDTH,
            (self.snake[0][1] + self.direction[1]) % GRID_HEIGHT
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
    
    def change_direction(self, new_dir):
        # Prevent 180-degree turns
        if (new_dir[0] != -self.direction[0] or 
            new_dir[1] != -self.direction[1]):
            self.direction = new_dir
    
    def draw(self, draw):
        # Clear screen
        draw.rectangle((0, 0, width, height), fill=BG_COLOR)
        
        # Draw snake
        for segment in self.snake:
            x, y = segment
            draw.rectangle(
                (x * GRID_SIZE, y * GRID_SIZE,
                 (x + 1) * GRID_SIZE - 1, (y + 1) * GRID_SIZE - 1),
                fill=SNAKE_COLOR
            )
        
        # Draw food
        x, y = self.food
        draw.rectangle(
            (x * GRID_SIZE, y * GRID_SIZE,
             (x + 1) * GRID_SIZE - 1, (y + 1) * GRID_SIZE - 1),
            fill=FOOD_COLOR
        )
        
        # Draw score
        draw.text((5, 5), f"Score: {self.score}", font=font, fill=TEXT_COLOR)
        
        # Draw game over or paused message
        if self.game_over:
            msg = "Game Over! Press RIGHT button to restart"
            draw.text((20, height//2), msg, font=font, fill=TEXT_COLOR)
        elif self.paused:
            msg = "PAUSED"
            draw.text((width//2 - 20, height//2), msg, font=font, fill=TEXT_COLOR)

def main():
    game = SnakeGame()
    last_update = time.monotonic()
    update_interval = 0.2  # Speed of snake movement
    
    while True:
        # Handle input
        if not button_A.value:  # Right front button pressed
            if game.game_over:
                game.reset_game()
                time.sleep(0.2)  # Debounce
                
        if not button_B.value:  # Left front button pressed
            game.paused = not game.paused
            time.sleep(0.2)  # Debounce
            
        if not game.game_over and not game.paused:
            if not button_U.value:  # Up pressed
                game.change_direction((0, -1))
            elif not button_D.value:  # Down pressed
                game.change_direction((0, 1))
            elif not button_L.value:  # Left pressed
                game.change_direction((-1, 0))
            elif not button_R.value:  # Right pressed
                game.change_direction((1, 0))
        
        # Update game state
        current_time = time.monotonic()
        if current_time - last_update > update_interval:
            game.update()
            last_update = current_time
        
        # Draw everything
        game.draw(draw)
        disp.image(image)
        
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