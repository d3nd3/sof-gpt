* sudo apt install xvfb chromium
* pip3 install selenium
* pip3 install undetected-chromedriver
* pip3 install webdriver-manager
* pip3 install pygame


* add to /etc/ssl/openssl.cnf

## Chat Commands

The sof-gpt client supports various chat commands that can be used in-game. All commands are centralized in a single `commands.py` file to ensure consistency between different parts of the system.

### Slash Commands (e.g., `/team 1`)
- `/team <0|1>` - Set team (0=red, 1=blue)
- `/spectator <0|1>` - Set spectator mode (0=player, 1=spectator)  
- `/name <name>` - Change player name
- `/skin <skin>` - Change player skin
- `/predicting <0|1>` - Set prediction mode
- `/kill` - Kill yourself
- `/reconnect` - Reconnect to server
- `/quit` - Disconnect from server
- `/stop` - Stop current GPT response
- `/test` - Test command
- `/help` - Show help message

### Bracket Commands (e.g., `[team_red_blue] 1`)
- `[team_red_blue] <0|1>` - Set team
- `[spectator] <0|1>` - Set spectator mode
- `[name] <name>` - Change player name
- `[skin] <skin>` - Change player skin
- `[predicting] <0|1>` - Set prediction mode
- `[forward_speed] <value>` - Set movement speed
- `[custom_pitch] <value>` - Set custom pitch angle
- `[custom_yaw] <value>` - Set custom yaw angle
- `[custom_roll] <value>` - Set custom roll angle
- `[pitch_speed] <value>` - Set pitch rotation speed
- `[yaw_speed] <value>` - Set yaw rotation speed
- `[roll_speed] <value>` - Set roll rotation speed
- `[speed_boost] <value>` - Set speed boost
- `[base_delay] <value>` - Set GPT response delay
- `[scaled_delay] <value>` - Set scaled response delay
- `[shoot180]` - Quick 180 degree turn

### Examples
```
/team 1          # Join blue team
/spectator 1     # Enter spectator mode
/name Player123  # Change name to Player123
/help            # Show comprehensive help with all commands
```

### Getting Help
Use `/help` in-game to see a complete list of all available commands and their usage. The help system shows both slash commands and bracket commands with examples.

### Command Architecture
The command system is designed with a centralized architecture:
- **`src/sof/commands.py`** - Contains all command implementations
- **`src/sof/chat_bridge.py`** - Handles chat-based command parsing (both `/` and `[` syntax)
- **`src/sof/client.py`** - Handles terminal-based command parsing

This ensures that all commands behave identically regardless of how they're invoked, and makes maintenance easier by having a single source of truth for command logic.

### Command Availability
Most commands are available in both interfaces:
- **Terminal**: Use `/command` syntax (e.g., `/team 1`, `/skin amu`)
- **Chat**: Use `/command` syntax (e.g., `/team 1`, `/skin amu`)
- **Settings**: Use `[command]` syntax (e.g., `[team_red_blue] 1`, `[skin] amu`)

The terminal interface provides quick access to the most commonly used commands, while the chat interface supports both slash commands and bracket commands for comprehensive control.

### Help System
- **`/help`** - Shows all available commands in a unified format
- **Terminal help** - Includes both general commands and terminal-specific commands
- **Chat help** - Shows the same command list for consistency

```
[openssl_init]
providers = provider_sect

# List of providers to load
[provider_sect]
default = default_sect
legacy = legacy_sect
# The fips section name should match the section name inside the
# included fipsmodule.cnf.
# fips = fips_sect

# If no providers are activated explicitly, the default one is activated implicitly.
# See man 7 OSSL_PROVIDER-default for more details.
#
# If you add a section explicitly activating any other provider(s), you most
# probably need to explicitly activate the default provider, otherwise it
# becomes unavailable in openssl.  As a consequence applications depending on
# OpenSSL may not work correctly which could lead to significant system
# problems including inability to remotely access the system.
[default_sect]
activate = 1

[legacy_sect]
activate = 1
```

