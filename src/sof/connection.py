import random
import socket
import time
import struct
import errno

from sof.packets.parse import Parser,packet_parsers
from sof.packets.types import *

import util


class Endpoint:
	def __init__(self,ip,port):
		self.ip = ip
		self.port = port
		self.players = []

	def removePlayer(self,player):
		if player.conn.connected > 0:
			util.say(player,f"Goodbye!")

		player.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		player.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		player.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))
		player.conn.netchan_transmit((util.str_to_byte(f"{CLC_STRINGCMD}disconnect")))

		# Remove self from endpoint
		self.players.remove(player)

		# Player is forgotten about now?

# this class represents the network code required to talk to server
# unique for each player , unique socket handle.
class Connection:
	def __init__(self,player,server,port):
		self.player = player
		self.server = (server,int(port))
		

		self.their_seq_is_r = 0
		self.their_seq = 0

		self.our_seq = 1
		self.our_ack = 0
		self.our_ack_is_r = 0
		self.our_seq_is_r = 0
		self.our_last_rel_seq = 0

		self.last_sent_time = time.time()
		self.last_packet_stamp = time.time()

		self.backup_rel_data = bytearray()
		self.future_rel_data = bytearray()
		self.dropped = 0


		self.busy = False
		self.qport=self.rand(5) & 0x07FF
		# self.qport = 33333
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# self.s.settimeout(0)
		self.s.setblocking(False)
		self.connected = 0
		self.expectmapname = False
		self.i_downloading = 0
		
		
	def rand(self,len):
		rand = []
		for x in range(0,len):
			i = random.randint(0,9);
			rand += str(i)
		return int(''.join(map(str, rand))) 
	def get_challenge(self,startTime):
		self.mychal = self.rand(10)
		# self.mychal = 1680425046
		buf = "getchallenge {}\x0A\x00".format(self.mychal)
		while True:
			print("[unconnected] Sending getchallenge to server")
			recent_send = time.time()
			self.send_unconnected(buf.encode('latin_1'))
			while True:	
				o = self.recv()
				# break only once we got the data
				if type(o) is memoryview:
					self.chal = bytes.decode(bytes(o[10:]),'latin_1')
					print(f"[unconnected] received challenge {self.chal}")
					return True
				now = time.time()
				if now - recent_send > 3:
					break
				if now - startTime > 20:
					print("[unconnected] Giving up!")
					return False
				time.sleep(0.1)

	def connect(self,startTime):
		buf = "connect 33 {} {} {} 3.14 {}\x0A".format(self.qport,self.chal,self.mychal,"\"" + self.player.make_userinfo() + "\"")
		# buf = "connect 33 {} {} {} 3.14 {}\x0A".format(self.qport,self.chal,self.mychal,self.player.make_userinfo())
		response = False
		while True:
			print("[unconnected] Sending connect to server")
			recent_send = time.time()
			self.send_unconnected(buf.encode('latin_1'))
			while True:
				o = self.recv()
				# break only once we got the data
				if type(o) is memoryview:
					response = util.mem_to_str(o)
					break
				now = time.time()
				if now - recent_send > 3:
					break
				if now - startTime > 20:
					print("[unconnected] Giving up!")
					return False

				time.sleep(0.1)
			# double break
			if response:
				break

		print(f"[unconnected] Received client_connect... {util.mem_to_str(o)}")
		
		# No spectator password eg.
		if response.startswith("rejected_spectator_password"):

			# we dont know the pass, try spec 0
			self.player.userinfo["spectator"] = "0"

			self.__init__(self.player,self.player.endpoint.ip,self.player.endpoint.port)
			self.player.timestamp_start = time.time()

			if not self.get_challenge(self.player.timestamp_start):
				return False
			# call ourself?
			if not self.connect(self.player.timestamp_start):
				return False
			return True
		return True
	def new(self):
		print("[connected] Sending new to server")
		buf = "\x04new\x00"
		self.connected = 1
		print(buf.encode('latin_1'))
		self.append_string_to_reliable(buf)


	def append_string_to_reliable(self,what):
		self.future_rel_data += what.encode('latin_1')

	def append_to_reliable(self,what):
		self.future_rel_data += what

	# WE VERIFY "THEIR" REMOTES PACKETS (PATH B)
	# THEY VERIFY "OUR" PACKETS (PATH A)

	# REFER TO DIAGRAM GOOGLE NOTES
	def netchan_process(self,view):
		# print("-------------------RECEIVING----------------------")
		# util.pretty_dump(view)


		#so must be connected packet...
		their_seq = struct.unpack_from('<I',view,0)[0]
		view = view[4:]

		# acquire reliable BITS
		their_seq_is_r = their_seq >> 31
		
		our_ack = struct.unpack_from('<I',view,0)[0]
		view = view[4:]

		our_ack_is_r = our_ack >> 31

		# strip reliable bit
		their_seq = their_seq & ~(1<<31)
		our_ack = our_ack & ~(1<<31)

		# conn.their_seq is only allowed to increase // discard stale or duplicated packets
		if their_seq <= self.their_seq:
			return (view, False)

		# measure how many sequence numbers were skipped
		self.dropped = their_seq - (self.their_seq+1);

		# clear reliable backups. ACKED
		# OUR PATH A PACKET HAS RETURNED TO US
		if our_ack_is_r == self.our_seq_is_r:
			self.backup_rel_data = bytearray()
			# print("<----------------")
			# print(f"ACKED OUR RELIABLE PACKET {our_ack}")
		
		# ----save stuff-----
		# IN_SEQ BECOMES OUT_ACK
		self.their_seq = their_seq 
		# THE SEQ NUMBER OF THE LAST PACKET THE REMOTE RECEIVED FROM US
		# Used to confirm that the conn.our_ack_is_r is valid ( > last_rel )
		self.our_ack = our_ack 
		self.our_ack_is_r = our_ack_is_r

		# THEIR PATH
		if their_seq_is_r:
			# TOGGLE REMOTES RELIABLE
			self.their_seq_is_r ^= 1

		self.last_packet_stamp = time.time()
		return (view, True)


	# called by CL_SendCmd
	# WE VERIFY "THEIR" REMOTES PACKETS (PATH B)
	# THEY VERIFY "OUR" PACKETS (PATH A)
	# every time this is called directly unreliable data is flushed through
	# seems its only called directly with disconnect command.
	# and incoming acks are checked with reliable toggle bit
	def netchan_transmit(self,unreliable_data):

		send_reliable = 0

		# print(f"Current in_ACk state is : {self.our_ack_is_r}")

		# PATH A WAS DROPPED?
		if self.our_ack > self.our_last_rel_seq and self.our_ack_is_r != self.our_seq_is_r:
			# print("---------------->")
			# print(f"Resending {self.our_last_rel_seq - 1}")
			send_reliable = 1

		# backup empty AND future_send non-empty
		# aka : BACKUP WAS ACKED in netchan_process : SEND NEW REL DATA
		if not len(self.backup_rel_data) and len(self.future_rel_data):
			self.backup_rel_data = bytearray(self.future_rel_data)
			self.future_rel_data = bytearray()
			self.our_seq_is_r ^= 1
			send_reliable = 1
			# print("---------------->")
			# print(f"GENERATING NEW RELIABLE PACKET {self.our_seq & (~(1<<31) & 0xFFFFFFFF)} MATCHING: {self.our_seq_is_r}")

		msg = bytearray(10)

		struct.pack_into('<I',msg,0,(self.our_seq & (~(1<<31) & 0xFFFFFFFF))|(send_reliable<<31))
		struct.pack_into('<I',msg,4,(self.their_seq & (~(1<<31) & 0xFFFFFFFF))|(self.their_seq_is_r<<31))
		struct.pack_into('<H',msg,8,self.qport)
		

		self.our_seq += 1
		self.last_sent_time = time.time()
		if send_reliable:
			msg += self.backup_rel_data
			self.our_last_rel_seq = self.our_seq

		# add unreliable here
		msg += unreliable_data

		# print("--------------SENDING CONNECTED-----------------")
		# util.pretty_dump(msg)

		self.s.sendto(msg,self.server)


	def send_unconnected(self,data):
		send_buffer = b'\xFF\xFF\xFF\xFF' + data
		self.s.sendto(send_buffer,self.server)
		# util.pretty_dump(send_buffer)

	def recv(self):
		while True:
			# 1400
			msg = bytearray(1400)
			view = memoryview(msg)
			try:
				nbytes = self.s.recv_into(view)
			# we dont actually use non blocking sockets, we use timeout. oops?
			except socket.error as e:
				err = e.args[0]
				if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
					return False
				print("Network Error")
				sys.exit(1)
			
			view = view[:nbytes]

			s=struct.unpack_from('<i',view,0)
			if s[0] == -1:
				# connectionless packet ?
				# print("[UNCONNECTED PACKET RECEIVED]: ",bytes(view),"\n")
				util.multiline_print(view)
				return view[4:]
			else:
				# print("[CONNECTED PACKET RECEIVED]: ",bytes(view),"\n")
				pass

			
			view,ret = self.netchan_process(view)
			if ret == False:
				# discard stale or duplicate packet
				print("Discarding.")
				continue

			# there are many commands inside 1 packet
			# if you cannot parse 1 packet, you can't parse the others.
			if self.expectmapname:
				pos = msg.find(b"maps/dm/",0)
				if pos >= 0:
					self.player.mapname = msg[pos:].split(b'.',1)[0].decode("latin_1")
					print (self.player.mapname)
					self.expectmapname = False
			# iterating 1 packet
			while view:
				# print(view.nbytes)

				cmd = struct.unpack_from('<B',view,0)[0]
				view = view[1:]

				pname = packetIDtoName(cmd)
				# print(f"---------PARSING PACKET : {pname}")
				if pname is None:
					# completely unrecognized packet
					break

				# ---------------parse the packet-----------------
				view = packet_parsers[pname](self,self.player,view)
				if view is None: 
					# unimplemented so cannot continue
					break
					
			# endwhile view

			# entire msg search
			
		return True
			
	def end(self):
		self.s.close
