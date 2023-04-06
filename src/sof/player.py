import time
import copy
import struct

from sof.packets.raw import COM_BlockSequenceCRCByte,completeUserCommandBitBuffer

from sof.connection import Connection

import sof.packets.types as types

from sof.packets.defines import *

class UserCmd:
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

		# other

		self.leanLeft = False
		self.leanRight = False

		self.buttonsPressed = 0
		self.shoot = False
		self.fireEvent = False
		self.altFireEvent = False

		self.msec = 20
		self.lightLevel = 5
		
		self.yaw = 0
		self.pitch = 0
		self.roll = 0

		self.yaw_before = 0
		self.pitch_before = 0
		self.roll_before = 0



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

		self.pitch_speed = 10
		self.yaw_speed = 10
		self.roll_speed = 10

		self.delta_pitch = 0
		self.delta_yaw = 0
		self.delta_roll = 0

		self.forward_speed = 100

		self.burst = False

		self.mode = False

		self.uc_now = UserCmd()

		self.usercmd = [ {"buffer":bytearray(64),"bit_length": 0} for i in range(0,2) ]

		self.textColor = P_GREEN
		# use player.make_userinfo to return the slash seperated string form.
		userinfo["name"] = name + self.textColor
		self.userinfo = userinfo
		self.past_userinfo = userinfo

	def initialize(self):
		self.init = True
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

	def make_userinfo(self):
		d = self.userinfo
		s = ""
		# s = "\""
		for key, value in d.items():
			s += '\\' + key + '\\' + value
		# s+= "\""
		return s
		

	def onEnterServer(self):
		self.timestamp_connected = time.time()
		# conn.send(True,(f"\x04say Hi interact with me using @sofgpt\x00").encode('ISO 8859-1'))
		self.conn.append_string_to_reliable(f"{types.CLC_STRINGCMD}say Hi!\x00")

		self.uc_now = UserCmd()

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

		buffer2 = bytearray()

		# update userinfo if needed
		if self.userinfo != self.past_userinfo:
			ui = self.make_userinfo()
			print(f"Updating userinfo!\nshow\n{ui}")
			buffer2 += (f"{types.CLC_USERINFO}{ui}\x00").encode('latin_1')
		self.past_userinfo = self.userinfo.copy()
		
		# CLC_MOVE
		move_start = len(buffer2)
		buffer2 += bytearray.fromhex('02 00 FF FF FF FF')
		# fill the 'buffer'

		written_buffer = bytearray(64)
		written_bytes = completeUserCommandBitBuffer(self,written_buffer);
		
		buffer2 += written_buffer[:written_bytes]
		self.mode = not self.mode
		# update lastServerFrame
		if self.lastServerFrame == -1:
			struct.pack_into('<i',buffer2,move_start+2,self.lastServerFrame);
		else:
			# print(f"lastServerFrame = {self.lastServerFrame}")
			# negative direction = older
			#positive = oldest
			trick_val = (self.lastServerFrame & 15) -2
			if trick_val > 15:
				trick_val -= 16
			if trick_val < 0:
				trick_val += 16
			trick_val += 16
			struct.pack_into('<I',buffer2,move_start+2,trick_val);
			# struct.pack_into('<I',buffer2,2,self.lastServerFrame);

		# length move_command and checksum byte ignored 6-2 = 4

		# byte *base, int length, int sequence
		blossom = COM_BlockSequenceCRCByte(buffer2[move_start+2:],self.conn.our_seq);
		# print(f'blossom is {blossom}\n')
		buffer2[1] = blossom

		# THUS :clc_move is unreliable
		
		self.conn.netchan_transmit(buffer2)

