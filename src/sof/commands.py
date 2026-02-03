"""
Centralized command definitions for sof-gpt
This file contains all command functions that can be used by both client.py and chat_bridge.py
"""

import util
import math
from sof.packets.types import CLC_STRINGCMD

class Commands:
    """Centralized command class containing all available commands"""
    
    # Player management commands
    @staticmethod
    def team_red_blue(p, data, terminal=False):
        """Set team (0=red, 1=blue)"""
        if not len(data):
            message = f"team_red_blue is {p.userinfo['team_red_blue']}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        p.userinfo["team_red_blue"] = data
        message = f"team_red_blue is now {data}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def spectator(p, data, terminal=False):
        """Set spectator mode (0=player, 1=spectator)"""
        if not len(data):
            message = f"spectator is {p.userinfo['spectator']}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        p.userinfo["spectator"] = data
        message = f"spectator is now {data}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def name(p, data, terminal=False):
        """Change player name"""
        if not len(data):
            message = f"name is {p.userinfo['name']}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        p.userinfo["name"] = data + p.main.gpt["toggle_color_1"]
        message = f"name is now {data}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def skin(p, data, terminal=False):
        """Change player skin"""
        if not len(data):
            message = f"skin is {p.userinfo['skin']}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        p.userinfo["skin"] = data
        message = f"skin is now {data}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def predicting(p, data, terminal=False):
        """Set prediction mode (0=off, 1=on)"""
        if not len(data):
            message = f"predicting is {p.isPredicting}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        predicting = int(data)
        if predicting == 0 or predicting == 1:
            p.setPredicting(predicting)
            message = f"predicting is now {p.isPredicting}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            
            # If turning on predicting, reconnect to apply the change
            if predicting == 1:
                Commands.reconnect(p, data, terminal)

    # Movement and control commands
    @staticmethod
    def forward_speed(p, data, terminal=False):
        """Set forward movement speed"""
        if not len(data):
            message = f"forward_speed is {p.uc_now.forwardSpeed}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        update = int(data)
        p.uc_now.forwardSpeed = update
        message = f"forward_speed is now {update}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def custom_pitch(p, data, terminal=False):
        """Set custom pitch angle"""
        p.custom_pitch = int(data)
        message = f"custom_pitch is now {p.custom_pitch}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def custom_yaw(p, data, terminal=False):
        """Set custom yaw angle"""
        p.custom_yaw = int(data)
        message = f"custom_yaw is now {p.custom_yaw}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def custom_roll(p, data, terminal=False):
        """Set custom roll angle"""
        p.custom_roll = int(data)
        message = f"custom_roll is now {p.custom_roll}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def pitch_speed(p, data, terminal=False):
        """Set pitch rotation speed"""
        if not len(data):
            message = f"pitch_speed is {p.pitch_speed}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        p.pitch_speed = int(data)
        message = f"pitch_speed is now {p.pitch_speed}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def yaw_speed(p, data, terminal=False):
        """Set yaw rotation speed"""
        if not len(data):
            message = f"yaw_speed is {p.yaw_speed}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        p.yaw_speed = int(data)
        message = f"yaw_speed is now {p.yaw_speed}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def roll_speed(p, data, terminal=False):
        """Set roll rotation speed"""
        if not len(data):
            message = f"roll_speed is {p.roll_speed}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        p.roll_speed = int(data)
        message = f"roll_speed is now {p.roll_speed}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def speed_boost(p, data, terminal=False):
        """Set speed boost"""
        if not len(data):
            message = f"speed_boost is {p.speed_boost}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        p.speed_boost = int(data)
        message = f"speed_boost is now {p.speed_boost}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    # GPT and chat settings
    @staticmethod
    def base_delay(p, data, terminal=False):
        """Set base delay for GPT responses"""
        if not len(data):
            message = f"base_delay is {p.main.gpt['base_delay']}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        delay = int(data)
        if delay >= 0 and delay <= 100:
            p.main.gpt["base_delay"] = delay
            message = f"base_delay is now {delay}"
            if terminal:
                print(message)
            else:
                util.say(p, message)

    @staticmethod
    def scaled_delay(p, data, terminal=False):
        """Set scaled delay for GPT responses"""
        if not len(data):
            message = f"scaled_delay is {p.main.gpt['scaled_delay']}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        delay = int(data)
        if delay >= 0 and delay <= 100:
            p.main.gpt["scaled_delay"] = delay
            message = f"scaled_delay is now {delay}"
            if terminal:
                print(message)
            else:
                util.say(p, message)

    # Game action commands
    @staticmethod
    def kill(p, data, terminal=False):
        """Kill yourself"""
        p.conn.append_string_to_reliable(f"{CLC_STRINGCMD}kill\x00")

    @staticmethod
    def reconnect(p, data, terminal=False):
        """Reconnect to server"""
        p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
        p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
        p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
        p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
        p.init = False

    @staticmethod
    def quit(p, data, terminal=False):
        """Disconnect from server"""
        p.endpoint.removePlayer(p)

    @staticmethod
    def stop(p, data, terminal=False):
        """Stop current GPT response"""
        p.main.gpt["chunks"] = []

    @staticmethod
    def test(p, data, terminal=False):
        """Test command"""
        message = "test"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def shoot180(p, data, terminal=False):
        """Quick 180 degree turn"""
        p.viewangles[1] = p.viewangles[1] + 2048
        if p.viewangles[1] > 2047:
            p.viewangles[1] -= 4096
        p.step1 = time.monotonic() + 0.008
        message = "done!"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def weaponselect(p, data, terminal=False):
        """Select weapon by ID"""
        weaponID = int(data)
        p.conn.append_string_to_reliable(f"{CLC_STRINGCMD}weaponselect {weaponID}\x00")

    @staticmethod
    def fps(p, data, terminal=False):
        """Set or show target FPS"""
        if not len(data):
            message = f"Current target fps: {p.main.FPS:.2f} (msec {p.main.msec_sleep})"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        try:
            new_fps = float(data)
            if new_fps <= 0:
                message = "FPS must be > 0"
                if terminal:
                    print(message)
                else:
                    util.say(p, message)
                return
            p.main.FPS = new_fps
            p.main.msec_sleep = math.ceil(1000/p.main.FPS)
            p.main.float_sleep = p.main.msec_sleep / 1000
            p.main.target_fps = 1000/p.main.msec_sleep
            message = f"FPS updated: target_fps={p.main.target_fps:.2f}, msec={p.main.msec_sleep}"
            if terminal:
                print(message)
            else:
                util.say(p, message)
        except Exception:
            message = "Usage: /fps <number>"
            if terminal:
                print(message)
            else:
                util.say(p, message)

    # Help command
    @staticmethod
    def gamepad_status(p, data, terminal=False):
        """Show current gamepad status"""
        import sof.keys
        status = sof.keys.get_gamepad_status()
        message = f"Gamepad status: {status}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def gamepad_reinit(p, data, terminal=False):
        """Force reinitialize the gamepad"""
        import sof.keys
        success = sof.keys.force_reinit_gamepad()
        message = "Gamepad reinitialized successfully" if success else "Failed to reinitialize gamepad"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def gamepad_debug(p, data, terminal=False):
        """Enable/disable gamepad debug mode"""
        import sof.keys
        if data.lower() in ['on', '1', 'true', 'enable']:
            sof.keys.set_debug_mode(True)
            message = "Gamepad debug mode enabled"
        elif data.lower() in ['off', '0', 'false', 'disable']:
            sof.keys.set_debug_mode(False)
            message = "Gamepad debug mode disabled"
        else:
            # Toggle debug mode
            import sof.keys
            current_mode = getattr(sof.keys, 'debug_mode', False)
            sof.keys.set_debug_mode(not current_mode)
            message = f"Gamepad debug mode {'enabled' if not current_mode else 'disabled'}"
        
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def toggle_rumble(p, data, terminal=False):
        """Toggle rumble on/off"""
        import sof.keys
        status = sof.keys.toggle_rumble()
        message = f"Rumble {'enabled' if status else 'disabled'}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def start_rumble(p, data, terminal=False):
        """Start rumble with optional intensity values"""
        import sof.keys
        if data:
            try:
                # Parse intensity values if provided
                parts = data.split()
                if len(parts) >= 2:
                    low, high = float(parts[0]), float(parts[1])
                    sof.keys.set_rumble_intensity(low, high)
                    success = sof.keys.start_rumble()
                else:
                    success = sof.keys.start_rumble()
            except ValueError:
                message = "Usage: /start_rumble [low_intensity] [high_intensity] (values 0.0-1.0)"
                if terminal:
                    print(message)
                else:
                    util.say(p, message)
                return
        else:
            success = sof.keys.start_rumble()
        
        message = "Rumble started" if success else "Failed to start rumble"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def stop_rumble(p, data, terminal=False):
        """Stop rumble"""
        import sof.keys
        success = sof.keys.stop_rumble()
        message = "Rumble stopped" if success else "Failed to stop rumble"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def set_rumble_intensity(p, data, terminal=False):
        """Set rumble intensity values"""
        import sof.keys
        if not data:
            message = "Usage: /set_rumble_intensity <low> <high> (values 0.0-1.0)"
            if terminal:
                print(message)
            else:
                util.say(p, message)
            return
        
        try:
            parts = data.split()
            if len(parts) >= 2:
                low, high = float(parts[0]), float(parts[1])
                sof.keys.set_rumble_intensity(low, high)
                message = f"Rumble intensity set to: Low={low:.2f}, High={high:.2f}"
            else:
                message = "Usage: /set_rumble_intensity <low> <high> (values 0.0-1.0)"
        except ValueError:
            message = "Usage: /set_rumble_intensity <low> <high> (values 0.0-1.0)"
        
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def get_rumble_status(p, data, terminal=False):
        """Show current rumble status"""
        import sof.keys
        status = sof.keys.get_rumble_status()
        message = f"Rumble status: {status}"
        if terminal:
            print(message)
        else:
            util.say(p, message)

    @staticmethod
    def help(p, data, terminal=False):
        """Show comprehensive help"""
        help_text = """Available commands:
/team <0|1> - Set team (0=red, 1=blue)
/spectator <0|1> - Set spectator mode (0=player, 1=spectator)
/name <name> - Change player name
/skin <skin> - Change player skin
/predicting <0|1> - Set prediction mode
/kill - Kill yourself
/reconnect - Reconnect to server
/quit - Disconnect from server
/stop - Stop current GPT response
/test - Test command
/help - Show this help message
/gamepad_status - Show current gamepad status
/gamepad_reinit - Force reinitialize gamepad
/gamepad_debug [on|off] - Enable/disable gamepad debug mode
/toggle_rumble - Toggle rumble on/off
/start_rumble [low] [high] - Start rumble with optional intensity
/stop_rumble - Stop rumble
/set_rumble_intensity <low> <high> - Set rumble intensity (0.0-1.0)
/get_rumble_status - Show current rumble status
/weapon <id> - Select weapon by ID
/speed_boost <value> - Set speed boost
/shoot180 - Quick 180 degree turn
/forward_speed <value> - Set movement speed
/custom_pitch <value> - Set custom pitch angle
/custom_yaw <value> - Set custom yaw angle
/custom_roll <value> - Set custom roll angle
/pitch_speed <value> - Set pitch rotation speed
/yaw_speed <value> - Set yaw rotation speed
/roll_speed <value> - Set roll rotation speed
/base_delay <value> - Set GPT response delay
/scaled_delay <value> - Set scaled response delay
/fps [value] - Set or show target FPS

Examples:
/team 1          # Join blue team
/spectator 1     # Enter spectator mode
/name Player123  # Change name
/skin amu        # Change skin
/gamepad_status  # Check gamepad connection status
/gamepad_reinit  # Force reinitialize gamepad
/gamepad_debug   # Toggle debug mode
/toggle_rumble   # Toggle rumble on/off
/start_rumble 0.5 0.8  # Start rumble with low=0.5, high=0.8
/set_rumble_intensity 0.3 0.7  # Set rumble intensity"""
        if terminal:
            print(help_text)
        else:
            util.say(p, help_text)

# Create a global instance for easy importing
commands = Commands()
