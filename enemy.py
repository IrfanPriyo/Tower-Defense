import pygame
import math
from settings import *
from bfs import bfs as _bfs_default

class Enemy:
    def __init__(self, path, wave=1, pathfind_fn=None):
        self.path = path
        self.path_index = 0
        self.row, self.col = path[0]
        self.x = float(self.col * TILE_SIZE + TILE_SIZE // 2)
        self.y = float(self.row * TILE_SIZE + TILE_SIZE // 2 + 80)
        self._pathfind = pathfind_fn if pathfind_fn is not None else _bfs_default
        self.speed = 1.2 + wave * 0.1
        self.hp = 80 + wave * 20
        self.max_hp = self.hp
        self.alive = True
        self.reached_end = False
        self.dead_counted = False
        self.anim_timer = 0
        self.eye_offset = 0

    def get_current_node(self):
        col = round((self.x - TILE_SIZE // 2) / TILE_SIZE)
        row = round((self.y - 80 - TILE_SIZE // 2) / TILE_SIZE)
        col = max(0, min(COLS - 1, col))
        row = max(0, min(ROWS - 1, row))
        return (row, col)

    def recalculate_path(self, grid):
        current_node = self.get_current_node()
        new_path = self._pathfind(grid, current_node, END)
        if new_path:
            self.path = new_path
            self.path_index = 0
            self.row, self.col = current_node
            self.x = float(self.col * TILE_SIZE + TILE_SIZE // 2)
            self.y = float(self.row * TILE_SIZE + TILE_SIZE // 2 + 80)

    def update(self):
        if not self.alive or self.reached_end:
            return
        self.anim_timer += 1
        self.eye_offset = int(math.sin(self.anim_timer * 0.2) * 2)
        if self.path_index >= len(self.path) - 1:
            self.reached_end = True
            return
        target_row, target_col = self.path[self.path_index + 1]
        target_x = float(target_col * TILE_SIZE + TILE_SIZE // 2)
        target_y = float(target_row * TILE_SIZE + TILE_SIZE // 2 + 80)
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < self.speed:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
            self.row, self.col = target_row, target_col
        else:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist

    def draw(self, surface):
        if not self.alive:
            return
        cx, cy = int(self.x), int(self.y)
        r = 14
        pygame.draw.circle(surface, DARK_RED, (cx, cy), r)
        pygame.draw.circle(surface, RED, (cx - 2, cy - 2), r - 2)
        pygame.draw.circle(surface, BLACK, (cx, cy), r, 2)
        eye_y = cy - 4 + self.eye_offset
        pygame.draw.ellipse(surface, YELLOW, (cx - 8, eye_y - 3, 6, 5))
        pygame.draw.ellipse(surface, BLACK, (cx - 7, eye_y - 2, 3, 3))
        pygame.draw.ellipse(surface, YELLOW, (cx + 2, eye_y - 3, 6, 5))
        pygame.draw.ellipse(surface, BLACK, (cx + 4, eye_y - 2, 3, 3))
        pygame.draw.line(surface, BLACK,
                        (cx - 9, eye_y - 5), (cx - 4, eye_y - 3), 2)
        pygame.draw.line(surface, BLACK,
                        (cx + 2, eye_y - 3), (cx + 8, eye_y - 5), 2)
        mouth_y = cy + 4
        pygame.draw.arc(surface, BLACK,
                       (cx - 6, mouth_y - 2, 12, 8),
                       math.pi, 2 * math.pi, 2)
        bar_w = 30
        bar_h = 5
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, BLACK,
                        (cx - bar_w // 2 - 1, cy - r - 9,
                         bar_w + 2, bar_h + 2))
        pygame.draw.rect(surface, DARK_RED,
                        (cx - bar_w // 2, cy - r - 8, bar_w, bar_h))
        pygame.draw.rect(surface, GREEN,
                        (cx - bar_w // 2, cy - r - 8,
                         int(bar_w * hp_ratio), bar_h))