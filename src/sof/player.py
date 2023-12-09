import time
import copy
import struct

from sof.packets.raw import COM_BlockSequenceCRCByte,completeUserCommandBitBuffer

from sof.connection import Connection

import sof.packets.types as types

from sof.packets.defines import *

from sof.keys import getJoystick

import util

class UserCmd:
	def __init__(self,msec):
		self.forwardspeed = 0
		self.upspeed = 0
		self.sidespeed = 0

		self.lean = 0

		self.buttonsPressed = 0
		self.fireEvent = 0.0
		self.altFireEvent = 0.0

		self.msec = msec
		self.lightLevel = 0
		# angles
		self.pitch = 0
		self.roll = 0
		self.yaw = 0
		


"""
typedef struct usercmd_s
{
	byte	msec;
	byte	buttons;
	byte	lightlevel;		// light level the player is standing on
	char	lean;			// -1 or 1
	short	angles[3];
	short	forwardmove;
	short	sidemove;
	short	upmove;
	float	fireEvent;
	float	altfireEvent;
} usercmd_t;
"""
class UserInput:
	def __init__(self):
		# roll
		self.rollRight = False
		self.rollLeft = False

		# pitch
		self.lookUp = False
		self.lookDown = False

		# yaw
		self.lookRight = False
		self.lookLeft = False

		# movement
		self.moveBack = False
		self.moveForward = False

		self.moveUp = False
		self.moveDown = False

		self.moveLeft = False
		self.moveRight = False

		self.fire = False
		self.altfire = False

		self.leanRight = False
		self.leanLeft = False

		self.rightJoystickSensX = 1
		self.rightJoystickSensY = 1

		self.leftJoystickSensX = 1
		self.rightJoystickSensY = 1

		self.use = False


# This now represents everything
# The Connection is only related because of having hostname/port
class Player:
	def __init__(self,main,endpoint,userinfo,name):
		self.main = main
		self.map = ""
		self.mapname = ""
		self.playernum = -1
		self.precache = ""
		self.timestamp_connected = 0
		self.timestamp_start = 0
		self.lastServerFrame = -1
		self.wasConnected = 0
		self.name = name
		self.init = False
		self.endpoint = endpoint

		# 9999 special value to say, don't use custom pitch
		self.custom_pitch = 9999
		self.custom_yaw = 9999
		self.custom_roll = 9999

		self.pitch_speed = 250
		self.yaw_speed = 2050
		self.roll_speed = 250

		self.delta_pitch = 0
		self.delta_yaw = 0
		self.delta_roll = 0

		self.forward_speed = 100

		self.isRunning = True
		if userinfo["predicting"] == "1":
			self.isPredicting = True
		else:
			self.isPredicting = False

		self.uc_null = UserCmd(0)
		# Internal to firing mechanics
		self.internal_allowed_to_fire = 2
		self.internal_allowed_to_fire_basic = True
		self.internal_allowed_to_fire_timer = time.time()
		self.internal_allowed_to_fire2 = True

		# userinfo dict creation
		# use player.make_userinfo to return the slash seperated string form.

		# name should start out color-less.
		userinfo["name"] = name + main.gpt["toggle_color_1"]
		self.userinfo = userinfo
		self.past_userinfo = self.userinfo.copy()

		self.health = 100
		self.armor = 0

		self.prev_health = self.health
		self.prev_armor = self.armor


	def initialize(self):
		self.init = True

		self.reinit_usercmd()

		self.conn = Connection(self,self.endpoint.ip,self.endpoint.port)
		self.timestamp_start = time.time()

		# these continually send/recv (fake_block)
		# should timeout this.

		if not self.conn.get_challenge(self.timestamp_start):
			return False
		if not self.conn.connect(self.timestamp_start):
			return False

		self.conn.out_seq = 0
		self.conn.in_seq = 0
		self.conn.reliable_s = 1
		self.conn.new()

		return True

	# soft cleaning of inputs values
	def reinit_usercmd(self):
		self.viewangles = [0,0,0]

		# this resets predicting which is a userinfo essentially.
		# thus removed isPredicting and isRunning into player.
		self.input = UserInput()
		self.uc_oldest = UserCmd(self.main.msec_sleep if self.main.msec_sleep < 256 else 255)
		self.uc_now = UserCmd(self.main.msec_sleep if self.main.msec_sleep < 256 else 255)
		self.uc_old = UserCmd(self.main.msec_sleep if self.main.msec_sleep < 256 else 255)
		self.uc_oldest = UserCmd(self.main.msec_sleep if self.main.msec_sleep < 256 else 255)

		# depends on userinfo and sets userinfo
		self.setPredicting(self.isPredicting)

	def setPredicting(self,val):
		if val:
			self.isPredicting = True
			self.userinfo["predicting"] = "1"
		else:
			self.isPredicting = False
			self.userinfo["predicting"] = "0"

	def make_userinfo(self):
		d = self.userinfo
		s = ""
		# s = "\""
		for key, value in d.items():
			s += '\\' + key + '\\' + value
		# s+= "\""
		print(f"user info length is currently : {len(s)}")
		return s
		

	def onEnterServer(self):
		self.timestamp_connected = time.time()
		# conn.send(True,(f"\x04say Hi interact with me using @sofgpt\x00").encode('ISO 8859-1'))
		self.conn.append_string_to_reliable(f"{types.CLC_STRINGCMD}say Hi!\x00")

	# you can append a bytes object to a bytesarray with += , str.encode() returns bytes.

	def moveAndSend(self):
		# connected has to be 1 at same point "new" is written into buffer.?
		if not self.conn.connected:
			return

		# print(f"???? {self.conn.connected}")
		# connecting process.
		if self.conn.connected == 1:
			# print(f"huh? {len(self.conn.future_rel_data)}")
			# only reliable packets are used when connecting.
			if len(self.conn.future_rel_data) or time.time() - self.conn.last_sent_time > 1:
				# if backup_rel_data is not empty, nothing happens here
				# except ack confirmations.
				self.conn.netchan_transmit(bytearray());
			return

		self.applyMove()

		buffer2 = bytearray()

		# update userinfo if needed
		if self.userinfo != self.past_userinfo:
			ui = self.make_userinfo()
			print(f"Updating userinfo!\nshow\n{ui}")
			self.conn.append_string_to_reliable(f"{types.CLC_USERINFO}{ui}\x00")

			self.past_userinfo = self.userinfo.copy()
		
		# CLC_MOVE
		move_start = len(buffer2)
		buffer2 += bytearray.fromhex('02 00 FF FF FF FF')
		# fill the 'buffer'

		written_buffer = bytearray(128)
		debugPrint=False
		# if self.conn.our_seq == 436:
		# 	debugPrint=True
		written_bytes = completeUserCommandBitBuffer(self,written_buffer,debugPrint=debugPrint);

		"""
		if self.conn.our_seq == 436:
			# print all bytes in written_buffer as hex bytes
			print(f"written_buffer = {written_buffer.hex()}")
		"""
		
		buffer2 += written_buffer[:written_bytes]
		
		# update lastServerFrame
		if self.lastServerFrame == -1:
			struct.pack_into('<i',buffer2,move_start+2,self.lastServerFrame);
		else:
			# print(f"lastServerFrame = {self.lastServerFrame}")
			# negative direction = older
			#positive = oldest
			# trick_val = (self.lastServerFrame & 15) -2
			# if trick_val > 15:
			# 	trick_val -= 16
			# if trick_val < 0:
			# 	trick_val += 16
			# trick_val += 16
			# struct.pack_into('<I',buffer2,move_start+2,trick_val);
			# Server takes average of the buffer to calculate ping. So if include oldest in average it makes ping higher.
			struct.pack_into('<I',buffer2,move_start+2,self.lastServerFrame);

		# length move_command and checksum byte ignored 6-2 = 4

		# byte *base, int length, int sequence
		# 4 bytes at beginning = lastServerFrame, 4 bytes at end = checksum appended bytes.
		blossom = COM_BlockSequenceCRCByte(buffer2[move_start+2:],self.conn.our_seq);
		# print(f'blossom is {blossom}\n')
		buffer2[1] = blossom

		# print(f"seq was {self.conn.our_seq} and blossom is {hex(blossom)}")

		# util.pretty_dump(buffer2[move_start+2:])

		# print("\n\n")
		

		# THUS :clc_move is unreliable
		
		self.conn.netchan_transmit(buffer2)


	# The cmd is freshly created every frame starting off at 0.
	def applyMove(self):

		# pitch
		cmd = self.uc_now
		# start from 0
		cmd.__init__(self.main.msec_sleep if self.main.msec_sleep < 256 else 255)

		if self.input.lookUp:
			self.viewangles[0] -= int(round(self.pitch_speed*self.input.rightJoystickSensY* self.main.float_sleep)) 
			if self.viewangles[0] < -2048 :
				self.viewangles[0] += 4096
		elif self.input.lookDown:
			self.viewangles[0] += int(round(self.pitch_speed*self.input.rightJoystickSensY* self.main.float_sleep))
			if self.viewangles[0] > 2047:
				self.viewangles[0] -= 4096

		if self.custom_pitch != 9999:
			self.viewangles[0] = self.custom_pitch

		# this this causes bug for player assume always have to send?
		# if state.pitch_before != state.pitch:
		# changed
		cmd.pitch = self.viewangles[0] - round(self.delta_pitch / 16)
		if cmd.pitch < -2048:
			cmd.pitch += 4096
		elif cmd.pitch > 2047:
			cmd.pitch -= 4096

		# yaw
		if self.input.lookRight:
			self.viewangles[1] -= int(round(self.yaw_speed*self.input.rightJoystickSensX* self.main.float_sleep))
			if self.viewangles[1] < -2048 :
				self.viewangles[1] += 4096
		elif self.input.lookLeft:
			self.viewangles[1] += int(round(self.yaw_speed*self.input.rightJoystickSensX* self.main.float_sleep))
			if self.viewangles[1] > 2047:
				self.viewangles[1] -= 4096

		if self.custom_yaw != 9999:
			self.viewangles[1] = self.custom_yaw

		cmd.yaw = self.viewangles[1] - round(self.delta_yaw / 16)
		if cmd.yaw < -2048:
			cmd.yaw += 4096
		elif cmd.yaw > 2047:
			cmd.yaw -= 4096

		# roll
		if self.input.rollRight:
			self.viewangles[2] -= self.roll_speed
			if self.viewangles[2] < -2048 :
				self.viewangles[2] += 4096
		elif self.input.rollLeft:
			self.viewangles[2] += self.roll_speed
			if self.viewangles[2] > 2047:
				self.viewangles[2] -= 4096

		if self.custom_roll != 9999:
			self.viewangles[2] = self.custom_roll

		cmd.roll = self.viewangles[2] - round(self.delta_roll / 16)
		if cmd.roll < -2048:
			cmd.roll += 4096
		elif cmd.roll > 2047:
			cmd.roll -= 4096

		# forward/backward
		if self.input.moveBack:
			# cmd.forwardspeed = int(round(-200* self.input.leftJoystickSensY))
			cmd.forwardspeed = -200
		elif self.input.moveForward:
			# cmd.forwardspeed = int(round(200 * self.input.leftJoystickSensY))
			cmd.forwardspeed = 200

		# left/right
		if self.input.moveLeft:
			cmd.sidespeed = -160
		elif self.input.moveRight:
			cmd.sidespeed = 160

		# up/down
		if self.input.moveDown:
			cmd.upspeed = -200
		elif self.input.moveUp:
			cmd.upspeed = 200

		# buttonn lean lightlevel
		
		if self.input.use:
			cmd.buttonsPressed |= BUTTON_USE

	
		if self.isRunning:
			cmd.buttonsPressed |= BUTTON_RUN

		# respawn / non-predicting
		if ( self.input.fire or self.isPredicting ) and self.internal_allowed_to_fire_basic:
			cmd.buttonsPressed |= BUTTON_ATTACK
			j,low,high = getJoystick(high=0.7)
			if j:
				j.rumble(low, high, 20)
				getJoystick(low=0)
			self.internal_allowed_to_fire_basic = False
		else:
			self.internal_allowed_to_fire_basic = True

		if self.input.leanRight:
			cmd.lean = 1
		elif self.input.leanLeft:
			cmd.lean = 2

		# cmd.lightLevel = 90
		cmd.lightLevel = 0x5

		"""
		Seems they control the rate of fire by not allowing you to fire 2 consecutive packets
		Lets simulate fast toggle then
		"""
		if self.isPredicting and self.input.fire and self.internal_allowed_to_fire >= 2:
		# if player.isPredicting and state.fireEvent and time_now - player.internal_allowed_to_fire_timer > 0.1:
			# want to fire
			cmd.fireEvent = 1.0
			# player.internal_allowed_to_fire_timer = time.time()
			self.internal_allowed_to_fire = 0
		# do not want to fire or not allowed to fire
		else:
			# 2 frames inactive
			self.internal_allowed_to_fire += 1

		if self.isPredicting and self.input.altfire and self.internal_allowed_to_fire2:
			# state.fireEvent forced to default 0.0 every frame
			cmd.altFireEvent = 1.0
			self.internal_allowed_to_fire2 = False
		else:
			self.internal_allowed_to_fire2 = True
