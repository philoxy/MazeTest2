#created without tutorials (mostly)

import pygame, sys, csv, os, json

playerx = 96
playery = 96

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((840, 712))
player_img1 = pygame.image.load("assets/player.png")
#setup for animations somehow???
#if key is still pressed_keys cycle through frames
#if key is not pressed_keys set to first frame (standing)
#wow im so smart this will 100% not work at all
player_img = player_img1
player_rect = pygame.Rect(80, 80, 32, 32)
#test_rect = pygame.Rect(64, 64, 32, 32)
icon = player_img1
pygame.display.set_caption("MAZETEST 2")
clock = pygame.time.Clock()

collide_down = False
collide_up = False
collide_right = False
collide_left = False
offsetX = 0
offsetY = 0

Tilegroup = pygame.sprite.Group()

#from a tutorial because i hate classes in pygame how the hell do you use them
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
        sprite.set_colorkey((0,0,0))
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
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = x, y


	def draw(self, surface):
		surface.blit(self.image, (self.rect.x, self.rect.y))

	def update(self):
		global collide_down, collide_up, collide_right, collide_left, playerx, playery
		pressed_keys = pygame.key.get_pressed()
		collide_down = False
		collide_up = False
		collide_right = False
		collide_left = False
		#print(self.rect.bottom)
		#print(player_rect.top)
		if self.rect.left - 32 <= player_rect.left <= self.rect.right:
			if pressed_keys[pygame.K_DOWN] and player_rect.bottom == self.rect.top:
				collide_down = True
			if pressed_keys[pygame.K_UP] and player_rect.top == self.rect.bottom:
				collide_up = True
		if self.rect.top - 32 <= player_rect.top <= self.rect.bottom:
			if pressed_keys[pygame.K_RIGHT] and player_rect.right == self.rect.left:
				collide_right = True
			if pressed_keys[pygame.K_LEFT] and player_rect.left == self.rect.right:
				collide_left = True


class TileMap():
	def __init__(self, filename, spritesheet):
		self.tile_size = 64
		self.spritesheet = spritesheet
		self.tiles = self.load_tiles(filename)
		self.map_surface = pygame.Surface((self.map_w, self.map_h))
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
				#if tile == "0":
				#	self.start_x, self.start_y = x * self.tile_size, y * self.tile_size
				if tile == "0":
					Temptile = Tile("wall2", x * self.tile_size, y * self.tile_size, self.spritesheet)
					tiles.append(Temptile)
				elif tile == "1":
					Temptile = Tile("wall1", x * self.tile_size, y * self.tile_size, self.spritesheet)
					tiles.append(Temptile)
				elif tile == "2":
					Temptile = Tile("transparent", x * self.tile_size, y * self.tile_size, self.spritesheet)
					tiles.append(Temptile)
				x += 1
				Tilegroup.add(Temptile)
			y += 1

		self.map_w, self.map_h = x * self.tile_size, y * self.tile_size
		return tiles

def update():
	global playerx, playery, offsetX, offsetY
	player_rect.center = (playerx, playery)
	map.draw_map(screen)
	screen.blit(player_img, player_rect)
	#screen.blit(player_img, test_rect)
	pygame.display.flip()

def collide():
		global collide_down, collide_up, collide_right, collide_left, playerx, playery
		pressed_keys = pygame.key.get_pressed()
		collide_down = False
		collide_up = False
		collide_right = False
		collide_left = False
		#print(self.rect.bottom)
		#print(player_rect.top)
		for i in list(Tilegroup.sprites()):
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

def move():
	global playerx, playery, collide_down, collide_up, collide_right, collide_left, offsetX, offsetY
	pressed_keys = pygame.key.get_pressed()
	#if pressed_keys[pygame.K_x]:
	#	move = 8
	#else:
	move = 4
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

spritesheet = Spritesheet('assets/spritesheet.png')
map = TileMap("levels/level1.csv", spritesheet)
#print(Tilegroup.sprites())
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
