import pygame
import traceback
from settings import init_fonts, init_sounds, init_images, WIDTH, HEIGHT
from menu import main_menu
from game import run_game

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tower Defense - BFS Pathfinding")

    fonts = init_fonts()
    sounds = init_sounds()
    images = init_images()

    while True:
        result = main_menu(screen, fonts, sounds, images)
        if isinstance(result, tuple) and result[0] == "start":
            run_game(screen, fonts, sounds, images, algo=result[1])

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")