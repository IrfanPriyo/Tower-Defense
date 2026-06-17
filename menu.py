import pygame
import math
from settings import *
from ui import draw_button


def main_menu(screen, fonts, sounds, images):
    dragging_slider = False

    while True:
        screen.fill((20, 40, 20))

        # Background grid
        for r in range(ROWS):
            for c in range(COLS):
                x = c * TILE_SIZE
                y = r * TILE_SIZE + 80
                rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, (50, 100, 50), rect)
                pygame.draw.rect(screen, (40, 90, 40), rect, 1)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # Title
        title = fonts["title"].render("TOWER DEFENSE", True, YELLOW)
        subtitle = fonts["medium"].render(
            "BFS  vs  A*  Pathfinding", True, GRAY)
        screen.blit(title,
                   (WIDTH // 2 - title.get_width() // 2, 70))
        screen.blit(subtitle,
                   (WIDTH // 2 - subtitle.get_width() // 2, 130))

        # Enemy preview
        cx, cy = WIDTH // 2, 210
        pygame.draw.circle(screen, DARK_RED, (cx, cy), 30)
        pygame.draw.circle(screen, RED, (cx - 4, cy - 4), 27)
        pygame.draw.circle(screen, BLACK, (cx, cy), 30, 3)
        pygame.draw.ellipse(screen, YELLOW, (cx - 16, cy - 10, 12, 10))
        pygame.draw.ellipse(screen, BLACK, (cx - 14, cy - 8, 6, 6))
        pygame.draw.ellipse(screen, YELLOW, (cx + 4, cy - 10, 12, 10))
        pygame.draw.ellipse(screen, BLACK, (cx + 7, cy - 8, 6, 6))
        pygame.draw.line(screen, BLACK,
                        (cx - 18, cy - 15), (cx - 8, cy - 8), 3)
        pygame.draw.line(screen, BLACK,
                        (cx + 4, cy - 8), (cx + 18, cy - 15), 3)
        pygame.draw.arc(screen, BLACK,
                       (cx - 12, cy + 4, 24, 16),
                       math.pi, 2 * math.pi, 3)

        # Volume slider
        from settings import master_volume
        vol_label = fonts["medium"].render(
            f"Volume: {int(master_volume * 100)}%", True, WHITE)
        screen.blit(vol_label,
                   (WIDTH // 2 - vol_label.get_width() // 2, 265))

        slider_x = WIDTH // 2 - 150
        slider_y = 305
        slider_w = 300
        slider_h = 12
        pygame.draw.rect(screen, DARK_GRAY,
                        (slider_x, slider_y, slider_w, slider_h),
                        border_radius=6)
        fill_w = int(slider_w * master_volume)
        pygame.draw.rect(screen, YELLOW,
                        (slider_x, slider_y, fill_w, slider_h),
                        border_radius=6)
        handle_x = slider_x + fill_w
        pygame.draw.circle(screen, WHITE,
                          (handle_x, slider_y + slider_h // 2), 12)
        pygame.draw.circle(screen, YELLOW,
                          (handle_x, slider_y + slider_h // 2), 12, 2)

        # Algorithm label
        algo_label = fonts["normal"].render("Select Pathfinding Algorithm:", True, WHITE)
        screen.blit(algo_label,
                   (WIDTH // 2 - algo_label.get_width() // 2, 340))

        # BFS and A* start buttons (side by side)
        btn_bfs = pygame.Rect(WIDTH // 2 - 210, 375, 190, 55)
        btn_astar = pygame.Rect(WIDTH // 2 + 20, 375, 190, 55)
        btn_quit = pygame.Rect(WIDTH // 2 - 100, 448, 200, 48)

        draw_button(screen, "BFS Mode", btn_bfs,
                   (30, 80, 160), (50, 110, 210), fonts)
        draw_button(screen, "A* Mode", btn_astar,
                   (130, 50, 10), (190, 80, 20), fonts)
        draw_button(screen, "QUIT", btn_quit,
                   (150, 30, 30), (200, 50, 50), fonts)

        # Description labels under buttons
        bfs_desc = fonts["small"].render("O(V+E) · explores all directions", True, (160, 200, 255))
        astar_desc = fonts["small"].render("O(E log V) · guided by heuristic", True, (255, 200, 120))
        screen.blit(bfs_desc,
                   (btn_bfs.x + btn_bfs.w // 2 - bfs_desc.get_width() // 2,
                    btn_bfs.y + btn_bfs.h + 4))
        screen.blit(astar_desc,
                   (btn_astar.x + btn_astar.w // 2 - astar_desc.get_width() // 2,
                    btn_astar.y + btn_astar.h + 4))

        inst = fonts["small"].render(
            "Left: Place tower | Right: Remove | P: Toggle path | R: Restart",
            True, GRAY)
        screen.blit(inst,
                   (WIDTH // 2 - inst.get_width() // 2, HEIGHT - 28))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                handle_rect = pygame.Rect(handle_x - 12,
                                         slider_y - 12, 24, 24)
                if handle_rect.collidepoint(mx, my):
                    dragging_slider = True
                if btn_bfs.collidepoint(mx, my):
                    return ("start", "bfs")
                if btn_astar.collidepoint(mx, my):
                    return ("start", "astar")
                if btn_quit.collidepoint(mx, my):
                    pygame.quit()
                    exit()
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False
            if event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    mx, my = event.pos
                    from settings import set_volume
                    vol = (mx - slider_x) / slider_w
                    vol = max(0.0, min(1.0, vol))
                    set_volume(sounds, vol)
