# -*- coding: utf-8 -*-
import math
import pygame
import random
from colors import WHITE, ORANGE, RED, GREEN, BLUE
from settings import ENEMY_SIZE

# FSM States
STATE_IDLE = "idle"
STATE_DEFENSE = "defense"
STATE_ATTACK = "attack"
STATE_HEAL = "heal"

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
        self.money_drop = 1.0
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
        self.hp -= dmg
        if self.hp <= 0 and not self.dead:
            self.dead = True

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
        self.money_drop = 3.0
        self.ability_cd = 0.0

    def update(self, dt, speed_mult=1.0, zone_mult=1.0):
        super().update(dt, speed_mult, zone_mult)
        self.ability_cd += dt * speed_mult

    def try_ability(self, game):
        # cast a telegraph zone near grid center
        import random
        if not game or self.dead:
            return
        gx = game.grid.cols // 2
        gy = game.grid.rows // 2
        c = random.randint(max(0, gx-1), min(game.grid.cols-1, gx+1))
        r = random.randint(max(0, gy-1), min(game.grid.rows-1, gy+1))
        px, py = game.grid.center_of(c, r)
        game.spawn_telegraph(px, py)


class TrueBoss(Enemy):
    def __init__(self, path_points, hp, speed, game=None):
        super().__init__(path_points, hp, speed, size=ENEMY_SIZE * 3)
        self.game = game
        self.money_drop = 10.0
        
        self.state = STATE_IDLE
        self.state_timer = 0.0
        
        # Cooldowns (5s for each skill)
        self.cooldowns = {
            STATE_DEFENSE: 5.0,
            STATE_ATTACK: 5.0,
            STATE_HEAL: 5.0
        }
        
        # Skill durations
        self.durations = {
            STATE_DEFENSE: 3.0,
            STATE_ATTACK: 1.0, # Cast time
            STATE_HEAL: 2.0
        }
        
        # Initial cooldowns to prevent spamming at start
        self.timers = {
            STATE_DEFENSE: 2.0,
            STATE_ATTACK: 4.0,
            STATE_HEAL: 6.0
        }

    def hit(self, dmg):
        # Defense state reduces damage by 50%
        if self.state == STATE_DEFENSE:
            dmg *= 0.5
        super().hit(dmg)

    def update(self, dt, speed_mult=1.0, zone_mult=1.0):
        if self.dead or self.reached:
            return

        # Update skill cooldowns
        for k in self.timers:
            self.timers[k] = max(0, self.timers[k] - dt * speed_mult)
            
        # State Machine
        self.state_timer = max(0, self.state_timer - dt * speed_mult)
        
        if self.state == STATE_IDLE:
            # Move normally
            super().update(dt, speed_mult, zone_mult)
            
            # Try to pick a ready skill
            self._try_skill()
            
        elif self.state == STATE_DEFENSE:
            # Continue moving while defending? Let's say yes, but slowly
            super().update(dt, speed_mult * 0.5, zone_mult)
            if self.state_timer <= 0:
                self.timers[STATE_DEFENSE] = self.cooldowns[STATE_DEFENSE]
                self.state = STATE_IDLE

        elif self.state == STATE_ATTACK:
            # Stop moving to cast
            if self.state_timer <= 0:
                # Cast effect
                self._cast_attack()
                self.timers[STATE_ATTACK] = self.cooldowns[STATE_ATTACK]
                self.state = STATE_IDLE

        elif self.state == STATE_HEAL:
            # Stop moving to heal
            # Heal tick (e.g., 5% max HP per second)
            heal_rate = 0.05 * self.max_hp
            self.hp = min(self.max_hp, self.hp + heal_rate * dt * speed_mult)
            
            if self.state_timer <= 0:
                self.timers[STATE_HEAL] = self.cooldowns[STATE_HEAL]
                self.state = STATE_IDLE

    def _try_skill(self):
        # Priority: Heal (if low HP) > Defense > Attack
        if self.timers[STATE_HEAL] <= 0 and self.hp < self.max_hp * 0.8:
            self.state = STATE_HEAL
            self.state_timer = self.durations[STATE_HEAL]
            return

        if self.timers[STATE_DEFENSE] <= 0:
            self.state = STATE_DEFENSE
            self.state_timer = self.durations[STATE_DEFENSE]
            return

        if self.timers[STATE_ATTACK] <= 0:
            self.state = STATE_ATTACK
            self.state_timer = self.durations[STATE_ATTACK]
            return

    def _cast_attack(self):
        # Destroy one random dice
        if self.game and self.game.grid:
            import random
            filled = []
            for c in range(self.game.grid.cols):
                for r in range(self.game.grid.rows):
                    if self.game.grid.get(c, r):
                        filled.append((c, r))
            
            if filled:
                c, r = random.choice(filled)
                self.game.grid.remove(c, r)
                # Optional: Add visual effect for destruction in main loop

    def draw(self, surf, font):
        # Override draw to show state
        r = pygame.Rect(int(self.x - self.size/2), int(self.y - self.size/2), self.size, self.size)
        color = ORANGE
        border_color = None
        border_width = 0
        
        if self.state == STATE_DEFENSE:
            color = BLUE # Defense color
            border_color = WHITE
            border_width = 4
        elif self.state == STATE_HEAL:
            color = GREEN # Heal color
            border_color = WHITE
            border_width = 4
        elif self.state == STATE_ATTACK:
            # Flashing red
            color = RED
            border_color = (255, 255, 0)
            border_width = 4
        
        pygame.draw.rect(surf, color, r, border_radius=10)
        if border_color:
             pygame.draw.rect(surf, border_color, r, width=border_width, border_radius=10)
        
        # Debuff colors on top
        if self.poison_timer > 0:
             pygame.draw.rect(surf, (180, 50, 255), r, width=2, border_radius=10)
        elif self.slow_timer > 0:
             pygame.draw.rect(surf, (100, 100, 255), r, width=2, border_radius=10)

        hp_txt = font.render(str(max(0, int(self.hp + 0.5))), True, WHITE)
        surf.blit(hp_txt, (r.centerx - hp_txt.get_width()//2, r.centery - hp_txt.get_height()//2))
