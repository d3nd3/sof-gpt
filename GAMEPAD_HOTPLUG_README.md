# Gamepad Hot-Plugging Support

This document describes the new hot-plugging functionality for Xbox controllers and gamepads in sof-gpt.

## Overview

Previously, gamepads had to be connected before launching the program. With the new hot-plugging support, you can now:

- **Plug in a gamepad** while the program is running and it will be automatically detected and initialized
- **Unplug a gamepad** and the program will gracefully handle the disconnection
- **Reconnect a gamepad** and it will be automatically reinitialized
- **Switch between different gamepads** seamlessly

## How It Works

### Automatic Detection
The system now monitors for `JOYDEVICEADDED` and `JOYDEVICEREMOVED` events from pygame, which are triggered when:
- A USB gamepad is plugged in
- A USB gamepad is unplugged
- A Bluetooth gamepad connects/disconnects

### Health Monitoring
- **Periodic checks**: Every 60 frames (~0.4 seconds at 145 FPS), the system verifies the gamepad is still valid
- **Event-driven checks**: Before processing any gamepad input, the system checks if the device is still valid
- **Automatic recovery**: If a gamepad becomes invalid, the system automatically attempts to find and initialize another available gamepad

### Robust Error Handling
- Gracefully handles cases where the gamepad becomes unresponsive
- Automatically reinitializes when needed
- Falls back to keyboard/mouse input when no gamepad is available

## New Commands

### `/gamepad_status`
Shows the current status of the connected gamepad, including:
- Connection status
- Device name
- Instance ID
- Number of buttons and axes

**Usage:**
```
/gamepad_status
```

**Example output:**
```
Gamepad status: Connected: Xbox 360 Controller (ID: 0, Buttons: 11, Axes: 6)
```

### `/gamepad_reinit`
Forces a complete reinitialization of the gamepad system. Useful for troubleshooting when:
- The gamepad becomes unresponsive
- You want to switch to a different gamepad
- The automatic detection isn't working

**Usage:**
```
/gamepad_reinit
```

## Technical Implementation

### New Functions in `src/sof/keys.py`

#### `check_and_reinit_gamepad()`
- Checks if the current gamepad is still valid
- Automatically reinitializes if needed
- Called periodically and before processing input

#### `handle_joystick_device_event(event)`
- Handles `JOYDEVICEADDED` and `JOYDEVICEREMOVED` events
- Manages gamepad lifecycle automatically

#### `get_gamepad_status()`
- Returns detailed information about the current gamepad
- Useful for debugging and monitoring

#### `force_reinit_gamepad()`
- Forces a complete reinitialization of the gamepad system
- Useful for troubleshooting

### Event Handling
The main event loop now processes:
- `pygame.JOYDEVICEADDED` - When a gamepad is connected
- `pygame.JOYDEVICEREMOVED` - When a gamepad is disconnected

### Periodic Health Checks
Added to the main game loop in `src/sof/client.py`:
```python
# Periodic gamepad health check (every 60 frames ~ 0.4 seconds at 145 FPS)
if self.framecount % 60 == 0:
    sof.keys.check_and_reinit_gamepad()
```

## Testing

A test script `test_gamepad_hotplug.py` is provided to demonstrate the functionality:

```bash
python3 test_gamepad_hotplug.py
```

**Test features:**
- Real-time gamepad status display
- Hot-plug event monitoring
- Manual reinitialization testing
- Input testing for connected gamepads

**Test instructions:**
1. Run the test script
2. Plug in or unplug a gamepad while it's running
3. Watch the console for hot-plug events
4. Use SPACE to check status, R to force reinit
5. Press ESC to exit

## Troubleshooting

### Gamepad Not Detected
1. Check if the gamepad is recognized by the system
2. Try `/gamepad_reinit` command
3. Verify USB/Bluetooth connection
4. Check if the gamepad requires drivers

### Gamepad Becomes Unresponsive
1. The system should automatically detect and recover
2. If not, use `/gamepad_reinit` command
3. Check physical connections
4. Try reconnecting the gamepad

### Pygame Version Issues
1. Use `/gamepad_debug on` to enable debug mode
2. Check console output for pygame version and event support
3. If device events aren't supported, hot-plugging relies on periodic health checks
4. Consider updating pygame to version 2.0+ for full hot-plugging support

### Multiple Gamepads
- The system automatically uses the first available gamepad
- Use `/gamepad_reinit` to switch between gamepads
- The system will automatically fall back to the next available gamepad

## Compatibility

### Gamepad Support
This implementation works with:
- Xbox 360 controllers (wired and wireless)
- Xbox One controllers (wired and wireless)
- PlayStation controllers (with appropriate drivers)
- Generic USB gamepads
- Bluetooth gamepads

### Pygame Version Compatibility
- **Pygame 2.0+**: Full hot-plugging support with `JOYDEVICEADDED`/`JOYDEVICEREMOVED` events
- **Pygame 1.9.x**: Limited hot-plugging support (periodic health checks only)
- **Older versions**: Basic gamepad support without hot-plugging events

The system automatically detects your pygame version and adjusts functionality accordingly. Even on older versions, the periodic health checks provide some level of hot-plugging support.

## Performance Impact

- **Minimal overhead**: Health checks occur only every 60 frames
- **Event-driven**: Most detection happens through pygame events
- **Efficient**: Only reinitializes when necessary
- **Non-blocking**: All operations are asynchronous

## Future Enhancements

Potential improvements for future versions:
- Support for multiple simultaneous gamepads
- Gamepad profile switching
- Custom button mapping
- Gamepad calibration tools
- Rumble feedback customization

## Conclusion

The new hot-plugging support makes sof-gpt much more user-friendly by eliminating the need to restart the program when connecting/disconnecting gamepads. The system is robust, efficient, and provides useful debugging tools for troubleshooting.
