import pygame


def keyup(p,key):
	if key == pygame.K_LEFT:
		p.uc_now.lookLeft = False
	elif key == pygame.K_RIGHT:
		p.uc_now.lookRight = False
	elif key == pygame.K_UP:
		p.uc_now.lookUp = False
	elif key == pygame.K_DOWN:
		p.uc_now.lookDown = False
	elif key == pygame.K_w:
		p.uc_now.moveForward = False
	elif key == pygame.K_s:
		p.uc_now.moveBack = False
	elif key == pygame.K_a:
		p.uc_now.moveLeft = False
	elif key == pygame.K_d:
		p.uc_now.moveRight = False
	elif key == pygame.K_RCTRL:
		p.uc_now.fireEvent = 0.0
	elif key == pygame.K_SPACE:
		print("REVIVE!")

def keydown(p,key):
	if key == pygame.K_LEFT:
		p.uc_now.lookLeft = True
	elif key == pygame.K_RIGHT:
		p.uc_now.lookRight = True
	elif key == pygame.K_UP:
		p.uc_now.lookUp = True
	elif key == pygame.K_DOWN:
		p.uc_now.lookDown = True
	elif key == pygame.K_w:
		p.uc_now.moveForward = True
	elif key == pygame.K_s:
		p.uc_now.moveBack = True
	elif key == pygame.K_a:
		p.uc_now.moveLeft = True
	elif key == pygame.K_d:
		p.uc_now.moveRight = True
	elif key == pygame.K_RCTRL:
		p.uc_now.fireEvent = 1.0

def process(player):
	for event in pygame.event.get():
		# Handle key down events
		if event.type == pygame.KEYDOWN:
			# p.uc_now.moveForward
			# print(f"Key : {event.key}")
			keydown(player,event.key)
		# Handle key up events
		elif event.type == pygame.KEYUP:
			# print(f"Key : {event.key}")
			keyup(player,event.key)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			player.uc_now.fireEvent = 1.0
		elif event.type == pygame.MOUSEBUTTONUP:
			player.uc_now.fireEvent = 0.0