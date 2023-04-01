from sof.player import Player
from sof.connection import Endpoint

import time


# this class represents the entire tool.
# ideally handles multiple connections
# and ideally there can be multiple players to a connection
class SofClient:
	def __init__(self):
		# dict of `ip:port`:Endpoint
		self.endpoints = {}
		
	# if connection already exists, append a player, else both
	def addEndpoint(self,host,port):
		key = host + port
		if not key in self.endpoints:
			self.endpoints[key] = Endpoint(host,port)
		return self.endpoints[key]

	# endpoint is a server/port + list of players
	# this adds a player to endpoint
	def addPlayerToEndpoint(self,endpoint,userinfo,name):
		p = Player(endpoint,userinfo,name)
		endpoint.players.append(p)

	def beginLoop(self):
		print("beginLoop")
		# 0.02 of a second = 20ms = 50fps
		frame_length = 0.02
		framecount = 0
		main_begin = before_cpu = time.time()
		connectedCount = 0
		while True:
			framecount += 1

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
				
					# sends heartbeat 50 times a second
					if c.connected:
						if not player.wasConnected:
							connectedCount +=1
							print(f"CONNECTED: New Total : {connectedCount}")
							time.sleep(0.5)
							player.onEnterServer()

						# send usercmds if connected
						player.sendMoveCommands()

						# send gpt output
						# self.output_gpt(player)
					else:
						if player.wasConnected:
							connectedCount -=1
							print(f"DISCONNECTED: New Total : {connectedCount}")

					if time.time() - player.conn.last_packet_stamp > 5.0:
						print("auto die no packet")
						player.init = False
						player.conn.last_packet_stamp = time.time()

					player.wasConnected = player.conn.connected
					

			now = time.time()
			fps = framecount / (now-main_begin)
			if (framecount % (50 * 10)) == 0:
				print(f"STATS: { len(self.endpoints)} endpoints. With { len( [ self.endpoints[e] for e in self.endpoints for p in self.endpoints[e].players if p.conn.connected ])} connected players" )
				# print(f"fps is {fps}")

			# ----sleep----
			exec_time = time.time() - before_cpu
			# too fast? sleep some
			if exec_time < frame_length:
				time.sleep(frame_length-exec_time)

			before_cpu = time.time()