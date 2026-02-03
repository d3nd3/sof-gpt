#!/usr/bin/env python3
"""
Test script for rumble functionality
This script demonstrates the new rumble control commands
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_rumble_commands():
    """Test the rumble functionality"""
    print("Testing Rumble Functionality")
    print("=" * 40)
    
    try:
        # Import the keys module
        import sof.keys
        
        # Initialize gamepad
        print("Initializing gamepad...")
        sof.keys.init_gamepad()
        
        if sof.keys.joystick == 0:
            print("No gamepad detected. Please connect a gamepad and run again.")
            return
        
        print(f"Gamepad connected: {sof.keys.joystick.get_name()}")
        print()
        
        # Test rumble status
        print("1. Getting rumble status...")
        status = sof.keys.get_rumble_status()
        print(f"   {status}")
        print()
        
        # Test setting rumble intensity
        print("2. Setting rumble intensity...")
        sof.keys.set_rumble_intensity(0.5, 0.8)
        print()
        
        # Test starting rumble
        print("3. Starting rumble...")
        success = sof.keys.start_rumble()
        if success:
            print("   Rumble started successfully!")
        else:
            print("   Failed to start rumble")
        print()
        
        # Wait a bit
        import time
        print("4. Rumbling for 2 seconds...")
        time.sleep(2)
        print()
        
        # Test stopping rumble
        print("5. Stopping rumble...")
        success = sof.keys.stop_rumble()
        if success:
            print("   Rumble stopped successfully!")
        else:
            print("   Failed to stop rumble")
        print()
        
        # Test toggling rumble
        print("6. Testing rumble toggle...")
        print("   Current state:", "enabled" if sof.keys.rumbleEnabled else "disabled")
        
        sof.keys.toggle_rumble()
        print("   After toggle:", "enabled" if sof.keys.rumbleEnabled else "disabled")
        
        sof.keys.toggle_rumble()
        print("   After second toggle:", "enabled" if sof.keys.rumbleEnabled else "disabled")
        print()
        
        # Test rumble with custom duration
        print("7. Testing rumble with custom duration...")
        sof.keys.start_rumble(0.3, 0.6, 1000)  # 1 second
        print("   Rumble started with 1 second duration")
        time.sleep(1.5)  # Wait for rumble to finish
        print()
        
        print("Rumble testing completed successfully!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the project root directory")
    except Exception as e:
        print(f"Error during testing: {e}")

def test_command_interface():
    """Test the command interface"""
    print("\nTesting Command Interface")
    print("=" * 40)
    
    try:
        import sof.commands
        
        # Create a mock player object for testing
        class MockPlayer:
            def __init__(self):
                self.userinfo = {}
        
        mock_player = MockPlayer()
        
        print("1. Testing /toggle_rumble command...")
        sof.commands.commands.toggle_rumble(mock_player, "", terminal=True)
        print()
        
        print("2. Testing /get_rumble_status command...")
        sof.commands.commands.get_rumble_status(mock_player, "", terminal=True)
        print()
        
        print("3. Testing /set_rumble_intensity command...")
        sof.commands.commands.set_rumble_intensity(mock_player, "0.4 0.9", terminal=True)
        print()
        
        print("4. Testing /start_rumble command...")
        sof.commands.commands.start_rumble(mock_player, "0.2 0.7", terminal=True)
        print()
        
        print("5. Testing /stop_rumble command...")
        sof.commands.commands.stop_rumble(mock_player, "", terminal=True)
        print()
        
        print("Command interface testing completed successfully!")
        
    except Exception as e:
        print(f"Error during command testing: {e}")

if __name__ == "__main__":
    print("SOF-GPT Rumble Test Suite")
    print("=" * 50)
    print()
    
    # Test the rumble functionality
    test_rumble_commands()
    
    # Test the command interface
    test_command_interface()
    
    print("\nAll tests completed!")
