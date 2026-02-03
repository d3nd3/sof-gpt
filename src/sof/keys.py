import pygame
import sys
import os
import time
from sof.packets.defines import *

import random

os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"

joystick = 0
rumbleLow = 0
rumbleHigh = 0
rumbleEnabled = True  # Global flag to control rumble state
debug_mode = False  # Flag to enable/disable debug output

def set_debug_mode(enabled):
	"""Enable or disable debug mode for event handling"""
	global debug_mode
	debug_mode = enabled
	print(f"Gamepad debug mode: {'enabled' if enabled else 'disabled'}")

def getJoystick(low=None,high=None):
	global rumbleLow,rumbleHigh
	
	if low is not None:
		rumbleLow = low
	if high is not None:
		rumbleHigh = high
	return (joystick,rumbleLow,rumbleHigh)

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

def check_and_reinit_gamepad():
	"""Check if gamepad is still valid and reinitialize if needed"""
	global joystick
	
	# Check if current joystick is still valid
	if joystick == 0 or not pygame.joystick.get_count():
		# No joystick available, try to initialize one
		if pygame.joystick.get_count() > 0:
			init_gamepad()
		return
	
	# Check if current joystick is still connected
	try:
		# Try to get joystick name to see if it's still valid
		joystick.get_name()
		# Also check if we can get basic info
		joystick.get_numbuttons()
		joystick.get_numaxes()
	except (pygame.error, AttributeError, OSError):
		# Joystick is no longer valid, try to reinitialize
		print("Gamepad disconnected, attempting to reinitialize...")
		joystick = 0
		if pygame.joystick.get_count() > 0:
			init_gamepad()

def debug_event(event):
	"""Debug function to inspect pygame events"""
	print(f"Event type: {event.type}")
	print(f"Event dict: {event.__dict__}")
	print(f"Event dir: {dir(event)}")

# Check pygame version compatibility once at module load
_pygame_has_device_events = None

def check_pygame_joystick_support():
	"""Check what joystick events are supported by this pygame version"""
	global _pygame_has_device_events
	
	if _pygame_has_device_events is None:
		pygame_version = pygame.version.ver
		print(f"Pygame version: {pygame_version}")
		
		# Check if newer joystick events are supported
		_pygame_has_device_events = hasattr(pygame, 'JOYDEVICEADDED') and hasattr(pygame, 'JOYDEVICEREMOVED')
		print(f"Device events supported: {_pygame_has_device_events}")
	
	return _pygame_has_device_events

def handle_joystick_device_event(event):
	"""Handle joystick device addition/removal events"""
	global joystick
	
	# Debug: show event details if debug mode is enabled
	if debug_mode:
		debug_event(event)
	
	# Check if this pygame version supports device events
	if not check_pygame_joystick_support():
		print("Warning: This pygame version doesn't support device hot-plugging events")
		return
	
	if event.type == pygame.JOYDEVICEADDED:
		# Get the device index from the event
		device_index = getattr(event, 'device_index', None)
		if device_index is not None:
			print(f"Gamepad device added: {device_index}")
		else:
			print("Gamepad device added")
		
		if joystick == 0:  # Only initialize if we don't have one
			init_gamepad()
	elif event.type == pygame.JOYDEVICEREMOVED:
		# Get the device index and instance ID from the event
		device_index = getattr(event, 'device_index', None)
		instance_id = getattr(event, 'instance_id', None)
		
		if device_index is not None:
			print(f"Gamepad device removed: {device_index}")
		else:
			print("Gamepad device removed")
		
		# Check if this was our current joystick
		if joystick != 0:
			try:
				# If we have instance_id, check if it matches our current joystick
				if instance_id is not None and joystick.get_instance_id() == instance_id:
					print("Current gamepad disconnected")
					joystick = 0
					# Try to find another available gamepad
					if pygame.joystick.get_count() > 0:
						init_gamepad()
				else:
					# No instance_id or doesn't match, just check if our joystick is still valid
					joystick.get_name()  # This will raise an error if invalid
			except (pygame.error, AttributeError):
				# Joystick is no longer valid, reset and try to find another
				print("Gamepad became invalid, attempting to reinitialize...")
				joystick = 0
				if pygame.joystick.get_count() > 0:
					init_gamepad()


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
	# print(button)

	if button == 0:#a
		p.conn.append_string_to_reliable(f"\x04itemuse\x00")
		pass
	elif button == 1:#b
		p.conn.append_string_to_reliable(f"\x04weapnext\x00")
		pass
	elif button == 2:#x
		p.conn.append_string_to_reliable(f"\x04weapprev\x00")
	elif button == 3:#y
		p.input.use = True
	elif button == 6:
		# select button (left)
		# randWave = random.randint(0, 3)
		# p.conn.append_string_to_reliable(f"\x04wave {randWave}\x00")
		p.conn.append_string_to_reliable(f"\x04itemnext\x00")
	elif button == 7:
		# start button (right)
		p.input.moveDown = True
	elif button == 8:
		#xbox button - not useful to use this for hold-down as system music controls
		p.conn.append_string_to_reliable(f"\x04wave 4\x00")
		pass
	elif button == 10:
		#rightjoypush
		pass

def gamepad_button_up(p,button):
	if button == 0: #A
		pass
	elif button == 1: #B
		pass
	elif button == 3:
		p.input.use = False
		pass
	elif button == 7:
		# menu button
		pass
	elif button == 8:
		#xbox button
		p.input.moveDown = False
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


itemuseTimestamp = 0
def gamepad_sticks(p,axis,value):
	global itemuseTimestamp
	# MOVE FORWARD/BACK
	if axis == 1:
		V = 0.25
		if value < V and value > -V:
			p.input.moveForward = False
			p.input.moveBack = False
		elif value > 0:
			# p.input.leftJoystickSensY = abs(value/(1-V))
			p.input.moveForward = False
			p.input.moveBack = True
		elif value < 0:
			# p.input.leftJoystickSensY = abs(value/(1-V))
			p.input.moveForward = True
			p.input.moveBack = False
	# MOVE RIGHT/LEFT
	elif axis == 0:
		V = 0.3
		if value < V and value > -V:
			p.input.moveRight = False
			p.input.moveLeft = False
		elif value > 0:
			p.input.moveRight = True
			p.input.moveLeft = False
		elif value < 0:
			p.input.moveRight = False
			p.input.moveLeft = True
	# LOOK RIGHT/LEFT
	elif axis == 3:
		V = 0.25
		if value < V and value > -V:
			p.input.lookLeft = False
			p.input.lookRight = False
		elif value > 0 :
			p.input.rightJoystickSensX = abs(value/(1-V))
			p.input.lookLeft = False
			p.input.lookRight = True
		elif value < 0 :
			p.input.rightJoystickSensX = abs(value/(1-V))
			p.input.lookLeft = True
			p.input.lookRight = False
	# LOOK UP/DOWN
	elif axis == 4:
		V = 0.5
		if value < V and value > -V:
			p.input.lookDown = False
			p.input.lookUp = False
		elif value > 0 :
			# p.input.rightJoystickSensY = abs(value/(1-V))
			p.input.lookDown = True
			p.input.lookUp = False
		elif value < 0 :
			# p.input.rightJoystickSensY = abs(value/(1-V))
			p.input.lookDown = False
			p.input.lookUp = True


	elif axis == 2:
		# L1 1.0=fully pressed, -1.0=fully depressed
		# now = time.time()
		if value > -1:
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
		if value > -1:
			"""
			Not vibrating
			Small vibrating
			Large vibrating
			Both vibrating
			"""
			
			p.input.fire = True
		else:
			# Stop rumble when not firing
			import sof.keys
			sof.keys.stop_rumble()
			p.input.fire = False


def start_rumble(low=None, high=None, duration=None):
	"""Start rumble on the connected gamepad"""
	global joystick, rumbleLow, rumbleHigh
	
	if joystick == 0 or not rumbleEnabled:
		return False
	
	try:
		if low is not None:
			rumbleLow = low
		if high is not None:
			rumbleHigh = high
		
		# Start rumble with current values
		if hasattr(joystick, 'rumble'):
			if duration:
				joystick.rumble(rumbleLow, rumbleHigh, duration)
			else:
				joystick.rumble(rumbleLow, rumbleHigh, 1000)  # Default 1 second duration
			return True
		else:
			print("Gamepad does not support rumble")
			return False
	except Exception as e:
		print(f"Error starting rumble: {e}")
		return False

def stop_rumble():
	"""Stop rumble on the connected gamepad"""
	global joystick
	
	if joystick == 0:
		return False
	
	try:
		if hasattr(joystick, 'stop_rumble'):
			joystick.stop_rumble()
			return True
		else:
			print("Gamepad does not support stop_rumble")
			return False
	except Exception as e:
		print(f"Error stopping rumble: {e}")
		return False

def toggle_rumble():
	"""Toggle rumble on/off"""
	global rumbleEnabled
	
	rumbleEnabled = not rumbleEnabled
	
	if not rumbleEnabled:
		stop_rumble()
	
	status = "enabled" if rumbleEnabled else "disabled"
	print(f"Rumble {status}")
	return rumbleEnabled

def set_rumble_intensity(low, high):
	"""Set rumble intensity values"""
	global rumbleLow, rumbleHigh
	
	rumbleLow = max(0.0, min(1.0, float(low)))
	rumbleHigh = max(0.0, min(1.0, float(high)))
	
	print(f"Rumble intensity set to: Low={rumbleLow:.2f}, High={rumbleHigh:.2f}")

def get_rumble_status():
	"""Get current rumble status"""
	global joystick, rumbleEnabled, rumbleLow, rumbleHigh
	
	if joystick == 0:
		return "No gamepad connected"
	
	rumble_support = "Yes" if hasattr(joystick, 'rumble') else "No"
	status = "enabled" if rumbleEnabled else "disabled"
	
	return f"Rumble: {status}, Support: {rumble_support}, Intensity: Low={rumbleLow:.2f}, High={rumbleHigh:.2f}"

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
		elif event.type == pygame.JOYDEVICEADDED:
			# Handle hot-plugging (if supported by this pygame version)
			handle_joystick_device_event(event)
		elif event.type == pygame.JOYDEVICEREMOVED:
			# Handle hot-unplugging (if supported by this pygame version)
			handle_joystick_device_event(event)
		elif event.type == pygame.JOYBUTTONDOWN:
			# Check if gamepad is still valid before processing
			check_and_reinit_gamepad()
			if joystick != 0:
				gamepad_button_down(player,event.button)
		elif event.type == pygame.JOYBUTTONUP:
			# Check if gamepad is still valid before processing
			check_and_reinit_gamepad()
			if joystick != 0:
				gamepad_button_up(player,event.button)
		elif event.type == pygame.JOYHATMOTION: # wasd
			# print("wasd")
			# print(event)
			#A position of (0, 0) means the hat is centered.
			# event.position
			# Check if gamepad is still valid before processing
			check_and_reinit_gamepad()
			if joystick != 0:
				gamepad_dpad(player,event.value)
		elif event.type == pygame.JOYAXISMOTION:
			# print(event)
			# Check if gamepad is still valid before processing
			check_and_reinit_gamepad()
			if joystick != 0:
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
	
def get_gamepad_status():
	"""Get current gamepad status for debugging"""
	global joystick
	
	if joystick == 0:
		return "No gamepad connected"
	
	try:
		name = joystick.get_name()
		instance_id = joystick.get_instance_id()
		button_count = joystick.get_numbuttons()
		axis_count = joystick.get_numaxes()
		return f"Connected: {name} (ID: {instance_id}, Buttons: {button_count}, Axes: {axis_count})"
	except (pygame.error, AttributeError):
		return "Gamepad error - needs reinitialization"

def force_reinit_gamepad():
	"""Force reinitialize the gamepad (useful for troubleshooting)"""
	global joystick
	
	print("Forcing gamepad reinitialization...")
	joystick = 0
	pygame.joystick.quit()
	pygame.joystick.init()
	
	if pygame.joystick.get_count() > 0:
		init_gamepad()
		return True
	else:
		print("No gamepads available for reinitialization")
		return False
	