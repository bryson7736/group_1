# -*- coding: utf-8 -*-
import math
import pygame
import random
from colors import WHITE, ORANGE
from settings import ENEMY_SIZE

class Enemy:
    """Moves along path; center displays an integer HP number."""
    def __init__(self, path_points, hp, speed, size=ENEMY_SIZE):
        self.path = list(path_points)
        self.hp = float(hp)
        self.max_hp = float(hp)
        self.speed = float(speed)
        self.size = size  # Added size attribute
        self.dead = False
        self.reached = False
        self.idx = 0           # path index (larger = further along)
        self.x, self.y = self.path[0]
        self.money_drop = 10.0
        self.slow_ratio = 1.0
        self.slow_timer = 0.0
        self.carries_coin = False
        self.poison_timer = 0.0
        self.poison_dmg = 0.0

    def apply_slow(self, ratio, duration):
        self.slow_ratio = min(self.slow_ratio, ratio)
        self.slow_timer = max(self.slow_timer, duration)

    def apply_poison(self, dmg, duration):
        self.poison_dmg = max(self.poison_dmg, dmg)
        self.poison_timer = max(self.poison_timer, duration)

    def hit(self, dmg):
        import time
        self.hp -= dmg
        if not hasattr(self, 'damage_history'):
            self.damage_history = []
        self.damage_history.append((time.time(), dmg))
        if self.hp <= 0 and not self.dead:
            self.dead = True

    @property
    def damage_taken_last_5s(self) -> float:
        import time
        now = time.time()
        if not hasattr(self, 'damage_history'):
            return 0.0
        # Filter and sum damage in the last 5 seconds
        return sum(dmg for ts, dmg in self.damage_history if now - ts <= 5.0)

    def update_damage_history(self, dt):
        """Prune old damage history entries."""
        import time
        now = time.time()
        if hasattr(self, 'damage_history'):
            self.damage_history = [(ts, dmg) for ts, dmg in self.damage_history if now - ts <= 5.0]

    def update(self, dt, speed_mult=1.0, zone_mult=1.0):
        if self.dead or self.reached or self.idx >= len(self.path) - 1:
            return
        
        # Status effects
        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_ratio = 1.0
        
        if self.poison_timer > 0:
            self.poison_timer -= dt
            # Poison damage tick
            self.hit(self.poison_dmg * dt)
            if self.dead:
                return

        tx, ty = self.path[self.idx + 1]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        step = self.speed * self.slow_ratio * speed_mult * zone_mult * dt
        if step >= dist and dist > 0:
            self.x, self.y = tx, ty
            self.idx += 1
            if self.idx >= len(self.path) - 1:
                self.reached = True
        elif dist > 0:
            nx, ny = dx / dist, dy / dist
            self.x += nx * step
            self.y += ny * step

    def draw(self, surf, font):
        r = pygame.Rect(int(self.x - self.size/2), int(self.y - self.size/2), self.size, self.size)
        color = ORANGE
        if self.poison_timer > 0:
            color = (180, 50, 255) # Purple for poison
        elif self.slow_timer > 0:
            color = (100, 100, 255) # Blue for slow
            
        pygame.draw.rect(surf, color, r, border_radius=10)
        hp_txt = font.render(str(max(0, int(self.hp + 0.5))), True, WHITE)
        surf.blit(hp_txt, (r.centerx - hp_txt.get_width()//2, r.centery - hp_txt.get_height()//2))

class BigEnemy(Enemy):
    def __init__(self, path_points, hp, speed):
        # BigEnemy is 3x larger than normal enemy (as per user customization)
        super().__init__(path_points, hp, speed, size=ENEMY_SIZE * 3)
        self.money_drop = 50.0
        self.ability_cd = 0.0

    def update(self, dt, speed_mult=1.0, zone_mult=1.0):
        super().update(dt, speed_mult, zone_mult)
        self.ability_cd += dt * speed_mult

    def try_ability(self, game):
        # cast a telegraph zone near grid center
        if not game or self.dead:
            return
        gx = game.grid.cols // 2
        gy = game.grid.rows // 2
        c = random.randint(max(0, gx-1), min(game.grid.cols-1, gx+1))
        r = random.randint(max(0, gy-1), min(game.grid.rows-1, gy+1))
        px, py = game.grid.center_of(c, r)
        game.spawn_telegraph(px, py)
