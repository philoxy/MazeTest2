#created without tutorials (mostly)

import pygame, sys, csv, os, json

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((640, 704))
player_img1 = pygame.image.load("assets/player/player.png")
#setup for animations somehow???
#if key is still pressed_keys cycle through frames
#if key is not pressed_keys set to first frame (standing)
#wow im so smart this will 100% not work at all
playerx = 96
playery = 96
player_img = player_img1
player_rect = pygame.Rect(playerx, playery, 32, 32)
icon = player_img1
pygame.display.set_caption("MAZETEST 2")
clock = pygame.time.Clock()

collide_down = False
collide_up = False
collide_right = False
collide_left = False
offsetX = 0
offsetY = 0
win = False

Tilegroup = pygame.sprite.Group()
Tilegroup_nocol = pygame.sprite.Group()
Tilegroup_wall = pygame.sprite.Group()
Tilegroup_exit = pygame.sprite.Group()

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

# seperate classes for no collision tiles (backgrounds n stuff)
# or just make a background image (easier?)
class Tile(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.image.set_colorkey((255, 0, 208))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y


	def draw(self, surface):
		surface.blit(self.image, (self.rect.x, self.rect.y))

class Tile_NoCol(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.image.set_colorkey((255, 0, 208))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y


	def draw(self, surface):
		surface.blit(self.image, (self.rect.x, self.rect.y))

class Tile_Wall(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.image.set_colorkey((255, 0, 208))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y


	def draw(self, surface):
		surface.blit(self.image, (self.rect.x, self.rect.y))

class Tile_Exit(pygame.sprite.Sprite):
	def __init__(self, image, x, y, spritesheet):
		pygame.sprite.Sprite.__init__(self)
		self.image = spritesheet.parse_sprite(image)
		self.image.set_colorkey((255, 0, 208))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y


	def draw(self, surface):
		surface.blit(self.image, (self.rect.x, self.rect.y))

class TileMap():
	def __init__(self, filename, spritesheet):
		self.tile_size = 64
		self.spritesheet = spritesheet
		self.tiles = self.load_tiles(filename)
		self.map_surface = pygame.Surface((self.map_w, self.map_h))
		#i have NO IDEA how to change the colorkey so you have to use 0, 0, 1 for black in rgb values
		self.map_surface.set_colorkey((0, 0, 0))
		self.load_map()

	def draw_map(self, surface):
		surface.blit(self.map_surface, (0, 0))

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
					Temptile = Tile("wall2", x * self.tile_size, y * self.tile_size, self.spritesheet)
					tiles.append(Temptile)
					Tilegroup.add(Temptile)
				elif tile == "1":
					Temptile = Tile("wall1", x * self.tile_size, y * self.tile_size, self.spritesheet)
					tiles.append(Temptile)
					Tilegroup.add(Temptile)
				elif tile == "2":
					Temptile = Tile_NoCol("transparent", x * self.tile_size, y * self.tile_size, self.spritesheet)
					tiles.append(Temptile)
					Tilegroup_nocol.add(Temptile)
				elif tile == "3":
					Temptile = Tile_Exit("exit", x * self.tile_size, y * self.tile_size, self.spritesheet)
					tiles.append(Temptile)
					Tilegroup_exit.add(Temptile)
				elif tile == "4":
					Temptile = Tile_Wall("wall3", x * self.tile_size, y * self.tile_size, self.spritesheet)
					tiles.append(Temptile)
					Tilegroup_wall.add(Temptile)
				x += 1
			y += 1

		self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
		return tiles

# general functions for player

def update():
	global playerx, playery, offsetX, offsetY
	player_rect.topleft = (playerx+32, playery)
	map_below.draw_map(screen)
	screen.blit(player_img, player_rect)
	map_above.draw_map(screen)
	pygame.display.flip()

def collide():
		global collide_down, collide_up, collide_right, collide_left, playerx, playery, win
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
		for i in list(Tilegroup_exit.sprites()):
			if player_rect.colliderect(i.rect):
				win = True

def move():
	global playerx, playery, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY
	pressed_keys = pygame.key.get_pressed()
	#sprinting lets you clip through walls
	#do whatever you want with this information
	#if pressed_keys[pygame.K_x]:
	#	move = 4
	#else:
	move = 2
	if pressed_keys[pygame.K_LEFT] and collide_left == False:
		playerx -= move
	if pressed_keys[pygame.K_RIGHT] and collide_right == False:
		playerx += move
	if pressed_keys[pygame.K_UP] and collide_up == False:
		playery -= move
	if pressed_keys[pygame.K_DOWN] and collide_down == False:
		playery += move
	offsetX = playerx
	offsetY = playery

def loadLevel(level_num):
	global spritesheet, map_below, map_above
	level_num = str(level_num)
	spritesheet = Spritesheet('assets/level'+level_num+'/spritesheet.png')
	map_below = TileMap('levels/level'+level_num+'/back.csv', spritesheet)
	map_above = TileMap('levels/level'+level_num+'/front.csv', spritesheet)

loadLevel(1)
#spritesheet = Spritesheet('assets/level1/spritesheet.png')
#map_below = TileMap("levels/level1/back.csv", spritesheet)
#map_above = TileMap("levels/level1/front.csv", spritesheet)

while win == False:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

	#Collision then movement
	collide()
	move()

	screen.fill((225, 255, 255))
	clock.tick(60)
	update()

