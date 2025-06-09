from sof.player import Player
from sof.connection import Endpoint

from sof.chat_bridge import output_gpt

from sof.packets.defines import *

import sof.packets.types as types

import sof.keys
import util

import time
import pygame

import os
import math
import threading
from queue import Queue


# this class represents the entire tool.
# ideally handles multiple connections/endpoints/servers
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

		self.FPS = 145 #change this
		# rounded up in msec, to lower frame-rate bound.
		self.msec_sleep = math.ceil(1000/self.FPS) #255 max for byte object msec command.
		print(f"Calculated msec of {self.msec_sleep}")
		self.float_sleep = self.msec_sleep / 1000 #in secs
		self.target_fps = 1000/self.msec_sleep

		self.framecount = 0
		self.main_begin = self.before_cpu = time.time()

		# thread safe queue
		self.user_input_queue = Queue()

		
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
			if not len(e.players):
				# Not working.
				pygame.quit()
				os._exit(0)
			# using list() so that we can remove from it easier.
			for player in list(e.players):
				if not player.init:
					# Reconnect an initted players
					# Creates Connection object and initialises connection parameters
					if not player.initialize():
						print("REMOVING! server not respond!")
						e.players.remove(player)
						continue

				c = player.conn

				# do this before recv(), since recv() can set connection parameters.
				if c.connected < 2:
					# from connected to disconnected/connecting
					if player.wasConnected == 2:
						self.connectedCount -=1
						print(f"DISCONNECTED: New Total : {self.connectedCount}")

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
						time.sleep(0.1)
						player.onEnterServer()


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

					# Check if there's user input in the queue
					if not self.user_input_queue.empty():
						user_input = self.user_input_queue.get()
						# Now you can use the user_input in the main thread
						# util.pretty_dump(util.str_to_byte(user_input))
						c.append_string_to_reliable(f"{types.CLC_STRINGCMD}{user_input}\x00")
				break
				
	def process_user_input(self):
		# Implement your logic for processing user input here
		while True:
			user_input = input()
			self.user_input_queue.put(user_input)

	def beginLoop(self,clock):
		print("Starting sof-gpt...")

		# Start a separate thread for user input
		input_thread = threading.Thread(target=self.process_user_input)
		input_thread.daemon = True
		input_thread.start()

		while True:
			self.framecount += 1

			#interacts with sof server
			self.talkToWorld()

			now = time.time()
			fps = self.framecount / (now-self.main_begin)

			# every 10 seconds
			if (self.framecount % (self.target_fps * 10)) == 0:
				num_eps = len(self.endpoints)
				num_players = len([ self.endpoints[e] for e in self.endpoints for p in self.endpoints[e].players ])

				# print(f"STATS: { num_eps } endpoints. With { len( [ self.endpoints[e] for e in self.endpoints for p in self.endpoints[e].players if p.conn.connected == 2 ])} connected players" )

				if num_players == 0:
					sys.exit(0)
				# print(f"fps is {fps}")

			"""
			# ----sleep----
			exec_time = time.time() - self.before_cpu
			# too fast? sleep some
			if exec_time < self.float_sleep:
				time.sleep(self.float_sleep-exec_time)

			self.before_cpu = time.time()
			"""
			# clock.tick(self.target_fps)
			clock.tick_busy_loop(math.floor(self.target_fps))
