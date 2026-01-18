import pygame

WIDTH, HEIGHT = 1000, 700
FPS = 60

# --- ШЛЯХИ ДО КАРТИНОК (змінюй тут) ---
IMG_PLAYER = "player.png"
IMG_ENEMY_BASIC = "enemy_basic.png"
IMG_ENEMY_ORANGE = "enemy_orange.png"
IMG_ENEMY_SNIPER = "enemy_sniper.png"
IMG_MEDKIT = "medkit.png"

# Кольори
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
HEALTH_CLR, AMMO_CLR = (255, 50, 50), (255, 200, 50)
DARK_GREEN, GRASS_COLOR = (15, 40, 15), (40, 100, 40)
TREE_COLOR, ROCK_COLOR = (10, 50, 10), (100, 100, 100)
PLAYER_CLR = (0, 100, 255)
ENEMY_BASIC, ENEMY_ORANGE, ENEMY_SNIPER = (200, 0, 0), (255, 165, 0), (128, 0, 128)
CROSSHAIR_CLR = (0, 255, 0)

# Баланс
START_COINS, PLAYER_HP = 100, 100
