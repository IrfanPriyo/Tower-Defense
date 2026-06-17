import os
import pygame

TILE_SIZE = 40
COLS = 20
ROWS = 15
WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE + 80

START = (7, 0)
END = (7, COLS - 1)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)
GREEN = (50, 200, 50)
DARK_GREEN = (20, 120, 20)
RED = (220, 50, 50)
DARK_RED = (150, 20, 20)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
BROWN = (101, 67, 33)
STONE = (150, 140, 130)
LIGHT_STONE = (190, 180, 170)
PATH_COLOR = (210, 180, 140)
GRASS_COLOR = (60, 130, 60)
TOWER_BG = (60, 60, 80)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def init_fonts():
    return {
        "small": pygame.font.SysFont("Arial", 14),
        "normal": pygame.font.SysFont("Arial", 18, bold=True),
        "medium": pygame.font.SysFont("Arial", 22, bold=True),
        "big": pygame.font.SysFont("Arial", 28, bold=True),
        "title": pygame.font.SysFont("Arial", 48, bold=True),
    }

master_volume = 0.5

def init_sounds():
    sounds = {
        "shoot": pygame.mixer.Sound(
            os.path.join(BASE_DIR, "sounds", "shoot.mp3")),
        "lives_lost": pygame.mixer.Sound(
            os.path.join(BASE_DIR, "sounds", "lives_lost.mp3")),
        "game_over": pygame.mixer.Sound(
            os.path.join(BASE_DIR, "sounds", "game_over.mp3")),
    }
    set_volume(sounds, master_volume)
    return sounds

def set_volume(sounds, vol):
    global master_volume
    master_volume = vol
    sounds["shoot"].set_volume(vol * 0.3)
    sounds["lives_lost"].set_volume(vol * 0.5)
    sounds["game_over"].set_volume(vol * 0.7)

def init_images():
    burning_baby = pygame.image.load(
        os.path.join(BASE_DIR, "images", "burning_baby.jpeg"))
    burning_baby = pygame.transform.scale(burning_baby, (300, 300))
    return {"burning_baby": burning_baby}