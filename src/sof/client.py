from sof.player import Player
from sof.connection import Endpoint

from sof.chat_bridge import output_gpt

import time

from sof.packets.defines import *

import sof.keys

import pygame

import sys

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
			"active" : False,
			"chunks" : [],
			"chunk_len_prev" : 0,
			"say_timestamp" : time.time(),
			"base_delay" : 1,
			"scaled_delay" : 4,

			"toggle_color" : False,
			"toggle_color_1" : P_WHITE,
			"toggle_color_2" : P_GREEN,
		}

		self.connectedCount = 0
		self.msec_sleep = 7
		self.float_sleep = 7 / 1000
		self.target_fps = round(1000/7)

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
			# using list() so that we can remove from it easier.
			for player in list(e.players):
				if not player.init:
					# Reconnect an initted players
					# Creates Connection object and initialises connection parameters
					if not player.initialize():
						print("REMOVING! server not respond!")
						e.players.remove(player)
						continue
				if not len(e.players):
					print("Exiting: no more valid players exist.")
					sys.exit(1)
				c = player.conn
				c.recv()
				# TODO: THERE IS BUG ON SOME MAPS THAT START PACKET WITH SVC_TMP_ENTITY
				
				sof.keys.process(player)

				# send usercmds if connected
				player.moveAndSend()

				pygame.display.update()
				
				# sends heartbeat fps times a second
				# connected 2 == fully connected , its resembling states from q2.
				if c.connected == 2:
					if player.wasConnected != 2:
						self.connectedCount +=1
						print(f"CONNECTED: New Total : {self.connectedCount}")
						# time.sleep(0.5)
						player.onEnterServer()

				elif c.connected == 0:
					if player.wasConnected > 0:
						self.connectedCount -=1
						print(f"DISCONNECTED: New Total : {self.connectedCount}")

				if time.time() - player.conn.last_packet_stamp > 15.0:
					print("auto die no packet")
					player.init = False
					player.conn.last_packet_stamp = time.time()

				player.wasConnected = player.conn.connected

			# TODO: make gpt output endpoint specific, meaning output to same endpoint the request was generated in.
			for player in e.players:
				if player.conn.connected == 2:
					# its timer restricted. so it doesnt spam
					output_gpt(self,player,player.conn)
				break
	def beginLoop(self):
		print("Starting sof-gpt...")
		while True:
			self.framecount += 1

			self.talkToWorld()

			now = time.time()
			fps = self.framecount / (now-self.main_begin)

			# every 10 seconds
			if (self.framecount % (self.target_fps * 10)) == 0:
				num_eps = len(self.endpoints)
				num_players = len([ self.endpoints[e] for e in self.endpoints for p in self.endpoints[e].players ])

				print(f"STATS: { num_eps } endpoints. With { len( [ self.endpoints[e] for e in self.endpoints for p in self.endpoints[e].players if p.conn.connected == 2 ])} connected players" )

				if num_players == 0:
					sys.exit(0)
				# print(f"fps is {fps}")

			# ----sleep----
			exec_time = time.time() - self.before_cpu
			# too fast? sleep some
			if exec_time < self.float_sleep:
				time.sleep(self.float_sleep-exec_time)

			self.before_cpu = time.time()
