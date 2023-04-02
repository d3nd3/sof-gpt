import time
import copy
import struct

from sof.packets.raw import COM_BlockSequenceCRCByte,completeUserCommandBitBuffer

from sof.connection import Connection

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

		self.mode = False


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
		self.wasConnected = False
		self.name = name
		self.init = False
		self.endpoint = endpoint



		self.setup_userinfo(userinfo,name)

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
		self.createUserCmds()
		return True

	def make_userinfo(self):
		d = self.userinfo
		s = '\"'
		for key, value in d.items():
			s += '\\' + key + '\\' + value
		s += '\"'
		return s
	def setup_userinfo(self,ui,name):
		ui["name"] = name
		self.userinfo = ui

	def createUserCmds(self):
		self.uc_now = UserCmd()
		self.uc_prev = copy.copy(self.uc_now)
		self.uc_prev_prev = copy.copy(self.uc_now)

	def onEnterServer(self):
		self.timestamp_connected = time.time()
		# conn.send(True,(f"\x04say Hi interact with me using @sofgpt\x00").encode('ISO 8859-1'))
		self.conn.send(True,(f"\x04say Hi!\x00").encode('ISO 8859-1'))
	def sendMoveCommands(self):

		buffer2 = bytearray.fromhex('02 00 FF FF FF FF')
		# fill the 'buffer'
		written_bytes,written_buffer = completeUserCommandBitBuffer(self);
		
		buffer2 += written_buffer[:written_bytes]
		self.uc_now.mode = not self.uc_now.mode
		# update lastServerFrame
		if self.lastServerFrame == -1:
			struct.pack_into('<i',buffer2,2,self.lastServerFrame);
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
			struct.pack_into('<I',buffer2,2,trick_val);
			# struct.pack_into('<I',buffer2,2,self.lastServerFrame);

		# length move_command and checksum byte ignored 6-2 = 4

		# byte *base, int length, int sequence
		blossom = COM_BlockSequenceCRCByte(buffer2[2:],self.conn.out_seq+1);
		# print(f'blossom is {blossom}\n')
		buffer2[1] = blossom

		# print(f'sending {buffer2}\n')
		self.conn.send(True,buffer2);

		self.uc_prev = copy.copy(self.uc_now)
		self.uc_prev_prev = copy.copy(self.uc_prev)

