# By: Philooxy | https://philoxy.github.io/

#idea list:
#buttons to open doors oooo

import pygame, sys, csv, os, json, math

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((640, 640), vsync=1)

icon = pygame.image.load("assets/icon.png")
icon.set_colorkey((255,0,208))
pygame.display.set_caption("MAZETEST 2")
pygame.display.set_icon(icon)
pygame.mixer.init()
clock = pygame.time.Clock()

font1 = pygame.font.Font('assets/determination.ttf', 26)
font1small = pygame.font.Font('assets/determination.ttf', 12)

#i will remove this eventually because its useless
All_Tiles = pygame.sprite.Group()

Tilegroup = pygame.sprite.Group()
Tilegroup_nocol = pygame.sprite.Group()
Tilegroup_wall = pygame.sprite.Group()
Tilegroup_wall2 = pygame.sprite.Group()
Tilegroup_exit = pygame.sprite.Group()
Tilegroup_ladder = pygame.sprite.Group()

playerx = 144
playery = 224
player_rect = pygame.Rect(playerx, playery, 32, 32)
collide_down, collide_up, collide_right, collide_left = False, False, False, False
offsetX = 0
offsetY = 0
animX = 0
animY = 0
walk = 0
addwalk = False
walksprite = 0
direction = 3
t0 = 0
# 0 left 1 up 2 right 3 down
move = 2
layer = 0
emote = 0
emotemenu = False
action = "walk"
restartable = False
ui_timer, ui_song, ui_topright, ui_levelname = False, False, False, False

def resetvars():
	global playerx, playery, player_rect, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY, animX, animY, walk, addwalk, walksprite, direction, move, layer, emote, emotemenu, action, ui_timer, ui_song, ui_topright, ui_levelname

	Tilegroup.empty()
	Tilegroup_nocol.empty()
	Tilegroup_wall.empty()
	Tilegroup_wall2.empty()
	Tilegroup_exit.empty()
	Tilegroup_ladder.empty()

	playerx = 144
	playery = 224
	player_rect = pygame.Rect(playerx, playery, 32, 32)
	collide_down, collide_up, collide_right, collide_left = False, False, False, False
	offsetX = 0
	offsetY = 0
	animX = 0
	animY = 0
	walk = 0
	addwalk = False
	walksprite = 0
	direction = 3
	# 0 left 1 up 2 right 3 down
	move = 2
	layer = 0
	emote = 0
	emotemenu = False
	action = "walk"
	ui_timer, ui_song, ui_topright, ui_levelname = False, False, False, False

	Tilegroup.empty()
	Tilegroup_nocol.empty()
	Tilegroup_wall.empty()
	Tilegroup_wall2.empty()
	Tilegroup_exit.empty()
	Tilegroup_ladder.empty()


# Spritesheet, Tile, and Tilemap classes from this tutorial: https://www.pygame.org/project/5291/7669
class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()
        self.meta_data = self.filename.replace('png', 'json')
        with open(self.meta_data) as f:
            self.data = json.load(f)
        f.close()

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((255,0,208))
        sprite.blit(self.sprite_sheet,(0, 0),(x, y, w, h))
        return sprite

    def parse_sprite(self, name):
        sprite = self.data['frames'][name]['frame']
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        image = self.get_sprite(x, y, w, h)
        return image

class Tile(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet, type):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.image.set_colorkey((255, 0, 208))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		self.type = type


	def draw(self, surface):
		global offsetX, offsetY
		surface.blit(self.image, (self.rect.x-offsetX, self.rect.y-offsetY))
	
class Tile_NoCol(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet, type):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.image.set_colorkey((255, 0, 208))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		self.type = type


	def draw(self, surface):
		global offsetX, offsetY
		surface.blit(self.image, (self.rect.x-offsetX, self.rect.y-offsetY))

class Tile_Wall(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet, type):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.image.set_colorkey((255, 0, 208))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		self.type = type


	def draw(self, surface):
		global offsetX, offsetY
		surface.blit(self.image, (self.rect.x-offsetX, self.rect.y-offsetY))

class Tile_Exit(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet, type):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.image.set_colorkey((255, 0, 208))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		self.type = type


	def draw(self, surface):
		global offsetX, offsetY
		surface.blit(self.image, (self.rect.x-offsetX, self.rect.y-offsetY))

class TileMap():
	def __init__(self, filename, spritesheet):
		self.filename = filename
		self.tile_size = 64
		self.spritesheet = spritesheet
		self.tiles = self.load_tiles(filename)
		self.map_surface = pygame.Surface((self.map_w, self.map_h))
		#i have NO IDEA how to change the colorkey so you have to use (0, 0, 1) for black in rgb values
		self.map_surface.set_colorkey((0, 0, 0))
		self.load_map()

	def draw_map(self, surface):
		global offsetX, offsetY, level_id
		if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
			surface.blit(self.map_surface, (-(offsetX % 64)-48, -(offsetY % 64)))
		else:
			surface.blit(self.map_surface, (336-offsetX, 384-offsetY))

	def load_map(self):
		for tile in self.tiles:
			tile.draw(self.map_surface)

	def read_csv(self, filename):
		map = []
		with open(os.path.join(filename)) as data:
			data = csv.reader(data, delimiter=",")
			for row in data:
				map.append(list(row))
		return map

	def load_tiles(self, filename):
		tiles = []
		map = self.read_csv(filename)
		x, y = 0, 0
		for row in map:
			x = 0
			for tile in row:
				if tile == "0":
					Temptile = Tile("wall2", x * self.tile_size, y * self.tile_size, self.spritesheet, "wall2")
					tiles.append(Temptile)
					Tilegroup.add(Temptile)
					All_Tiles.add(Temptile)

				elif tile == "1":
					Temptile = Tile("wall1", x * self.tile_size, y * self.tile_size, self.spritesheet, "wall1")
					tiles.append(Temptile)
					Tilegroup.add(Temptile)
					All_Tiles.add(Temptile)

				elif tile == "2":
					Temptile = Tile_NoCol("bridge", x * self.tile_size, y * self.tile_size, self.spritesheet, "bridge")
					tiles.append(Temptile)
					Tilegroup_nocol.add(Temptile)
					All_Tiles.add(Temptile)

				elif tile == "3":
					Temptile = Tile_Exit("exit", x * self.tile_size, y * self.tile_size, self.spritesheet, "exit")
					tiles.append(Temptile)
					Tilegroup_exit.add(Temptile)
					All_Tiles.add(Temptile)

				elif tile == "4":
					Temptile = Tile_Wall("wall3", x * self.tile_size, y * self.tile_size, self.spritesheet, "wall3")
					tiles.append(Temptile)
					Tilegroup_wall.add(Temptile)
					All_Tiles.add(Temptile)

				elif tile == "5":
					Temptile = Tile_NoCol("path", x * self.tile_size, y * self.tile_size, self.spritesheet, "path")
					tiles.append(Temptile)
					Tilegroup_nocol.add(Temptile)
					All_Tiles.add(Temptile)

				elif tile == "6":
					Temptile = Tile_NoCol("bridge2", x * self.tile_size, y * self.tile_size, self.spritesheet, "bridge2")
					tiles.append(Temptile)
					Tilegroup_nocol.add(Temptile)
					All_Tiles.add(Temptile)

				elif tile == "7":
					Temptile = Tile_NoCol("ladder", x * self.tile_size, y * self.tile_size, self.spritesheet, "ladder")
					tiles.append(Temptile)
					Tilegroup_ladder.add(Temptile)
					All_Tiles.add(Temptile)

				elif tile == "10":
					Temptile = Tile_Wall("blank", x * self.tile_size, y * self.tile_size, self.spritesheet, "blank")
					tiles.append(Temptile)
					Tilegroup_wall.add(Temptile)
					All_Tiles.add(Temptile)

				x += 1
			y += 1

		self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
		return tiles

# general functions for player

def collide():
		global collide_down, collide_up, collide_right, collide_left, playerx, playery, walk, layer, player_rect, action, win
		pressed_keys = pygame.key.get_pressed()
		collide_down = False
		collide_up = False
		collide_right = False
		collide_left = False

		for i in list(Tilegroup.sprites()):
			if i.rect.left - 31 <= player_rect.left <= i.rect.right - 1:
				if pressed_keys[pygame.K_DOWN] and player_rect.bottom - 16 == i.rect.top:
					collide_down = True
				if pressed_keys[pygame.K_UP] and player_rect.top + 16 == i.rect.bottom:
					collide_up = True
			if i.rect.top - 15 <= player_rect.top <= i.rect.bottom - 17:
				if pressed_keys[pygame.K_RIGHT] and player_rect.right == i.rect.left:
					collide_right = True
				if pressed_keys[pygame.K_LEFT] and player_rect.left == i.rect.right:
					collide_left = True

		for i in list(Tilegroup_wall.sprites()):
			if not layer == 1 and (i.type == "wall2" or i.type == "wall3"):
				if i.rect.left - 31 <= player_rect.left <= i.rect.right - 1:
					if pressed_keys[pygame.K_DOWN] and player_rect.bottom - 16 == i.rect.top:
						collide_down = True
					if pressed_keys[pygame.K_UP] and player_rect.top + 16 == i.rect.bottom:
						collide_up = True
				if i.rect.top - 15 <= player_rect.top <= i.rect.bottom - 1:
					if pressed_keys[pygame.K_RIGHT] and player_rect.right == i.rect.left:
						collide_right = True
					if pressed_keys[pygame.K_LEFT] and player_rect.left == i.rect.right:
						collide_left = True

			# this is just any generic block collision
			elif layer == 1 and i.type == "blank":
				if i.rect.left - 31 <= player_rect.left <= i.rect.right - 1:
					if pressed_keys[pygame.K_DOWN] and player_rect.bottom == i.rect.top:
						collide_down = True
					if pressed_keys[pygame.K_UP] and player_rect.top == i.rect.bottom:
						collide_up = True
				if i.rect.top - 31 <= player_rect.top <= i.rect.bottom - 1:
					if pressed_keys[pygame.K_RIGHT] and player_rect.right == i.rect.left:
						collide_right = True
					if pressed_keys[pygame.K_LEFT] and player_rect.left == i.rect.right:
						collide_left = True

		for i in list(Tilegroup_exit.sprites()):
			if i.rect.left + 12 <= player_rect.center[0] <= i.rect.right - 12 and i.rect.top + 12 <= player_rect.center[1] <= i.rect.bottom - 12:
				winlvl("win")

		for i in list(Tilegroup_ladder.sprites()):
			if player_rect.colliderect(i.rect):
				action = "climb"
				if pressed_keys[pygame.K_UP]:
					layer = 1
				elif pressed_keys[pygame.K_DOWN]:
					layer = 0

				

def movep():
	global playerx, playery, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY, walk, walksprite, direction, addwalk, emote, action, emotemenu, restartable, topright_text
	addwalk, run = False, False
	pressed_keys = pygame.key.get_pressed()

	#sprinting

	if pressed_keys[pygame.K_x] and action == "walk":
		playerx = 4*round(playerx/4)
		playery = 4*round(playery/4)
		move = 4
		run = True
	else:
		move = 2

	#movement

	if pressed_keys[pygame.K_LEFT]:
		direction = 0
		if collide_left == False:
			playerx -= move
			addwalk = True
	if pressed_keys[pygame.K_RIGHT]:
		direction = 2
		if collide_right == False:
			playerx += move
			addwalk = True
	if pressed_keys[pygame.K_UP]:
		direction = 1
		if collide_up == False:
			playery -= move
			addwalk = True
	if pressed_keys[pygame.K_DOWN]:
		direction = 3
		if collide_down == False:
			playery += move
			addwalk = True

	if pressed_keys[pygame.K_r] and restartable == True:
		topright_text = "Restarting..."
		winlvl("restart")
	if pressed_keys[pygame.K_ESCAPE] and restartable == True:
		topright_text = "Exiting..."
		winlvl("exit")

	#animation frame thingy idk

	if addwalk == True:
		if run == False:
			walk += 1
		else:
			walk += 1.5
		if walk > 40:
			walk = 1
	else:
		walk = 0

	if walk == 0:
		walksprite = 0
	elif 1 <= walk <= 10:
		walksprite = 1
	elif 11 <= walk <= 20:
		walksprite = 2
	elif 21 <= walk <= 30:
		walksprite = 3
	elif 32 <= walk <= 40:
		walksprite = 4

	offsetX = playerx
	offsetY = playery

def loadLevel(level_num):
	global spritesheet, map_below, map_above, map_below2, map_above2, level_mus, bg, songname, levelname, topright_text
	level_num = str(level_num)
	spritesheet = Spritesheet('levels/level'+level_num+'/spritesheet.png')
	map_below = TileMap('levels/level'+level_num+'/level'+level_num+'_back.csv', spritesheet)
	map_above = TileMap('levels/level'+level_num+'/level'+level_num+'_front.csv', spritesheet)
	map_above2 = TileMap('levels/level'+level_num+'/level'+level_num+'_front2.csv', spritesheet)
	map_below2 = TileMap('levels/level'+level_num+'/level'+level_num+'_back2.csv', spritesheet)
	bg = TileMap('levels/level'+level_num+'/level'+level_num+'_bg.csv', spritesheet)
	with open("levels/level"+level_num+"/info.txt", "r") as f:
		texty = f.read()
		texty = texty.split("\n")
		levelname = texty[0]
		songname = texty[1]
		topright_text = texty[2]
	level_mus = pygame.mixer.music.load("assets/music/level"+level_num+".mp3")
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(0.1)



def player_img_load(image_path):
	global player_img1
	player_img1 = pygame.image.load("assets/player/"+image_path)

def winlvl(type):
	global level_id, animY, layer, player_img1, run, restartable, topright_text
	restartable = False
	animY = 0
	layer = 1
	player_img_load("anim/wee.png")
	if type == "win":
		tada = pygame.mixer.Sound("assets/sounds/tada.mp3")
		channel = tada.play()
		tada.set_volume(0.5)
	exponent, timery = 1, 1
	player_img_temp = player_img1
	while timery <= 100:
		if timery/5 == round(timery/5):
			player_img1 = pygame.transform.rotate(player_img_temp, 90*timery)
		timery += 1
		exponent = exponent * 1.03
		animY += round(exponent)
		update()
	if type == "win":
		level_id += 1
		run = False
	elif type == "restart":
		update()
		run = False
	elif type == "exit":
		update()
		run = False
		sys.exit()



def update():
	global playerx, playery, offsetX, offsetY, player_img1, player_rect, action, clock, animY, ui_timer, ui_levelname, ui_song, topright_text

	screen.fill((255, 255, 255))
	clock.tick(60)
	
	player_img = player_img1
	player_img.set_colorkey((255, 0, 208))
	player_rect.topleft = (playerx, playery)
	bg.draw_map(screen)
	map_below.draw_map(screen)
	map_below2.draw_map(screen)

	if layer == 1 or action == "climb":
		map_above.draw_map(screen)
		map_above2.draw_map(screen)
		screen.blit(player_img, pygame.Rect(320+animX, 352-animY, 32, 32))
	elif layer == 0:
		screen.blit(player_img, pygame.Rect(320+animX, 352-animY, 32, 32))
		map_above.draw_map(screen)
		map_above2.draw_map(screen)

	if ui_timer == True:
		timer()

	if ui_levelname == True:
		level_name()

	if ui_song == True:
		song_name()

	if ui_topright == True:
		topright_text2 = font1small.render(topright_text, True, (255, 255, 255))
		topright_text2_rect = topright_text2.get_rect()
		topright_text2_rect.topright = (624, 16)
		screen.blit(topright_text2, topright_text2_rect)
	pygame.display.flip()


#i have no idea how to optimize any of this lmao
def animate():
	global direction, walksprite, player_img1, action, emote, animX, animY, playerx, playery
	if action == "walk":
		if direction == 0:
			if walksprite == 0:
				player_img1 = pygame.image.load("assets/player/idle/side.png")
			else:
				player_img1 = pygame.image.load("assets/player/walk/side"+str(walksprite)+".png")

			player_img1 = pygame.transform.flip(player_img1, True, False)
		if direction == 1:
			if walksprite == 0:
				player_img1 = pygame.image.load("assets/player/idle/up.png")
			else:
				player_img1 = pygame.image.load("assets/player/walk/up"+str(walksprite)+".png")
		if direction == 2:
			if walksprite == 0:
				player_img1 = pygame.image.load("assets/player/idle/side.png")
			else:
				player_img1 = pygame.image.load("assets/player/walk/side"+str(walksprite)+".png")
		if direction == 3:
			if walksprite == 0:
				player_img1 = pygame.image.load("assets/player/idle/down.png")
			else:
				player_img1 = pygame.image.load("assets/player/walk/down"+str(walksprite)+".png")

	if emote == 1:
		player_img1 = pygame.image.load("assets/player/emote/why.png")
		#animation test
		#while animX <= 64:
			#animX += 4
			#update()
		#playerx += animX
		#animX = 0
	elif emote == 2:
		for i in range(3):
			player_img1 = pygame.transform.rotate(player_img1, 90)

		


	player_img1.set_colorkey((255, 0, 208))
	player_img = player_img1


# hud elements

def timer():
	global ui_timer, t0
	ms = pygame.time.get_ticks()-t0
	seconds = math.floor(ms/1000)
	if seconds < 10:
		seconds = "0"+str(seconds)
	minutes = math.floor(ms/60000)
	if minutes < 10:
		minutes = "0"+str(minutes)
	ms = math.floor(ms/10)
	if ms < 10:
		ms = "00"+str(ms)
	elif 10 < ms < 100:
		ms = "0"+str(ms)
	timer_text = font1.render("Time: "+str(minutes)+":"+str(seconds)+'"'+str(ms), True, (255, 255, 255))
	timer_text_rect = timer_text.get_rect()
	timer_text_rect.bottomleft = (16, 624)
	screen.blit(timer_text, timer_text_rect)

emotewheel = pygame.image.load("assets/hud/emotewheel.png")
emotewheel.set_colorkey((255, 0, 208))

def emotes():
	global emotemenu, emotewheel, addwalk, emote
	pressed_keys = pygame.key.get_pressed()

	if pressed_keys[pygame.K_e]:
		if emotemenu == False:
			emotemenu = True
		elif emotemenu == True:
			emotemenu = False

	if pressed_keys[pygame.K_0] and addwalk == False:
		emote = 1
		emotemenu = False
	elif pressed_keys[pygame.K_1] and addwalk == False:
		emote = 2
		emotemenu = False
	if emotemenu == True:
		screen.blit(emotewheel, (440, 440))

def level_name():
	global levelname
	name_text = font1.render(levelname, True, (255, 255, 255))
	name_text_rect = name_text.get_rect()
	name_text_rect.topleft = (16, 16)
	screen.blit(name_text, name_text_rect)

def song_name():
	global songname
	song_text = font1small.render("Song: "+songname, True, (255, 255, 255))
	song_text_rect = song_text.get_rect()
	song_text_rect.topleft = (16, 48)
	screen.blit(song_text, song_text_rect)

def intro():
	global animY, player_img1, layer, ui_song, ui_timer, ui_topright, ui_levelname, topright_text

	collide()
	movep()
	animate()
	update()

	# make it say 3 2 1 go or something
	exponent, timery, layer = 1, 1, 1
	animY = 625
	player_img_load("anim/wee.png")
	while timery <= 100:
			if timery >= 1:
				ui_levelname = True
			if timery >= 25:
				ui_song = True
			if timery >= 50:
				ui_timer = True
			if timery >= 75:
				ui_topright = True
			timery += 1
			exponent = exponent * 1.03
			animY -= round(exponent)
			update()
	exponent, timery, layer = 1, 1, 0

level_id = 1
loadLevel(level_id)

run = True
restartable = True
while True:

	resetvars()
	loadLevel(level_id)
	intro()
	t0 = pygame.time.get_ticks()

	restartable = True
	run = True
	while run:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()

		emote = 0

		action = "walk"
		#Collision, then movement, then animations
		collide()
		movep()
			
		# hud elements
		emotes()

		animate()

		update()