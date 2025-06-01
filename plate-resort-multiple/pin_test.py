#!/usr/bin/env python3
import board

# Print all available attributes in board module
print("Available board pins:")
for pin in dir(board):
    if not pin.startswith('__'):  # Skip internal attributes
        print(pin) 