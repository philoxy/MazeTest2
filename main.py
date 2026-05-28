import pygame, sys

playerx = 60
playery = 60

screen = pygame.display.set_mode((640, 480))
player_img1 = pygame.image.load("assets/player.png")
#setup for animations somehow???
#if key is still pressed_keys cycle through frames
#if key is not pressed_keys set to first frame (standing)
#wow im so smart this will 100% not work at all
player_img = player_img1
player_rect = pygame.Rect(80, 80, 32, 32)
test_rect = pygame.Rect(60, 60, 32, 32)
icon = player_img1
pygame.display.set_caption("Undertale 2")
clock = pygame.time.Clock()

#i have to inefficiently use 4 lines because pygame complains otherwise
collide_down = False
collide_up = False
collide_right = False
collide_left = False

def loadmap():
	print("not yet lol")
	#if areatype = whatever
	#load this song
	#elif areatype = whatever2
	#load another song
	#or just make a json why is it always json
	#things to add:
	#load the map itself (with tiles) (i dont wanna make sprites waasdfljasfjlk)
	#

def update():
	global playerx, playery
	player_rect.center = (playerx, playery)
	screen.blit(player_img, player_rect)
	screen.blit(player_img, test_rect)
	#print(playerx)
	#print(playery)
	pygame.display.flip()

def collide():
	global collide_down, collide_up, collide_right, collide_left
	pressed_keys = pygame.key.get_pressed()
	#print(player_rect)
	#print(test_rect)
	collide_down = False
	collide_up = False
	collide_right = False
	collide_left = False
	if pressed_keys[pygame.K_DOWN] and player_rect.bottom == test_rect.top:
		collide_down = True
	elif pressed_keys[pygame.K_UP] and player_rect.top == test_rect.bottom:
		collide_up = True
	elif pressed_keys[pygame.K_RIGHT] and player_rect.right == test_rect.left:
		collide_right = True
	elif pressed_keys[pygame.K_LEFT] and player_rect.left == test_rect.right:
		collide_left = True


def move():
	global playerx, playery, collide_down, collide_up, collide_right, collide_left
	#if player bottom collide when pressing down
	#dont move
	#if player up collide when pressing up
	#dont move
	#etc etc
	#if player within certain area
	#move player
	#else
	#move screen
	#if player near edge
	#dont move screen or player
	pressed_keys = pygame.key.get_pressed()
	if pressed_keys[pygame.K_LSHIFT]:
		move = 5
	else:
		move = 2
	if pressed_keys[pygame.K_LEFT] and collide_left == False:
		playerx -= move
	if pressed_keys[pygame.K_RIGHT] and collide_right == False:
		playerx += move
	if pressed_keys[pygame.K_UP] and collide_up == False:
		playery -= move
	if pressed_keys[pygame.K_DOWN] and collide_down == False:
		playery += move
	

run = True
while run:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
			
	#print(collide_down)
	#print(collide_left)
	#print(collide_right)
	#print(collide_up)
	collide()
	move()

	screen.fill((225, 255, 255))
	clock.tick(60)
	update()
