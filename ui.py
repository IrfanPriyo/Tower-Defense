import pygame
import math
from settings import *

def draw_button(surface, text, rect, color, hover_color,
                fonts, text_color=WHITE):
    mx, my = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(mx, my)
    pygame.draw.rect(surface, hover_color if is_hover else color,
                    rect, border_radius=10)
    pygame.draw.rect(surface, YELLOW, rect, 2, border_radius=10)
    t = fonts["medium"].render(text, True, text_color)
    surface.blit(t, (rect.x + rect.w // 2 - t.get_width() // 2,
                     rect.y + rect.h // 2 - t.get_height() // 2))
    return is_hover

def draw_arrow(surface, from_pos, to_pos):
    fx = from_pos[1] * TILE_SIZE + TILE_SIZE // 2
    fy = from_pos[0] * TILE_SIZE + TILE_SIZE // 2 + 80
    tx = to_pos[1] * TILE_SIZE + TILE_SIZE // 2
    ty = to_pos[0] * TILE_SIZE + TILE_SIZE // 2 + 80
    angle = math.atan2(ty - fy, tx - fx)
    arrow_len = 10
    arrow_angle = math.pi / 6
    ax = tx - arrow_len * math.cos(angle - arrow_angle)
    ay = ty - arrow_len * math.sin(angle - arrow_angle)
    bx = tx - arrow_len * math.cos(angle + arrow_angle)
    by = ty - arrow_len * math.sin(angle + arrow_angle)
    pygame.draw.line(surface, (180, 140, 90),
                    (int(fx), int(fy)), (int(tx), int(ty)), 2)
    pygame.draw.polygon(surface, (180, 140, 90),
                       [(int(tx), int(ty)),
                        (int(ax), int(ay)),
                        (int(bx), int(by))])

def draw_grid(surface, grid, path, show_path):
    path_set = set(path) if path else set()
    for r in range(ROWS):
        for c in range(COLS):
            x = c * TILE_SIZE
            y = r * TILE_SIZE + 80
            rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            if (r, c) == START:
                pygame.draw.rect(surface, GREEN, rect)
                pygame.draw.rect(surface, DARK_GREEN, rect, 3)
            elif (r, c) == END:
                pygame.draw.rect(surface, RED, rect)
                pygame.draw.rect(surface, DARK_RED, rect, 3)
            elif grid[r][c] == 2:
                pygame.draw.rect(surface, (34, 85, 34), rect)
                pygame.draw.rect(surface, BLACK, rect, 1)
                pygame.draw.circle(surface, DARK_GREEN,
                                  (x + TILE_SIZE // 2,
                                   y + TILE_SIZE // 2 - 3), 12)
                pygame.draw.rect(surface, BROWN,
                                (x + TILE_SIZE // 2 - 3,
                                 y + TILE_SIZE // 2 + 6, 6, 8))
            elif grid[r][c] == 1:
                pygame.draw.rect(surface, TOWER_BG, rect)
                pygame.draw.rect(surface, YELLOW, rect, 2)
            elif show_path and (r, c) in path_set:
                pygame.draw.rect(surface, PATH_COLOR, rect)
                pygame.draw.rect(surface, (180, 150, 110), rect, 1)
            else:
                pygame.draw.rect(surface, GRASS_COLOR, rect)
                pygame.draw.rect(surface, (50, 120, 50), rect, 1)
    if show_path and path and len(path) > 1:
        for i in range(len(path) - 1):
            draw_arrow(surface, path[i], path[i + 1])
    sx = START[1] * TILE_SIZE
    sy = START[0] * TILE_SIZE + 80
    ex = END[1] * TILE_SIZE
    ey = END[0] * TILE_SIZE + 80
    s_text = pygame.font.SysFont("Arial", 18, bold=True).render("S", True, WHITE)
    e_text = pygame.font.SysFont("Arial", 18, bold=True).render("E", True, WHITE)
    surface.blit(s_text, (sx + TILE_SIZE // 2 - s_text.get_width() // 2,
                          sy + TILE_SIZE // 2 - s_text.get_height() // 2))
    surface.blit(e_text, (ex + TILE_SIZE // 2 - e_text.get_width() // 2,
                          ey + TILE_SIZE // 2 - e_text.get_height() // 2))

def draw_header(surface, score, lives, wave,
                enemies_alive, enemies_to_spawn, spawned, fonts, algo="bfs"):
    pygame.draw.rect(surface, (30, 30, 30), (0, 0, WIDTH, 80))
    pygame.draw.rect(surface, YELLOW, (0, 0, WIDTH, 80), 2)
    algo_label = "BFS" if algo == "bfs" else "A*"
    title = fonts["big"].render(
        f"Tower Defense  —  {algo_label} Pathfinding", True, YELLOW)
    surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 2))
    inst = fonts["small"].render(
        "Left: Place tower | Right: Remove | P: Path | R: Restart",
        True, GRAY)
    surface.blit(inst, (WIDTH // 2 - inst.get_width() // 2, 30))
    pygame.draw.rect(surface, (50, 50, 50), (5, 48, 130, 26), border_radius=5)
    score_text = fonts["normal"].render(f"Score: {score}", True, YELLOW)
    surface.blit(score_text, (10, 51))
    pygame.draw.rect(surface, (50, 50, 50),
                    (WIDTH // 2 - 65, 48, 130, 26), border_radius=5)
    lives_text = fonts["normal"].render(f"Lives: {lives}", True, RED)
    surface.blit(lives_text,
                (WIDTH // 2 - lives_text.get_width() // 2, 51))
    pygame.draw.rect(surface, (50, 50, 50),
                    (WIDTH - 230, 48, 110, 26), border_radius=5)
    wave_text = fonts["normal"].render(f"Wave: {wave}", True, GREEN)
    surface.blit(wave_text, (WIDTH - 225, 51))
    remaining = max(0, enemies_to_spawn - spawned) + enemies_alive
    pygame.draw.rect(surface, (50, 50, 50),
                    (WIDTH - 115, 48, 110, 26), border_radius=5)
    enemy_text = fonts["small"].render(f"Enemies: {remaining}", True, ORANGE)
    surface.blit(enemy_text, (WIDTH - 110, 54))

def draw_settings_popup(surface, volume, fonts):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))
    pw, ph = 340, 260
    px = WIDTH // 2 - pw // 2
    py = HEIGHT // 2 - ph // 2
    pygame.draw.rect(surface, (30, 30, 30),
                    (px, py, pw, ph), border_radius=15)
    pygame.draw.rect(surface, YELLOW,
                    (px, py, pw, ph), 2, border_radius=15)
    t = fonts["big"].render("Settings", True, YELLOW)
    surface.blit(t, (px + pw // 2 - t.get_width() // 2, py + 15))
    vl = fonts["medium"].render(f"Volume: {int(volume * 100)}%", True, WHITE)
    surface.blit(vl, (px + pw // 2 - vl.get_width() // 2, py + 70))
    slider_x = px + 30
    slider_y = py + 110
    slider_w = pw - 60
    slider_h = 10
    pygame.draw.rect(surface, DARK_GRAY,
                    (slider_x, slider_y, slider_w, slider_h),
                    border_radius=5)
    fill_w = int(slider_w * volume)
    pygame.draw.rect(surface, YELLOW,
                    (slider_x, slider_y, fill_w, slider_h),
                    border_radius=5)
    handle_x = slider_x + fill_w
    pygame.draw.circle(surface, WHITE,
                      (handle_x, slider_y + slider_h // 2), 10)
    pygame.draw.circle(surface, YELLOW,
                      (handle_x, slider_y + slider_h // 2), 10, 2)
    btn_restart = pygame.Rect(px + 20, py + 145, 140, 42)
    btn_quit = pygame.Rect(px + 180, py + 145, 140, 42)
    btn_close = pygame.Rect(px + pw // 2 - 70, py + 200, 140, 42)
    draw_button(surface, "Restart", btn_restart,
               (50, 100, 50), (70, 150, 70), fonts)
    draw_button(surface, "Quit", btn_quit,
               (150, 30, 30), (200, 50, 50), fonts)
    draw_button(surface, "Close", btn_close,
               (50, 50, 100), (70, 70, 150), fonts)
    return {
        "slider_x": slider_x,
        "slider_y": slider_y,
        "slider_w": slider_w,
        "slider_h": slider_h,
        "btn_restart": btn_restart,
        "btn_quit": btn_quit,
        "btn_close": btn_close
    }