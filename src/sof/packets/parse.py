import sof.chat_bridge as GPT

from sof.packets.defines import *

import struct
import time

import re

import util

from sof.keys import getJoystick

class Parser:
	"""
		parse a null terminated string
		returns a tuple containing the string parsed
		and the remaining of buffer without the string
	"""
	def string(buf):
		startstr = buf
		count = 0
		while buf:
			if buf[0] == 0x00: #or view is none
				buf = buf[1:]
				break;
			buf = buf[1:]
			count += 1
		return (startstr[:count],buf)

	"""
		parse a stufftext type packet
		returns list of mirror packets
		seperates newline and removes 'cmd ' from them
	"""

	def stufftext(buf,conn,player):

		b = buf.tobytes().decode('latin_1')
		b = b.split("\n")
		# return only 'cmd' stufftexts but remove cmd from front
		retlist = [each[4:] for each in b if each and each.find("cmd ",0) >=0]
		
		# process non 'cmd' stufftexts...
		for a in b:
			if a and a.find("cmd ",0) < 0:
				if a.find("precache ",0) == 0:
					player.precache = a[9:]
					conn.append_string_to_reliable("\x04download {}.eal\x00".format(player.mapname))
					conn.i_downloading = 1
					# print("SERVED BY PRECACHE STUFFTEXT\n")
				elif a.find("reconnect",0) == 0:
					print("They want you to reconnect by stufftext\n")
					# player.initialize()
					player.init = False
				elif a.find("team_red_blue ",0) == 0:
					# print(f"Set team_red_blue to {a.split()[1]}")
					player.userinfo["team_red_blue"] = a.split()[1] 

					
		return retlist

# if return None will break the packet-scan loop

def svc_bad(conn,player,view):
	return None

def svc_temp_entity(conn,player,view):
	return None

def svc_layout(conn,player,view):
	return None

def svc_unused(conn,player,view):
	return None

def svc_sound_info(conn,player,view):
	return None

def svc_effect(conn,player,view):
	return None

def svc_equip(conn,player,view):
	return None

def svc_nop(conn,player,view):
	return None

def svc_disconnect(conn,player,view):
	# print("PACKET: disconnect\n")
	player.init = False
	return view
def svc_reconnect(conn,player,view):
	return None

def svc_sound(conn,player,view):
	return None

def svc_print(conn,player,view):
	view=view[1:]
	s,view = Parser.string(view)
	s = util.mem_to_str(s)
	if s == "Server restarted\n":
		print("Server restart detected via print\n");
		player.init = False
		return view

	if "sof1.org/viewtopic.php?t=4660" not in s:
		print("PACKET: print\n",s)

	return view


def svc_nameprint(conn,player,view):
	# 1st byte = client id 2nd byte = teamsay
	data1 = struct.unpack_from('<B',view,0)[0]
	view=view[1:]
	try:
		data2 = struct.unpack_from('<B',view,0)[0]
		view=view[1:]
	except:
		# this only happens when > 32 clients in server
		print("----------WEIRD DATA RECEIVED-------------")
		return
	

	s,view = Parser.string(view)
	input_str = s.tobytes().decode('latin_1')

	print(f"client {data1} says : {input_str}")

	# define the regular expression pattern
	pattern = r"^\[.+\]\s(.*)\n"

	# util.pretty_dump(input_str.encode(('latin_1')))

	# test input string
	# input_str = "nameHere : [1 m] some content"

	content = input_str
	# test for pattern
	match = re.search(pattern, input_str)
	if match:
		content = match.group(1)
		
	# print(f"Content: {content}")
	
	content = content.strip()
	if content.find("@sofgpt ") == 0:
		content = content[8:]
		GPT.interact(content,player)
	
	return view

def svc_stufftext(conn,player,view):
	s,view = Parser.string(view)
	# print(f"{s.tobytes()}")

	# returns cmd based strings
	cmd_stufftexts=Parser.stufftext(s,conn,player)

	for a in cmd_stufftexts:
		if a.find("configstrings ",0) == 0:
			conn.append_string_to_reliable("\x04"+a+"\x00")
		elif a.find("begin",0) == 0:
			conn.connected = 2
			# send it back to server
			conn.append_string_to_reliable(f"\x04begin {player.precache}\x00")
		elif a.find(".check ",0) == 0:
			
			a = a.replace("#cl_minfps","5")
			a = a.replace("#cl_maxfps","30")

			a = a.replace("#gl_drawmode","0")
			a = a.replace("#gl_fogmode","0")
			a = a.replace("#gl_modulate","2")
			a = a.replace("#gl_lockpvs","0")
			a = a.replace("#gl_nobind","0")
			a = a.replace("#gl_driver","opengl32")
			a = a.replace("#gl_showtris","0")
			a = a.replace("#gl_drawflat","0")
			a = a.replace("#gl_dlightintensity","2")
			a = a.replace("#gl_nobind","0")
			a = a.replace("#r_nearclipdist","4")
			a = a.replace("#r_drawworld","1")
			a = a.replace("#r_fullbright","0")

			a = a.replace("#ghl_shadow_dist","25")
			a = a.replace("#cl_testlights","0")
			a = a.replace("#cl_testblend","0")
			# send it back to server
			conn.append_string_to_reliable(f"\x04{a}\x00")
		elif a.find("baselines ",0) == 0:
			# send it back to server
			conn.append_string_to_reliable(f"\x04{a}\x00")
		else:
			# send it back to server
			conn.append_string_to_reliable(f"\x04{a}\x00")

	return view

def svc_serverdata(conn,player,view):
	# print("PACKET: serverdata\n")
	conn.connected = 1
	conn.expectmapname = True
	view = view[9:]
	s,view = Parser.string(view)
	player.playernum = struct.unpack_from('<h',view,0)[0]
	view = view[2:]
	s,view = Parser.string(view)
	player.map = s.tobytes().decode("latin_1")

	return view

def svc_configstring(conn,player,view):
	#print("PACKET: configstring\n")
	normalindex = struct.unpack_from('<h',view,0)[0]
	view=view[2:]
	configcheat = struct.unpack_from('<h',view,0)[0]
	view=view[2:]
	if configcheat == -1:
		# networkstring
		s,view = Parser.string(view)
	else:
		# configcheat
		# expects to read configstring from local cache. using configcheat as index.
		# reduces network bandwidth, but still has high latency costs..
		# q2 uses this for cs_models only, by prefix string with *
		# sof is using it for all configstring types.
		pass
		

	return view

def svc_spawnbaseline(conn,player,view):
	# search for precache hm\
	data = view.tobytes()
	find_precache = data.find(b"\x0dprecache",0)
	if find_precache >= 0:
		player.precache = int(data[find_precache+9:].split(b'\x0a',1)[0])
		# print(f"acquired precache number : {player.precache}\n")
		# print (f"download  {player.mapname}.eal")
		conn.append_string_to_reliable(f"\x04download {player.mapname}.eal\x00")
		conn.i_downloading = 1
		# print("SERVED BY BASELINE\n")
	else:
		# assume more baselines...
		fail = True
		find_more_base = data.find(b"\x0dcmd baselines ",0)
		if find_more_base >= 0:
			pattern = r"\x0dcmd (baselines .*)\x0a"
			match = re.search(pattern, data[find_more_base:].decode("latin-1"))
			if match:
				conn.append_string_to_reliable(f"\x04{match.group(1)}\x00")
				fail = False
		
		if fail:
			print("Ooops cannot enter server no precache dead end\n")
			player.endpoint.removePlayer(player)
	
	return None

	tmp2 = 0
	tmp = struct.unpack_from('<b',view,0)[0]
	view=view[1:]
	if tmp < 0:
		tmp = struct.unpack_from('<b',view,0)[0] << 8 | tmp
		view=view[1:]
	tmp2 = tmp
	if tmp2 < 0:
		tmp = struct.unpack_from('<b',view,0)[0] << 16 | tmp
		view=view[1:]
		tmp2 = tmp

	if tmp2 & 0x800000:
		tmp = struct.unpack_from('<b',view,0)[0] << 24 | tmp
		view=view[1:]
		tmp2 = tmp

	if tmp2 & 0x1000000:
		tmp3 = struct.unpack_from('<h',view,0)[0]
		view=view[2:]

	
	# delta_sequence
	tmp = struct.unpack_from('<l',view,0)[0]
	view=view[4:]
		
	# delta_entity
	tmp = struct.unpack_from('<h',view,0)[0]
	view=view[2:]

	# delta_flags
	delta_flags = struct.unpack_from('<b',view,0)[0]
	view=view[1:]
		
	if delta_flags & ENTITY_BITS:
		# this delta is for an entity
		delta_entity = MSG_ReadBits(read_buffer, MAX_EDICT_BITS)
		parsed_message['delta_entity'] = delta_entity

		# update the entity
		if delta_entity >= 0 and delta_entity < MAX_EDICTS:
			entities[delta_entity] = ParseDeltaEntity(read_buffer, entities[delta_entity])
		else:
			raise Exception("Invalid delta entity number")
	else:
		# this delta is for a client
		client_num = delta_entity - 1
		parsed_message['client_num'] = client_num

		if client_num >= MAX_CLIENTS:
			raise Exception("Invalid client number")

		# update the client state
		ParseDeltaClient(read_buffer, client_num, delta_flags, parsed_message)

		return parsed_message

	

def svc_centerprint(conn,player,view):
	return None

def svc_captionprint(conn,player,view):
	return None

def svc_download(conn,player,view):
	#print("PACKET: download\n")
	view=view[3:]

	if conn.i_downloading == 1:
		conn.append_string_to_reliable(f"\x04download {player.mapname}.sp\x00")
		conn.i_downloading += 1
	elif conn.i_downloading == 2:
		conn.append_string_to_reliable(f"\x04download {player.mapname}.wrs\x00")
		conn.i_downloading += 1
	elif conn.i_downloading == 3:
		conn.append_string_to_reliable(f"\x04sv_precache {player.precache}\x00")
		conn.i_downloading = 0;


	return view
def svc_playerinfo(conn,player,view):
	return None

def svc_packetentities(conn,player,view):
	return None

def svc_deltapacketentities(conn,player,view):
	return None

def svc_frame(conn,player,view):
	# print("svc_Frame")
	player.lastServerFrame = struct.unpack_from('<I',view,0)[0]
	# print(f"received frame = {self.bot.lastServerFrame}")
	view=view[4:]
	view=view[4:]
	view=view[4:]
	areabits = struct.unpack_from('<B',view,0)[0]
	view=view[1:]
	view=view[areabits:]
	cmd = struct.unpack_from('<B',view,0)[0]
	view=view[1:]

	# readPlayerState
	flags = struct.unpack_from('<I',view,0)[0]
	view=view[4:]
	if flags & PS_GUN:
		view=view[2:]
		view=view[1:]
	if flags & PS_GUN_CLIP:
		view=view[1:]
	if flags & PS_GUN_AMMO:
		view=view[2:]
	if flags & PS_GUN_RELOAD:
		view=view[1:]
	if flags & PS_RESTART_COUNT:
		view=view[1:]
	if flags & PS_BUTTONS_INHIBIT:
		view=view[1:]
	if flags & PS_BOD:
		view=view[2:]
	if flags & PS_M_TYPE:
		view=view[1:]
	if flags & PS_M_ORIGIN:
		view=view[2:]
		view=view[2:]
		view=view[2:] 
	if flags & PS_M_VELOCITY:
		view=view[2:]
		view=view[2:]
		view=view[2:]
	if flags & PS_M_TIME:
		view=view[1:]
	if flags & PS_M_FLAGS:
		view=view[1:]
	if flags & PS_M_GRAVITY:
		view=view[2:]
	if flags & PS_M_DELTA_ANGLES:
		player.delta_pitch = struct.unpack_from('<h',view[:2],0)[0]	
		view=view[2:]
		player.delta_yaw = struct.unpack_from('<h',view[:2],0)[0]
		view=view[2:]
		player.delta_roll = struct.unpack_from('<h',view[:2],0)[0]
		view=view[2:]
	# else:
		# player.delta_pitch = 0
	# print(f"delta_pitch = {player.delta_pitch}")
	if flags & PS_M_movESCALE:
		view=view[1:]
	if flags & PS_VIEWOFFSET:
		view=view[1:]
		view=view[1:]
		view=view[1:]
	if flags & PS_VIEWANGLES:
		view=view[2:]
		view=view[2:]
		view=view[2:]
	if flags & PS_REMOTE_VIEWANGLES:
		view=view[2:]
		view=view[2:]
		view=view[2:]
	if flags & PS_REMOTE_VIEWORIGIN:
		view=view[2:]
		view=view[2:]
		view=view[2:]
	if flags & PS_REMOTE_ID:
		view=view[1:]
		view=view[1:]
	if flags & PS_KICKANGLES:
		view=view[1:]
		view=view[1:]
		view=view[1:]
	if flags & PS_WEAPONKICKANGLES:
		view=view[1:]
	if flags & PS_BLEND:
		view=view[1:]
		view=view[1:]
		view=view[1:]
		view=view[1:]
	if flags & PS_FOV:
		view=view[1:]
	if flags & PS_RDFLAGS:
		view=view[1:]

	# Long
	statbits = struct.unpack_from('<i',view,0)[0]
	view=view[4:]
	
	#ParseStats
	# STAT_HEALTH = 1
	# STAT_ARMOUR = 5
	for k in range(16):
		if ( statbits & ( 1<<k) ):
			if k == 1:
				player.prev_health = player.health
				player.health = struct.unpack_from('<h',view,0)[0]
				dmg = player.prev_health - player.health
				if dmg > 0 and player.prev_health > 0:
					# print("LOSE HEALTH")
					dmgRatio = dmg/100
					j,low,high = getJoystick(low=0.6 + 0.4*dmgRatio)
					if j:
						j.rumble(low,high,round(100 + 400*dmgRatio))
						getJoystick(high=0)
			elif k == 5:
				"""
				player.prev_armor = player.armor
				player.armor = struct.unpack_from('<h',view,0)[0]
				if player.armor - player.prev_armor < 0 and player.prev_armor > 0:
					# print("LOSE ARMOR")
					getJoystick().rumble(1,0,100)
				"""
			view=view[2:]

	if flags & PS_CINEMATICFREEZE:
		view=view[1:]
	if flags & PS_MUSICID:
		view=view[1:]
	if flags & PS_AMBSOUNDID:
		view=view[2:]
	if flags & PS_DMRANK:
		view=view[1:]
		view=view[1:]
	if flags & PS_SPECTATORID:
		view=view[1:]

	
	cmd = struct.unpack_from('<B',view,0)[0]
	view=view[1:]

	# readEntities
	skinnum = 100;
	newnum = 0;
	entitycount = 0;
	while 1:
		skinnum = 100;
		flags = struct.unpack_from('<B',view,0)[0]
		view=view[1:]

		if flags & U_MOREBITS1:
			flags |= struct.unpack_from('<B',view,0)[0] << 8;
			view=view[1:]
		if flags & U_MOREBITS2:
			flags |= struct.unpack_from('<B',view,0)[0] << 16;
			view=view[1:]
		if flags & U_MOREBITS3:
			flags |= struct.unpack_from('<B',view,0)[0] << 24;
			view=view[1:]
		if flags & U_NUMBER16:
			newnum = struct.unpack_from('<h',view,0)[0]
			view=view[2:]
		else:
			newnum = struct.unpack_from('<B',view,0)[0]
			view=view[1:]
		if not newnum:
			break
		entitycount += 1

		if flags & U_MODEL:
			view=view[1:]
		if flags & U_RENDERMODEL:
			view=view[1:]
		if flags & U_FRAME8:
			view=view[1:]
		if flags & U_FRAME16:
			view=view[2:]
		if ( flags & (U_SKIN8|U_SKIN16) ) == (U_SKIN8|U_SKIN16):
			skinnum = struct.unpack_from('<i',view,0)[0]
			view=view[4:]
		elif flags & U_SKIN8:
			skinnum = struct.unpack_from('<b',view,0)[0]
			view=view[1:]
		elif flags & U_SKIN16:
			skinnum = struct.unpack_from('<h',view,0)[0]
			view=view[2:]
		if (flags & (U_EFFECTS8|U_EFFECTS16) ) == (U_EFFECTS8|U_EFFECTS16):
			view=view[4:]
		elif flags & U_EFFECTS8:
			view=view[1:]
		elif flags & U_EFFECTS16:
			view=view[2:]

		if ( flags & (U_RENDERFX8|U_RENDERFX16) ) == (U_RENDERFX8|U_RENDERFX16):
			view=view[4:]
		elif flags & U_RENDERFX8:
			view=view[1:]
		elif flags & U_RENDERFX16:
			view=view[2:]
		if flags & U_ORIGIN1:
			view=view[2:]
		if flags & U_ORIGIN2:
			view=view[2:]
		if flags & U_ORIGIN3:
			view=view[2:]
		if flags & U_ANGLE1:
			view=view[1:]
		if flags & U_ANGLE2:
			view=view[1:]
		if flags & U_ANGLEDIFF:
			view=view[1:]
		if flags & U_ANGLE3:
			view=view[1:]
		if flags & U_SOUND:
			view=view[1:]
			view=view[1:]
		if flags & U_EVENT:
			c = struct.unpack_from('<b',view,0)[0]
			view=view[1:]
			view=view[1:]
			if c < 0:
				c = struct.unpack_from('<b',view,0)[0]
				view=view[1:]
				view=view[1:]
				if c < 0:
					c = struct.unpack_from('<b',view,0)[0]
					view=view[1:]
					view=view[1:]

		if flags & U_SOLID:
			if skinnum == player.playernum:
				solid = struct.unpack_from('<i',view,0)[0]
			view=view[4:]
		if flags & U_EFFECT:
			x = struct.unpack_from('<h',view,0)[0]
			view=view[2:]
			for j in range(12):
				if x & (1<<j):
					view=view[2:]

	return view
def svc_culledEvent(conn,player,view):
	return None

def svc_damagetexture(conn,player,view):
	return None

def svc_ghoulreliable(conn,player,view):
	# print("PACKET: ghoul reliable\n")
	size = struct.unpack_from('<h',view,0)[0]
	view = view[2:]
	view = view[size:]

	return view

def svc_ghoulunreliable(conn,player,view):
	return None

def svc_ric(conn,player,view):
	return None

def svc_restart_predn(conn,player,view):
	return None

def svc_rebuild_pred_inv(conn,player,view):
	return None

def svc_countdown(conn,player,view):
	return None

def svc_cinprint(conn,player,view):
	return None

def svc_playernamecols(conn,player,view):
	return None
# [short] string index [color]
def svc_sp_print(conn,player,view):
	
	stringPackageIndex = view[0]
	view=view[1:]

	stringPackageId = view[0]
	view=view[1:]

	# color = view[0]
	# view=view[1:]

	# s,view = Parser.string(view)
	print(f"PACKET: sp_print : Index:{stringPackageIndex} Id:{stringPackageId}")
	return view

def svc_removeconfigstring(conn,player,view):
	return None

# [short] string index
# [byte] count of data bytes 
# [data bytes] 
# [color] at end of bytes
def svc_sp_print_data_1(conn,player,view):

	stringPackageIndex = view[0]
	view=view[1:]

	stringPackageId = view[0]
	view=view[1:]

	dataBytes=view[0]
	view=view[1:]

	data=view[:dataBytes]
	view=view[dataBytes:]

	# util.pretty_dump(data)

	# color = view[0]
	# view=view[1:]

	if stringPackageId == 0: #GENERAL
		if stringPackageIndex == 61:
			print(f"[GENERAL] {util.mem_to_str(data)} entered the game.")
	if stringPackageId == 17: #SOFPLUS
		if stringPackageIndex == 0:
			# slot == data[:4]
			print(f"[SOFPLUS] Incoming player [{struct.unpack_from('<i',data,0)[0]}]: {util.mem_to_str(data[4:-1])}")
		if stringPackageIndex == 21:
			s,_ = Parser.string(data)
			ss,_ = Parser.string(_)
			print(f"[SOFPLUS] Timelimit={util.mem_to_str(s)} Remaining={util.mem_to_str(ss)}")
	elif stringPackageId == 12: #BOT
		if stringPackageIndex == 4:
			print(f"[BOTS] {util.mem_to_str(data[4:-1])} disconnected.")
	elif stringPackageId == 18: #CUSTOM
		if stringPackageIndex == 12 or stringPackageIndex == 13 : #highscores
			print(f"[CUSTOM] {util.mem_to_str(data)}")

	print(f"PACKET: sp_print_data_1 : Id:{stringPackageId} Index:{stringPackageIndex} DataBytes:{dataBytes} Data:{data.tobytes()}")
	return view
# [short] string index 
# [short] count of data bytes 
# [data bytes] 
# [color] at end of bytes
def svc_sp_print_data_2(conn,player,view):

	stringPackageIndex = view[0]
	view=view[1:]

	stringPackageId = view[0]
	view=view[1:]

	dataBytes = struct.unpack_from('<H',view,0)[0]
	view=view[2:]
	# print(dataBytes)
	data=view[:dataBytes]
	view=view[dataBytes:]

	# util.pretty_dump(data)
	# color = view[0]
	# view=view[1:]

	
	print(f"PACKET: sp_print_data_2 : Id:{stringPackageId} Index:{stringPackageIndex} DataBytes:{dataBytes} Data:{data.tobytes()}")

	return view

def svc_welcomeprint(conn,player,view):
	s,view = Parser.string(view)
	s = util.mem_to_str(s)
	print("PACKET: welcomeprint\n",s)
	return view

def svc_sp_print_obit(conn,player,view):
	return None

def svc_force_con_notify(conn,player,view):
	return None



packet_parsers = {
	"svc_bad" : svc_bad,
	"svc_temp_entity" : svc_temp_entity,
	"svc_layout" : svc_layout,
	"svc_UNUSED" : svc_unused,
	"svc_sound_info" : svc_sound_info,
	"svc_effect" : svc_effect,
	"svc_equip" : svc_equip,
	"svc_nop" : svc_nop,
	"svc_disconnect" : svc_disconnect,
	"svc_reconnect" : svc_reconnect,
	"svc_sound" : svc_sound,
	"svc_print" : svc_print,
	"svc_nameprint" : svc_nameprint,
	"svc_stufftext" : svc_stufftext,
	"svc_serverdata" : svc_serverdata,
	"svc_configstring" : svc_configstring,
	"svc_spawnbaseline" : svc_spawnbaseline,
	"svc_centerprint" : svc_centerprint,
	"svc_captionprint" : svc_captionprint,
	"svc_download" : svc_download,
	"svc_playerinfo" : svc_playerinfo,
	"svc_packetentities" : svc_packetentities,
	"svc_deltapacketentities" : svc_deltapacketentities,
	"svc_frame" : svc_frame,
	"svc_culledEvent" : svc_culledEvent,
	"svc_damagetexture" : svc_damagetexture,
	"svc_ghoulreliable" : svc_ghoulreliable,
	"svc_ghoulunreliable" : svc_ghoulunreliable,
	"svc_ric" : svc_ric,
	"svc_restart_predn" : svc_restart_predn,
	"svc_rebuild_pred_inv" : svc_rebuild_pred_inv,
	"svc_countdown" : svc_countdown,
	"svc_cinprint" : svc_cinprint,
	"svc_playernamecols" : svc_playernamecols,
	"svc_sp_print" : svc_sp_print,
	"svc_removeconfigstring" : svc_removeconfigstring,
	"svc_sp_print_data_1" : svc_sp_print_data_1,
	"svc_sp_print_data_2" : svc_sp_print_data_2,
	"svc_welcomeprint" : svc_welcomeprint,
	"svc_sp_print_obit" : svc_sp_print_obit,
	"svc_force_con_notify" : svc_force_con_notify
}


