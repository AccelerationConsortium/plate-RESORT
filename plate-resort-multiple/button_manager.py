#!/usr/bin/env python3

import board
from digitalio import DigitalInOut, Direction, Pull
import time

class ButtonManager:
    def __init__(self):
        # Initialize buttons with pull-ups
        self.button_A = DigitalInOut(board.D5)  # Front button A
        self.button_A.direction = Direction.INPUT
        self.button_A.pull = Pull.UP

        self.button_B = DigitalInOut(board.D6)  # Front button B
        self.button_B.direction = Direction.INPUT
        self.button_B.pull = Pull.UP

        self.button_L = DigitalInOut(board.D27) # Left
        self.button_L.direction = Direction.INPUT
        self.button_L.pull = Pull.UP

        self.button_R = DigitalInOut(board.D23) # Right
        self.button_R.direction = Direction.INPUT
        self.button_R.pull = Pull.UP

        self.button_U = DigitalInOut(board.D17) # Up
        self.button_U.direction = Direction.INPUT
        self.button_U.pull = Pull.UP

        self.button_D = DigitalInOut(board.D22) # Down
        self.button_D.direction = Direction.INPUT
        self.button_D.pull = Pull.UP

    def check_button_a(self):
        """Check if button A is pressed"""
        if not self.button_A.value:
            time.sleep(0.2)  # Debounce
            return True
        return False

    def check_button_b(self):
        """Check if button B is pressed"""
        if not self.button_B.value:
            time.sleep(0.2)  # Debounce
            return True
        return False

    def get_snake_controls(self):
        """Get snake game control states"""
        return {
            'up': not self.button_U.value,
            'down': not self.button_D.value,
            'left': not self.button_L.value,
            'right': not self.button_R.value
        } 