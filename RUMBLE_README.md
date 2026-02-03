# Joystick Rumble Control for SOF-GPT

This document describes the new joystick rumble control functionality that has been implemented in SOF-GPT.

## Overview

The rumble system allows players to control haptic feedback on their gamepad/joystick through in-game commands. This enhances the gaming experience by providing tactile feedback for various game events.

## Features

- **Rumble Toggle**: Enable/disable rumble functionality
- **Intensity Control**: Set low and high frequency rumble intensities (0.0-1.0)
- **Duration Control**: Control how long rumble effects last
- **Automatic Rumble**: Game events automatically trigger rumble (damage, firing, etc.)
- **Status Monitoring**: Check current rumble settings and gamepad support

## Commands

### `/toggle_rumble`
Toggles rumble on/off. When disabled, no rumble effects will occur.

**Usage**: `/toggle_rumble`

**Example**: `/toggle_rumble`

### `/start_rumble [low] [high]`
Starts rumble with optional intensity values.

**Usage**: `/start_rumble [low_intensity] [high_intensity]`

**Parameters**:
- `low_intensity`: Low frequency rumble intensity (0.0-1.0, optional)
- `high_intensity`: High frequency rumble intensity (0.0-1.0, optional)

**Examples**:
- `/start_rumble` - Start rumble with current intensity settings
- `/start_rumble 0.5 0.8` - Start rumble with low=0.5, high=0.8

### `/stop_rumble`
Stops any currently active rumble.

**Usage**: `/stop_rumble`

**Example**: `/stop_rumble`

### `/set_rumble_intensity <low> <high>`
Sets the rumble intensity values for future rumble effects.

**Usage**: `/set_rumble_intensity <low> <high>`

**Parameters**:
- `low`: Low frequency rumble intensity (0.0-1.0)
- `high`: High frequency rumble intensity (0.0-1.0)

**Example**: `/set_rumble_intensity 0.3 0.7`

### `/get_rumble_status`
Shows the current rumble status, including enabled state, gamepad support, and intensity values.

**Usage**: `/get_rumble_status`

**Example**: `/get_rumble_status`

## Automatic Rumble Events

The system automatically triggers rumble for various game events:

1. **Taking Damage**: Rumble intensity scales with damage amount
2. **Losing Armor**: Strong rumble effect when armor is depleted
3. **Firing Weapons**: Light rumble when shooting

## Technical Details

### Rumble Intensity Values
- **Low Frequency (0.0-1.0)**: Controls the left motor (usually stronger, lower frequency)
- **High Frequency (0.0-1.0)**: Controls the right motor (usually higher frequency, more subtle)

### Gamepad Support
The system automatically detects if your gamepad supports rumble and provides appropriate feedback. If rumble is not supported, commands will still work but won't produce haptic effects.

### Global Control
The `rumbleEnabled` flag controls whether rumble effects are active. When disabled:
- Manual rumble commands won't work
- Automatic game event rumble is suppressed
- Existing rumble effects are stopped

## Testing

Use the provided test script to verify rumble functionality:

```bash
python3 test_rumble.py
```

This script will:
1. Initialize your gamepad
2. Test all rumble functions
3. Verify command interface
4. Provide feedback on success/failure

## Troubleshooting

### No Rumble Effects
1. Check if rumble is enabled: `/get_rumble_status`
2. Verify gamepad connection: `/gamepad_status`
3. Ensure your gamepad supports rumble
4. Try reinitializing: `/gamepad_reinit`

### Rumble Too Strong/Weak
1. Adjust intensity: `/set_rumble_intensity 0.2 0.5`
2. Test with different values to find your preference
3. Remember: values range from 0.0 (off) to 1.0 (maximum)

### Gamepad Not Detected
1. Check physical connection
2. Verify gamepad is recognized by your OS
3. Use `/gamepad_reinit` to force reinitialization
4. Check `/gamepad_status` for connection details

## Integration with Existing Code

The rumble system integrates seamlessly with existing gamepad functionality:

- **Backward Compatible**: Existing rumble calls still work
- **Enhanced Control**: New functions provide better rumble management
- **Event-Driven**: Automatic rumble for game events
- **Configurable**: Easy to adjust rumble behavior

## Future Enhancements

Potential improvements for the rumble system:

1. **Profile System**: Save/load rumble preferences
2. **Event Customization**: Allow players to customize which events trigger rumble
3. **Pattern Support**: Complex rumble patterns for different game states
4. **Accessibility**: Options for players with sensitivity to haptic feedback

## Files Modified

- `src/sof/keys.py` - Core rumble control functions
- `src/sof/commands.py` - Command interface for rumble control
- `src/sof/packets/parse.py` - Integration with damage/armor events
- `src/sof/player.py` - Integration with weapon firing events

## Dependencies

- **pygame**: For gamepad input and rumble support
- **Python 3.6+**: For f-string support and modern Python features

## License

This functionality is part of the SOF-GPT project and follows the same licensing terms.
