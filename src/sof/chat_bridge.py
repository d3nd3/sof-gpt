from gpt.ask_question import libVersion as gpt_ask

from functools import partial

from sof.packets.defines import *
from sof.packets.types import *

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
		p.uc_now.buttonsPressed |= BUTTON_ACTION
	def minus_use(p, data):
		p.uc_now.buttonsPressed &= ~BUTTON_ACTION

	def weaponselect(p, data):
		weaponID = int(data)
		p.conn.append_string_to_reliable(f"{CLC_STRINGCMD}weaponselect {weaponID}\x00")
	# SETTINGS
	# -----------------------------------------------------------------------
	def base_delay(p, data):
		if not len(data):
			util.say(p, f"base_delay is {p.main.gpt['base_delay']}")
			return
		delay = int(data)
		if delay >= 0 and delay <= 100:
			p.main.gpt["base_delay"] = delay
			util.say(p,f"base_delay is now {delay}")

	def scaled_delay(p, data):
		if not len(data):
			util.say(p, f"scaled_delay is {p.main.gpt['scaled_delay']}")
			return
		delay = int(data)
		if delay >= 0 and delay <= 100:
			p.main.gpt["scaled_delay"] = delay
			util.say(p,f"scaled_delay is now {delay}")

	def forward_speed(p, data):
		if not len(data):
			util.say(p, f"forward_speed is {p.uc_now.forwardSpeed}")
			return
		update = int(data)
		p.uc_now.forwardSpeed = update
		util.say(p,f"forward_speed is now {update}")

	def custom_pitch(p,data):
		p.custom_pitch = int(data)
		util.say(p,f"custom_pitch is now {p.custom_pitch}")

	def custom_yaw(p,data):
		p.custom_yaw = int(data)
		util.say(p,f"custom_yaw is now {p.custom_yaw}")

	def custom_roll(p,data):
		p.custom_roll = int(data)
		util.say(p,f"custom_roll is now {p.custom_roll}")

	def pitch_speed(p,data):
		if not len(data):
			util.say(p, f"pitch_speed is {p.pitch_speed}")
			return

		p.pitch_speed = int(data)
		util.say(p,f"pitch_speed is now {p.pitch_speed}")

	def yaw_speed(p,data):
		if not len(data):
			util.say(p, f"yaw_speed is {p.yaw_speed}")
			return
		p.yaw_speed = int(data)
		util.say(p,f"yaw_speed is now {p.yaw_speed}")

	def roll_speed(p,data):
		if not len(data):
			util.say(p, f"roll_speed is {p.roll_speed}")
			return

		p.roll_speed = int(data)
		util.say(p,f"roll_speed is now {p.roll_speed}")
		
	def skin(p, data):
		if not len(data):
			util.say(p, f"skin is {p.userinfo['skin']}")
			return
		p.userinfo["skin"] = data
		util.say(p,f"skin is now {data}")

	# Server does not allow you to set predicting 1 after connection
	# But does allow you to turn it off
	def predicting(p, data):
		if not len(data):
			util.say(p, f"predicting is {p.isPredicting}")
			return
		predicting = int(data)
		if predicting == 0 or predicting == 1:
			p.setPredicting(predicting)
			util.say( p ,  f"predicting is now {p.isPredicting}" )

			GPT_COMMANDS.reconnect(p,data)

	def spectator(p,data):
		if not len(data):
			util.say(p, f"spectator is {p.userinfo['spectator']}")
			return
		p.userinfo["spectator"] = data
		util.say(p,f"spectator is now {data}")

	def cl_run(p, data):
		if not len(data):
			util.say(p, f"cl_run is {p.isPredicting}")
			return
		cl_run = int(data)
		if cl_rum == 0 or cl_run == 1:
			p.input.isRunning = cl_run
			util.say( p ,  f"cl_run is now {p.isRunning}" )


	# COMMANDS
	# -----------------------------------------------------------------------
	def stop(p, data):
		p.main.gpt["chunks"] = []

	def reconnect(p,data):
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.init = False

	def kill(p, data):
		p.conn.append_string_to_reliable(f"{CLC_STRINGCMD}kill\x00")

	def test(p, data):
		util.say(p,"test")

	def quit(p,data):
		util.say(p,f"Goodbye!")
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))

		# Remove self from endpoint
		p.endpoint.removePlayer(p)

		# Player is forgotten about now?


sof_chat_inputs = {
	# angles
	"+rollright": (lambda p, data: GPT_COMMANDS.plus_rollright(p, data)),
	"-rollright": (lambda p, data: GPT_COMMANDS.minus_rollright(p, data)),
	"+rollleft": (lambda p, data: GPT_COMMANDS.plus_rollleft(p, data)),
	"-rollleft": (lambda p, data: GPT_COMMANDS.minus_rollleft(p, data)),

	"+lookup": (lambda p, data: GPT_COMMANDS.plus_lookup(p, data)),
	"-lookup": (lambda p, data: GPT_COMMANDS.minus_lookup(p, data)),
	"+lookdown": (lambda p, data: GPT_COMMANDS.plus_lookdown(p, data)),
	"-lookdown": (lambda p, data: GPT_COMMANDS.minus_lookdown(p, data)),

	"+right": (lambda p, data: GPT_COMMANDS.plus_right(p, data)),
	"-right": (lambda p, data: GPT_COMMANDS.minus_right(p, data)),
	"+left": (lambda p, data: GPT_COMMANDS.plus_left(p, data)),
	"-left": (lambda p, data: GPT_COMMANDS.minus_left(p, data)),

	# movement
	"+forward": (lambda p, data: GPT_COMMANDS.plus_forward(p, data)),
	"-forward": (lambda p, data: GPT_COMMANDS.minus_forward(p, data)),
	"+back": (lambda p, data: GPT_COMMANDS.plus_back(p, data)),
	"-back": (lambda p, data: GPT_COMMANDS.minus_back(p, data)),

	"+moveright": (lambda p, data: GPT_COMMANDS.plus_moveright(p, data)),
	"-moveright": (lambda p, data: GPT_COMMANDS.minus_moveright(p, data)),
	"+moveleft": (lambda p, data: GPT_COMMANDS.plus_moveleft(p, data)),
	"-moveleft": (lambda p, data: GPT_COMMANDS.minus_moveleft(p, data)),

	"+moveup": (lambda p, data: GPT_COMMANDS.plus_moveup(p, data)),
	"-moveup": (lambda p, data: GPT_COMMANDS.minus_moveup(p, data)),
	"+movedown": (lambda p, data: GPT_COMMANDS.plus_movedown(p, data)),
	"-movedown": (lambda p, data: GPT_COMMANDS.minus_movedown(p, data)),

	"+leanleft": (lambda p, data: GPT_COMMANDS.plus_leanleft(p, data)),
	"-leanleft": (lambda p, data: GPT_COMMANDS.minus_leanleft(p, data)),
	"+leanright": (lambda p, data: GPT_COMMANDS.plus_leanright(p, data)),
	"-leanright": (lambda p, data: GPT_COMMANDS.minus_leanright(p, data)),

	# interactions
	"+attack": (lambda p, data: GPT_COMMANDS.plus_attack(p, data)),
	"-attack": (lambda p, data: GPT_COMMANDS.minus_attack(p, data)),
	"+altattack": (lambda p, data: GPT_COMMANDS.plus_altattack(p, data)),
	"-altattack": (lambda p, data: GPT_COMMANDS.minus_altattack(p, data)),
	"+use": (lambda p, data: GPT_COMMANDS.plus_use(p, data)),
	"-use": (lambda p, data: GPT_COMMANDS.minus_use(p, data)),

	"weaponselect": (lambda p, data: GPT_COMMANDS.weaponselect(p, data))
}

sof_chat_commands = {
	"test": (lambda p, data: GPT_COMMANDS.test(p, data)),
	"kill": (lambda p, data: GPT_COMMANDS.kill(p, data)),
	"reconnect": (lambda p, data: GPT_COMMANDS.reconnect(p, data)),
	"stop": (lambda p, data: GPT_COMMANDS.stop(p, data)),
	"quit": (lambda p, data: GPT_COMMANDS.quit(p, data)),
}

sof_chat_settings = {
	# settings
	"base_delay": (lambda p, data: GPT_COMMANDS.base_delay(p, data)),
	"scaled_delay": (lambda p, data: GPT_COMMANDS.scaled_delay(p, data)),

	"spectator": (lambda p, data: GPT_COMMANDS.spectator(p, data)),
	"skin": (lambda p, data: GPT_COMMANDS.skin(p, data)),
	"predicting": (lambda p, data: GPT_COMMANDS.predicting(p, data)),

	"forward_speed": (lambda p, data: GPT_COMMANDS.forward_speed(p, data)),

	"custom_pitch": (lambda p, data: GPT_COMMANDS.custom_pitch(p, data)),
	"custom_yaw": (lambda p, data: GPT_COMMANDS.custom_yaw(p, data)),
	"custom_roll": (lambda p, data: GPT_COMMANDS.custom_roll(p, data)),

	"pitch_speed": (lambda p, data: GPT_COMMANDS.pitch_speed(p, data)),
	"yaw_speed": (lambda p, data: GPT_COMMANDS.yaw_speed(p, data)),
	"roll_speed": (lambda p, data: GPT_COMMANDS.roll_speed(p, data)),
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
				

			util.changeTextColor(player,color)
			conn.append_string_to_reliable(f"\x04say {chunks[0]}\x00")
	
			len_prev = len(chunks[0])
			if len(chunks) == 1:
				# cleanup
				util.changeTextColor(player,player.textColor)
				chunks = []
				len_prev = 0
			else:
				chunks = chunks[1:]

		main.gpt["chunk_len_prev"] = len_prev
		main.gpt["chunks"] = chunks
