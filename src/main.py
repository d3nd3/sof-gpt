from sof.client import SofClient

import sys
import time

import util
from sof.packets.raw import COM_BlockSequenceCRCByte

import pygame

import sof.keys as keys


def hex_string_to_bytearray(hex_string):
	hex_list = hex_string.split()
	byte_list = [int(x, 16) for x in hex_list]
	return bytearray(byte_list)


def test_checksum():
	# seq = int(sys.argv[1])
	# data = bytearray(sys.argv[2].encode("latin-1"))

	seq = 103
	data = hex_string_to_bytearray("13 00 00 00 01 20 00 05 00 fa 17 c0 42 11 00 00 f0 47 00 08 40 01 80 fe 05 b0 50 04 00 00 fc 11 00 02 50 00 a0 7f 01 2c 14 01 00 00 7f")
	print(f"seq : {seq}\ndata : {data}")

	blossom = COM_BlockSequenceCRCByte(data,seq);
	print(f"blossom is {hex(blossom)}")	
	sys.exit(0)


if __name__ == "__main__":
	# test_checksum()

	# util.print_bits(b"FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")
	# sys.exit(1)
	ip = sys.argv[1]
	port = sys.argv[2]
	name = sys.argv[3]
	print(f"ip : {ip}\nport : {port}\nname : {name}")

	client = SofClient()

	pygame.init()
	screen = pygame.display.set_mode((600, 600))

	keys.init_gamepad()
	# Create a clock object to control the frame rate
	clock = pygame.time.Clock()
	
	# name and predicting overriden inside player.py
	userinfo = {
		"predicting"			: "1",
		"spectator_password" 	: "acadie",
		"password"				: "acadie",
		"cl_violence"			: "0",
		"spectator"				: "1",
		"skin"					: "widowmaker",
		"teamname"				: "Ministry of Sin",
		"fov"					: "95",
		"msg"					: "0",
		"rate"					: "25000",
		"allow_download_models" : "1",
		"team_red_blue"			: "0",
		"bestweap"				: "" #safe/unsafe
	}

	
	# endpoints store players
	# connection is just a class that stores socket and funcs for the socket
	# each player will create a connection class (socket)
	
	endpoint = client.addEndpoint(ip,port)
	# green visible font

	# 16+ player unconnectable client struggles.
	# 13 clients = message over flow. ( 2 + 11)
	for i in range(0,1):
		print(i,"clients")
		client.addPlayerToEndpoint(endpoint,userinfo,name)
	
	# endpoint = client.addEndpoint("5.135.46.179","28926")
	# client.addPlayerToEndpoint(endpoint,userinfo,name)


	# endpoint = client.addEndpoint("5.135.46.179","28920")
	# client.addPlayerToEndpoint(endpoint,userinfo,name)

	client.beginLoop(clock)




