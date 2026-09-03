import pygame

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

def loadAnimSprites(animRange, path):
    animList = []
    for i in range(animRange):
        animList.append(loadify(f'assets/player/{path}{i+1}.png'))
    return animList

def loadify(img):
    return pygame.image.load(img).convert_alpha()
player_idle_right = loadify("assets/player/idle/side.png")
player_idle_left = pygame.transform.flip(player_idle_right, True, False)
player_idle_up = loadify("assets/player/idle/up.png")
player_idle_down = loadify("assets/player/idle/down.png")
idle = [player_idle_left, player_idle_up, player_idle_right, player_idle_down]

walk_down = loadAnimSprites(4, "walk/down")
walk_right = loadAnimSprites(4, "walk/side")
walk_up = loadAnimSprites(4, "walk/up")
walk_left = []
for i in range(len(walk_right)):
    walk_left.append(pygame.transform.flip(walk_right[i], True, False))

player_idle_climb = loadify("assets/player/climb/climb2.png")
climb = loadAnimSprites(4, "climb/climb")

player_anim_wee = loadify("assets/player/anim/wee.png")
player_emote_why = loadify("assets/player/anim/why.png")
tada = pygame.mixer.Sound("assets/sounds/tada.mp3")