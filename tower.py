import pygame
import math
from settings import *

class Bullet:
    def __init__(self, x, y, target, damage=20):
        self.x = float(x)
        self.y = float(y)
        self.target = target
        self.speed = 8
        self.alive = True
        self.damage = damage
        self.trail = []

    def update(self):
        if not self.target.alive or self.target.reached_end:
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < self.speed:
            self.target.hp -= self.damage
            if self.target.hp <= 0:
                self.target.alive = False
            self.alive = False
        else:
            self.trail.append((int(self.x), int(self.y)))
            if len(self.trail) > 5:
                self.trail.pop(0)
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist

    def draw(self, surface):
        if not self.alive:
            return
        for i, (tx, ty) in enumerate(self.trail):
            radius = max(1, i // 2)
            pygame.draw.circle(surface, YELLOW, (tx, ty), radius)
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 4)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 2)


class Tower:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.range = 3
        self.damage = 20
        self.fire_rate = 45
        self.timer = 0
        self.angle = 0
        self.bullets = []

    def get_center(self):
        x = self.col * TILE_SIZE + TILE_SIZE // 2
        y = self.row * TILE_SIZE + TILE_SIZE // 2 + 80
        return x, y

    def update(self, enemies, sounds):
        self.timer += 1
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.alive]
        if self.timer >= self.fire_rate:
            self.timer = 0
            self.shoot(enemies, sounds)

    def shoot(self, enemies, sounds):
        best = None
        best_progress = -1
        for enemy in enemies:
            if not enemy.alive or enemy.reached_end:
                continue
            dist = ((enemy.row - self.row) ** 2 +
                   (enemy.col - self.col) ** 2) ** 0.5
            if dist <= self.range and enemy.path_index > best_progress:
                best_progress = enemy.path_index
                best = enemy
        if best:
            cx, cy = self.get_center()
            self.angle = math.atan2(best.y - cy, best.x - cx)
            bullet = Bullet(cx, cy, best, self.damage)
            self.bullets.append(bullet)
            sounds["shoot"].play()

    def draw(self, surface, fonts):
        x = self.col * TILE_SIZE
        y = self.row * TILE_SIZE + 80
        cx = x + TILE_SIZE // 2
        cy = y + TILE_SIZE // 2
        pygame.draw.rect(surface, TOWER_BG, (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, STONE,
                        (x + 3, y + 3, TILE_SIZE - 6, TILE_SIZE - 6))
        pygame.draw.rect(surface, LIGHT_STONE,
                        (x + 3, y + 3, TILE_SIZE - 6, 4))
        pygame.draw.rect(surface, DARK_GRAY,
                        (x + 3, y + 3, TILE_SIZE - 6, TILE_SIZE - 6), 2)
        for i in range(3):
            mx = x + 5 + i * 11
            pygame.draw.rect(surface, STONE, (mx, y - 2, 6, 7))
            pygame.draw.rect(surface, DARK_GRAY, (mx, y - 2, 6, 7), 1)
        barrel_len = 14
        bx = cx + int(math.cos(self.angle) * barrel_len)
        by = cy + int(math.sin(self.angle) * barrel_len)
        pygame.draw.line(surface, DARK_GRAY, (cx, cy), (bx, by), 5)
        pygame.draw.circle(surface, DARK_GRAY, (cx, cy), 6)
        pygame.draw.circle(surface, STONE, (cx, cy), 4)
        for bullet in self.bullets:
            bullet.draw(surface)
        mx, my = pygame.mouse.get_pos()
        hc = mx // TILE_SIZE
        hr = (my - 80) // TILE_SIZE
        if hr == self.row and hc == self.col:
            range_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (255, 255, 0, 40),
                              (cx, cy), self.range * TILE_SIZE)
            pygame.draw.circle(range_surf, (255, 255, 0, 120),
                              (cx, cy), self.range * TILE_SIZE, 2)
            surface.blit(range_surf, (0, 0))
            tooltip_lines = [
                f"DMG: {self.damage}",
                f"RNG: {self.range}",
                f"SPD: {60 // self.fire_rate}/s"
            ]
            tw = 90
            th = len(tooltip_lines) * 20 + 8
            tx = min(cx + 20, WIDTH - tw - 5)
            ty = max(cy - th, 85)
            pygame.draw.rect(surface, (30, 30, 30),
                            (tx, ty, tw, th), border_radius=5)
            pygame.draw.rect(surface, YELLOW,
                            (tx, ty, tw, th), 1, border_radius=5)
            for i, line in enumerate(tooltip_lines):
                t = fonts["small"].render(line, True, WHITE)
                surface.blit(t, (tx + 6, ty + 4 + i * 20))