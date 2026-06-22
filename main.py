# By: Philooxy | https://philoxy.github.io/
# new record 800 lines

import pygame, sys, csv, os, json, math

pygame.init()
pygame.font.init()
WIDTH = 640
HEIGHT = 640
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=1) 

icon = pygame.image.load("assets/icon.png")
icon.set_colorkey((255,0,208))
pygame.display.set_caption("MAZETEST 2")
pygame.display.set_icon(icon)
pygame.mixer.init()
clock = pygame.time.Clock()

font1 = pygame.font.Font('assets/determination.ttf', 24)
font1small = pygame.font.Font('assets/determination.ttf', 12)
font1big = pygame.font.Font('assets/determination.ttf', 80)

Tilegroup = pygame.sprite.Group()
Tilegroup_nocol = pygame.sprite.Group()
player_img1 = icon

playerx = WIDTH/2-208
playery = HEIGHT/2-96
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
t0, t1 = 0, 0
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
cover = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
cover.fill((0,0,0,100))
version = "0.8.7"
volume = 1
dialoguetext, dialoguecounter = "", 0

def resetvars():
	global playerx, playery, player_rect, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY, animX, animY, walk, addwalk, walksprite, direction, move, layer, emote, emotemenu, action, ui_timer, ui_song, ui_topright, ui_levelname, ui_timer2, shadow, button_pressed, cover, dialoguetext, dialoguecounter

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
	cover = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
	cover.fill((0,0,0,100))
	dialoguetext, dialoguecounter = "", 0


# Spritesheet, Tile, and Tilemap classes from this tutorial: https://www.pygame.org/project/5291/7669
class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()
        self.meta_data = "assets/spritesheet.json"
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
		if self.type == "interact":
			self.coords = (x, y)


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
			surface.blit(self.map_surface, (-(offsetX % 128)-48, -(offsetY % 128)-32))
		else:
			surface.blit(self.map_surface, ((WIDTH/2+16)-offsetX, HEIGHT/2-offsetY))

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
		bg_filename = "levels/level"+str(level_id)+"/level"+str(level_id)+"_bg.csv"
		front3_filename = "levels/level"+str(level_id)+"/level"+str(level_id)+"_front3.csv"
		x, y = 0, 0
		for row in map:
			x = 0
			for tile in row:
				if tile == "0":
					#for context this was wall2
					Temptile = Tile("water", x * self.tile_size, y * self.tile_size, self.spritesheet, "water")
					tiles.append(Temptile)
					if self.filename == bg_filename or self.filename == front3_filename:
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "1":
					Temptile = Tile("wall1", x * self.tile_size, y * self.tile_size, self.spritesheet, "wall1")
					tiles.append(Temptile)
					if self.filename == bg_filename or self.filename == front3_filename:
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
					if self.filename == bg_filename or self.filename == front3_filename:
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "4":
					Temptile = Tile("wall3", x * self.tile_size, y * self.tile_size, self.spritesheet, "wall3")
					tiles.append(Temptile)
					if self.filename == bg_filename or self.filename == front3_filename:
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
					if self.filename == bg_filename or self.filename == front3_filename:
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
					if self.filename == bg_filename or self.filename == front3_filename:
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "10":
					Temptile = Tile("blank", x * self.tile_size, y * self.tile_size, self.spritesheet, "blank")
					tiles.append(Temptile)
					if self.filename == bg_filename or self.filename == front3_filename:
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
					if self.filename == bg_filename or self.filename == front3_filename:
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				elif tile == "12":
					Temptile = Tile("blank", x * self.tile_size, y * self.tile_size, self.spritesheet, "interact")
					tiles.append(Temptile)
					if self.filename == bg_filename or self.filename == front3_filename:
						Tilegroup_nocol.add(Temptile)
					else:
						Tilegroup.add(Temptile)

				x += 1
			y += 1

		self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
		return tiles

# general functions for player

def collide():
	global collide_down, collide_up, collide_right, collide_left, playerx, playery, walk, layer, player_rect, action, win, playery, direction, map_below, map_below2, map_above, map_above2, map_above3, level_id, button_pressed, offsetX, offsetY, run, move, keypress2, interactions, dialoguecounter, dialoguetext, title
	pressed_keys = pygame.key.get_pressed()
	collide_down = False
	collide_up = False
	collide_right = False
	collide_left = False

	do_collision = False

	for i in list(Tilegroup.sprites()):

		if layer == 0 and i.type == "wall3":
			offsetY_top, offsetY_bottom = 16, 0
			do_collision = True

		if i.type == "ladder" or i.type == "button" or i.type == "interact":
			if i.rect.colliderect(pygame.Rect(player_rect.x, player_rect.y, 32, 33)):
				do_collision = False
				if i.rect.bottom >= player_rect.top >= i.rect.top - 33 and i.rect.left + 34 >= player_rect.left >= i.rect.left and i.type == "ladder":
					if i.rect.top - 17 <= player_rect.top <= i.rect.bottom:
						action = "climb"
					if i.rect.top - 33 <= player_rect.top <= i.rect.top:
						if pressed_keys[pygame.K_DOWN]:
							layer = -1
						else:
							layer = 1
					else:
						layer = 0
				if i.type == "button" and button_pressed == False:
					offsetX_temp, offsetY_temp = offsetX, offsetY
					offsetX, offsetY = 0, 0
					button_pressed = True
					level_num = str(level_id)
					map_below = TileMap('levels/level'+level_num+'/level'+level_num+'_back.csv', spritesheet)
					map_above = TileMap('levels/level'+level_num+'/level'+level_num+'_front.csv', spritesheet)
					map_above2 = TileMap('levels/level'+level_num+'/level'+level_num+'_front2.csv', spritesheet)
					map_below2 = TileMap('levels/level'+level_num+'/level'+level_num+'_back2.csv', spritesheet)
					map_above3 = TileMap('levels/level'+level_num+'/level'+level_num+'_front3.csv', spritesheet)

				if i.type == "interact":
					if keypress2 == False and pressed_keys[pygame.K_z]:
						tempname = str(int(i.coords[0]/64))+"-"+str(int(i.coords[1]/64))
						temptype = interactions[tempname]["type"]
						tempdir = interactions[tempname]["direction"]
						if temptype == "dialogue" and direction == tempdir:
							dialoguetext = ""
							if dialoguecounter > len(interactions[tempname])-2:
								dialoguecounter = 0
							if dialoguecounter != len(interactions[tempname])-2:
								dialoguetext = interactions[tempname][str(dialoguecounter)]
							dialoguecounter += 1
						elif temptype == "cutscene":
							print("not yet")
					if pressed_keys[pygame.K_z]:
						keypress2 = True
					else:
						keypress2 = False

					if dialoguetext != "":
						collide_down, collide_left, collide_right, collide_up = True, True, True, True


		# this is just any generic block collision
		if ((layer == 1 or layer == -1) and i.type == "blank") or i.type == "water" or (i.type == "door" and button_pressed == False):
			offsetY_top, offsetY_bottom = 0, 0
			do_collision = True

		if i.type == "exit":
			if i.rect.left + 12 <= player_rect.center[0] <= i.rect.right - 12 and i.rect.top + 12 <= player_rect.center[1] <= i.rect.bottom - 12:
				winlvl("win")

		if (layer == 0 or layer == -1) and i.type == "wall1":
			offsetY_top, offsetY_bottom = 0, 16
			do_collision = True

		#This has to be here or level 2 collision fails
		if i.type == "ladder" or i.type == "button" or i.type == "exit" or (layer != 1 and i.type == "blank") or ((layer == 1 or layer == -1) and i.type == "wall3") or (i.type == "wall1" and layer == 1) or (i.type == "door" and button_pressed == True) or i.type == "interact":
			do_collision = False

		if do_collision:
			if i.rect.left - 31 <= player_rect.left <= i.rect.right - 1:
				if pressed_keys[pygame.K_DOWN] and i.rect.top <= player_rect.bottom - offsetY_top <= i.rect.top + 4:
					collide_down = True
				if pressed_keys[pygame.K_UP] and i.rect.bottom >= player_rect.top + offsetY_bottom >= i.rect.bottom - 4:
					collide_up = True
			if i.rect.top - 31 + offsetY_top <= player_rect.top <= i.rect.bottom - 1 - offsetY_bottom:
				if pressed_keys[pygame.K_RIGHT] and i.rect.left <= player_rect.right <= i.rect.left + 4:
					collide_right = True
				if pressed_keys[pygame.K_LEFT] and i.rect.right >= player_rect.left >= i.rect.right - 4:
					collide_left = True

			if (player_rect.right, player_rect.top) == (i.rect.left+4, i.rect.bottom-offsetY_bottom-4):
				playerx -= 4
			elif (player_rect.right, player_rect.top) == (i.rect.left+2, i.rect.bottom-offsetY_bottom-2):
				playerx -= 2

			if (player_rect.left, player_rect.top) == (i.rect.right-4, i.rect.bottom-offsetY_bottom-4):
				playerx += 4
			if (player_rect.left, player_rect.top) == (i.rect.right-2, i.rect.bottom-offsetY_bottom-2):
				playerx += 2

			if (player_rect.right, player_rect.bottom) == (i.rect.left+4, i.rect.top+offsetY_top+4):
				playerx -= 4
			if (player_rect.right, player_rect.bottom) == (i.rect.left+2, i.rect.top+offsetY_top+2):
				playerx -= 2

			if (player_rect.left, player_rect.bottom) == (i.rect.right-4, i.rect.top+offsetY_top+4):
				playerx += 4
			if (player_rect.left, player_rect.bottom) == (i.rect.right-2, i.rect.top+offsetY_top+2):
				playerx += 2

def movep():
	global volume, playerx, playery, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY, walk, walksprite, direction, addwalk, emote, action, emotemenu, restartable, topright_text, WIDTH, HEIGHT, dialoguetext
	addwalk, run = False, False
	pressed_keys = pygame.key.get_pressed()

	if dialoguetext != "":
		walksprite = 0

	if dialoguetext == "":
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
		winlvl("restart")
	elif pressed_keys[pygame.K_ESCAPE] and restartable == True and not pressed_keys[pygame.K_z]:
		winlvl("exit")

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
	global volume, spritesheet, map_below, map_above, map_below2, map_above2, map_above3, level_mus, bg, songname, levelname, topright_text, shadow, interactions
	level_num = str(level_num)
	tempdir = "levels/level"+level_num+"/"
	spritesheet = Spritesheet(tempdir+"spritesheet.png")
	map_below = TileMap(tempdir+"level"+level_num+"_back.csv", spritesheet)
	map_above = TileMap(tempdir+'level'+level_num+'_front.csv', spritesheet)
	map_above2 = TileMap(tempdir+'level'+level_num+'_front2.csv', spritesheet)
	map_below2 = TileMap(tempdir+'level'+level_num+'_back2.csv', spritesheet)
	map_above3 = TileMap(tempdir+'level'+level_num+'_front3.csv', spritesheet)
	bg = TileMap(tempdir+'level'+level_num+'_bg.csv', spritesheet)
	with open(tempdir+"info.txt", "r") as f:
		texty = f.read()
		texty = texty.split("\n")
		levelname = texty[0]
		songname = texty[1]
		topright_text = texty[2]
		if texty[3] == "1":
			shadow = True
		elif texty[3] == "0":
			shadow = False
	f.close()
	with open(tempdir+'interact.json') as f:
		interactions = json.load(f)
	f.close()
	level_mus = pygame.mixer.music.load("assets/music/level"+level_num+".mp3")
	pygame.mixer.music.play(-1)
	pygame.mixer.music.set_volume(0.1*volume)

def player_img_load(image_path):
	global player_img1
	player_img1 = pygame.image.load("assets/player/"+image_path)
	player_img1.set_colorkey((255, 0, 208))

def winlvl(type):
	global level_id, animY, layer, player_img1, run, restartable, topright_text, win, title, t0, offsetX, offsetY, titletype
	restartable = False
	animY = 0
	if not type == "exit":
		layer = 1
		player_img_load("anim/wee.png")
	win = True
	if type == "win":
		tada = pygame.mixer.Sound("assets/sounds/tada.mp3")
		channel = tada.play()
		tada.set_volume(0.5*volume)
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
		titletype = "pause"
		t1 = pygame.time.get_ticks()-t0
		while title:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			titlescreen()

		t2 = pygame.time.get_ticks()-t0
		t0 += (t2-t1)

def update():
	global playerx, playery, offsetX, offsetY, player_img1, player_rect, action, clock, animY, ui_timer, ui_levelname, ui_song, topright_text, shadow, shadowcircle, WIDTH, HEIGHT, dialoguetext

	clock.tick(60)

	screen.fill((0,0,0))

	bg.draw_map(screen)
	
	player_img = player_img1
	player_img.set_colorkey((255, 0, 208))
	player_rect.topleft = (playerx-32, playery)
	map_below.draw_map(screen)
	map_below2.draw_map(screen)

	if layer == 1 or action == "climb" or layer == -1:
		map_above.draw_map(screen)
		map_above2.draw_map(screen)
		screen.blit(player_img, pygame.Rect((WIDTH/2-32)+animX, (HEIGHT/2-32)-animY, 32, 32))
	elif layer == 0:
		screen.blit(player_img, pygame.Rect((WIDTH/2-32)+animX, (HEIGHT/2-32)-animY, 32, 32))
		map_above.draw_map(screen)
		map_above2.draw_map(screen)

	map_above3.draw_map(screen)

	if shadow == True:
		screen.blit(cover, (0,0))
		screen.blit(shadowcircle, pygame.Rect(WIDTH/2-720, HEIGHT/2-512, 0, 0))

	emotes()

	if ui_timer == True:
		timer()

	if ui_levelname == True:
		level_name()

	if ui_song == True:
		song_name()

	if ui_topright == True:
		topright_text2 = font1small.render(topright_text, True, (255, 255, 255))
		topright_text2_rect = topright_text2.get_rect()
		topright_text2_rect.topright = (WIDTH-16, 16)
		screen.blit(topright_text2, topright_text2_rect)

	if dialoguetext != "":
		dialoguebox = pygame.Surface((580,196))
		dialoguebox.fill((0,0,0))
		screen.blit(dialoguebox, (WIDTH/2-290,HEIGHT-256, 620, 196))
		rendertext(dialoguetext, "normal", (255, 255, 255), (WIDTH/2-270, HEIGHT-246), "topleft")
	pygame.display.flip()

def animate():
	global direction, walksprite, player_img1, action, emote, animX, animY, playerx, playery, offsetX, offsetY, layer, dialoguetext
	if action == "walk":
		if direction == 0 or direction == 2:
			if walksprite == 0:
				player_img_load("idle/side.png")
			else:
				player_img_load("walk/side"+str(walksprite)+".png")

			if direction == 0:
				player_img1 = pygame.transform.flip(player_img1, True, False)
		if direction == 1:
			if walksprite == 0:
				player_img_load("idle/up.png")
			else:
				player_img_load("walk/up"+str(walksprite)+".png")
		if direction == 3:
			if walksprite == 0:
				player_img_load("idle/down.png")
			else:
				player_img_load("walk/down"+str(walksprite)+".png")
	elif action == "climb":
		if walksprite == 0:
			player_img_load("climb/climb2.png")
		else:
			player_img_load("climb/climb"+str(walksprite)+".png")

	if emote == 1:
		player_img_load("anim/why.png")
		for i in range(30):
			update()
	elif emote == 2:
		player_img1.set_colorkey((255, 0, 208))
		player_img_load("anim/wee.png")
		tempcounter = 0
		templayer = layer
		layer = 1
		for i in range(126):
			animX = 100*math.sin(i/10)
			if i/8 == math.floor(i/8):
				tempcounter += 1

			if tempcounter > 3:
				tempcounter = 0

			if tempcounter == 0:
				player_img_load("idle/side.png")
				player_img1 = pygame.transform.flip(player_img1, True, False)
			if tempcounter == 1:
				player_img_load("idle/up.png")
			if tempcounter == 2:
				player_img_load("idle/side.png")
			if tempcounter == 3:
				player_img_load("idle/down.png")

			update()
		layer = templayer
		animX = 0


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
	timer_text_rect.bottomleft = (16, HEIGHT-16)
	screen.blit(timer_text, timer_text_rect)

emotewheel = pygame.image.load("assets/hud/emotewheel.png")
emotewheel.set_colorkey((255, 0, 208))

def emotes():
	global emotemenu, emotewheel, emote, keypress, dialoguetext
	pressed_keys = pygame.key.get_pressed()

	if pressed_keys[pygame.K_e] and keypress == False:
		if emotemenu == True:
			emotemenu = False
		elif emotemenu == False:
			emotemenu = True

	if dialoguetext != "":
		emotemenu = False

	if emotemenu == True:
		screen.blit(emotewheel, (WIDTH-200, HEIGHT-200))
		if pressed_keys[pygame.K_1]:
			emote = 2
			emotemenu = False
		elif pressed_keys[pygame.K_2]:
			emote = 1
			emotemenu = False

	if pressed_keys[pygame.K_e]:
		keypress = True
	else:
		keypress = False

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


def resetScreen():
	global WIDTH, HEIGHT, cover, screen
	temp_screen_status = pygame.display.is_fullscreen()
	screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED|pygame.HWSURFACE, vsync=1) 
	cover = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
	cover.fill((0,0,0,100))
	if temp_screen_status == True:
		pygame.display.toggle_fullscreen()


def titlescreen():
	global volume, offsetX, offsetY, title, xdir, ydir, title_text2, title_text2_rect, cursor, keypress, level_mus, cover, shadow, titletype, maxcursor, offsetX, offsetY, level_id, prev_title, version, HEIGHT, WIDTH, screen

	maxcursor = 1

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
	offsetX += 0.5*xdir
	if offsetY >= map_below.map_surface.get_size()[1]-192:
		ydir = -1
	elif offsetY <= +192:
		ydir = 1
	offsetY += 0.5*ydir

	pressed_keys = pygame.key.get_pressed()
	if keypress == False:
		if pressed_keys[pygame.K_UP]:
			cursor -= 1
		elif pressed_keys[pygame.K_DOWN]:
			cursor += 1
		elif titletype == "lvlselect" or titletype == "res":
			if pressed_keys[pygame.K_LEFT]:
				cursor -= 4
			elif pressed_keys[pygame.K_RIGHT]:
				cursor += 4
		elif titletype == "options" and cursor == 0:
			if pressed_keys[pygame.K_LEFT]:
				volume -= 0.1
			elif pressed_keys[pygame.K_RIGHT]:
				volume += 0.1
			if volume > 1:
				volume = 0
			if volume < 0:
				volume = 1
			volume = int(round(volume*10))/10
		if pressed_keys[pygame.K_z]:
			if titletype == "title":
				if cursor == 0:
					title = False
				if cursor == 1:
					titletype = "lvlselect"
					cursor = 0
				if cursor == 2:
					prev_title = "title"
					titletype = "options"
					cursor = 0
				if cursor == 3:
					prev_title = "title"
					titletype = "help"
					cursor = 0
				if cursor == 4:
					sys.exit()
			elif titletype == "pause":
				if cursor == 0:
					title = False
				if cursor == 1:
					title = False
					winlvl("restart")
				if cursor == 2:
					prev_title = "pause"
					titletype = "options"
					cursor = 0
				if cursor == 3:
					prev_title = "pause"
					titletype = "help"
					cursor = 0
				if cursor == 4:
					sys.exit()
			elif titletype == "lvlselect":
				# temporary if statement until i make all lthe levels
				if cursor == 0 or cursor == 1:
					offsetX, offsetY = 0, 0
					level_id = cursor+1
					title = False
				if cursor == 7:
					titletype = "title"
					cursor = 0
			elif titletype == "options":
				if cursor == 1:
					pygame.display.toggle_fullscreen()
				if cursor == 2:
					titletype = "res"
					cursor = 0
				if cursor == 3:
					titletype = prev_title
					cursor = 0
			elif titletype == "help":
				if cursor == 0:
					print("about")
				if cursor == 1:
					print("controls")
				if cursor == 2:
					print("how to play")
				if cursor == 3:
					titletype = prev_title
					cursor = 0
			elif titletype == "res":
				if cursor == 0:
					WIDTH = 640
					HEIGHT = 640
					resetScreen()
				if cursor == 1:
					WIDTH = 1280
					HEIGHT = 720
					resetScreen()
				if cursor == 2:
					WIDTH = 1280
					HEIGHT = 1024
					resetScreen()
				if cursor == 3:
					WIDTH = 768
					HEIGHT = 576
					resetScreen()
				if cursor == 4:
					WIDTH = 1440
					HEIGHT = 900
					resetScreen()
				if cursor == 5:
					titletype = "options"
					cursor = 0

	if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_z] or pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_RIGHT]:
		keypress = True
	else:
		keypress = False
	
	if titletype == "title" or titletype == "pause":
		maxcursor = 4
	elif titletype == "lvlselect":
		maxcursor = 7
	elif titletype == "options" or titletype == "help":
		maxcursor = 3
	elif titletype == "res":
		maxcursor = 5

	if cursor < 0:
		cursor = maxcursor
	elif cursor > maxcursor:
		cursor = 0

	cursory = cursor

	screen.blit(cover, (0,0))
	if shadow == True:
		screen.blit(shadowcircle, pygame.Rect(WIDTH/2-720, HEIGHT/2-512, 0, 0))


	if titletype == "title":
		text1 = font1big.render("MAZETEST 2", True, (255, 255, 255))
		rendertext("Version "+version, "small", (255, 255, 255), (WIDTH-10, HEIGHT-40), "topright")
		rendertext("By Philooxy", "small", (255, 255, 255), (WIDTH-10, HEIGHT-10), "bottomright")

		rendertext("Play", "normal", (255, 255, 255), (120, HEIGHT*(8/16)), "topleft")
		rendertext("Level Select", "normal", (255, 255, 255), (120, HEIGHT*(9/16)), "topleft")
		rendertext("Options", "normal", (255, 255, 255), (120, HEIGHT*(10/16)), "topleft")
		rendertext("Help", "normal", (255, 255, 255), (120, HEIGHT*(11/16)), "topleft")
		rendertext("Quit", "normal", (255, 0, 0), (120, HEIGHT*(12/16)), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90, HEIGHT/2+(HEIGHT/16)*cursory), "topleft")

	elif titletype == "pause":
		text1 = font1big.render("Paused", True, (255, 255, 255))
		rendertext("MAZETEST 2 v"+version, "small", (255, 255, 255), (WIDTH-10, HEIGHT-10), "bottomright")

		rendertext("Resume", "normal", (255, 255, 255), (120, HEIGHT*(8/16)), "topleft")
		rendertext("Restart", "normal", (255, 255, 255), (120, HEIGHT*(9/16)), "topleft")
		rendertext("Options", "normal", (255, 255, 255), (120, HEIGHT*(10/16)), "topleft")
		rendertext("Help", "normal", (255, 255, 255), (120, HEIGHT*(11/16)), "topleft")
		rendertext("Quit", "normal", (255, 0, 0), (120, HEIGHT*(12/16)), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90, HEIGHT/2+(HEIGHT/16)*cursory), "topleft")

	elif titletype == "lvlselect":
		text1 = font1big.render("Levels", True, (255, 255, 255))

		rendertext("Level 1", "normal", (255, 255, 255), (120, HEIGHT*(8/16)), "topleft")
		rendertext("Level 2", "normal", (255, 255, 255), (120, HEIGHT*(9/16)), "topleft")
		rendertext("Level 3", "normal", (255, 255, 255), (120, HEIGHT*(10/16)), "topleft")
		rendertext("Level 4", "normal", (255, 255, 255), (120, HEIGHT*(11/16)), "topleft")
		rendertext("Level 5", "normal", (255, 255, 255), (320, HEIGHT*(8/16)), "topleft")
		rendertext("Level 6", "normal", (255, 255, 255), (320, HEIGHT*(9/16)), "topleft")
		rendertext("Level 7", "normal", (255, 255, 255), (320, HEIGHT*(10/16)), "topleft")
		rendertext("Back", "normal", (255, 0, 0), (320, HEIGHT*(11/16)), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90+math.floor(cursor/4)*200, HEIGHT/2+(HEIGHT/16)*(cursor % 4)), "topleft")

	elif titletype == "options":
		text1 = font1big.render("Options", True, (255, 255, 255))

		if pygame.display.is_fullscreen() == True:
			fullscreen_status = "On"
		else:
			fullscreen_status = "Off"

		rendertext("Volume: "+str(int(volume*100))+"%", "normal", (255, 255, 255), (120, HEIGHT*(8/16)), "topleft")
		rendertext("Fullscreen: "+fullscreen_status, "normal", (255, 255, 255), (120, HEIGHT*(9/16)), "topleft")
		rendertext("Resolution...", "normal", (255, 255, 255), (120, HEIGHT*(10/16)), "topleft")
		rendertext("Back", "normal", (255, 0, 0), (120, HEIGHT*(11/16)), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90, HEIGHT/2+(HEIGHT/16)*cursory), "topleft")

	elif titletype == "res":
		text1 = font1big.render("Resolution", True, (255, 255, 255))

		rendertext("640x640 (1:1)", "normal", (255, 255, 255), (120, HEIGHT*(8/16)), "topleft")
		rendertext("1280x720 (16:9)", "normal", (255, 255, 255), (120, HEIGHT*(9/16)), "topleft")
		rendertext("1280x1024 (5:4)", "normal", (255, 255, 255), (120, HEIGHT*(10/16)), "topleft")
		rendertext("768x576 (4:3)", "normal", (255, 255, 255), (120, HEIGHT*(11/16)), "topleft")
		rendertext("1440X900 (8:5)", "normal", (255, 255, 255), (120, HEIGHT*(12/16)), "topleft")
		rendertext("Back", "normal", (255, 0, 0), (120, HEIGHT*(13/16)), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90, HEIGHT/2+(HEIGHT/16)*cursory), "topleft")

	elif titletype == "help":
		text1 = font1big.render("Help", True, (255, 255, 255))

		rendertext("About", "normal", (255, 255, 255), (120, HEIGHT*(8/16)), "topleft")
		rendertext("Controls", "normal", (255, 255, 255), (120, HEIGHT*(9/16)), "topleft")
		rendertext("How to play", "normal", (255, 255, 255), (120, HEIGHT*(10/16)), "topleft")
		rendertext("Back", "normal", (255, 0, 0), (120, HEIGHT*(11/16)), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90, HEIGHT/2+(HEIGHT/16)*cursory), "topleft")


	text2 = pygame.transform.rotate(text1, 5*(math.sin(offsetX/50)))
	text1_rect = text2.get_rect()
	text1_rect.center = (WIDTH/2, HEIGHT/5)
	screen.blit(text2, text1_rect)

	pygame.mixer.music.set_volume(0.1*volume)

	pygame.display.flip()

shadowcircle = pygame.image.load("assets/shadow.png")
shadowcircle.set_colorkey((255, 0, 208))

run, restartable, title = True, True, True
loadLevel(level_id)
offsetX, offsetY, xdir, ydir = 0, 256, 1, 1
cursor = 0
title_mus = pygame.mixer.music.load("assets/music/hotel1.mp3")
pygame.mixer.music.play(-1)
keypress, keypress2 = False, False
titletype, prev_title = "title", "title"
dialoguecounter = 0

while title:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
	titlescreen()

offsetY, offsetX = 0, 0
pygame.mixer.music.stop()
while True:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

	resetvars()
	try:
		loadLevel(level_id)
	except FileNotFoundError:
		print("level not found")
		sys.exit()
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

		update()

		animate()