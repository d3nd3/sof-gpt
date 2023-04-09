from sof.player import Player
from sof.connection import Endpoint

from sof.chat_bridge import output_gpt

import time

from sof.packets.defines import *

import sof.keys

import pygame

# this class represents the entire tool.
# ideally handles multiple connections
# and ideally there can be multiple players to a connection

# I refer to this as `main`
class SofClient:
	def __init__(self):
		# dict of `ip:port`:Endpoint
		self.endpoints = {}
		# there can only be 1 instance of gpt
		self.gpt = {
			"chunks" : [],
			"chunk_len_prev" : 0,
			"say_timestamp" : time.time(),
			"base_delay" : 1,
			"scaled_delay" : 4,

			"toggle_color" : False,
			"toggle_color_1" : P_WHITE,
			"toggle_color_2" : P_GREEN
		}

		self.connectedCount = 0
		self.target_fps = 1 / 50
		self.framecount = 0
		self.main_begin = self.before_cpu = time.time()
		
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
			for player in list(e.players):
				if not player.init:
					if not player.initialize():
						print("REMOVING!server not respond!")
						e.players.remove(player)
						continue
				c = player.conn
				c.recv()
				# TODO: THERE IS BUG ON SOME MAPS THAT START PACKET WITH SVC_TMP_ENTITY
				
				sof.keys.process(player)

				# send usercmds if connected
				player.moveAndSend()

				pygame.display.update()
				
				# sends heartbeat 50 times a second
				if c.connected == 2:
					if player.wasConnected != 2:
						self.connectedCount +=1
						print(f"CONNECTED: New Total : {self.connectedCount}")
						# time.sleep(0.5)
						player.onEnterServer()

					# send gpt output
					output_gpt(self,player,c)
				elif c.connected == 0:
					if player.wasConnected > 0:
						self.connectedCount -=1
						print(f"DISCONNECTED: New Total : {self.connectedCount}")

				if time.time() - player.conn.last_packet_stamp > 15.0:
					print("auto die no packet")
					player.init = False
					player.conn.last_packet_stamp = time.time()

				player.wasConnected = player.conn.connected


	def beginLoop(self):
		print("beginLoop")
		# 0.02 of a second = 20ms = 50fps
		
		
		while True:
			self.framecount += 1

			self.talkToWorld()
					
			now = time.time()
			fps = self.framecount / (now-self.main_begin)
			if (self.framecount % (50 * 10)) == 0:
				print(f"STATS: { len(self.endpoints)} endpoints. With { len( [ self.endpoints[e] for e in self.endpoints for p in self.endpoints[e].players if p.conn.connected ])} connected players" )
				# print(f"fps is {fps}")

			# ----sleep----
			exec_time = time.time() - self.before_cpu
			# too fast? sleep some
			if exec_time < self.target_fps:
				time.sleep(self.target_fps-exec_time)

			self.before_cpu = time.time()