# Chat GUI Notification Features

This document describes the new notification checkbox functionality added to the SoF Chat GUI.

## Overview

The chat GUI now includes a notification settings panel that allows users to toggle different types of notifications on/off. This provides better control over what messages are displayed and when sounds are played.

## Features

### Notification Types

The following notification types can be toggled:

1. **Chat Messages** - Player chat messages from other players
   - Format: `[slot] name: message`
   - Example: `[1] PlayerName: Hello everyone!`

2. **Server Messages** - Server print messages (svc_print)
   - Format: `[PRINT] message`
   - Example: `[PRINT] Server restarted`

3. **String Package Prints** - Game events, weapons/items, and other string package messages (svc_sp_print*)
   - Formats: 
     - `[GENERAL] message` - Death messages, score updates, player joins, etc.
     - `[WEAPONS/ITEMS] message` - Pickup notifications, ammo updates, etc.
     - `[SOFPLUS] message` - SOFPlus specific messages
     - `[dm_ctf] message` - CTF game mode messages
     - `[BOT] message` - Bot-related messages
     - `[SOFPLUS_CUSTOM] message` - Custom SOFPlus messages
   - Examples:
     - `[GENERAL] PlayerName joined the game`
     - `[GENERAL] PlayerName was sniped by PlayerName2`
     - `[WEAPONS/ITEMS] Picked up a knife`
     - `[WEAPONS/ITEMS] Ammo is now 30 for your 9mm pistol...`

### Sound Notifications

- Sound notifications are controlled by the existing `set_sound_enabled()` method
- Sounds will only play for messages that are both enabled AND have sound enabled
- This provides granular control over audio notifications

## UI Layout

The chat GUI now has three main sections:

1. **Chat Text Area** (top) - Displays filtered messages based on notification settings
2. **Notification Settings Panel** (middle) - Checkboxes for each notification type
3. **Input Row** (bottom) - Message input field and send button

## Configuration

### Automatic Saving

Notification settings are automatically saved to the user's configuration file when changed:
- Location: `~/.config/sof-gpt/config.json`
- Key: `notification_settings`
- Format: JSON object with boolean values for each notification type

### Loading Settings

Settings are automatically loaded when the chat GUI starts, restoring the user's previous preferences.

## API Changes

### ChatUI Constructor

```python
ChatUI(on_send: Callable[[str], None], 
       title: str = "SoF Chat", 
       on_settings_changed: Optional[Callable[[], None]] = None)
```

New parameter: `on_settings_changed` - Optional callback function called when notification settings change.

### New Methods

```python
def get_notification_settings(self) -> dict:
    """Get current notification settings"""
    
def set_notification_settings(self, settings: dict) -> None:
    """Set notification settings from external source"""
```

### SofClient Integration

The SofClient class now:
- Automatically loads notification settings from config
- Saves notification settings when they change
- Integrates with the existing configuration system

## Usage Examples

### Basic Usage

```python
from src.ui.chat_gui import ChatUI

def on_send(message):
    print(f"Message: {message}")

def on_settings_changed():
    print("Settings changed!")

# Create chat UI with notification settings
chat_ui = ChatUI(on_send=on_send, on_settings_changed=on_settings_changed)
chat_ui.start()
```

### Programmatically Control Settings

```python
# Get current settings
settings = chat_ui.get_notification_settings()
print(f"Chat messages enabled: {settings['chat_messages']}")

# Change settings programmatically
chat_ui.set_notification_settings({
    'chat_messages': False,
    'server_messages': True,
    'string_package_prints': True
})
```

## Testing

Run the test script to see the notification features in action:

```bash
python3 test_notification_gui.py
```

This will open a test chat GUI window where you can:
- See all notification type checkboxes
- Test the filtering functionality
- Verify the UI layout and behavior

## Technical Details

### Message Filtering

Messages are filtered using regex patterns that match the prefix of each message type:
- Chat messages: `^\[\d+\]\s+\w+:\s+`
- Server messages: `^\[PRINT\]\s+`
- String package prints: `^\[(GENERAL|WEAPONS/ITEMS|SOFPLUS|dm_ctf|BOT|SOFPLUS_CUSTOM)\]\s+`

### Thread Safety

The notification settings are thread-safe and can be modified from both the UI thread and external threads.

### Backward Compatibility

All existing functionality is preserved:
- The `set_sound_enabled()` method still works as before
- Existing chat functionality is unchanged
- Configuration loading/saving maintains backward compatibility
