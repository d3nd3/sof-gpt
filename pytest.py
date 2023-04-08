import pygame
import random

import time

pygame.init()

# Set screen size
screen = pygame.display.set_mode((600, 600))
# Set font
font = pygame.font.Font(None, 36)

while True:
	pygame.display.update()
	time.sleep(0.01)


# Set colors
white = (255, 255, 255)
black = (0, 0, 0)

# Set player and obstacle variables
player_pos = [300, 550]
player_size = 50
obstacle_size = 50
obstacle_pos = [random.randint(0, 550), 0]
obstacle_list = [obstacle_pos]

# Set game speed
speed = 10

# Set score
score = 0



def drop_obstacles(obstacle_list):
	delay = random.random()
	if len(obstacle_list) < 10 and delay < 0.1:
		x_pos = random.randint(0, 550)
		y_pos = 0
		obstacle_list.append([x_pos, y_pos])

def draw_obstacles(obstacle_list):
	for obstacle_pos in obstacle_list:
		pygame.draw.rect(screen, black, (obstacle_pos[0], obstacle_pos[1], obstacle_size, obstacle_size))

def update_obstacle_positions(obstacle_list):
	global score
	for idx, obstacle_pos in enumerate(obstacle_list):
		if obstacle_pos[1] >= 0 and obstacle_pos[1] < 600:
			obstacle_pos[1] += speed
		else:
			obstacle_list.pop(idx)
			score += 1

def collision_check(obstacle_list, player_pos):
	for obstacle_pos in obstacle_list:
		if detect_collision(obstacle_pos, player_pos):
			return True
	return False

def detect_collision(player_pos, obstacle_pos):
	p_x = player_pos[0]
	p_y = player_pos[1]

	o_x = obstacle_pos[0]
	o_y = obstacle_pos[1]

	if (o_x >= p_x and o_x < (p_x + player_size)) or (p_x >= o_x and p_x < (o_x + obstacle_size)):
		if (o_y >= p_y and o_y < (p_y + player_size)) or (p_y >= o_y and p_y < (o_y + obstacle_size)):
			return True
	return False

game_over = False

while not game_over:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			game_over = True
		if event.type == pygame.KEYDOWN:
			x = player_pos[0]
			y = player_pos[1]
			if event.key == pygame.K_LEFT:
				x -= player_size
			elif event.key == pygame.K_RIGHT:
				x += player_size

			player_pos = [x,y]

	screen.fill(white)

	drop_obstacles(obstacle_list)
	update_obstacle_positions(obstacle_list)

	text = font.render("Score: " + str(score), True, black)
	screen.blit(text, (450,10))

	if collision_check(obstacle_list, player_pos):
		game_over = True

	draw_obstacles(obstacle_list)

	pygame.draw.rect(screen, black, (player_pos[0], player_pos[1], player_size, player_size))

	pygame.display.update()

	time.sleep(0.05)
