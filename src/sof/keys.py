import pygame
import sys
import os
import time
from sof.packets.defines import *

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

def init_gamepad():
	global joystick
	pygame.joystick.init()

	# Make sure at least one joystick/gamepad is connected
	if pygame.joystick.get_count() == 0:
		print("No gamepad detected.")
		return None

	# Initialize the first joystick
	joystick = pygame.joystick.Joystick(0)
	joystick.init()

	print(f"Initialized {joystick.get_name()}")


def keyup(p,key):
	if key == pygame.K_LEFT:
		p.input.lookLeft = False
	elif key == pygame.K_RIGHT:
		p.input.lookRight = False
	elif key == pygame.K_UP:
		p.input.lookUp = False
	elif key == pygame.K_DOWN:
		p.input.lookDown = False
	elif key == pygame.K_w:
		p.input.moveForward = False
	elif key == pygame.K_s:
		p.input.moveBack = False
	elif key == pygame.K_a:
		p.input.moveLeft = False
	elif key == pygame.K_d:
		p.input.moveRight = False
	elif key == pygame.K_RCTRL:
		p.input.fireEvent = 0.0
	elif key == pygame.K_SPACE:
		print("REVIVE!")

def keydown(p,key):
	if key == pygame.K_LEFT:
		p.input.lookLeft = True
	elif key == pygame.K_RIGHT:
		p.input.lookRight = True
	elif key == pygame.K_UP:
		p.input.lookUp = True
	elif key == pygame.K_DOWN:
		p.input.lookDown = True
	elif key == pygame.K_w:
		p.input.moveForward = True
	elif key == pygame.K_s:
		p.input.moveBack = True
	elif key == pygame.K_a:
		p.input.moveLeft = True
	elif key == pygame.K_d:
		p.input.moveRight = True
	elif key == pygame.K_RCTRL:
		p.input.fireEvent = 1.0


def gamepad_button_down(p,button):
	print(button)

	if button == 0:
		p.input.use = True
		pass
	elif button == 1:
		p.conn.append_string_to_reliable(f"\x04weapnext\x00")
		pass
	elif button == 2:
		p.conn.append_string_to_reliable(f"\x04weapprev\x00")
	elif button == 3:
		p.conn.append_string_to_reliable(f"\x04itemuse\x00")

def gamepad_button_up(p,button):
	if button == 0: #A
		p.input.use = False
	elif button == 1: #B
		pass
	elif button == 3:
		pass
"""
It just sets forwardspeed.
By default it will want to stand still.
"""
def gamepad_dpad(p,states):
	# [0] == horizontal
	# [1] == vertical
	if states[1] == 0:
		p.input.moveForward = False
		p.input.moveBack = False
	elif states[1] > 0 :
		p.input.moveForward = True
		p.input.moveBack = False
	elif states[1] < 0 :
		p.input.moveForward = False
		p.input.moveBack = True

	if states[0] == 0 :
		p.input.moveRight = False
		p.input.moveLeft = False
	elif states[0] > 0 :
		p.input.moveRight = True
		p.input.moveLeft = False
	elif states[0] < 0 :
		p.input.moveLeft = True
		p.input.moveRight = False

epsilon = 0.1
epsilon2 = -epsilon

ep_pitch = 0.25
ep_pitch2 = -ep_pitch

itemuseTimestamp = 0
def gamepad_sticks(p,axis,value):
	global itemuseTimestamp
	if axis == 1:
		if value < epsilon and value > epsilon2:
			p.input.moveForward = False
			p.input.moveBack = False
		elif value > 0:
			p.input.leftJoystickSensY = abs(value)
			p.input.moveForward = False
			p.input.moveBack = True
		elif value < 0:
			p.input.leftJoystickSensY = abs(value)
			p.input.moveForward = True
			p.input.moveBack = False
	elif axis == 0:
		if value < epsilon and value > epsilon2:
			p.input.moveRight = False
			p.input.moveLeft = False
		elif value > 0:
			p.input.moveRight = True
			p.input.moveLeft = False
		elif value < 0:
			p.input.moveRight = False
			p.input.moveLeft = True
	elif axis == 3:
		if value < epsilon and value > epsilon2:
			p.input.lookLeft = False
			p.input.lookRight = False
		elif value > 0 :
			p.input.rightJoystickSensX = abs(value)
			p.input.lookLeft = False
			p.input.lookRight = True
		elif value < 0 :
			p.input.rightJoystickSensX = abs(value)
			p.input.lookLeft = True
			p.input.lookRight = False
	elif axis == 4:
		if value < ep_pitch and value > ep_pitch2:
			p.input.lookDown = False
			p.input.lookUp = False
		elif value > 0 :
			p.input.rightJoystickSensY = abs(value)
			p.input.lookDown = True
			p.input.lookUp = False
		elif value < 0 :
			p.input.rightJoystickSensY = abs(value)
			p.input.lookDown = False
			p.input.lookUp = True


	elif axis == 2:
		# L1 1.0=fully pressed, -1.0=fully depressed
		# now = time.time()
		if value > -0.9:
			p.input.moveUp = True
			"""
			if now - itemuseTimestamp > 1:
				p.conn.append_string_to_reliable(f"\x04itemuse\x00")	
			"""
		else:
			p.input.moveUp = False
			# itemuseTimestamp = now
			
	elif axis == 5:
		# R1 1.0=fully pressed, -1.0=fully depressed
		if value > -0.9:
			p.input.fire = True
		else:
			p.input.fire = False


def process(player):
	"""
	pygame.event.pump()
	# Get state of buttons
	for i in range(joystick.get_numbuttons()):
		button_state = joystick.get_button(i)
		if button_state == 1:
			print(f"Button {i} pressed")
	"""
	# Add a small delay to control the print speed
	# pygame.time.delay(10)
	
	for event in pygame.event.get():
		# print(event)
		if event.type == pygame.QUIT:
			player.endpoint.removePlayer(player)
		elif event.type == pygame.JOYBUTTONDOWN:
			gamepad_button_down(player,event.button)
		elif event.type == pygame.JOYBUTTONUP:
			gamepad_button_up(player,event.button)
		elif event.type == pygame.JOYHATMOTION: # wasd
			# print("wasd")
			# print(event)
			#A position of (0, 0) means the hat is centered.
			# event.position
			gamepad_dpad(player,event.value)
		elif event.type == pygame.JOYAXISMOTION:
			# print(event)
			gamepad_sticks(player,event.axis,event.value)
			
		# Handle key down events
		elif event.type == pygame.KEYDOWN:
			# p.input.moveForward
			# print(f"Key : {event.key}")
			keydown(player,event.key)
		# Handle key up events
		elif event.type == pygame.KEYUP:
			# print(f"Key : {event.key}")
			keyup(player,event.key)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			player.input.fire = True
		elif event.type == pygame.MOUSEBUTTONUP:
			player.input.fire = False
		else:
			# print(f"unknown event : {event.type}")
			pass
	