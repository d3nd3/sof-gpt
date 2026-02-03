#!/usr/bin/env python3
"""
Test script for gamepad hot-plugging functionality
This script demonstrates how the gamepad can be detected and used after being plugged in.
"""

import pygame
import time
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sof.keys import init_gamepad, check_and_reinit_gamepad, get_gamepad_status, force_reinit_gamepad

def test_gamepad_hotplug():
    """Test the gamepad hot-plugging functionality"""
    
    print("Gamepad Hot-Plugging Test")
    print("=" * 40)
    
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Gamepad Hot-Plug Test")
    
    # Set environment variable for background joystick events
    os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
    
    # Initialize joystick subsystem
    pygame.joystick.init()
    
    print(f"Initial joystick count: {pygame.joystick.get_count()}")
    
    # Try to initialize gamepad
    init_gamepad()
    
    clock = pygame.time.Clock()
    running = True
    frame_count = 0
    
    print("\nInstructions:")
    print("- Plug in or unplug a gamepad while the program is running")
    print("- Watch the console for hot-plug events")
    print("- Press ESC to exit")
    print("- Press SPACE to check gamepad status")
    print("- Press R to force reinitialize gamepad")
    print("\nPress any key to start...")
    
    # Wait for key press
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                waiting = False
                break
            elif event.type == pygame.QUIT:
                return
        clock.tick(60)
    
    print("\nStarting main loop...")
    
    while running:
        frame_count += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    print(f"\nGamepad status: {get_gamepad_status()}")
                elif event.key == pygame.K_r:
                    print("\nForcing gamepad reinitialization...")
                    force_reinit_gamepad()
            elif event.type == pygame.JOYDEVICEADDED:
                # Get the device index from the event
                device_index = getattr(event, 'device_index', None)
                if device_index is not None:
                    print(f"\n[EVENT] Gamepad device added: {device_index}")
                else:
                    print("\n[EVENT] Gamepad device added")
                check_and_reinit_gamepad()
            elif event.type == pygame.JOYDEVICEREMOVED:
                # Get the device index from the event
                device_index = getattr(event, 'device_index', None)
                if device_index is not None:
                    print(f"\n[EVENT] Gamepad device removed: {device_index}")
                else:
                    print("\n[EVENT] Gamepad device removed")
                check_and_reinit_gamepad()
            elif event.type == pygame.JOYBUTTONDOWN:
                print(f"[GAMEPAD] Button {event.button} pressed")
            elif event.type == pygame.JOYAXISMOTION:
                if abs(event.value) > 0.1:  # Only print significant movements
                    print(f"[GAMEPAD] Axis {event.axis}: {event.value:.3f}")
        
        # Periodic gamepad health check (every 60 frames)
        if frame_count % 60 == 0:
            check_and_reinit_gamepad()
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw status text
        font = pygame.font.Font(None, 36)
        status_text = get_gamepad_status()
        text_surface = font.render(status_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(400, 300))
        screen.blit(text_surface, text_rect)
        
        # Draw instructions
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "ESC: Exit",
            "SPACE: Check status", 
            "R: Force reinit",
            "Plug/unplug gamepad to test hot-plugging"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = font_small.render(instruction, True, (200, 200, 200))
            inst_rect = inst_surface.get_rect(center=(400, 400 + i * 30))
            screen.blit(inst_surface, inst_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("\nTest completed!")

if __name__ == "__main__":
    try:
        test_gamepad_hotplug()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()
