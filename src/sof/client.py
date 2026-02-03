from sof.player import Player
from sof.connection import Endpoint

from sof.chat_bridge import output_gpt
import sof.chat_bridge as GPT
from sof.commands import commands

from sof.packets.defines import *

import sof.packets.types as types

import sof.keys
import util
from ui.chat_gui import ChatUI

import time
import pygame

import os
import math
import threading
from queue import Queue
import json


# this class represents the entire tool.
# ideally handles multiple connections/endpoints/servers
# and ideally there can be multiple players to a connection

# I refer to this as `main`
class SofClient:
	def __init__(self):
		# dict of `ip:port`:Endpoint
		self.endpoints = {}
		# there can only be 1 instance of gpt
		self.gpt = {
			"active" : False,
			"chunks" : [],
			"chunk_len_prev" : 0,
			"say_timestamp" : time.time(),
			"base_delay" : 1,
			"scaled_delay" : 4,

			"toggle_color" : False,
			"toggle_color_1" : P_WHITE,
			"toggle_color_2" : P_GREEN,
		}

		self.connectedCount = 0

		# slot id -> player name mapping (for GUI chat display)
		self.slot_to_name = {}
		# cache of configstrings by index (for playerinfo lookup)
		self.configstrings = {}
		self.cs_playerskins_base = None
		# Track indices that look like playerskins and their parsed names
		self.playerskins_indices = set()
		self.playerskin_index_to_name = {}

		self.FPS = 145 #change this
		# rounded up in msec, to lower frame-rate bound.
		self.msec_sleep = math.ceil(1000/self.FPS) #255 max for byte object msec command.
		print(f"Calculated msec of {self.msec_sleep}")
		self.float_sleep = self.msec_sleep / 1000 #in secs
		self.target_fps = 1000/self.msec_sleep

		self.framecount = 0
		self.main_begin = self.before_cpu = time.time()

		# thread safe queue
		self.user_input_queue = Queue()
		# GUI chat input queue
		self.gui_chat_queue = Queue()

		# Persistent config (e.g., RCON passwords)
		self.rcon_passwords = {}
		self._config_path = self._get_config_file_path()
		self._load_config()

		# GUI chat window
		self.chat_ui = ChatUI(self._on_gui_send, title="SoF Chat", on_settings_changed=self.save_notification_settings)
		# Apply user setting for audible notifications if present
		self.chat_ui.set_sound_enabled(bool(self._get_config_value("audio_notify", True)))
		
		# Load notification settings from config
		notification_settings = self._get_config_value("notification_settings", {})
		if notification_settings:
			self.chat_ui.set_notification_settings(notification_settings)
		# RCON UI (lazy start)
		self.rcon_ui = None
		self.rcon_output_queue = Queue()
		# Deprecated global; kept for backward compatibility fallback
		self.rcon_password = ""

	def set_playerskins_base(self, base_index: int):
		self.cs_playerskins_base = int(base_index)
		print(f"[playerskins-base] set to {self.cs_playerskins_base}")

	def get_playerskins_base(self):
		return self.cs_playerskins_base

	def register_playerskin(self, index: int, name: str):
		self.playerskins_indices.add(int(index))
		self.playerskin_index_to_name[int(index)] = name
		# If base not known, attempt to infer
		if self.cs_playerskins_base is None:
			base_candidate = int(index)  # fallback until we infer below
			# Try infer base by maximizing the count of indices in [base, base+CS_MAXCLIENTS)
			best_base = None
			best_count = -1
			for idx in list(self.playerskins_indices):
				base = idx  # assume slot 0 at this idx
				count = sum(1 for j in self.playerskins_indices if base <= j < base + CS_MAXCLIENTS)
				if count > best_count:
					best_count = count
					best_base = base
			if best_base is not None and best_count >= 2:
				self.set_playerskins_base(best_base)

	def get_name_for_slot(self, slot: int):
		# Prefer direct lookup with known base
		if self.cs_playerskins_base is not None:
			idx = self.cs_playerskins_base + int(slot)
			name = self.playerskin_index_to_name.get(idx)
			if name:
				return name
			ci = self.configstrings.get(idx)
			if ci:
				parts = ci.split('\\')
				if parts and parts[0]:
					return parts[0]
		# Try infer base from existing indices by voting
		candidates = {}
		for idx in self.playerskins_indices:
			base = idx - int(slot)
			candidates[base] = candidates.get(base, 0) + 1
		if candidates:
			best_base = max(candidates.items(), key=lambda kv: kv[1])[0]
			self.set_playerskins_base(best_base)
			idx = best_base + int(slot)
			name = self.playerskin_index_to_name.get(idx)
			if name:
				return name
			ci = self.configstrings.get(idx)
			if ci:
				parts = ci.split('\\')
				if parts and parts[0]:
					return parts[0]
		return None

		
	# if connection already exists, append a player, else both
	def addEndpoint(self,host,port):
		key = host + port
		if not key in self.endpoints:
			self.endpoints[key] = Endpoint(host,port)
		return self.endpoints[key]

	# endpoint is a server/port + list of players
	# this adds a player to endpoint
	def addPlayerToEndpoint(self,endpoint,userinfo,name):
		p = Player(self,endpoint,userinfo,name)
		endpoint.players.append(p)


	# TODO STORE ORIGIN PLAYER OF GPT REQUEST, ENSURE OUTPUT GOES THERE.
	def talkToWorld(self):

		# begin getchallenge for each connection
		# Player doesnt renew, but Connection does.
		# Store wasConnected in player
		for ep_key,e in self.endpoints.items():
			if not len(e.players):
				# Not working.
				pygame.quit()
				os._exit(0)
			# using list() so that we can remove from it easier.
			for player in list(e.players):
				if not player.init:
					# Reconnect an initted players
					# Creates Connection object and initialises connection parameters
					if not player.initialize():
						print("REMOVING! server not respond!")
						e.players.remove(player)
						continue

				c = player.conn

				# do this before recv(), since recv() can set connection parameters.
				if c.connected < 2:
					# from connected to disconnected/connecting
					if player.wasConnected == 2:
						self.connectedCount -=1
						print(f"DISCONNECTED: New Total : {self.connectedCount}")

				c.recv()
				
				# TODO: THERE IS BUG ON SOME MAPS THAT START PACKET WITH SVC_TMP_ENTITY
				
				sof.keys.process(player)

				# Periodic gamepad health check (every 60 frames ~ 0.4 seconds at 145 FPS)
				if self.framecount % 60 == 0:
					sof.keys.check_and_reinit_gamepad()

				# send usercmds if connected
				player.moveAndSend()

				if hasattr(player, 'step2') and player.step2 is not None:
					if time.monotonic() >= player.step2:
						player.step2 = None # Clear the timer
						player.input.fire = False
						
						
						player.viewangles[1] = player.viewangles[1] + 2048
						if player.viewangles[1] > 2047:
							player.viewangles[1] -= 4096
							
				if hasattr(player, 'step1') and player.step1 is not None:
					if time.monotonic() >= player.step1:
						player.step1 = None # Clear the timer
						player.input.fire = True
						player.step2 = time.monotonic() + 0.008
						
						
						
				

				pygame.display.update()
				
				# sends heartbeat fps times a second
				# connected 2 == fully connected , its resembling states from q2.
				if c.connected == 2:
					if player.wasConnected != 2:
						self.connectedCount +=1
						print(f"CONNECTED: New Total : {self.connectedCount}")
						time.sleep(0.1)
						player.onEnterServer()


				if time.time() - player.conn.last_packet_stamp > 15.0:
					print("auto die no packet")
					player.init = False
					player.conn.last_packet_stamp = time.time()

				player.wasConnected = player.conn.connected

			# TODO: make gpt output endpoint specific, meaning output to same endpoint the request was generated in.
			for player in e.players:
				if player.conn.connected == 2:
					# its timer restricted. so it doesnt spam
					output_gpt(self,player,player.conn)

					# Drain terminal command queue
					while not self.user_input_queue.empty():
						cmd_line = self.user_input_queue.get()
						self._execute_terminal_command(player, cmd_line)

					# Drain GUI chat queue
					while not self.gui_chat_queue.empty():
						text = self.gui_chat_queue.get()
						player.conn.append_string_to_reliable(f"{types.CLC_STRINGCMD}say {text}\x00")
				break

	def _on_gui_send(self, text: str):
		self.gui_chat_queue.put(text)

	def _on_rcon_send(self, text: str):
		low = text.strip()
		if low.startswith("/rconpass "):
			parts = low.split()
			# Allow two forms:
			# 1) /rconpass <pwd>                      -> save for current server
			# 2) /rconpass <ip:port> <pwd>            -> save for specified server
			try:
				if len(parts) == 2:
					player = self._get_primary_player()
					if not player:
						self.on_rcon_output("[rcon] No active server; connect first or specify ip:port")
						return
					ip = player.endpoint.ip
					port = int(player.endpoint.port)
					pwd = parts[1]
					self._set_rcon_password_for(ip, port, pwd)
					self.rcon_password = pwd
					self.on_rcon_output(f"[rcon] Password saved for {ip}:{port}")
					return
				elif len(parts) == 3 and ":" in parts[1]:
					ip_port = parts[1]
					ip, port_s = ip_port.split(":", 1)
					pwd = parts[2]
					self._set_rcon_password_for(ip, int(port_s), pwd)
					self.on_rcon_output(f"[rcon] Password saved for {ip}:{int(port_s)}")
					return
				else:
					self.on_rcon_output("Usage: /rconpass <pwd>  or  /rconpass <ip:port> <pwd>")
					return
			except Exception as e:
				self.on_rcon_output(f"[rcon] Error saving password: {e}")
				return
		self._send_rcon(text)

	def on_game_chat(self, message: str, play_sound: bool = False):
		# Called from packet parser to display chat in GUI
		try:
			self.chat_ui.post(message, play_sound)
		except Exception:
			pass

	def on_rcon_output(self, message: str):
		# Called from connection for unconnected RCON responses
		try:
			self._ensure_rcon_ui()
			# Ensure UI is visible when first output arrives
			if not self.rcon_ui.is_visible():
				self.rcon_ui.show()
			self.rcon_ui.post(message.rstrip("\r\n"))
		except Exception:
			# Swallow UI errors; avoid crashing network loop
			pass

	def _get_primary_player(self):
		for _, endpoint in self.endpoints.items():
			for player in endpoint.players:
				# Prefer a fully connected player if available
				try:
					if player.conn and player.conn.connected == 2:
						return player
				except Exception:
					pass
				# Fallback to first player
				return player
		return None

	def _get_config_dir(self):
		xdg = os.environ.get("XDG_CONFIG_HOME")
		if not xdg:
			xdg = os.path.join(os.path.expanduser("~"), ".config")
		path = os.path.join(xdg, "sof-gpt")
		try:
			os.makedirs(path, exist_ok=True)
		except Exception:
			pass
		return path

	def _get_config_file_path(self):
		return os.path.join(self._get_config_dir(), "config.json")

	def _load_config(self):
		try:
			with open(self._config_path, "r", encoding="utf-8") as f:
				data = json.load(f)
				self.rcon_passwords = dict(data.get("rcon_passwords", {}))
				self._config_blob = data
		except Exception:
			self.rcon_passwords = {}
			self._config_blob = {}

	def _save_config(self):
		try:
			data = dict(self._config_blob) if hasattr(self, "_config_blob") and isinstance(self._config_blob, dict) else {}
			data["rcon_passwords"] = self.rcon_passwords
			with open(self._config_path, "w", encoding="utf-8") as f:
				json.dump(data, f, indent=2, sort_keys=True)
		except Exception:
			pass

	def _set_config_value(self, key: str, value):
		if not hasattr(self, "_config_blob") or not isinstance(self._config_blob, dict):
			self._config_blob = {}
		self._config_blob[key] = value
		self._save_config()

	def save_notification_settings(self):
		"""Save current notification settings to config"""
		if hasattr(self, 'chat_ui') and self.chat_ui:
			settings = self.chat_ui.get_notification_settings()
			self._set_config_value("notification_settings", settings)

	def _get_config_value(self, key: str, default=None):
		try:
			return self._config_blob.get(key, default)
		except Exception:
			return default

	def _get_rcon_password_for(self, ip: str, port: int):
		return self.rcon_passwords.get(f"{ip}:{int(port)}")

	def _set_rcon_password_for(self, ip: str, port: int, password: str):
		self.rcon_passwords[f"{ip}:{int(port)}"] = password
		self._save_config()

	def _ensure_rcon_ui(self):
		if self.rcon_ui is None:
			self.rcon_ui = ChatUI(self._on_rcon_send, title="SoF RCON")
			self.rcon_ui.start()

	def _toggle_rcon_window(self):
		self._ensure_rcon_ui()
		if self.rcon_ui.is_visible():
			self.rcon_ui.hide()
		else:
			self.rcon_ui.show()

	def _send_rcon(self, command: str):
		# Send unconnected RCON packet to the current endpoint server of the primary player
		player = self._get_primary_player()
		if not player:
			print("[rcon] No active player/server to send command")
			return
		endpoint = player.endpoint
		ip, port = endpoint.ip, int(endpoint.port)
		password = self._get_rcon_password_for(ip, port) or self.rcon_password
		if not password:
			print(f"Set RCON password first with /rconpass <pwd> (for {ip}:{port})")
			return
		try:
			server = (ip, port)
			msg = f"rcon {password} {command}".encode('latin_1', errors='ignore')
			payload = b"\xff\xff\xff\xff" + msg
			player.conn.s.sendto(payload, server)
			print(f"[rcon] sent to {server}: {command}")
		except Exception as e:
			print(f"[rcon] send error: {e}")

	def _execute_terminal_command(self, player, line: str):
		line = line.strip()
		if not line:
			return
		# sofgpt invocation
		for prefix in ("@sofgpt ", "/gpt ", "gpt "):
			if line.lower().startswith(prefix):
				content = line[len(prefix):]
				GPT.interact(content, player)
				return
		# built-ins
		low = line.lower()
		low = low.lstrip()
		if low == "/help":
			commands.help(player, "", terminal=True)
			print("\nTerminal-specific commands:")
			print("  /gpt <text>                   - Ask GPT; same as @sofgpt <text>")
			print("  /chat                         - Toggle chat window visibility")
			print("  /audionotify [on|off]         - Toggle audible notifications for chat/RCON")
			print("  /skins                        - Dump player clientinfo from configstrings")
			print("  /rconpass <pwd>               - Set and save RCON password for current server")
			print("  /rconwin                      - Toggle RCON window")
			print("  /rcon <command>               - Send RCON command (also in RCON window)")
			return

		# Commands that can take arguments
		if low.startswith("/say "):
			player.conn.append_string_to_reliable(f"{types.CLC_STRINGCMD}say {line[5:]}\x00")
			return
		
		if low == "/weapon" or low.startswith("/weapon "):
			if len(line.split()) > 1:
				commands.weaponselect(player, line.split(None,1)[1], terminal=True)
			else:
				print("Usage: /weapon <id> - Select weapon by ID")
			return
		if low == "/name" or low.startswith("/name "):
			if len(line.split()) > 1:
				commands.name(player, line.split(None,1)[1], terminal=True)
			else:
				commands.name(player, "", terminal=True)
			return
		if low == "/skin" or low.startswith("/skin "):
			if len(line.split()) > 1:
				commands.skin(player, line.split(None,1)[1], terminal=True)
			else:
				commands.skin(player, "", terminal=True)
			return
		if low == "/team" or low.startswith("/team "):
			if len(line.split()) > 1:
				commands.team_red_blue(player, line.split(None,1)[1], terminal=True)
			else:
				commands.team_red_blue(player, "", terminal=True)
			return
		if low == "/spectator" or low.startswith("/spectator "):
			if len(line.split()) > 1:
				commands.spectator(player, line.split(None,1)[1], terminal=True)
			else:
				commands.spectator(player, "", terminal=True)
			return
		if low == "/predicting" or low.startswith("/predicting "):
			if len(line.split()) > 1:
				commands.predicting(player, line.split(None,1)[1], terminal=True)
			else:
				commands.predicting(player, "", terminal=True)
			return
		if low == "/speed_boost" or low.startswith("/speed_boost "):
			if len(line.split()) > 1:
				commands.speed_boost(player, line.split(None,1)[1], terminal=True)
			else:
				commands.speed_boost(player, "", terminal=True)
			return
		
		# Movement and control commands
		if low == "/forward_speed" or low.startswith("/forward_speed "):
			if len(line.split()) > 1:
				commands.forward_speed(player, line.split(None,1)[1], terminal=True)
			else:
				commands.forward_speed(player, "", terminal=True)
			return
		if low == "/custom_pitch" or low.startswith("/custom_pitch "):
			if len(line.split()) > 1:
				commands.custom_pitch(player, line.split(None,1)[1], terminal=True)
			else:
				commands.custom_pitch(player, "", terminal=True)
			return
		if low == "/custom_yaw" or low.startswith("/custom_yaw "):
			if len(line.split()) > 1:
				commands.custom_yaw(player, line.split(None,1)[1], terminal=True)
			else:
				commands.custom_yaw(player, "", terminal=True)
			return
		if low == "/custom_roll" or low.startswith("/custom_roll "):
			if len(line.split()) > 1:
				commands.custom_roll(player, line.split(None,1)[1], terminal=True)
			else:
				commands.custom_roll(player, "", terminal=True)
			return
		if low == "/pitch_speed" or low.startswith("/pitch_speed "):
			if len(line.split()) > 1:
				commands.pitch_speed(player, line.split(None,1)[1], terminal=True)
			else:
				commands.pitch_speed(player, "", terminal=True)
			return
		if low == "/yaw_speed" or low.startswith("/yaw_speed "):
			if len(line.split()) > 1:
				commands.yaw_speed(player, line.split(None,1)[1], terminal=True)
			else:
				commands.yaw_speed(player, "", terminal=True)
			return
		if low == "/roll_speed" or low.startswith("/roll_speed "):
			if len(line.split()) > 1:
				commands.roll_speed(player, line.split(None,1)[1], terminal=True)
			else:
				commands.roll_speed(player, "", terminal=True)
			return
		
		# GPT and chat settings
		if low == "/base_delay" or low.startswith("/base_delay "):
			if len(line.split()) > 1:
				commands.base_delay(player, line.split(None,1)[1], terminal=True)
			else:
				commands.base_delay(player, "", terminal=True)
			return
		if low == "/scaled_delay" or low.startswith("/scaled_delay "):
			if len(line.split()) > 1:
				commands.scaled_delay(player, line.split(None,1)[1], terminal=True)
			else:
				commands.scaled_delay(player, "", terminal=True)
			return
		
		# FPS command
		if low == "/fps" or low.startswith("/fps "):
			if len(line.split()) > 1:
				commands.fps(player, line.split(None,1)[1], terminal=True)
			else:
				commands.fps(player, "", terminal=True)
			return
		


		if low == "/rconpass" or low.startswith("/rconpass "):
			pwd = line.split(None,1)[1]
			self.rcon_password = pwd  # backward compatible fallback
			try:
				ip = player.endpoint.ip
				port = player.endpoint.port
				self._set_rcon_password_for(ip, port, pwd)
				print(f"RCON password saved for {ip}:{port}")
			except Exception:
				print("RCON password updated")
			return
		
		if low == "/audionotify" or low.startswith("/audionotify "):
			parts = low.split()
			if len(parts) == 1:
				current = bool(self._get_config_value("audio_notify", True))
				new_val = not current
			else:
				arg = parts[1].lower()
				if arg in ("on", "1", "true", "yes"):
					new_val = True
				elif arg in ("off", "0", "false", "no"):
					new_val = False
				else:
					print("Usage: /audionotify [on|off]")
					return
			self._set_config_value("audio_notify", bool(new_val))
			try:
				self.chat_ui.set_sound_enabled(bool(new_val))
			except Exception:
				pass
			print(f"Audio notifications {'enabled' if new_val else 'disabled'}")
			return
		# 0 Argument commands
		if low == "/reconnect":
			commands.reconnect(player, "", terminal=True)
			return
		if low == "/quit":
			commands.quit(player, "", terminal=True)
			return
		if low == "/shoot180":
			commands.shoot180(player, "", terminal=True)
			return
		if low == "/kill":
			commands.kill(player, "", terminal=True)
			return
		if low == "/stop":
			commands.stop(player, "", terminal=True)
			return
		if low == "/test":
			commands.test(player, "", terminal=True)
			return
		
		# Commands that can be called without arguments to show current values
		if low == "/forward_speed":
			commands.forward_speed(player, "", terminal=True)
			return
		if low == "/custom_pitch":
			commands.custom_pitch(player, "", terminal=True)
			return
		if low == "/custom_yaw":
			commands.custom_yaw(player, "", terminal=True)
			return
		if low == "/custom_roll":
			commands.custom_roll(player, "", terminal=True)
			return
		if low == "/pitch_speed":
			commands.pitch_speed(player, "", terminal=True)
			return
		if low == "/yaw_speed":
			commands.yaw_speed(player, "", terminal=True)
			return
		if low == "/roll_speed":
			commands.roll_speed(player, "", terminal=True)
			return
		if low == "/base_delay":
			commands.base_delay(player, "", terminal=True)
			return
		if low == "/scaled_delay":
			commands.scaled_delay(player, "", terminal=True)
			return
		if low == "/team":
			commands.team_red_blue(player, "", terminal=True)
			return
		if low == "/spectator":
			commands.spectator(player, "", terminal=True)
			return
		if low == "/name":
			commands.name(player, "", terminal=True)
			return
		if low == "/skin":
			commands.skin(player, "", terminal=True)
			return
		if low == "/predicting":
			commands.predicting(player, "", terminal=True)
			return
		if low == "/speed_boost":
			commands.speed_boost(player, "", terminal=True)
			return

		if low == "/gamepad_status":
			commands.gamepad_status(player, "", terminal=True)
			return

		if low == "/gamepad_reinit":
			commands.gamepad_reinit(player, "", terminal=True)
			return

		if low == "/gamepad_debug" or low.startswith("/gamepad_debug "):
			commands.gamepad_debug(player, line.split(None, 1)[1] if len(line.split()) > 1 else "", terminal=True)
			return

		if low == "/chat":
			try:
				if self.chat_ui.is_visible():
					self.chat_ui.hide()
				else:
					self.chat_ui.show()
			except Exception:
				pass
			return
		if low == "/skins":
			base = self.get_playerskins_base() or CS_PLAYERSKINS
			for slot in range(CS_MAXCLIENTS):
				idx = base + slot
				ci = self.configstrings.get(idx)
				if ci:
					print(f"[{slot}] {ci}")
			return
		
		if low == "/rconwin":
			self._toggle_rcon_window()
			return
		if low.startswith("/rcon "):
			cmd = line.split(None,1)[1]
			self._send_rcon(cmd)
			return

		if not low.startswith("/"):
			# default: treat as GPT content
			GPT.interact(line, player)

	def set_slot_name(self, slot_id: int, name: str):
		self.slot_to_name[int(slot_id)] = name

	def get_slot_name(self, slot_id: int):
		return self.slot_to_name.get(int(slot_id))
				
	def process_user_input(self):
		# Implement your logic for processing user input here
		while True:
			user_input = input()
			self.user_input_queue.put(user_input)

	def beginLoop(self,clock):
		print("Starting sof-gpt...")

		# Start GUI chat window
		self.chat_ui.start()

		# Start a separate thread for terminal commands
		input_thread = threading.Thread(target=self.process_user_input, name="TerminalInputThread")
		input_thread.daemon = True
		input_thread.start()

		while True:
			self.framecount += 1

			#interacts with sof server
			self.talkToWorld()

			now = time.time()
			fps = self.framecount / (now-self.main_begin)

			# every 10 seconds
			if (self.framecount % (self.target_fps * 10)) == 0:
				num_eps = len(self.endpoints)
				num_players = len([ self.endpoints[e] for e in self.endpoints for p in self.endpoints[e].players ])

				# print(f"STATS: { num_eps } endpoints. With { len( [ self.endpoints[e] for e in self.endpoints for p in self.endpoints[e].players if p.conn.connected == 2 ])} connected players" )

				if num_players == 0:
					sys.exit(0)
				# print(f"fps is {fps}")

			"""
			# ----sleep----
			exec_time = time.time() - self.before_cpu
			# too fast? sleep some
			if exec_time < self.float_sleep:
				time.sleep(self.float_sleep-exec_time)

			self.before_cpu = time.time()
			"""
			# clock.tick(self.target_fps)
			clock.tick_busy_loop(math.floor(self.target_fps))
