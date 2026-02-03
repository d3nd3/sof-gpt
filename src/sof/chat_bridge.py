from gpt.ask_question import libVersion as gpt_ask

from functools import partial

from sof.packets.defines import *
from sof.packets.types import *
from sof.commands import commands

import util
import time
import sys


class GPT_COMMANDS:
	
	# INPUT
	# -----------------------------------------------------------------------
	# ROLL
	def plus_rollleft(p, data):
		p.input.rollLeft = True
	def minus_rollleft(p, data):
		p.input.rollLeft = False

	def plus_rollright(p, data):
		p.input.rollRight = True
	def minus_rollright(p, data):
		p.input.rollRight = False

	# PITCH
	def plus_lookup(p, data):
		p.input.lookUp = True
	def minus_lookup(p, data):
		p.input.lookUp = False

	def plus_lookdown(p, data):
		p.input.lookDown = True
	def minus_lookdown(p, data):
		p.input.lookDown = False

	# YAW
	def plus_left(p, data):
		p.input.lookLeft = True
	def minus_left(p, data):
		p.input.lookLeft = False

	def plus_right(p, data):
		p.input.lookRight = True
	def minus_right(p, data):
		p.input.lookRight = False


	# FORWARD
	def plus_forward(p, data):
		p.input.moveForward = True
	def minus_forward(p, data):
		p.input.moveForward = False
	def plus_back(p, data):
		p.input.moveBack = True
	def minus_back(p, data):
		p.input.moveBack = False

	# SIDEWAYS
	def plus_moveright(p, data):
		p.input.moveRight = True
	def minus_moveright(p, data):
		p.input.moveRight = False
	def plus_moveleft(p, data):
		p.input.moveLeft = True
	def minus_moveleft(p, data):
		p.input.moveLeft = False

	# JUMP/CROUCH
	def plus_moveup(p, data):
		p.input.moveUp = True
	def minus_moveup(p, data):
		p.input.moveUp = False
	def plus_movedown(p, data):
		p.input.moveDown = True
	def minus_movedown(p, data):
		p.input.moveDown = False

	def plus_leanleft(p, data):
		p.input.leanLeft = True
	def minus_leanleft(p, data):
		p.input.leanLeft = False
	def plus_leanright(p, data):
		p.input.leanRight = True
	def minus_leanright(p, data):
		p.input.leanRight = False

	# OTHER
	def plus_attack(p, data):
		p.input.fire = True
	def minus_attack(p, data):
		p.input.fire = False

	def plus_altattack(p, data):
		p.input.altfire = True
	def minus_altattack(p, data):
		p.input.altfire = False

	def plus_use(p, data):
		p.input.use = True
	def minus_use(p, data):
		p.input.use = False

	def weaponselect(p, data):
		commands.weaponselect(p, data)
	# SETTINGS
	# -----------------------------------------------------------------------

	# Chat-Gpt parsing settings
	def base_delay(p, data):
		commands.base_delay(p, data)

	def scaled_delay(p, data):
		commands.scaled_delay(p, data)

	def forward_speed(p, data):
		commands.forward_speed(p, data)

	def custom_pitch(p,data):
		commands.custom_pitch(p, data)

	def custom_yaw(p,data):
		commands.custom_yaw(p, data)

	def custom_roll(p,data):
		commands.custom_roll(p, data)

	def pitch_speed(p,data):
		commands.pitch_speed(p, data)

	def yaw_speed(p,data):
		commands.yaw_speed(p, data)

	def roll_speed(p,data):
		commands.roll_speed(p, data)

	def speed_boost(p,data):
		commands.speed_boost(p, data)
		
	def skin(p, data):
		commands.skin(p, data)

	def name(p, data):
		commands.name(p, data)

	# Server does not allow you to set predicting 1 after connection
	# But does allow you to turn it off
	def predicting(p, data):
		commands.predicting(p, data)

	def spectator(p,data):
		commands.spectator(p, data)

	def team_red_blue(p,data):
		commands.team_red_blue(p, data)

	def cl_run(p, data):
		if not len(data):
			util.say(p, f"cl_run is {p.isPredicting}")
			return
		cl_run = int(data)
		if cl_run == 0 or cl_run == 1:
			p.isRunning = cl_run
			util.say( p ,  f"cl_run is now {p.isRunning}" )

	def shoot180(p,data):
		commands.shoot180(p, data)



	# COMMANDS
	# -----------------------------------------------------------------------
	def stop(p, data):
		commands.stop(p, data)

	def reconnect(p,data):
		commands.reconnect(p, data)

	def kill(p, data):
		commands.kill(p, data)

	def test(p, data):
		commands.test(p, data)

	def quit(p,data):
		commands.quit(p, data)

	def help(p, data):
		commands.help(p, data)


sof_chat_inputs = {
	# angles
	"+rollright": GPT_COMMANDS.plus_rollright,
	"-rollright": GPT_COMMANDS.minus_rollright,
	"+rollleft": GPT_COMMANDS.plus_rollleft,
	"-rollleft": GPT_COMMANDS.minus_rollleft,

	"+lookup": GPT_COMMANDS.plus_lookup,
	"-lookup": GPT_COMMANDS.minus_lookup,
	"+lookdown": GPT_COMMANDS.plus_lookdown,
	"-lookdown": GPT_COMMANDS.minus_lookdown,

	"+right": GPT_COMMANDS.plus_right,
	"-right": GPT_COMMANDS.minus_right,
	"+left": GPT_COMMANDS.plus_left,
	"-left": GPT_COMMANDS.minus_left,

	# movement
	"+forward": GPT_COMMANDS.plus_forward,
	"-forward": GPT_COMMANDS.minus_forward,
	"+back": GPT_COMMANDS.plus_back,
	"-back": GPT_COMMANDS.minus_back,

	"+moveright": GPT_COMMANDS.plus_moveright,
	"-moveright": GPT_COMMANDS.minus_moveright,
	"+moveleft": GPT_COMMANDS.plus_moveleft,
	"-moveleft": GPT_COMMANDS.minus_moveleft,

	"+moveup": GPT_COMMANDS.plus_moveup,
	"-moveup": GPT_COMMANDS.minus_moveup,
	"+movedown": GPT_COMMANDS.plus_movedown,
	"-movedown": GPT_COMMANDS.minus_movedown,

	"+leanleft": GPT_COMMANDS.plus_leanleft,
	"-leanleft": GPT_COMMANDS.minus_leanleft,
	"+leanright": GPT_COMMANDS.plus_leanright,
	"-leanright": GPT_COMMANDS.minus_leanright,

	# interactions
	"+attack": GPT_COMMANDS.plus_attack,
	"-attack": GPT_COMMANDS.minus_attack,
	"+altattack": GPT_COMMANDS.plus_altattack,
	"-altattack": GPT_COMMANDS.minus_altattack,
	"+use": GPT_COMMANDS.plus_use,
	"-use": GPT_COMMANDS.minus_use,

	"weaponselect": GPT_COMMANDS.weaponselect
}

sof_chat_commands = {
	"test": commands.test,
	"kill": commands.kill,
	"reconnect": commands.reconnect,
	"stop": commands.stop,
	"quit": commands.quit,
	"team": commands.team_red_blue,
	"spectator": commands.spectator,
	"name": commands.name,
	"skin": commands.skin,
	"predicting": commands.predicting,
	"help": commands.help,
	"gamepad_status": commands.gamepad_status,
	"gamepad_reinit": commands.gamepad_reinit,
	"gamepad_debug": commands.gamepad_debug,
	"toggle_rumble": commands.toggle_rumble,
	"start_rumble": commands.start_rumble,
	"stop_rumble": commands.stop_rumble,
	"set_rumble_intensity": commands.set_rumble_intensity,
	"get_rumble_status": commands.get_rumble_status,
	"fps": commands.fps,
	"weaponselect": commands.weaponselect,
	"weapon": commands.weaponselect,  # Alias for weaponselect
}

sof_chat_settings = {
	# settings

	# chat-gpt output settings
	"base_delay": commands.base_delay,
	"scaled_delay": commands.scaled_delay,

	"spectator": commands.spectator,
	"skin": commands.skin,
	"name": commands.name,
	"predicting": commands.predicting,
	"team_red_blue": commands.team_red_blue,

	"forward_speed": commands.forward_speed,

	"custom_pitch": commands.custom_pitch,
	"custom_yaw": commands.custom_yaw,
	"custom_roll": commands.custom_roll,

	"pitch_speed": commands.pitch_speed,
	"yaw_speed": commands.yaw_speed,
	"roll_speed": commands.roll_speed,

	"speed_boost": commands.speed_boost,

	"shoot180": commands.shoot180,
}

def interact(msg,player):
	main = player.main
	# util.pretty_dump(msg.encode('latin_1'))
	if msg.startswith("["):
		end = msg.find("]")
		if end > 0:
			cmd = msg[1:end]
			print(f"{cmd} command")
			if cmd in sof_chat_inputs:
				sof_chat_inputs[cmd](player,msg[end+1:])
			elif cmd in sof_chat_commands:
				sof_chat_commands[cmd](player,msg[end+1:])
			elif cmd in sof_chat_settings:
				sof_chat_settings[cmd](player,msg[end+1:])
	elif not main.gpt["active"] and not len(main.gpt["chunks"]):
		main.gpt["active"] = True
		# not in a request?lets go
		# pass
		# RECURSION???
		print("Summoning the genie...")
		# Calling talkToWorld here is allowing another instance into here.
		answer = gpt_ask(msg,main.talkToWorld)
		generate_chunks_gpt(main,answer)
		main.gpt["active"] = False


# split the gpt response into chunks that fit nicely into sof say
def generate_chunks_gpt(main,response):
	chunks = main.gpt["chunks"]
	main.gpt["say_timestamp"] = time.time()
	flood_msgs = 4
	flood_persecond = 1
	max_chunk_size = 150

	# Split the message by words and newlines
	segments = response.split('\n')
	
	for segment in segments:
		words = segment.split()
		chunk = ''
		for word in words:
			if len(chunk) + len(word) + 1 <= max_chunk_size:
				if chunk:
					chunk += ' '
				chunk += word
			else:
				chunks.append(chunk)
				chunk = word
		if chunk:
			chunks.append(chunk)


	# for i in range(len(chunks) - 1):
	# 	chunks[i] += '\n'

	main.gpt["chunks"] = chunks

	# print(f"finished generating chunks : {len(main.gpt["chunks"])}")

len_prev=0
# Prints one lines of gpt text , and removes it from list.
# len_prev is used to scale the timer so that it is longer for larger text length
# called by main loop for the endpoint/player which requested the gpt.
def output_gpt(main,player,conn):

	len_prev = main.gpt["chunk_len_prev"]
	chunks = main.gpt["chunks"]

	base_delay = main.gpt["base_delay"]
	scaled_delay = main.gpt["scaled_delay"]

	# larger delay if the text length is larger because takes time to read
	if len(chunks):
		if not len_prev :
			len_prev = 0
		if time.time() - main.gpt["say_timestamp"] > base_delay+scaled_delay*len_prev/150:
			main.gpt["say_timestamp"] = time.time()

			main.gpt["toggle_color"] = not main.gpt["toggle_color"]
			if main.gpt["toggle_color"]:
				color = main.gpt["toggle_color_2"]
			else:
				color = main.gpt["toggle_color_1"]
				
			# this has a delayed effect because userinfo is appended last.
			# thus you are specifying color for next message
			util.changeTextColor(player,color)
			conn.append_string_to_reliable(f"\x04say {chunks[0]}\x00")
	
			len_prev = len(chunks[0])
			if len(chunks) == 1:
				# cleanup
				# restores original text color, necessary?
				# util.changeTextColor(player,player.textColor)
				chunks = []
				len_prev = 0
			else:
				chunks = chunks[1:]

		main.gpt["chunk_len_prev"] = len_prev
		main.gpt["chunks"] = chunks
