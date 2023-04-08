import struct
import hashlib
import time
from sof.packets.defines import *

yaw = 2047;
roll = 0;
pitch = 2048; # 0 = look flat //  2047 = down_max // 2048 = up_max
one = bytes((1,))
zero = bytes((0,))

bitpos = 0

# out_bytearray, in_bytearray, in_bits
def dataToBits(stream, indata, bits, nosign=True):
	global bitpos
		
	for i in range(bits):
		# convert bitpos into byte?
		currentByte = bitpos // 8
		inByte = i // 8
		# get the bit from inshort , grab it from right to left (normal)
		targetbit = indata[inByte] & (1<<(i % 8))

		# printf("byte %i bit %i before : %02X\n",currentByte,bitpos,stream[currentByte]);


		# pick teh bit from the right to left (normal)
		# unsigned char out_bitmask = one << (7-(bitpos % 8));
		out_bitmask = 1 << (bitpos % 8)
		# is it a 1 or a 0 ?
		if targetbit:
			# case BIT is 1
			# printf("its 1\n");
			# write the bit to the stream
			# print(f"current byte = {currentByte}\n")
			# print(f"out_bitmask = {out_bitmask}\n")

			stream[currentByte] = stream[currentByte] | out_bitmask
		else:
			# case BIT is 0
			# printf("its 0\n");
			# write the bit to the stream
			stream[currentByte] = stream[currentByte] & ~out_bitmask
		bitpos += 1

	return bits

# moveUp is less.
def tenbit(n):
	# n = n * 0.01 * 510
	return 510 + int(n)

def simpleDeltaUsercmd(player,bitbuffer):
	bits_written = 0

	bits_written += dataToBits(append_bitbuffer,zero,1)
	bits_written += dataToBits(append_bitbuffer,zero,1)
	bits_written += dataToBits(append_bitbuffer,zero,1)

	bits_written += dataToBits(append_bitbuffer,zero,1)
	bits_written += dataToBits(append_bitbuffer,zero,1)
	bits_written += dataToBits(append_bitbuffer,zero,1)

	# buttons,lean,light
	bits_written += dataToBits(append_bitbuffer,one,1)
	bits_written += dataToBits(append_bitbuffer,zero,8)
	bits_written += dataToBits(append_bitbuffer,zero,1)
	bits_written += dataToBits(append_bitbuffer,zero,1)

	# msec
	bits_written += dataToBits(append_bitbuffer,bytes((20,)),8)

	# prediction_fire
	bits_written += dataToBits(append_bitbuffer,zero,1)
	bits_written += dataToBits(append_bitbuffer,zero,1)

	return bits_written

"""
1 [pitch]
111111000000 [pitch]
1 [yaw]
111111000000 [yaw]
1 [roll]
111111000000 [roll]

1 [fwd]
0110001101 [fwd]
1 [upmove]
0111100101 [upmove]
1 [side]
0110001101 [side]

1 [buttons]
11111111 [buttons]
0 [lean]
0001010 [lightlevel 7bit]

001000000000000000000000001111111 [fire1 32b float]

001000000000000000000000001111111 [fire2 32b float]

00000 [When lean is active, msec shrinks by 1 bit]
"""

# ----------------------------------------------------
	# -2048 == looking up ( protection bug )
	# -2047 == looking up
	# NEGATIVE == UP
	#  0 = flat ( 2048 looking up, 2047 lookoing down)
	# POSITIVE == DOWN
	# 2047 == looking down ( protection bug )
	# 2048 == looking up ( protection bug)
# ----------------------------------------------------
	# 65536 / 4096 = 16
	# delta pitch is in 65536 ( 16 bits )
	# convert to 12 bits ( 4096 )

# -2048 -> 2047
# since it writes bits, bitpos is handling the position
# Shooting with BUTTON_ATTACK requires predicting cvar 0.

# max packet size in bytes and bits?
# 163 bits
# 20 bytes remainder 3
# 21 bytes


# TODO : CANNOT MOVE DIAGONALLY.
def deltaUsercmd(player,bitbuffer):

	bits_written = 0

	time_now = time.time()

	state = player.uc_now
	d = bytearray(4)

	# will compare state.before with state.now

	if state.lookUp:
		state.pitch -= player.pitch_speed
		if state.pitch < -2048 :
			state.pitch += 4096
	elif state.lookDown:
		state.pitch += player.pitch_speed
		if state.pitch > 2047:
			state.pitch -= 4096

	if player.custom_pitch != 9999:
		state.pitch = player.custom_pitch

	# this this causes bug for player assume always have to send?
	# if state.pitch_before != state.pitch:
	# changed
	network_pitch = state.pitch - (player.delta_pitch // 16)
	if network_pitch < -2048:
		network_pitch += 4096
	elif network_pitch > 2047:
		network_pitch -= 4096

	bits_written += dataToBits(bitbuffer,one,1)
	struct.pack_into('<h',d,0,network_pitch)
	bits_written += dataToBits(bitbuffer,d,12)
	# else:
	# 	bits_written += dataToBits(bitbuffer,zero,1)

	# /*
	# **************************YAW*********************************
	# */
	
	if state.lookRight:
		state.yaw -= player.yaw_speed
		if state.yaw < -2048 :
			state.yaw += 4096
	elif state.lookLeft:
		state.yaw += player.yaw_speed
		if state.yaw > 2047:
			state.yaw -= 4096

	if player.custom_yaw != 9999:
		state.yaw = player.custom_yaw

	# if state.yaw_before != state.yaw:
	# 	# changed
	network_yaw = state.yaw - (player.delta_yaw // 16)
	if network_yaw < -2048:
		network_yaw += 4096
	elif network_yaw > 2047:
		network_yaw -= 4096

	bits_written += dataToBits(bitbuffer,one,1)
	struct.pack_into('<h',d,0,network_yaw)
	bits_written += dataToBits(bitbuffer,d,12)
	
	# else:
	# 	# this resets aim? == bad?
	# 	bits_written += dataToBits(bitbuffer,zero,1)
	# 
	# **************************ROLL*********************************
	# */
	# ROLL_ANGLE  -2047 -> 2047 AKA 0 -> 4095
	
	if state.rollRight:
		state.roll -= player.roll_speed
		if state.roll < -2048 :
			state.roll += 4096
	elif state.rollLeft:
		state.roll += player.roll_speed
		if state.roll > 2047:
			state.roll -= 4096

	if player.custom_roll != 9999:
		state.roll = player.custom_roll

	# if state.roll_before != state.roll:
	network_roll = state.roll - (player.delta_roll // 16)
	if network_roll < -2048:
		network_roll += 4096
	elif network_roll > 2047:
		network_roll -= 4096

	bits_written += dataToBits(bitbuffer,one,1)
	struct.pack_into('<h',d,0,network_roll)
	bits_written += dataToBits(bitbuffer,d,12)
	# else:
	# 	bits_written += dataToBits(bitbuffer,zero,1)
	# 
	# **************************FORWARDMOVE*********************************
	# 
	if state.moveBack:
		bits_written += dataToBits(bitbuffer,one,1)
		struct.pack_into('<H',d,0,tenbit(-200))
		# struct.pack_into('<h',d,0,-200)
		bits_written += dataToBits(bitbuffer,d,10)
	elif state.moveForward:
		bits_written += dataToBits(bitbuffer,one,1)
		struct.pack_into('<H',d,0,tenbit(200))
		# struct.pack_into('<h',d,0,200)
		bits_written += dataToBits(bitbuffer,d,10)
	else:
		# IMPORTANT TO INIT CHARACTER CORRECTLY (REFUSES TO MOVE + INVIS)
		bits_written += dataToBits(bitbuffer,zero,1)
		# bits_written += dataToBits(bitbuffer,one,1)
		# struct.pack_into('<H',d,0,tenbit(0))
		# bits_written += dataToBits(bitbuffer,d,10)
	
	# /*
	# **************************SIDEMOVE*********************************
	# */
	if state.moveLeft:
		# optional
		bits_written += dataToBits(bitbuffer,one,1)
		struct.pack_into('<H',d,0,tenbit(-160))
		# struct.pack_into('<h',d,0,-160)
		# non-optional
		bits_written += dataToBits(bitbuffer,d,10)
	elif state.moveRight:
		# optional
		bits_written += dataToBits(bitbuffer,one,1)
		struct.pack_into('<H',d,0,tenbit(160))
		# struct.pack_into('<h',d,0,160)
		# non-optional
		bits_written += dataToBits(bitbuffer,d,10)
	else:
		# THIS IS IMPORTANT TO INIT THE CHARACTER CORRECTLY (REFUSES TO MOVE + INVIS)
		bits_written += dataToBits(bitbuffer,zero,1)
		# bits_written += dataToBits(bitbuffer,one,1)
		# struct.pack_into('<H',d,0,tenbit(0))
		# bits_written += dataToBits(bitbuffer,d,10)
		

	# /*
	# **************************UPMOVE*********************************
	# */ I believe this -160 -> 160
	if state.moveUp:
		bits_written += dataToBits(bitbuffer,one,1)
		struct.pack_into('<H',d,0,tenbit(200))
		# struct.pack_into('<h',d,0,200)
		bits_written += dataToBits(bitbuffer,d,10)
	elif state.moveDown:
		bits_written += dataToBits(bitbuffer,one,1)
		# struct.pack_into('<h',d,0,-200)
		struct.pack_into('<H',d,0,tenbit(-200))
		bits_written += dataToBits(bitbuffer,d,10)
	else:
		bits_written += dataToBits(bitbuffer,one,1)
		struct.pack_into('<H',d,0,tenbit(0))
		bits_written += dataToBits(bitbuffer,d,10)

		# player always running ( never lands ) == bad
		# bits_written += dataToBits(bitbuffer,zero,1)

	# using fireEvent as the control variable for firing
	# NON-PREDICTING FIRE
	# if not player.isPredicting
	"""
		If you don't send 1 frame of not attacking for every
		attack, it will give bad checksum.
	"""
	
	# always turn this off?
	state.buttonsPressed &= ~BUTTON_ATTACK
	# only touch BUTTON_ATTACK when predicting is off
	if not player.isPredicting:
		if state.fireEvent and player.internal_allowed_to_fire_basic:
			state.buttonsPressed |= BUTTON_ATTACK
			player.internal_allowed_to_fire_basic = False
		else:
			player.internal_allowed_to_fire_basic = True
			
	else:
		# predicting death respawn
		if state.dead >= 2:
			state.dead -= 1
			if state.dead % 2 == 0:
				state.buttonsPressed |= BUTTON_ATTACK
			else:
				state.buttonsPressed &= ~BUTTON_ATTACK


	# BUTTONS
	if state.buttonsPressed:
		bits_written += dataToBits(bitbuffer,one,1)
		b = bytes((state.buttonsPressed,))
		bits_written += dataToBits(bitbuffer,b,8)
	else:
		bits_written += dataToBits(bitbuffer,zero,1)

	# LEAN - reduces msec by 1 bit when active
	if state.leanLeft:
		bits_written += dataToBits(bitbuffer,one,1)
		bits_written += dataToBits(bitbuffer,zero,1)
	elif state.leanRight:
		bits_written += dataToBits(bitbuffer,one,1)
		bits_written += dataToBits(bitbuffer,one,1)
	else:
		bits_written += dataToBits(bitbuffer,zero,1)
	

	# [But][Lean][Light][Msec][FF][5?]
	# /*
	# **************************LIGHTLEVEL*********************************
	# */
	# lightlevel - used for visibility a.i of computer to target you?


	bits_written += dataToBits(bitbuffer,one,1)
	state.lightLevel = 20
	b = bytes((state.lightLevel,))
	bits_written += dataToBits(bitbuffer,b,5)

	b = bytes((state.msec,))
	bits_written += dataToBits(bitbuffer,b,8)
	
	"""
	Seems they control the rate of fire by not allowing you to fire 2 consecutive packets
	Lets simulate fast toggle then
	"""
	if player.isPredicting and state.fireEvent and player.internal_allowed_to_fire >= 2:
	# if player.isPredicting and state.fireEvent and time_now - player.internal_allowed_to_fire_timer > 0.1:
		# want to fire
		val = 1.0
		bits_written += dataToBits(bitbuffer,one,1)
		struct.pack_into('<f',d,0,val)
		bits_written += dataToBits(bitbuffer,d,32)
		# player.internal_allowed_to_fire_timer = time.time()
		player.internal_allowed_to_fire = 0
	# do not want to fire or not allowed to fire
	else:
		# 2 frames inactive
		player.internal_allowed_to_fire += 1
		bits_written += dataToBits(bitbuffer,zero,1)
		
	if player.isPredicting and state.altFireEvent and player.internal_allowed_to_fire2:
		# state.fireEvent forced to default 0.0 every frame
		
		val = 1.0
		bits_written += dataToBits(bitbuffer,one,1)
		struct.pack_into('<f',d,0,val)
		bits_written += dataToBits(bitbuffer,d,32)
		player.internal_allowed_to_fire2 = False
	else:
		player.internal_allowed_to_fire2 = True
		bits_written += dataToBits(bitbuffer,zero,1)

	# QUESTION OF WHETHER IT EXPECTS TOGGLE BEHAVIOR
	# if fireEvent is a toggle, no need for before check
	# state.fire_before = state.fireEvent
	# state.fireEvent = 0.0

	state.pitch_before = state.pitch
	state.yaw_before = state.yaw
	state.roll_before = state.roll

	state.fire_before = state.fireEvent
	state.buttons_before = state.buttonsPressed

	return bits_written


def completeUserCommandBitBuffer(player,return_buffer):
	# assume points to the next bit to write ( thus is bit count )
	global bitpos
	bitpos = 0

	bitpos_now = bitpos
	bits = deltaUsercmd(player,return_buffer)
	bits = deltaUsercmd(player,return_buffer)
	bits = deltaUsercmd(player,return_buffer)

	# bytesWritten = (bitpos+7)//8
	bytesWritten = bitpos//8
	# print(f"BYTES WRITTEN = {bytesWritten}")
	return bytesWritten

chktbl2 = b'\x60\xe5\x60\x3e\x00\x00\x00\x00\xdf\xbf\x79\x3f\x61\xfe\x8a\x3d\x54\xe3\x55\x3e\xdf\xbf\x79\x3f\xa1\x67\xdb\x3e\x00\x00\x00\x00\xbe\x4d\x67\x3f\xe5\x62\x94\x3e\x5a\x9e\x57\x3e\x82\x02\x6f\x3f\x5f\x99\x07\x3e\x86\xaa\xd0\x3e\xbe\x4d\x67\x3f\xf2\xd2\x1d\x3f\x00\x00\x00\x00\x19\x90\x49\x3f\x2b\x89\x00\x3f\x20\x7f\x59\x3e\x88\x9c\x56\x3f\x6a\xdd\xb6\x3e\x76\xe2\xd2\x3e\x88\x9c\x56\x3f\xcb\x14\x43\x3e\x76\x19\x16\x3f\x19\x90\x49\x3f\x1d\x3d\x46\x3f\x00\x00\x00\x00\xca\xfa\x21\x3f\xb8\xe4\x30\x3f\xe2\xca\x59\x3e\xa9\xdc\x30\x3f\xf1\xb7\x11\x3f\xbe\xbd\xd3\x3e\x89\xea\x35\x3f\x86\xe4\xd4\x3e\x01\x69\x17\x3f\xa9\xdc\x30\x3f\x7d\x09\x75\x3e\x4c\x89\x3c\x3f\xca\xfa\x21\x3f\x2b\xf9\x64\x3f\x00\x00\x00\x00\x3c\xf9\xe4\x3e\xe9\x9c\x57\x3f\x54\xe3\x55\x3e\x64\x76\xfe\x3e\x49\xb9\x3f\x3f\x86\xaa\xd0\x3e\x59\xc3\x05\x3f\x03\x79\x1e\x3f\x76\x19\x16\x3f\x59\xc3\x05\x3f\x4d\xf7\xea\x3e\x4c\x89\x3c\x3f\x64\x76\xfe\x3e\x62\x83\x8d\x3e\x44\xc4\x59\x3f\x3c\xf9\xe4\x3e\xbf\xf1\x35\xbe\xb1\x30\x04\x3e\xdf\xbf\x79\x3f\xae\xb6\xe2\xbd\x5d\x70\xae\x3e\x82\x02\x6f\x3f\x91\x80\xb1\xbe\x8c\xf6\x80\x3e\xbe\x4d\x67\x3f\xb0\xe3\x3f\xbd\x13\x0c\x0b\x3f\x78\x9c\x56\x3f\x06\x0e\x90\xbe\xfd\x14\xef\x3e\x78\x9c\x56\x3f\x57\x5d\xff\xbe\x6e\x88\xb9\x3e\x19\x90\x49\x3f\xba\x4d\x38\x3c\xa6\x0f\x39\x3f\xa9\xdc\x30\x3f\x59\xa3\x5e\xbe\x6a\x4d\x2b\x3f\x89\xea\x35\x3f\x4c\x36\xde\xbe\x5b\x06\x14\x3f\xa9\xdc\x30\x3f\xee\x60\x20\xbf\x20\x0b\xe9\x3e\xca\xfa\x21\x3f\xea\x5d\x7c\x3d\x79\x95\x5d\x3f\x64\x76\xfe\x3e\x57\xec\x1f\xbe\xbc\x94\x56\x3f\x59\xc3\x05\x3f\x86\x90\xbb\xbe\x8b\x19\x45\x3f\x59\xc3\x05\x3f\x21\x01\x0f\xbf\x76\xfe\x29\x3f\x64\x76\xfe\x3e\x4f\x3e\x39\xbf\x4f\x96\x06\x3f\x3c\xf9\xe4\x3e\xbf\xf1\x35\xbe\xb1\x30\x04\xbe\xdf\xbf\x79\x3f\x72\x6a\xb7\xbe\x00\x00\x00\x00\x82\x02\x6f\x3f\x91\x80\xb1\xbe\x8c\xf6\x80\xbe\xbe\x4d\x67\x3f\xa1\xf2\x07\xbf\x6b\x7e\xfc\x3d\x78\x9c\x56\x3f\xa1\xf2\x07\xbf\xf1\x7e\xfc\xbd\x78\x9c\x56\x3f\x57\x5d\xff\xbe\x6e\x88\xb9\xbe\x19\x90\x49\x3f\x1d\x1d\x2f\xbf\xfa\xb3\x6f\x3e\xa9\xdc\x30\x3f\x36\x1e\x34\xbf\x00\x00\x00\x00\x89\xea\x35\x3f\x1d\x1d\x2f\xbf\x3e\xb4\x6f\xbe\xa9\xdc\x30\x3f\xdd\x60\x20\xbf\x20\x0b\xe9\xbe\xca\xfa\x21\x3f\x5d\xdd\x4d\xbf\xc7\xf2\xa6\x3e\x64\x76\xfe\x3e\xf4\x6e\x58\xbf\x0f\x48\xe2\x3d\x59\xc3\x05\x3f\xf4\x6e\x58\xbf\x0f\x48\xe2\xbd\x59\xc3\x05\x3f\x5d\xdd\x4d\xbf\xc7\xf2\xa6\xbe\x64\x76\xfe\x3e\x4f\x3e\x39\xbf\x4f\x96\x06\xbf\x3c\xf9\xe4\x3e\x61\xfe\x8a\x3d\x54\xe3\x55\xbe\xdf\xbf\x79\x3f\xae\xb6\xe2\xbd\x5d\x70\xae\xbe\x82\x02\x6f\x3f\xa2\x99\x07\x3e\x86\xaa\xd0\xbe\xbe\x4d\x67\x3f\x06\x0e\x90\xbe\xfd\x14\xef\xbe\x88\x9c\x56\x3f\xb0\xe3\x3f\xbd\x13\x0c\x0b\xbf\x88\x9c\x56\x3f\xcb\x14\x43\x3e\x76\x19\x16\xbf\x19\x90\x49\x3f\x4c\x36\xde\xbe\x5b\x06\x14\xbf\x98\xdc\x30\x3f\x59\xa3\x5e\xbe\x6a\x4d\x2b\xbf\x89\xea\x35\x3f\xba\x4d\x38\x3c\xa6\x0f\x39\xbf\x98\xdc\x30\x3f\x7d\x09\x75\x3e\x4c\x89\x3c\xbf\xca\xfa\x21\x3f\x21\x01\x0f\xbf\x76\xfe\x29\xbf\x64\x76\xfe\x3e\x86\x90\xbb\xbe\x8b\x19\x45\xbf\x59\xc3\x05\x3f\x57\xec\x1f\xbe\xbc\x94\x56\xbf\x59\xc3\x05\x3f\xf6\x5e\x7c\x3d\x79\x95\x5d\xbf\x64\x76\xfe\x3e\x62\x83\x8d\x3e\x44\xc4\x59\xbf\x3c\xf9\xe4\x3e\xe5\x62\x94\x3e\x5a\x9e\x57\xbe\x82\x02\x6f\x3f\x6a\xdd\xb6\x3e\x76\xe2\xd2\xbe\x78\x9c\x56\x3f\x2b\x89\x00\x3f\x20\x7f\x59\xbe\x78\x9c\x56\x3f\x86\xe4\xd4\x3e\x01\x69\x17\xbf\x98\xdc\x30\x3f\xf1\xb7\x11\x3f\xbe\xbd\xd3\xbe\x89\xea\x35\x3f\xb8\xe4\x30\x3f\xe2\xca\x59\xbe\x98\xdc\x30\x3f\x4d\xf7\xea\x3e\x4c\x89\x3c\xbf\x64\x76\xfe\x3e\x03\x79\x1e\x3f\x76\x19\x16\xbf\x59\xc3\x05\x3f\x49\xb9\x3f\x3f\x86\xaa\xd0\xbe\x59\xc3\x05\x3f\xe9\x9c\x57\x3f\x54\xe3\x55\xbe\x64\x76\xfe\x3e\x8c\xb9\x73\x3f\xb1\x30\x04\xbe\xd5\x03\x8e\x3e\x8c\xb9\x73\x3f\xb1\x30\x04\x3e\xd5\x03\x8e\x3e\x3a\x93\x76\x3f\x6a\xf6\x80\xbe\x42\x7c\xc0\x3d\x36\xca\x7e\x3f\x00\x00\x00\x00\x54\xe6\xc6\x3d\x29\x93\x76\x3f\x8c\xf6\x80\x3e\x42\x7c\xc0\x3d\x7c\x62\x6d\x3f\x6e\x88\xb9\xbe\x42\x7c\xc0\xbd\x7b\xc0\x7c\x3f\x6b\x7e\xfc\xbd\x8c\xf2\xcc\xbd\x7b\xc0\x7c\x3f\xf1\x7e\xfc\x3d\x8c\xf2\xcc\xbd\x7c\x62\x6d\x3f\x6e\x88\xb9\x3e\x42\x7c\xc0\xbd\x35\x9a\x58\x3f\x20\x0b\xe9\xbe\xd5\x03\x8e\xbe\xd8\x80\x6c\x3f\xfa\xb3\x6f\xbe\x13\x10\x9b\xbe\x0f\x43\x73\x3f\x00\x00\x00\x00\x80\x7e\x9f\xbe\xd8\x80\x6c\x3f\x3e\xb4\x6f\x3e\x13\x10\x9b\xbe\x35\x9a\x58\x3f\x20\x0b\xe9\x3e\xd5\x03\x8e\xbe\x4f\x3e\x39\x3f\x4f\x96\x06\xbf\x3c\xf9\xe4\xbe\x5d\xdd\x4d\x3f\xc7\xf2\xa6\xbe\x64\x76\xfe\xbe\xf4\x6e\x58\x3f\x0f\x48\xe2\xbd\x59\xc3\x05\xbf\xf4\x6e\x58\x3f\x0f\x48\xe2\x3d\x59\xc3\x05\xbf\x5d\xdd\x4d\x3f\xc7\xf2\xa6\x3e\x64\x76\xfe\xbe\x4f\x3e\x39\x3f\x4f\x96\x06\x3f\x3c\xf9\xe4\xbe\x9e\x7d\xd5\x3e\x79\x95\x5d\x3f\xd5\x03\x8e\x3e\x4c\x8a\x2f\x3e\x21\x02\x72\x3f\xd5\x03\x8e\x3e\x7b\x85\x09\x3f\xbc\x94\x56\x3f\x42\x7c\xc0\x3d\xfb\x77\x9d\x3e\xd2\x51\x72\x3f\x54\xe6\xc6\x3d\xa2\xec\x6d\x3d\xb9\x6e\x7e\x3f\x42\x7c\xc0\x3d\x03\x95\x21\x3f\x8b\x19\x45\x3f\x42\x7c\xc0\xbd\x64\x3e\xd8\x3e\xdc\xa0\x66\x3f\x8c\xf2\xcc\xbd\xa7\x59\x40\x3e\x70\x22\x7a\x3f\x8c\xf2\xcc\xbd\xa2\xec\x6d\xbd\xb9\x6e\x7e\x3f\x42\x7c\xc0\xbd\xa9\xc0\x31\x3f\x76\xfe\x29\x3f\xd5\x03\x8e\xbe\x90\x13\x02\x3f\xe4\x68\x4e\x3f\x13\x10\x9b\xbe\x1d\x58\x96\x3e\x1d\x5b\x67\x3f\x80\x7e\x9f\xbe\x99\xb9\x80\x3d\x2e\x72\x73\x3f\x13\x10\x9b\xbe\x4c\x8a\x2f\xbe\x21\x02\x72\x3f\xd5\x03\x8e\xbe\x21\x01\x0f\x3f\x76\xfe\x29\x3f\x64\x76\xfe\xbe\x86\x90\xbb\x3e\x8b\x19\x45\x3f\x59\xc3\x05\xbf\x57\xec\x1f\x3e\xbc\x94\x56\x3f\x59\xc3\x05\xbf\xea\x5d\x7c\xbd\x79\x95\x5d\x3f\x64\x76\xfe\xbe\x62\x83\x8d\xbe\x44\xc4\x59\x3f\x3c\xf9\xe4\xbe\xa9\xc0\x31\xbf\x76\xfe\x29\x3f\xd5\x03\x8e\x3e\x35\x9a\x58\xbf\x20\x0b\xe9\x3e\xd5\x03\x8e\x3e\x03\x95\x21\xbf\x8b\x19\x45\x3f\x42\x7c\xc0\x3d\x21\x21\x4e\xbf\x05\xc3\x15\x3f\x54\xe6\xc6\x3d\x7c\x62\x6d\xbf\x6e\x88\xb9\x3e\x42\x7c\xc0\x3d\x7b\x85\x09\xbf\xbc\x94\x56\x3f\x42\x7c\xc0\xbd\xd0\xed\x39\xbf\x11\x19\x2e\x3f\x8c\xf2\xcc\xbd\x46\x08\x5f\xbf\x3d\x0f\xf6\x3e\x8c\xf2\xcc\xbd\x3a\x93\x76\xbf\x6a\xf6\x80\x3e\x42\x7c\xc0\xbd\x9e\x7d\xd5\xbe\x79\x95\x5d\x3f\xd5\x03\x8e\xbe\x93\x1c\x1c\xbf\x80\x7e\x3b\x3f\x13\x10\x9b\xbe\x96\xcd\x44\xbf\x59\xfc\x0e\x3f\x80\x7e\x9f\xbe\x08\x8f\x62\xbf\x6f\x10\xb5\x3e\x13\x10\x9b\xbe\x8c\xb9\x73\xbf\xb1\x30\x04\x3e\xd5\x03\x8e\xbe\x4d\xf7\xea\xbe\x4c\x89\x3c\x3f\x64\x76\xfe\xbe\x03\x79\x1e\xbf\x76\x19\x16\x3f\x59\xc3\x05\xbf\x49\xb9\x3f\xbf\x86\xaa\xd0\x3e\x59\xc3\x05\xbf\xe9\x9c\x57\xbf\x54\xe3\x55\x3e\x64\x76\xfe\xbe\x2b\xf9\x64\xbf\x00\x00\x00\x00\x3c\xf9\xe4\xbe\x35\x9a\x58\xbf\x20\x0b\xe9\xbe\xd5\x03\x8e\x3e\xa9\xc0\x31\xbf\x76\xfe\x29\xbf\xd5\x03\x8e\x3e\x6b\x62\x6d\xbf\x6e\x88\xb9\xbe\x42\x7c\xc0\x3d\x21\x21\x4e\xbf\x05\xc3\x15\xbf\x54\xe6\xc6\x3d\x03\x95\x21\xbf\x8b\x19\x45\xbf\x42\x7c\xc0\x3d\x3a\x93\x76\xbf\x8c\xf6\x80\xbe\x42\x7c\xc0\xbd\x46\x08\x5f\xbf\x3d\x0f\xf6\xbe\x8c\xf2\xcc\xbd\xd0\xed\x39\xbf\x11\x19\x2e\xbf\x8c\xf2\xcc\xbd\x7b\x85\x09\xbf\xbc\x94\x56\xbf\x42\x7c\xc0\xbd\x8c\xb9\x73\xbf\xb1\x30\x04\xbe\xd5\x03\x8e\xbe\x08\x8f\x62\xbf\x6f\x10\xb5\xbe\x13\x10\x9b\xbe\x96\xcd\x44\xbf\x59\xfc\x0e\xbf\x80\x7e\x9f\xbe\x93\x1c\x1c\xbf\x80\x7e\x3b\xbf\x13\x10\x9b\xbe\x9e\x7d\xd5\xbe\x79\x95\x5d\xbf\xd5\x03\x8e\xbe\xe9\x9c\x57\xbf\x97\xe3\x55\xbe\x64\x76\xfe\xbe\x49\xb9\x3f\xbf\x86\xaa\xd0\xbe\x59\xc3\x05\xbf\x03\x79\x1e\xbf\x76\x19\x16\xbf\x59\xc3\x05\xbf\x4d\xf7\xea\xbe\x4c\x89\x3c\xbf\x64\x76\xfe\xbe\x62\x83\x8d\xbe\x44\xc4\x59\xbf\x3c\xf9\xe4\xbe\x4c\x8a\x2f\x3e\x21\x02\x72\xbf\xd5\x03\x8e\x3e\x9e\x7d\xd5\x3e\x79\x95\x5d\xbf\xd5\x03\x8e\x3e\xa2\xec\x6d\x3d\xb9\x6e\x7e\xbf\x42\x7c\xc0\x3d\xfb\x77\x9d\x3e\xd2\x51\x72\xbf\x54\xe6\xc6\x3d\x7b\x85\x09\x3f\xab\x94\x56\xbf\x42\x7c\xc0\x3d\xa2\xec\x6d\xbd\xb9\x6e\x7e\xbf\x42\x7c\xc0\xbd\xa7\x59\x40\x3e\x70\x22\x7a\xbf\x8c\xf2\xcc\xbd\x64\x3e\xd8\x3e\xcb\xa0\x66\xbf\x8c\xf2\xcc\xbd\x03\x95\x21\x3f\x7a\x19\x45\xbf\x42\x7c\xc0\xbd\x4c\x8a\x2f\xbe\x21\x02\x72\xbf\xd5\x03\x8e\xbe\x99\xb9\x80\x3d\x2e\x72\x73\xbf\x13\x10\x9b\xbe\x1d\x58\x96\x3e\x1d\x5b\x67\xbf\x80\x7e\x9f\xbe\x90\x13\x02\x3f\xe4\x68\x4e\xbf\x13\x10\x9b\xbe\xa9\xc0\x31\x3f\x76\xfe\x29\xbf\xd5\x03\x8e\xbe\xea\x5d\x7c\xbd\x79\x95\x5d\xbf\x64\x76\xfe\xbe\x57\xec\x1f\x3e\xbc\x94\x56\xbf\x59\xc3\x05\xbf\x86\x90\xbb\x3e\x8b\x19\x45\xbf\x59\xc3\x05\xbf\x21\x01\x0f\x3f\x76\xfe\x29\xbf\x64\x76\xfe\xbe\x21\x21\x4e\x3f\x05\xc3\x15\x3f\x54\xe6\xc6\xbd\xd0\xed\x39\x3f\x11\x19\x2e\x3f\x8c\xf2\xcc\x3d\x46\x08\x5f\x3f\x3d\x0f\xf6\x3e\x8c\xf2\xcc\x3d\x93\x1c\x1c\x3f\x80\x7e\x3b\x3f\x13\x10\x9b\x3e\x96\xcd\x44\x3f\x59\xfc\x0e\x3f\x80\x7e\x9f\x3e\x08\x8f\x62\x3f\x6f\x10\xb5\x3e\x13\x10\x9b\x3e\xfb\x77\x9d\xbe\xd2\x51\x72\x3f\x54\xe6\xc6\xbd\x64\x3e\xd8\xbe\xcb\xa0\x66\x3f\x8c\xf2\xcc\x3d\xa7\x59\x40\xbe\x70\x22\x7a\x3f\x8c\xf2\xcc\x3d\x90\x13\x02\xbf\xe4\x68\x4e\x3f\x13\x10\x9b\x3e\x1d\x58\x96\xbe\x1d\x5b\x67\x3f\x80\x7e\x9f\x3e\x99\xb9\x80\xbd\x2e\x72\x73\x3f\x13\x10\x9b\x3e\x36\xca\x7e\xbf\x00\x00\x00\x00\x54\xe6\xc6\xbd\x7b\xc0\x7c\xbf\xf1\x7e\xfc\xbd\x8c\xf2\xcc\x3d\x7b\xc0\x7c\xbf\x6b\x7e\xfc\x3d\x8c\xf2\xcc\x3d\xd8\x80\x6c\xbf\x3e\xb4\x6f\xbe\x13\x10\x9b\x3e\x0f\x43\x73\xbf\x00\x00\x00\x00\x80\x7e\x9f\x3e\xd8\x80\x6c\xbf\xfa\xb3\x6f\x3e\x13\x10\x9b\x3e\xfb\x77\x9d\xbe\xd2\x51\x72\xbf\x54\xe6\xc6\xbd\xa7\x59\x40\xbe\x70\x22\x7a\xbf\x8c\xf2\xcc\x3d\x64\x3e\xd8\xbe\xdc\xa0\x66\xbf\x8c\xf2\xcc\x3d\x99\xb9\x80\xbd\x2e\x72\x73\xbf\x13\x10\x9b\x3e\x1d\x58\x96\xbe\x1d\x5b\x67\xbf\x80\x7e\x9f\x3e\x90\x13\x02\xbf\xe4\x68\x4e\xbf\x13\x10\x9b\x3e\x21\x21\x4e\x3f\xf4\xc2\x15\xbf\x54\xe6\xc6\xbd\x46\x08\x5f\x3f\x3d\x0f\xf6\xbe\x8c\xf2\xcc\x3d\xd0\xed\x39\x3f\x11\x19\x2e\xbf\x8c\xf2\xcc\x3d\x08\x8f\x62\x3f\x6f\x10\xb5\xbe\x13\x10\x9b\x3e\x96\xcd\x44\x3f\x59\xfc\x0e\xbf\x80\x7e\x9f\x3e\x93\x1c\x1c\x3f\x80\x7e\x3b\xbf\x13\x10\x9b\x3e\x61\xfe\x8a\xbd\x54\xe3\x55\x3e\xdf\xbf\x79\xbf\xbf\xf1\x35\x3e\xb1\x30\x04\x3e\xdf\xbf\x79\xbf\x5f\x99\x07\xbe\x86\xaa\xd0\x3e\xbe\x4d\x67\xbf\xae\xb6\xe2\x3d\x5d\x70\xae\x3e\x82\x02\x6f\xbf\x91\x80\xb1\x3e\x8c\xf6\x80\x3e\xbe\x4d\x67\xbf\xcb\x14\x43\xbe\x76\x19\x16\x3f\x19\x90\x49\xbf\xb0\xe3\x3f\x3d\x13\x0c\x0b\x3f\x88\x9c\x56\xbf\x06\x0e\x90\x3e\xfd\x14\xef\x3e\x88\x9c\x56\xbf\x57\x5d\xff\x3e\x6e\x88\xb9\x3e\x19\x90\x49\xbf\x7d\x09\x75\xbe\x4c\x89\x3c\x3f\xca\xfa\x21\xbf\xba\x4d\x38\xbc\xa6\x0f\x39\x3f\xa9\xdc\x30\xbf\x59\xa3\x5e\x3e\x6a\x4d\x2b\x3f\x89\xea\x35\xbf\x4c\x36\xde\x3e\x5b\x06\x14\x3f\xa9\xdc\x30\xbf\xee\x60\x20\x3f\x20\x0b\xe9\x3e\xca\xfa\x21\xbf\x60\xe5\x60\xbe\x00\x00\x00\x00\xdf\xbf\x79\xbf\xa1\x67\xdb\xbe\x00\x00\x00\x00\xbe\x4d\x67\xbf\xe5\x62\x94\xbe\x5a\x9e\x57\x3e\x82\x02\x6f\xbf\xf2\xd2\x1d\xbf\x00\x00\x00\x00\x19\x90\x49\xbf\x2b\x89\x00\xbf\x20\x7f\x59\x3e\x88\x9c\x56\xbf\x6a\xdd\xb6\xbe\x76\xe2\xd2\x3e\x88\x9c\x56\xbf\x1d\x3d\x46\xbf\x00\x00\x00\x00\xca\xfa\x21\xbf\xb8\xe4\x30\xbf\xe2\xca\x59\x3e\xa9\xdc\x30\xbf\xf1\xb7\x11\xbf\xbe\xbd\xd3\x3e\x89\xea\x35\xbf\x86\xe4\xd4\xbe\x01\x69\x17\x3f\xa9\xdc\x30\xbf\x61\xfe\x8a\xbd\x54\xe3\x55\xbe\xdf\xbf\x79\xbf\x5f\x99\x07\xbe\x86\xaa\xd0\xbe\xbe\x4d\x67\xbf\xe5\x62\x94\xbe\x5a\x9e\x57\xbe\x82\x02\x6f\xbf\xcb\x14\x43\xbe\x76\x19\x16\xbf\x19\x90\x49\xbf\x6a\xdd\xb6\xbe\x76\xe2\xd2\xbe\x78\x9c\x56\xbf\x2b\x89\x00\xbf\x20\x7f\x59\xbe\x78\x9c\x56\xbf\x7d\x09\x75\xbe\x4c\x89\x3c\xbf\xca\xfa\x21\xbf\x86\xe4\xd4\xbe\x01\x69\x17\xbf\xa9\xdc\x30\xbf\xf1\xb7\x11\xbf\xe0\xbd\xd3\xbe\x89\xea\x35\xbf\xb8\xe4\x30\xbf\xe2\xca\x59\xbe\xa9\xdc\x30\xbf\xbf\xf1\x35\x3e\xb1\x30\x04\xbe\xdf\xbf\x79\xbf\x91\x80\xb1\x3e\x6a\xf6\x80\xbe\xbe\x4d\x67\xbf\xae\xb6\xe2\x3d\x5d\x70\xae\xbe\x82\x02\x6f\xbf\x57\x5d\xff\x3e\x6e\x88\xb9\xbe\x19\x90\x49\xbf\x06\x0e\x90\x3e\xfd\x14\xef\xbe\x78\x9c\x56\xbf\xb0\xe3\x3f\x3d\x13\x0c\x0b\xbf\x78\x9c\x56\xbf\xee\x60\x20\x3f\x20\x0b\xe9\xbe\xca\xfa\x21\xbf\x4c\x36\xde\x3e\x5b\x06\x14\xbf\x98\xdc\x30\xbf\x59\xa3\x5e\x3e\x6a\x4d\x2b\xbf\x89\xea\x35\xbf\xba\x4d\x38\xbc\xa6\x0f\x39\xbf\x98\xdc\x30\xbf\x72\x6a\xb7\x3e\x00\x00\x00\x00\x82\x02\x6f\xbf\xa1\xf2\x07\x3f\xf1\x7e\xfc\x3d\x78\x9c\x56\xbf\xb2\xf2\x07\x3f\x6b\x7e\xfc\xbd\x78\x9c\x56\xbf\x1d\x1d\x2f\x3f\x3e\xb4\x6f\x3e\x98\xdc\x30\xbf\x36\x1e\x34\x3f\x00\x00\x00\x00\x89\xea\x35\xbf\x1d\x1d\x2f\x3f\xfa\xb3\x6f\xbe\x98\xdc\x30\xbf'


# bytes and bytearray are integers
def	COM_BlockSequenceCRCByte (base, sequence):
	p = memoryview(chktbl2)
	p = p[(sequence % 2996):]

	# max total len = 64
	if len(base) > 60:
		# truncate to 60 length
		base = base[:60]


	base.append((sequence & 0xff) ^ p[0])
	base.append(p[1])
	base.append(((sequence>>8) & 0xff) ^ p[2])
	base.append(p[3])
	
	# md5 here
	# print(hashlib.new('md4',base).hexdigest())

	# print(f"base is " + "".join("\\x{0:02x}".format(x) for x in base))

	h = hashlib.new('md4',base).digest()
	d1 = struct.unpack_from('<I',h,0)[0]
	d2 = struct.unpack_from('<I',h,4)[0]
	d3 = struct.unpack_from('<I',h,8)[0]
	d4 = struct.unpack_from('<I',h,12)[0]
	# print(hex(d1))
	# print(hex(d2))
	# print(hex(d3))
	# print(hex(d4))
	checksum = (d1 ^ d2 ^ d3 ^ d4) 
	# print(f'checksum is {checksum}')
	# print(f'checksum is {checksum& 0xff}')
	return checksum & 0xff;
