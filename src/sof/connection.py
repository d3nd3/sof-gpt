import random
import socket
import time
import struct
import errno

from sof.packets.parse import Parser,packet_parsers
from sof.packets.types import packetIDtoName

from util import pretty_dump

class Endpoint:
	def __init__(self,ip,port):
		self.ip = ip
		self.port = port
		self.players = []

# this class represents the network code required to talk to server
# unique for each player , unique socket handle.
class Connection:
	def __init__(self,player,server,port):
		self.player = player
		self.server = (server,int(port))
		self.last_rel_sent,self.reliable_r_ack,self.reliable_s,self.reliable_r,self.out_seq,self.in_seq,self.in_ack=0,0,0,0,0,0,0
		self.busy = False
		self.qport=self.rand(5)
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.settimeout(0)
		self.connected = False
		self.expectmapname = False
		self.i_downloading = 0
		self.last_packet_stamp = 0
		
	def rand(self,len):
		rand = []
		for x in range(0,len):
			i = random.randint(0,9);
			rand += str(i)
		return int(''.join(map(str, rand))) & 0x7FFF
	def get_challenge(self,startTime):
		print("[unconnected] Sending getchallenge to server")
		self.mychal = self.rand(10)
		buf = "getchallenge {}\x0A\x00".format(self.mychal)
		
		self.send(False,buf.encode('ISO 8859-1'))
		while True:
			# time.sleep(1)
			o = self.recv()
			# break only once we got the data
			if type(o) is memoryview:
				self.chal = bytes.decode(bytes(o[10:]),'ISO 8859-1')
				break
			if time.time() - startTime > 5:
				print("[unconnected] Giving up!")
				return False

		print(f"[unconnected] received challenge {self.chal}")
		return True
		

	def connect(self,startTime):
		print("[unconnected] Sending connect to server")
		#sprintf(tmp_buf,"connect 33 %hu %lu %lu 3.14 "userinfo"\x0A\x00",qport,i_chal,mychal);
		self.qport = self.rand(5)
		buf = "connect 33 {} {} {} 3.14 {}\x0A".format(self.qport,self.chal,self.mychal,self.player.make_userinfo())

		self.send(False,buf.encode('ISO 8859-1'))
		while True:	
			# time.sleep(1)

			o = self.recv()
			if type(o) is memoryview:
				break

			if time.time() - startTime > 5:
				print("[unconnected] Giving up!")
				return False
		return True
	def new(self):
		print("[connected] Sending new to server")
		buf = "\x04new\x00"
		print(buf.encode('ISO 8859-1'))
		self.send(True,buf.encode('ISO 8859-1'))


	def send(self,rel,data):
		if rel:
			self.out_seq += 1
			msg = bytearray(10)
			# print(f"reliable_s is {self.reliable_s}")
			# print(f"reliable_r is {self.reliable_r}")
			struct.pack_into('<I',msg,0,(self.out_seq & (~(1<<31) & 0xFFFFFFFF))|(self.reliable_s<<31))
			struct.pack_into('<I',msg,4,(self.in_seq & (~(1<<31) & 0xFFFFFFFF))|(self.reliable_r<<31))
			struct.pack_into('<H',msg,8,self.qport)
			ba = msg + data
		else:
			ba = b'\xFF\xFF\xFF\xFF' + data
		self.s.sendto(ba,self.server)


	def recv(self):
		while True:
			msg = bytearray(1400)
			view = memoryview(msg)
			try:
				nbytes = self.s.recv_into(view)
			except socket.error as e:
				err = e.args[0]
				if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
					return False
				print("Network Error")
				sys.exit(1)
			self.last_packet_stamp = time.time()
			view = view[:nbytes]

			# pretty_dump(view)

			s=struct.unpack_from('<i',view,0)
			if s[0] == -1:
				# connectionless packet ?
				# print("[UNCONNECTED PACKET RECEIVED]: ",bytes(view),"\n")
				return view[4:]
			else:
				# print("[CONNECTED PACKET RECEIVED]: ",bytes(view),"\n")
				pass
			#so must be connected packet...
			self.in_seq = struct.unpack_from('<I',view,0)[0]
			view = view[4:]
			reliable_message = self.in_seq >> 31
			
			if reliable_message :
				self.reliable_r ^= 1

			# turn off last bit
			self.in_seq = self.in_seq & ~(1<<31)
			# s=struct.unpack_from('<i',view,0)
			view = view[4:]

			# there are many commands inside 1 packet
			# if you cannot parse 1 packet, you can't parse the others.
			if self.expectmapname:
				pos = msg.find(b"maps/dm/",0)
				if pos >= 0:
					self.player.mapname = msg[pos:].split(b'.',1)[0].decode("ISO 8859-1")
					print (self.player.mapname)
					self.expectmapname = False
			while view:
				# print(view.nbytes)
				cmd = struct.unpack_from('<B',view,0)[0]
				# print(f"---------PARSING PACKET : {packetIDtoName(cmd)}")
				view = view[1:]

				pname = packetIDtoName(cmd)
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
