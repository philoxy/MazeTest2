# By: Philooxy | https://philoxy.github.io/
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame, sys, csv, json, math
from images import *

Tilegroup = pygame.sprite.Group()
Tilegroup_nocol = pygame.sprite.Group()
player_img1 = icon

playerx = WIDTH/2-208
playery = HEIGHT/2-96
player_rect = pygame.Rect(playerx, playery, 32, 32)
player_rect2 = pygame.Rect((WIDTH/2-16), (HEIGHT/2+16), 32, 16)
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
level_id = 0
cover = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
cover.fill((0,0,0,100))
version = "0.8.9"
volume = 1
dialoguetext, dialoguecounter = ["","","","",""], 0
pressed_keys = pygame.key.get_pressed()
keypress2 = False

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
	dialoguetext, dialoguecounter = ["","","","",""], 0


# Spritesheet, Tile, and Tilemap classes from this tutorial: https://www.pygame.org/project/5291/7669
class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert_alpha()
        self.meta_data = "assets/spritesheet.json"
        with open(self.meta_data) as f:
            self.data = json.load(f)
        f.close()

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.blit(self.sprite_sheet,(0, 0),(x, y, w, h))
        return sprite

    def parse_sprite(self, name):
        sprite = self.data['frames'][name]['frame']
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        image = self.get_sprite(x, y, w, h)
        return image

def loadTile(type, type2, spritesheet, nocol, x, y, list):
	global Tilegroup_nocol, Tilegroup
	Temptile = Tile(type, x*64, y*64, spritesheet, type2)
	list.append(Temptile)
	if nocol:
		Tilegroup_nocol.add(Temptile)
	else:
		Tilegroup.add(Temptile)

	return list

class Tile(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet, type):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y
		self.type = type
		self.coords = (x, y)


	def draw(self, surface):
		global offsetX, offsetY
		surface.blit(self.image, (self.rect.x-offsetX, self.rect.y-offsetY))

tileList = [["water", "water"], ["wall1", "wall1"], ["bridge", "bridge"], ["exit", "exit"], ["wall3", "wall3"], ["path", "path"], ["bridge2", "bridge2"], ["ladder", "ladder"], ["button", "button"], ["button", "button"], ["wall2", "wall2"], ["door", "door"], ["blank2", "blank2"]]
maps = []

class TileMap():
	def __init__(self, filename, spritesheet):
		global maps
		self.filename = filename
		self.tile_size = 64
		self.spritesheet = spritesheet
		self.tiles = self.load_tiles(filename)
		self.map_surface = pygame.Surface((self.map_w, self.map_h))
		self.map_surface.set_colorkey((0, 0, 0))
		maps.append(self)
		self.load_map()

	def draw_map(self, surface):
		global offsetX, offsetY, level_id, playerx, playery
		if self.filename == f'levels/level{level_id}/level{level_id}_bg.csv':
			surface.blit(self.map_surface, (-(offsetX % 128)-48, -(offsetY % 128)))
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
		global level_id, button_pressed, offsetX, offsetY, tileList
		tiles = []
		map = self.read_csv(filename)
		self.map = map
		bg_filename = f"levels/level{level_id}/level{level_id}_bg.csv"
		front2_filename = f"levels/level{level_id}/level{level_id}_front2.csv"
		x, y = 0, 0
		nocol = False
		for row in map:
			x = 0
			for tile in row:
				tile = int(tile)
				self.map[y][x] = tileList[tile][1]
				if tileList[tile][1] == "door" and tile == -1:
					self.map[y][x] = "blank"
				nocol = False
				match tile:
					case 8 | 9 | 11:
						if not button_pressed:
							tileList[tile][0] = f'{tileList[tile][1]}1'
						else:
							tileList[tile][0] = f'{tileList[tile][1]}2'
					case 2 | 6:
						nocol = True

				if self.filename == bg_filename or self.filename == front2_filename:
					nocol = True
				if tile != -1:
					tiles = loadTile(tileList[tile][0], tileList[tile][1], self.spritesheet, nocol, x, y, tiles)

				x += 1
			y += 1

		self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
		return tiles

def checkTile(x, y):
	global maps
	tiles = []
	for i in maps:
		tiles.append(i.map[y][x])
	return tiles

def rectCollide(rect1, rect2, offsetTop, offsetBottom):
	global playerx, collide_left, collide_up, collide_right, collide_down
	pressed_keys = pygame.key.get_pressed()

	if rect1.left - 31 <= rect2.left <= rect1.right -1 :
		if pressed_keys[pygame.K_DOWN] and rect1.top <= rect2.bottom - offsetTop <= rect1.top + 4:
			collide_down = True
		if pressed_keys[pygame.K_UP] and rect1.bottom >= rect2.top + offsetBottom >= rect1.bottom - 4:
			collide_up = True
	if rect1.top - 31 + offsetTop <= rect2.top <= rect1.bottom - offsetBottom -1:
		if pressed_keys[pygame.K_RIGHT] and rect1.left <= rect2.right <= rect1.left + 4:
			collide_right = True
		if pressed_keys[pygame.K_LEFT] and rect1.right >= rect2.left >= rect1.right - 4:
			collide_left = True

	if (rect2.right, rect2.top) == (rect1.left+4, rect1.bottom-offsetBottom-4):
		playerx -= 4
	elif (rect2.right, rect2.top) == (rect1.left+2, rect1.bottom-offsetBottom-2):
		playerx -= 2

	if (rect2.left, rect2.top) == (rect1.right-4, rect1.bottom-offsetBottom-4):
		playerx += 4
	if (rect2.left, rect2.top) == (rect1.right-2, rect1.bottom-offsetBottom-2):
		playerx += 2

	if (rect2.right, rect2.bottom) == (rect1.left+4, rect1.top+offsetTop+4):
		playerx -= 4
	if (rect2.right, rect2.bottom) == (rect1.left+2, rect1.top+offsetTop+2):
		playerx -= 2

	if (rect2.left, rect2.bottom) == (rect1.right-4, rect1.top+offsetTop+4):
		playerx += 4
	if (rect2.left, rect2.bottom) == (rect1.right-2, rect1.top+offsetTop+2):
		playerx += 2
# because any() didnt work
def matchVar(var, *args):
	matching = False
	for argument in args:
		if var == argument:
			matching = True
	return matching

def collide():
	global collide_down, collide_up, collide_right, collide_left, playerx, playery, walk, layer, player_rect, player_rect2, action, win, playery, direction, map_below, map_below2, map_above, map_above2, level_id, button_pressed, offsetX, offsetY, run, move, keypress2, interactions, dialoguecounter, dialoguetext, title, pressed_keys
	collide_down = False
	collide_up = False
	collide_right = False
	collide_left = False

	pressed_keys = pygame.key.get_pressed()

	for i in list(Tilegroup.sprites()):

		do_collision = False
		offsetY_top, offsetY_bottom = 0, 16

		tiles = checkTile(int(i.coords[0]/64), int(i.coords[1]/64))

		if tiles[2] == "ladder":
			if i.rect.colliderect(player_rect):
				if i.rect.top - 17 <= player_rect.top <= i.rect.bottom:
					action = "climb"
				if i.rect.top - 33 <= player_rect.top <= i.rect.top:
					if pressed_keys[pygame.K_DOWN]:
						layer = -1
					else:
						layer = 1
				else:
					layer = 0
			do_collision = False
			if not action == "climb":
				do_collision = True
		if i.type == "button" and button_pressed == False and i.rect.colliderect(player_rect):
			offsetX_temp, offsetY_temp = offsetX, offsetY
			offsetX, offsetY = 0, 0
			button_pressed = True
			level_num = str(level_id)
			maps = []
			Tilegroup.empty()
			Tilegroup_nocol.empty()
			map_below = TileMap(f'levels/level{level_num}/level{level_num}_back.csv', spritesheet)
			map_above = TileMap(f'levels/level{level_num}/level{level_num}_front.csv', spritesheet)
			map_below2 = TileMap(f'levels/level{level_num}/level{level_num}_back2.csv', spritesheet)
			map_above2 = TileMap(f'levels/level{level_num}/level{level_num}_front2.csv', spritesheet)

		if i.type == "exit":
			if i.rect.left + 12 <= player_rect.center[0] <= i.rect.right - 12 and i.rect.top + 12 <= player_rect.center[1] <= i.rect.bottom - 12:
				winlvl("win")

		if i.type == "door" and not button_pressed:
			offsetY_bottom = 0
			do_collision = True

		if action == "climb":

			if matchVar(i.type, "blank2"):
				do_collision = True

			if tiles[1] == "blank" and not tiles[2] == "ladder":
				do_collision = True

		if matchVar(tiles[0], "water", "wall1", "wall2") and (not action == "climb" or not tiles[2] == "ladder"):
			do_collision = True

		if tiles[0] == "wall1" and tiles[2] == "ladder":
			do_collision = False

		if player_rect.left <= 0:
			collide_left = True
		if player_rect.right >= len(map_below.map[0])*64:
			collide_right = True
		if player_rect.top <= 0:
			collide_up = True
		if player_rect.bottom >= len(map_below.map)*64:
			collide_down = True

		if layer == 0 and i.type == "wall3":
			offsetY_top, offsetY_bottom = 16, 0
			do_collision = True

		if (layer == 1 or layer == -1) and not matchVar(tiles[1], "wall3", "bridge") and matchVar(tiles[0], "path"):
			do_collision = True

		if layer == 1 and not action == "climb" and matchVar(tiles[1], "bridge", "wall3") and matchVar(tiles[0], "wall1", "wall2", "path", "water"):
			do_collision = False

		if do_collision:
			rectCollide(i.rect, player_rect, offsetY_top, offsetY_bottom)

def movep():
	global volume, playerx, playery, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY, walk, walksprite, direction, addwalk, emote, action, emotemenu, restartable, topright_text, WIDTH, HEIGHT, dialoguetext, pressed_keys
	addwalk, run = False, False
	pressed_keys = pygame.key.get_pressed()

	if dialoguetext != ["","","","",""]:
		walksprite = 0

	if dialoguetext == ["","","","",""]:
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
	global volume, spritesheet, map_below, map_above, map_below2, map_above2, level_mus, bg, songname, levelname, topright_text, shadow, interactions, maps, playerx, playery
	maps = []
	tempdir = f'levels/level{level_num}/'
	spritesheet = Spritesheet(f'{tempdir}spritesheet.png')
	map_below = TileMap(f'{tempdir}/level{level_num}_back.csv', spritesheet)
	map_above = TileMap(f'{tempdir}/level{level_num}_front.csv', spritesheet)
	map_below2 = TileMap(f'{tempdir}/level{level_num}_back2.csv', spritesheet)
	map_above2 = TileMap(f'{tempdir}/level{level_num}_front2.csv', spritesheet)
	bg = TileMap(f'{tempdir}level{level_num}_bg.csv', spritesheet)
	maps.remove(map_above2)
	maps.remove(bg)
	with open(f'{tempdir}info.txt', "r") as f:
		texty = f.read()
		texty = texty.split("\n")
		levelname = texty[0]
		songname = texty[1]
		topright_text = texty[2]
		if texty[3] == "1":
			shadow = True
		else:
			shadow = False
		temppos = json.loads(texty[4])
		playerx, playery = temppos[0]*64+48, temppos[1]*64+32

	try:
		with open(f'{tempdir}interact.json') as f:
			interactions = json.load(f)
	except FileNotFoundError:
		interactions = []

	if level_num != 0:
		level_mus = pygame.mixer.music.load(f'assets/music/level{level_num}.mp3')
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
		player_anim_wee
	win = True
	if type == "win":
		tada.play()
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

def facingRect(rect):
	global direction, player_rect
	facing = False
	#if direction == 0:
	#	if rect:
	#return facing

def dialogue():
	global interactions, offsetX, offsetY, dialoguetext, dialoguecounter, keypress2, collide_left, collide_down, collide_right, collide_up, playerx, playery, player_rect, player_rect2, layer, pressed_keys
	
	for i in interactions:
		tempobj = loadify(f'levels/level{level_id}/interact/{i}.png')
		#tempobjrect = tempobj.get_rect()
		tempobjrect = pygame.Rect((WIDTH/2)-offsetX+interactions[i]["posx"] + interactions[i]["colx1"]+16, (HEIGHT/2)-offsetY+interactions[i]["posy"] + interactions[i]["coly1"],  interactions[i]["colx2"], interactions[i]["coly2"])

		tempobjrect2 = pygame.Rect((WIDTH/2)-offsetX+interactions[i]["posx"] + interactions[i]["rectx1"]+16, (HEIGHT/2)-offsetY+interactions[i]["posy"] + interactions[i]["recty1"], interactions[i]["rectx2"], interactions[i]["recty2"])
		offsetY_top, offsetY_bottom = 0, 0

		if layer == interactions[i]["layer"]:

			rectCollide(tempobjrect, player_rect2, 0, 0)

		if player_rect2.colliderect(tempobjrect2):

			if keypress2 == False and pressed_keys[pygame.K_z] and layer == interactions[i]["layer"]:
				dialoguetext = ["","","","",""]
				if dialoguecounter > len(interactions[i])-11:
					dialoguecounter = 0
				if dialoguecounter != len(interactions[i])-11:
					dialoguetext = interactions[i][str(dialoguecounter)]
				dialoguecounter += 1

			if pressed_keys[pygame.K_z]:
				keypress2 = True
			else:
				keypress2 = False

			if dialoguetext != ["","","","",""]:
				collide_down, collide_left, collide_right, collide_up = True, True, True, True

		#pygame.draw.rect(screen, (255, 255, 0), tempobjrect2)
		#pygame.draw.rect(screen, (255, 0, 255), tempobjrect)

	#pygame.draw.rect(screen, (255,0,0), player_rect2)

def drawNpc(layer):
	global tempobj, tempobjrect, offsetX, interactions
	for i in interactions:
		if interactions[i]["layer"] == layer:
			tempobj = loadify(f'levels/level{level_id}/interact/{i}.png')
			tempobjrect = tempobj.get_rect()
			tempobjrect = pygame.Rect((WIDTH/2)-offsetX+interactions[i]["posx"], (HEIGHT/2)-offsetY+interactions[i]["posy"], tempobjrect[2], tempobjrect[3])
			tempobj.set_colorkey((255, 0, 208))
			screen.blit(tempobj, pygame.Rect(tempobjrect))

def npcdisplay(npclayer, dispplayer):
	global interactions, playery, player_img1

	player_img = player_img1
	player_img.set_colorkey((255, 0, 208))

	if len(interactions) != 0:
		for i in interactions:
			if interactions[i]["layer"] == npclayer:
				tempobj = pygame.image.load(f'levels/level{level_id}/interact/{str(i)}.png')
				tempobjrect = tempobj.get_rect()
				tempobjrect = pygame.Rect((WIDTH/2)-offsetX+interactions[i]["posx"]+16, (HEIGHT/2)-offsetY+interactions[i]["posy"], tempobjrect[2], tempobjrect[3])
				tempobj.set_colorkey((255, 0, 208))

				if dispplayer == True:
					if playery < interactions[i]["posy"] + interactions[i]["recty1"] + (interactions[i]["recty2"]/2) - 20:
						screen.blit(player_img, pygame.Rect((WIDTH/2-32)+animX, (HEIGHT/2-32)-animY, 32, 32))
						screen.blit(tempobj, tempobjrect)
					else:
						screen.blit(tempobj, tempobjrect)
						screen.blit(player_img, pygame.Rect((WIDTH/2-32)+animX, (HEIGHT/2-32)-animY, 32, 32))
				else:
					screen.blit(tempobj, tempobjrect)
	else:
		if dispplayer == True:
			screen.blit(player_img, pygame.Rect((WIDTH/2-32)+animX, (HEIGHT/2-32)-animY, 32, 32))

def update():
	global playerx, playery, offsetX, offsetY, player_img1, player_rect, player_rect2, action, clock, animY, ui_timer, ui_levelname, ui_song, topright_text, shadow, shadowcircle, WIDTH, HEIGHT, dialoguetext, interactions

	clock.tick(60)

	screen.fill((0,0,0))

	bg.draw_map(screen)
	
	player_img = player_img1
	player_img.set_colorkey((255, 0, 208))
	player_rect.topleft = (playerx-32, playery)
	player_rect2 = pygame.Rect((WIDTH/2-16), (HEIGHT/2+16), 32, 16)
	map_below.draw_map(screen)
	map_below2.draw_map(screen)

	npcdisplay(0, False)

	if layer == 1 or action == "climb" or layer == -1:
		map_above.draw_map(screen)
		npcdisplay(1, True)

	elif layer == 0:

		npcdisplay(0, True)
		map_above.draw_map(screen)
		npcdisplay(1, False)

	dialogue()

	map_above2.draw_map(screen)

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

	if dialoguetext != ["","","","",""]:
		dialoguebox = pygame.Surface((600,226))
		dialoguebox.fill((255,255,255))
		screen.blit(dialoguebox, (WIDTH/2-300,HEIGHT-266, 620, 226))

		dialoguebox2 = pygame.Surface((580,206))
		dialoguebox2.fill((0,0,0))
		screen.blit(dialoguebox2, (WIDTH/2-290,HEIGHT-256, 620, 206))
		rendertext(dialoguetext[0], "normal", (255, 255, 255), (WIDTH/2-280, HEIGHT-246), "topleft")
		rendertext(dialoguetext[1], "normal", (255, 255, 255), (WIDTH/2-280, HEIGHT-206), "topleft")
		rendertext(dialoguetext[2], "normal", (255, 255, 255), (WIDTH/2-280, HEIGHT-166), "topleft")
		rendertext(dialoguetext[3], "normal", (255, 255, 255), (WIDTH/2-280, HEIGHT-126), "topleft")
		rendertext(dialoguetext[4], "normal", (255, 255, 255), (WIDTH/2-280, HEIGHT- 86), "topleft")

	pygame.display.flip()

def animateSprites(idle, walkList, walkAnimCounter):
	if walkAnimCounter == 0:
		img = idle
	else:
		img = walkList[walkAnimCounter-1]

	return img

def animate():
	global direction, walksprite, player_img1, action, emote, animX, animY, playerx, playery, offsetX, offsetY, layer, dialoguetext
	if action == "walk":
		if direction == 0:
			player_img1 = animateSprites(player_idle_left, walk_left, walksprite)

		if direction == 1:
			player_img1 = animateSprites(player_idle_up, walk_up, walksprite)

		if direction == 2:
			player_img1 = animateSprites(player_idle_right, walk_right, walksprite)

		if direction == 3:
			player_img1 = animateSprites(player_idle_down, walk_down, walksprite)
	elif action == "climb":
		player_img1 = animateSprites(player_idle_climb, climb, walksprite)

	if emote == 1:
		player_img1 = player_emote_why
		for i in range(30):
			update()
	elif emote == 2:
		player_img1.set_colorkey((255, 0, 208))
		player_img1 = player_anim_wee
		tempcounter = 0
		templayer = layer
		layer = 1
		for i in range(126):
			animX = 100*math.sin(i/10)
			if i/8 == math.floor(i/8):
				tempcounter += 1

			if tempcounter > 3:
				tempcounter = 0

			player_img1 = idle[tempcounter]

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

	if dialoguetext != ["","","","",""]:
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
	player_img1 = player_anim_wee
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
	global volume, offsetX, offsetY, title, xdir, ydir, title_text2, title_text2_rect, cursor, keypress, level_mus, cover, shadow, titletype, maxcursor, offsetX, offsetY, level_id, prev_title, version, HEIGHT, WIDTH, screen, keypress2, pressed_keys

	maxcursor = 1

	screen.fill((255,255,255))
	bg.draw_map(screen)
	map_below.draw_map(screen)
	map_below2.draw_map(screen)
	dialogue()
	map_above.draw_map(screen)
	if level_id == 0:
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
		if pressed_keys[pygame.K_z] or pressed_keys[pygame.K_RETURN]:
			if titletype == "title":
				if cursor == 0:
					title = False
					level_id = 1
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
					keypress2 = False
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

	if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_z] or pressed_keys[pygame.K_RETURN] or pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_RIGHT]:
		keypress = True
	else:
		keypress = False

	if pressed_keys[pygame.K_z]:
		keypress2 = True
	else:
		keypress2 = False
	
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
		rendertext(f'Version v{version}', "small", (255, 255, 255), (WIDTH-10, HEIGHT-40), "topright")
		rendertext("By Philooxy", "small", (255, 255, 255), (WIDTH-10, HEIGHT-10), "bottomright")

		rendertext("Play", "normal", (255, 255, 255), (120, HEIGHT*(8/16)), "topleft")
		rendertext("Level Select", "normal", (255, 255, 255), (120, HEIGHT*(9/16)), "topleft")
		rendertext("Options", "normal", (255, 255, 255), (120, HEIGHT*(10/16)), "topleft")
		rendertext("Help", "normal", (255, 255, 255), (120, HEIGHT*(11/16)), "topleft")
		rendertext("Quit", "normal", (255, 0, 0), (120, HEIGHT*(12/16)), "topleft")
		rendertext("*", "normal", (255, 255, 255), (90, HEIGHT/2+(HEIGHT/16)*cursory), "topleft")

	elif titletype == "pause":
		text1 = font1big.render("Paused", True, (255, 255, 255))
		rendertext(f'MAZETEST 2 v{version}', "small", (255, 255, 255), (WIDTH-10, HEIGHT-10), "bottomright")

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
loadLevel(0)
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
		dialogue()
		movep()

		update()

		animate()