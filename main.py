# By: Philooxy | https://philoxy.github.io/
# new record 800 lines

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
font1big = pygame.font.Font('assets/determination.ttf', 80)

Tilegroup = pygame.sprite.Group()
Tilegroup_nocol = pygame.sprite.Group()
player_img1 = icon

playerx = 112
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
t0, t1 = 0, 0
# 0 left 1 up 2 right 3 down
move = 2
layer = 0
emote = 0
emotemenu = False
action = "walk"
restartable = False
ui_timer, ui_song, ui_topright, ui_levelname, ui_timer2 = False, False, False, False, False
shadow = False
button_pressed = False
level_id = 1
cover = pygame.Surface((640,640), pygame.SRCALPHA)
cover.fill((0,0,0,100))

def resetvars():
	global playerx, playery, player_rect, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY, animX, animY, walk, addwalk, walksprite, direction, move, layer, emote, emotemenu, action, ui_timer, ui_song, ui_topright, ui_levelname, ui_timer2, shadow, button_pressed

	Tilegroup.empty()
	Tilegroup_nocol.empty()

	playerx = 176
	playery = 240
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
	move = 2
	layer = 0
	emote = 0
	emotemenu = False
	action = "walk"
	ui_timer, ui_song, ui_topright, ui_levelname, ui_timer2 = False, False, False, False, False
	shadow = False
	button_pressed = False


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
		global offsetX, offsetY, level_id, playerx, playery
		if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
			surface.blit(self.map_surface, (-(offsetX % 128)-48, -(offsetY % 128)))
		else:
			surface.blit(self.map_surface, (336-offsetX, 320-offsetY))

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
		global level_id, button_pressed, offsetX, offsetY
		tiles = []
		map = self.read_csv(filename)
		x, y = 0, 0
		for row in map:
			x = 0
			for tile in row:
				if tile == "0":
					Temptile = Tile("water", x * self.tile_size, y * self.tile_size, self.spritesheet, "water")
					tiles.append(Temptile)
					if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "1":
					Temptile = Tile("wall1", x * self.tile_size, y * self.tile_size, self.spritesheet, "wall1")
					tiles.append(Temptile)
					if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "2":
					Temptile = Tile("bridge", x * self.tile_size, y * self.tile_size, self.spritesheet, "bridge")
					tiles.append(Temptile)
					Tilegroup_nocol.add(Temptile)

				elif tile == "3":
					Temptile = Tile("exit", x * self.tile_size, y * self.tile_size, self.spritesheet, "exit")
					tiles.append(Temptile)
					if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "4":
					Temptile = Tile("wall3", x * self.tile_size, y * self.tile_size, self.spritesheet, "wall3")
					tiles.append(Temptile)
					if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "5":
					Temptile = Tile("path", x * self.tile_size, y * self.tile_size, self.spritesheet, "path")
					tiles.append(Temptile)
					Tilegroup_nocol.add(Temptile)

				elif tile == "6":
					Temptile = Tile("bridge2", x * self.tile_size, y * self.tile_size, self.spritesheet, "bridge2")
					tiles.append(Temptile)
					Tilegroup_nocol.add(Temptile)

				elif tile == "7":
					Temptile = Tile("ladder", x * self.tile_size, y * self.tile_size, self.spritesheet, "ladder")
					tiles.append(Temptile)
					if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "8":
					if button_pressed == False:
						buttontype = "button1"
					else:
						buttontype = "button2"
					Temptile = Tile(buttontype, x * self.tile_size, y * self.tile_size, self.spritesheet, "button")
					tiles.append(Temptile)
					if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "10":
					Temptile = Tile("blank", x * self.tile_size, y * self.tile_size, self.spritesheet, "blank")
					tiles.append(Temptile)
					if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "11":
					if button_pressed == False:
						doortype = "door1"
					else:
						doortype = "door2"
					Temptile = Tile(doortype, x * self.tile_size, y * self.tile_size, self.spritesheet, "door")
					tiles.append(Temptile)
					if self.filename == "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv":
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				x += 1
			y += 1

		self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
		return tiles

# general functions for player


#this function is a mess please dont look at it
#im not that good at pygame ok
def collide():
	global collide_down, collide_up, collide_right, collide_left, playerx, playery, walk, layer, player_rect, action, win, playery, direction, map_below2, level_id, button_pressed, offsetX, offsetY, run, move
	pressed_keys = pygame.key.get_pressed()
	collide_down = False
	collide_up = False
	collide_right = False
	collide_left = False

	for i in list(Tilegroup.sprites()):

		if not layer == 1 and (i.type == "wall3"):
			if i.rect.left - 31 <= player_rect.left <= i.rect.right - 1:
				if pressed_keys[pygame.K_DOWN] and i.rect.top <= player_rect.bottom - 16 <= i.rect.top + 4:
					collide_down = True
				if pressed_keys[pygame.K_UP] and i.rect.bottom >= player_rect.top + 16 >= i.rect.bottom - 4:
					collide_up = True
			if i.rect.top - 15 <= player_rect.top <= i.rect.bottom - 1:
				if pressed_keys[pygame.K_RIGHT] and i.rect.left <= player_rect.right <= i.rect.left + 4:
					collide_right = True
				if pressed_keys[pygame.K_LEFT] and i.rect.right >= player_rect.left >= i.rect.right - 4:
					collide_left = True

			if (player_rect.right, player_rect.top) == (i.rect.left+4, i.rect.bottom-4):
				playerx -= 4
			elif (player_rect.right, player_rect.top) == (i.rect.left+2, i.rect.bottom-2):
				playerx -= 2

			if (player_rect.left, player_rect.top) == (i.rect.right-4, i.rect.bottom-4):
				playerx += 4
			if (player_rect.left, player_rect.top) == (i.rect.right-2, i.rect.bottom-2):
				playerx += 2

			if (player_rect.right, player_rect.bottom) == (i.rect.left+4, i.rect.top+16+4):
				playerx -= 4
			if (player_rect.right, player_rect.bottom) == (i.rect.left+2, i.rect.top+16+2):
				playerx -= 2

			if (player_rect.left, player_rect.bottom) == (i.rect.left-4, i.rect.bottom+16+4):
				playerx -= 4
			if (player_rect.left, player_rect.bottom) == (i.rect.left-2, i.rect.bottom+16+2):
				playerx -= 2

		# this is just any generic block collision
		elif (layer == 1 and i.type == "blank") or i.type == "water" or (i.type == "door" and button_pressed == False):
			if i.rect.left - 31 <= player_rect.left <= i.rect.right - 1:
				if pressed_keys[pygame.K_DOWN] and i.rect.top <= player_rect.bottom <= i.rect.top + 4:
					collide_down = True
				if pressed_keys[pygame.K_UP] and i.rect.bottom >= player_rect.top >= i.rect.bottom - 4:
					collide_up = True
			if i.rect.top - 31 <= player_rect.top <= i.rect.bottom - 1:
				if pressed_keys[pygame.K_RIGHT] and i.rect.left <= player_rect.right <= i.rect.left + 4:
					collide_right = True
				if pressed_keys[pygame.K_LEFT] and i.rect.right >= player_rect.left >= i.rect.right - 4:
					collide_left = True

			
			if (player_rect.right, player_rect.top) == (i.rect.left+4, i.rect.bottom-4):
				playerx -= 4
			elif (player_rect.right, player_rect.top) == (i.rect.left+2, i.rect.bottom-2):
				playerx -= 2

			if (player_rect.left, player_rect.top) == (i.rect.right-4, i.rect.bottom-4):
				playerx += 4
			if (player_rect.left, player_rect.top) == (i.rect.right-2, i.rect.bottom-2):
				playerx += 2

			if (player_rect.right, player_rect.bottom) == (i.rect.left+4, i.rect.top+4):
				playerx -= 4
			if (player_rect.right, player_rect.bottom) == (i.rect.left+2, i.rect.top+2):
				playerx -= 2

			if (player_rect.left, player_rect.bottom) == (i.rect.left-4, i.rect.bottom+4):
				playerx -= 4
			if (player_rect.left, player_rect.bottom) == (i.rect.left-2, i.rect.bottom+2):
				playerx -= 2
		
		elif i.type == "exit":
			if i.rect.left + 12 <= player_rect.center[0] <= i.rect.right - 12 and i.rect.top + 12 <= player_rect.center[1] <= i.rect.bottom - 12:
				winlvl("win")

		elif i.type == "ladder" or i.type == "button":
			if player_rect.colliderect(i.rect):
				if i.rect.bottom+1 >= player_rect.center[1] >= i.rect.top and i.type == "ladder":
					action = "climb"
					if i.rect.top <= player_rect.center[1]<= i.rect.top + 32:
						layer = 1
					else:
						layer = 0
				if i.type == "button" and button_pressed == False:
					offsetX2, offsetY2 = offsetX, offsetY
					offsetX, offsetY = 0, 0
					button_pressed = True
					map_below_temp = TileMap('levels/level'+str(level_id)+'/level'+str(level_id)+'_back2.csv', spritesheet)
					map_below2 = map_below_temp
					offsetX, offsetY = offsetX2, offsetY2
					

		elif layer == 0 and i.type == "wall1":
			if i.rect.left - 31 <= player_rect.left <= i.rect.right - 1:
				if pressed_keys[pygame.K_DOWN] and i.rect.top <= player_rect.bottom - 16 <= i.rect.top + 4:
					collide_down = True
				if pressed_keys[pygame.K_UP] and i.rect.bottom >= player_rect.top + 16 >= i.rect.bottom - 4:
					collide_up = True
			if i.rect.top - 15 <= player_rect.top <= i.rect.bottom - 17:
				if pressed_keys[pygame.K_RIGHT] and i.rect.left <= player_rect.right <= i.rect.left + 4:
					collide_right = True
				if pressed_keys[pygame.K_LEFT] and i.rect.right >= player_rect.left >= i.rect.right - 4:
					collide_left = True

			if (player_rect.right, player_rect.top) == (i.rect.left+4, i.rect.bottom-16-4):
				playerx -= 4
			elif (player_rect.right, player_rect.top) == (i.rect.left+2, i.rect.bottom-16-2):
				playerx -= 2

			if (player_rect.left, player_rect.top) == (i.rect.right-4, i.rect.bottom-16-4):
				playerx += 4
			if (player_rect.left, player_rect.top) == (i.rect.right-2, i.rect.bottom-16-2):
				playerx += 2

			if (player_rect.right, player_rect.bottom) == (i.rect.left+4, i.rect.top+16+4):
				playerx -= 4
			if (player_rect.right, player_rect.bottom) == (i.rect.left+2, i.rect.top+16+2):
				playerx -= 2

			if (player_rect.left, player_rect.bottom) == (i.rect.left-4, i.rect.bottom+16+4):
				playerx -= 4
			if (player_rect.left, player_rect.bottom) == (i.rect.left-2, i.rect.bottom+16+2):
				playerx -= 2



				

def movep():
	global playerx, playery, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY, walk, walksprite, direction, addwalk, emote, action, emotemenu, restartable, topright_text
	addwalk, run = False, False
	pressed_keys = pygame.key.get_pressed()

	if pressed_keys[pygame.K_x] and action == "walk":
		playerx = 4*round(playerx/4)
		playery = 4*round(playery/4)
		move = 4
		run = True
	else:
		move = 2

	if pressed_keys[pygame.K_LEFT]:
		direction = 0
		if collide_left == False:
			playerx -= move
			addwalk = True
	elif pressed_keys[pygame.K_RIGHT]:
		direction = 2
		if collide_right == False:
			playerx += move
			addwalk = True
	if pressed_keys[pygame.K_UP]:
		direction = 1
		if collide_up == False:
			playery -= move
			addwalk = True
	elif pressed_keys[pygame.K_DOWN]:
		direction = 3
		if collide_down == False:
			playery += move
			addwalk = True

	if pressed_keys[pygame.K_r] and restartable == True:
		pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()/4)
		winlvl("restart")
		pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()*4)
	elif pressed_keys[pygame.K_ESCAPE] and restartable == True:
		pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()/4)
		winlvl("exit")
		pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()*4)

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
	global spritesheet, map_below, map_above, map_below2, map_above2, map_above3, level_mus, bg, songname, levelname, topright_text, shadow
	level_num = str(level_num)
	spritesheet = Spritesheet('levels/level'+level_num+'/spritesheet.png')
	map_below = TileMap('levels/level'+level_num+'/level'+level_num+'_back.csv', spritesheet)
	map_above = TileMap('levels/level'+level_num+'/level'+level_num+'_front.csv', spritesheet)
	map_above2 = TileMap('levels/level'+level_num+'/level'+level_num+'_front2.csv', spritesheet)
	map_below2 = TileMap('levels/level'+level_num+'/level'+level_num+'_back2.csv', spritesheet)
	map_above3 = TileMap('levels/level'+level_num+'/level'+level_num+'_front3.csv', spritesheet)
	bg = TileMap('levels/level'+level_num+'/level'+level_num+'_bg.csv', spritesheet)
	with open("levels/level"+level_num+"/info.txt", "r") as f:
		texty = f.read()
		texty = texty.split("\n")
		levelname = texty[0]
		songname = texty[1]
		topright_text = texty[2]
		if texty[3] == "1":
			shadow = True
		elif texty[3] == "0":
			shadow = False
	level_mus = pygame.mixer.music.load("assets/music/level"+level_num+".mp3")
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(0.1)

def player_img_load(image_path):
	global player_img1
	player_img1 = pygame.image.load("assets/player/"+image_path)

def winlvl(type):
	global level_id, animY, layer, player_img1, run, restartable, topright_text, win, title, t0, offsetX, offsetY
	restartable = False
	animY = 0
	if not type == "exit":
		layer = 1
		player_img_load("anim/wee.png")
	win = True
	if type == "win":
		tada = pygame.mixer.Sound("assets/sounds/tada.mp3")
		channel = tada.play()
		tada.set_volume(0.5)
	exponent, timery = 1, 1
	if not type == "exit":
		player_img_temp = player_img1
		while timery <= 100:
			if timery/5 == round(timery/5):
				player_img1 = pygame.transform.rotozoom(player_img_temp, 90*timery, 1/(timery/5))
			timery += 1
			exponent = exponent * 1.03
			animY += round(exponent)
			update()
	if type == "win":
		level_id += 1
		run = False
		resetvars()
		try:
			loadLevel(level_id)
		except FileNotFoundError:
			print("next level not found")
			sys.exit()
	elif type == "restart":
		update()
		run = False
	elif type == "exit":
		update()
		restartable = True
		title = True
		t1 = pygame.time.get_ticks()-t0
		while title:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			titlescreen("pause")

		t2 = pygame.time.get_ticks()-t0
		t0 += (t2-t1)

def update():
	global playerx, playery, offsetX, offsetY, player_img1, player_rect, action, clock, animY, ui_timer, ui_levelname, ui_song, topright_text, shadow, shadowcircle

	clock.tick(60)

	bg.draw_map(screen)
	
	player_img = player_img1
	player_img.set_colorkey((255, 0, 208))
	player_rect.topleft = (playerx-32, playery)
	map_below.draw_map(screen)
	map_below2.draw_map(screen)

	if layer == 1 or action == "climb":
		map_above.draw_map(screen)
		map_above2.draw_map(screen)
		screen.blit(player_img, pygame.Rect(288+animX, 288-animY, 32, 32))
	elif layer == 0:
		screen.blit(player_img, pygame.Rect(288+animX, 288-animY, 32, 32))
		map_above.draw_map(screen)
		map_above2.draw_map(screen)

	map_above3.draw_map(screen)

	if shadow == True:
		screen.blit(cover, (0,0))
		screen.blit(shadowcircle, pygame.Rect(0,0,640,640))

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
	elif action == "climb":
		if walksprite == 0:
			player_img1 = pygame.image.load("assets/player/climb/climb2.png")
		else:
			player_img1 = pygame.image.load("assets/player/climb/climb"+str(walksprite)+".png")

	if emote == 1:
		player_img1 = pygame.image.load("assets/player/emote/why.png")
	elif emote == 2:
		for i in range(3):
			player_img1 = pygame.transform.rotate(player_img1, 90)

	player_img1.set_colorkey((255, 0, 208))
	player_img = player_img1

def timer():
	global ui_timer, t0, win, ui_timer2, minutes, seconds, ms
	ms = (pygame.time.get_ticks()-t0)
	seconds = math.floor(ms/1000) % 60
	ms = math.floor((ms-seconds*1000))
	ms2 = ms % 1000
	if seconds < 10:
		seconds = "0"+str(seconds)
	minutes = math.floor(ms/60000)
	if minutes < 10:
		minutes = "0"+str(minutes)
	if ms < 10:
		ms = "00"+str(ms)
	elif 10 < ms < 100:
		ms = "0"+str(ms)
		
	if ui_timer2 == True:
		timer_text = font1.render("Time: "+str(minutes)+":"+str(seconds)+'"'+str(ms2), True, (255, 255, 255))
	else:
		timer_text = font1.render('Time: 00:00"00', True, (255, 255, 255))
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
	global animY, player_img1, layer, ui_song, ui_timer, ui_topright, ui_levelname, topright_text, animX, animY, player_img1, ui_timer2

	collide()
	movep()
	animate()
	update()

	# make it say 3 2 1 go or something
	exponent, layer = 1, 1
	animY = 625
	player_img_load("anim/wee.png")
	for i in range(99):
		if i >= 1:
			ui_levelname = True
		if i >= 25:
			ui_song = True
		if i >= 50:
			ui_timer = True
		if i >= 75:
			ui_topright = True
		exponent = exponent * 1.03
		animY -= round(exponent)
		update()
	ui_timer2 = True
	exponent, layer = 1, 0
	animY = 0

def rendertext(text, fontsize, color, place, position):
	if fontsize == "small":
		text1 = font1small.render(text, True, color)
	elif fontsize == "big":
		text1 = font1big.render(text, True, color)
	elif fontsize == "normal":
		text1 = font1.render(text, True, color)

	text1_rect = text1.get_rect()
	if position == "topleft":
		text1_rect.topleft = place
	elif position == "topright":
			text1_rect.topright = place
	elif position == "bottomleft":
			text1_rect.bottomleft = place
	elif position == "bottomright":
			text1_rect.bottomright = place
	elif position == "center":
		text1_rect.center = place
	screen.blit(text1, text1_rect)

def titlescreen(titletype):
	global offsetX, offsetY, title, xdir, ydir, title_text2, title_text2_rect, cursor, keypress, level_mus, cover, shadow

	screen.fill((255,255,255))
	bg.draw_map(screen)
	map_below.draw_map(screen)
	map_below2.draw_map(screen)
	map_above.draw_map(screen)
	map_above2.draw_map(screen)
	if offsetX >= map_below.map_surface.get_size()[0]-192:
		xdir = -1
	elif offsetX <= +192:
		xdir = 1
	offsetX += 1*xdir
	if offsetY >= map_below.map_surface.get_size()[1]-192:
		ydir = -1
	elif offsetY <= +192:
		ydir = 1
	offsetY += 1*ydir

	#VERY useful bit of code
	pressed_keys = pygame.key.get_pressed()
	if keypress == False:
		if pressed_keys[pygame.K_UP]:
			cursor -= 1
		elif pressed_keys[pygame.K_DOWN]:
			cursor += 1
		if pressed_keys[pygame.K_z]:
			if titletype == "title":
				if cursor == 0:
					title = False
				if cursor == 1:
					print("not yet")
				if cursor == 2:
					titletype == "options"
				if cursor == 3:
					titletype == "help"
				if cursor == 4:
					sys.exit()
			elif titletype == "pause":
				if cursor == 0:
					title = False
				if cursor == 1:
					title = False
					winlvl("restart")
				if cursor == 2:
					titletype == "options"
				if cursor == 3:
					titletype == "help"
				if cursor == 4:
					sys.exit()
	if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_z]:
		keypress = True
	else:
		keypress = False
	
	maxcursor = 4

	if cursor < 0:
		cursor = maxcursor
	elif cursor > maxcursor:
		cursor = 0

	cursory = 60*cursor

	if shadow == True:
		screen.blit(shadowcircle, pygame.Rect(0,0,640,640))

	screen.blit(cover, (0,0))

	if titletype == "title":
		text1 = font1big.render("MAZETEST 2", True, (255, 255, 255))
		text2 = pygame.transform.rotate(text1, 5*(math.sin(offsetX/50)))
		text1_rect = text2.get_rect()
		text1_rect.center = (320, 128)
		screen.blit(text2, text1_rect)
		rendertext("Version 0.8.3", "small", (255, 255, 255), (630, 600), "topright")
		rendertext("By Philooxy", "small", (255, 255, 255), (630, 630), "bottomright")

		rendertext("Play", "normal", (255, 255, 255), (120, 320), "topleft")
		rendertext("Level Select", "normal", (255, 255, 255), (120, 380), "topleft")
		rendertext("Options", "normal", (255, 255, 255), (120, 440), "topleft")
		rendertext("Help", "normal", (255, 255, 255), (120, 500), "topleft")
		rendertext("Quit", "normal", (255, 0, 0), (120, 560), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90, 320+cursory), "topleft")

	elif titletype == "pause":
		text1 = font1big.render("Paused", True, (255, 255, 255))
		text2 = pygame.transform.rotate(text1, 5*(math.sin(offsetX/50)))
		text1_rect = text2.get_rect()
		text1_rect.center = (320, 128)
		screen.blit(text2, text1_rect)
		rendertext("MAZETEST 2 v0.8.3", "small", (255, 255, 255), (630, 630), "bottomright")

		rendertext("Resume", "normal", (255, 255, 255), (120, 320), "topleft")
		rendertext("Restart", "normal", (255, 255, 255), (120, 380), "topleft")
		rendertext("Options", "normal", (255, 255, 255), (120, 440), "topleft")
		rendertext("Help", "normal", (255, 255, 255), (120, 500), "topleft")
		rendertext("Quit", "normal", (255, 0, 0), (120, 560), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90, 320+cursory), "topleft")

	pygame.display.flip()

shadowcircle = pygame.image.load("assets/shadow.png")
shadowcircle.set_colorkey((255, 0, 208))

run, restartable, title = True, True, True
loadLevel(level_id)
offsetX, offsetY, xdir, ydir = 0, 256, 1, 1
cursor = 0
title_mus = pygame.mixer.music.load("assets/music/hotel1.mp3")
pygame.mixer.music.play(-1)
keypress = False

while title:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	titlescreen("title")

offsetY, offsetX = 0, 0
pygame.mixer.music.stop()
while True:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

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

		emote, action = 0, "walk"

		collide()
		movep()

		emotes()

		animate()

		update()