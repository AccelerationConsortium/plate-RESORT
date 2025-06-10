#!/usr/bin/env python3

from display_manager import DisplayManager
from servo_controller import ServoController
from adc_manager import ADCManager
from button_manager import ButtonManager
from snake_game import SnakeGame
import time

def main():
    in_snake_game = False  # Ensure this is always defined
    try:
        # Initialize components in correct order
        adc = ADCManager()
        display = DisplayManager(adc)
        servo = ServoController(adc)
        buttons = ButtonManager()
          # Start display
        display.init_display()
        display.start_display_thread()
        
        print("Starting servo control (Press A to cycle angles, B for Snake Game, Ctrl+C to exit)...")
        
        # Initialize game state
        snake = None
        
        while True:
            if not in_snake_game:
                # Normal servo control mode
                if buttons.check_button_a():
                    # Get next angle before movement
                    next_angle = servo.get_next_angle()
                    # Update display immediately with new target
                    display.update_state(next_angle, True)
                    # Now start the movement
                    servo.cycle_angle()
                elif buttons.check_button_b():
                    print("Starting Snake Game...")
                    in_snake_game = True
                    display.stop_display_thread()
                    snake = SnakeGame(display.disp, display.draw)
                    continue
                
                # Update display with servo state
                state = servo.get_state()
                display.update_state(
                    state['target_angle'],
                    state['is_moving']
                )
            else:
                # Snake game mode
                if buttons.check_button_b():
                    print("Exiting Snake Game...")
                    in_snake_game = False
                    snake = None
                    display.start_display_thread()
                    continue
                
                # Update snake game
                controls = buttons.get_snake_controls()
                snake.update(controls)
                snake.draw_game()
            
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        if not in_snake_game:
            display.stop_display_thread()
        display.clear_display()
        servo.stop()
        print("Cleanup completed")

if __name__ == "__main__":
    main()
