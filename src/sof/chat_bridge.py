from gpt.ask_question import libVersion as gpt_ask

from functools import partial

from sof.packets.defines import *
from sof.packets.types import *

import util
import time
import sys


class GPT_COMMANDS:
	
	# ROLL
	def plus_rollleft(p, data):
		p.uc_now.rollLeft = True
	def minus_rollleft(p, data):
		p.uc_now.rollLeft = False

	def plus_rollright(p, data):
		p.uc_now.rollRight = True
	def minus_rollright(p, data):
		p.uc_now.rollRight = False

	# PITCH
	def plus_lookup(p, data):
		p.uc_now.lookUp = True
	def minus_lookup(p, data):
		p.uc_now.lookUp = False

	def plus_lookdown(p, data):
		p.uc_now.lookDown = True
	def minus_lookdown(p, data):
		p.uc_now.lookDown = False

	# YAW
	def plus_left(p, data):
		p.uc_now.lookLeft = True
	def minus_left(p, data):
		p.uc_now.lookLeft = False

	def plus_right(p, data):
		p.uc_now.lookRight = True
	def minus_right(p, data):
		p.uc_now.lookRight = False


	# FORWARD
	def plus_forward(p, data):
		p.uc_now.moveForward = True
	def minus_forward(p, data):
		p.uc_now.moveForward = False
	def plus_back(p, data):
		p.uc_now.moveBack = True
	def minus_back(p, data):
		p.uc_now.moveBack = False

	# SIDEWAYS
	def plus_moveright(p, data):
		p.uc_now.moveRight = True
	def minus_moveright(p, data):
		p.uc_now.moveRight = False
	def plus_moveleft(p, data):
		p.uc_now.moveLeft = True
	def minus_moveleft(p, data):
		p.uc_now.moveLeft = False

	# JUMP/CROUCH
	def plus_moveup(p, data):
		p.uc_now.moveUp = True
	def minus_moveup(p, data):
		p.uc_now.moveUp = False
	def plus_moveup(p, data):
		p.uc_now.moveDown = True
	def minus_moveup(p, data):
		p.uc_now.moveDown = False


	# OTHER
	def plus_attack(p, data):
		p.uc_now.buttonsPressed |= BUTTON_ATTACK
	def minus_attack(p, data):
		p.uc_now.buttonsPressed &= ~BUTTON_ATTACK

	def plus_altattack(p, data):
		p.uc_now.buttonsPressed |= BUTTON_ALTATTACK
	def minus_altattack(p, data):
		p.uc_now.buttonsPressed &= ~BUTTON_ALTATTACK

	def plus_use(p, data):
		p.uc_now.buttonsPressed |= BUTTON_ACTION
	def minus_use(p, data):
		p.uc_now.buttonsPressed &= ~BUTTON_ACTION

	# SETTINGS
	def base_delay(p, data):
		delay = int(data)
		if delay >= 0 and delay <= 100:
			p.main.gpt["base_delay"] = delay
			util.say(p,f"base_delay is now {delay}")

	def scaled_delay(p, data):
		delay = int(data)
		if delay >= 0 and delay <= 100:
			p.main.gpt["scaled_delay"] = delay
			util.say(p,f"scaled_delay is now {delay}")

	def forward_speed(p, data):
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
		p.pitch_speed = int(data)
		util.say(p,f"pitch_speed is now {p.pitch_speed}")

	def yaw_speed(p,data):
		p.yaw_speed = int(data)
		util.say(p,f"yaw_speed is now {p.yaw_speed}")

	def roll_speed(p,data):
		p.roll_speed = int(data)
		util.say(p,f"roll_speed is now {p.roll_speed}")
		
	def skin(p, data):
		p.userinfo["skin"] = data
		util.say(p,f"skin is now {data}")

	# COMMANDS
	def stop(p, data):
		p.main.gpt["chunks"] = []

	def kill(p, data):
		util.say(p,"kill")

	def test(p, data):
		util.say(p,"test")
		p.uc_now.fireEvent = True

	def quit(p,data):
		util.say(p,f"Goodbye!")
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		p.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		sys.exit(0)


gpt_commands = {
	
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

	# other
	
	"+attack": (lambda p, data: GPT_COMMANDS.plus_attack(p, data)),
	"-attack": (lambda p, data: GPT_COMMANDS.minus_attack(p, data)),
	"+altattack": (lambda p, data: GPT_COMMANDS.plus_altattack(p, data)),
	"-altattack": (lambda p, data: GPT_COMMANDS.minus_altattack(p, data)),
	"+use": (lambda p, data: GPT_COMMANDS.plus_use(p, data)),
	"-use": (lambda p, data: GPT_COMMANDS.minus_use(p, data)),

	# settings
	"base_delay": (lambda p, data: GPT_COMMANDS.base_delay(p, data)),
	"scaled_delay": (lambda p, data: GPT_COMMANDS.scaled_delay(p, data)),

	"forward_speed": (lambda p, data: GPT_COMMANDS.forward_speed(p, data)),

	"custom_pitch": (lambda p, data: GPT_COMMANDS.custom_pitch(p, data)),
	"custom_yaw": (lambda p, data: GPT_COMMANDS.custom_yaw(p, data)),
	"custom_roll": (lambda p, data: GPT_COMMANDS.custom_roll(p, data)),

	"pitch_speed": (lambda p, data: GPT_COMMANDS.pitch_speed(p, data)),
	"yaw_speed": (lambda p, data: GPT_COMMANDS.yaw_speed(p, data)),
	"roll_speed": (lambda p, data: GPT_COMMANDS.roll_speed(p, data)),


	#commands
	"test": (lambda p, data: GPT_COMMANDS.test(p, data)),
	"kill": (lambda p, data: GPT_COMMANDS.kill(p, data)),
	"skin": (lambda p, data: GPT_COMMANDS.skin(p, data)),
	"stop": (lambda p, data: GPT_COMMANDS.stop(p, data)),
	# "quit": (lambda p, data: GPT_COMMANDS.quit(p, data)),
}

def interact(msg,player):
	main = player.main
	if msg.startswith("["):
		end = msg.find("]")
		# util.pretty_dump(msg.encode('latin_1'))
		if end > 0:
			cmd = msg[1:end]
			print(f"{cmd} command")
			if cmd in gpt_commands:
				gpt_commands[cmd](player,msg[end+1:])
	elif not len(main.gpt["chunks"]):
		# not in a request?lets go
		pass
		# answer = gpt_ask(msg,main.talkToWorld)
		# generate_chunks_gpt(main,answer)


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
				color = main.gpt["toggle_color_1"]
			else:
				color = main.gpt["toggle_color_2"]

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
