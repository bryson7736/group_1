# -*- coding: utf-8 -*-
import math, os, pygame, random
from colors import WHITE, DICE_COLORS
from settings import BASE_RANGE, BASE_FIRE_RATE, FIRE_RATE_STEP, MAX_DIE_LEVEL, ASSET_FILES, FPS
from settings import BOSS_ZONE_SLOW_DICE, FREEZE_DURATION, FREEZE_SLOW_RATIO
from settings import BOSS_ZONE_SLOW_DICE, FREEZE_DURATION, FREEZE_SLOW_RATIO
from projectiles import Bullet, ChainBolt, ExplosiveBullet

DIE_SINGLE = "single"
DIE_MULTI = "multi"
DIE_FREEZE = "freeze"
DIE_WIND = "wind"
DIE_POISON = "poison"
DIE_IRON = "iron"
DIE_FIRE = "fire"
DIE_TYPES = [DIE_SINGLE, DIE_MULTI, DIE_FREEZE, DIE_WIND, DIE_POISON, DIE_IRON, DIE_FIRE]

_dice_images_cache = {}

def _load_die_image(die_type):
    if die_type in _dice_images_cache:
        return _dice_images_cache[die_type]
    p = ASSET_FILES.get("dice", {}).get(die_type)
    if p and os.path.exists(os.path.join("assets", p)):
        img = pygame.image.load(os.path.join("assets", p)).convert_alpha()
        _dice_images_cache[die_type] = img
        return img
    _dice_images_cache[die_type] = None
    return None

class Die:
    """Base die: renders a colored card (or PNG), handles firing cadence."""
    def __init__(self, game, c, r, level=1):
        self.game = game
        self.c = c
        self.r = r
        self.level = level
        self.type = DIE_SINGLE
        self.base_range = BASE_RANGE  # Store base range
        self.base_fire_rate = max(12, BASE_FIRE_RATE - (self.level - 1) * FIRE_RATE_STEP)
        self.cool = 0.0
        self.image = None
        # Ensure period in seconds initialized at construction
        self.base_period_sec = self.base_fire_rate / FPS
    
    @property
    def range(self):
        """Effective range with in-game upgrades applied."""
        return self.base_range * self.game.ingame_upgrades.get_range_multiplier()

    @property
    def x(self):
        return self.game.grid.center_of(self.c, self.r)[0]

    @property
    def y(self):
        return self.game.grid.center_of(self.c, self.r)[1]

    def set_level(self, lv):
        self.level = max(1, min(MAX_DIE_LEVEL, lv))
        self.base_fire_rate = max(8, BASE_FIRE_RATE - (self.level - 1) * FIRE_RATE_STEP)
        # Convert frame-based rate to seconds for stable timing across FPS
        self.base_period_sec = self.base_fire_rate / FPS
        self.cool = 0.0

    def can_merge_with(self, other):
        return other and (self.type == other.type) and (self.level == other.level)

    def draw(self, surf, selected):
        rect = self.game.grid.rect_at(self.c, self.r).inflate(-12, -12)
        base_col = DICE_COLORS.get(self.type, (140, 140, 160))
        pygame.draw.rect(surf, base_col, rect, border_radius=14)
        if selected:
            pygame.draw.rect(surf, WHITE, rect, width=3, border_radius=14)

        font = self.game.font_big
        lvl = font.render(f"Lv {self.level}", True, WHITE)
        surf.blit(lvl, (rect.centerx - lvl.get_width() // 2, rect.centery - lvl.get_height() // 2))

        if not self.image:
            self.image = _load_die_image(self.type)
        if self.image:
            ir = self.image.get_rect()
            scale = min(rect.w * 0.6 / ir.w, rect.h * 0.45 / ir.h)
            img = pygame.transform.smoothscale(self.image, (int(ir.w * scale), int(ir.h * scale)))
            surf.blit(img, (rect.centerx - img.get_width() // 2, rect.y + 8))

        pygame.draw.rect(surf, (255,255,255), rect, width=2, border_radius=14)
        glow = rect.copy()
        glow.h = int(rect.h * 0.35)
        highlight = pygame.Surface((glow.w, glow.h), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 42))
        surf.blit(highlight, glow.topleft)

    def update(self, dt):
        # dice period can be increased by boss zone effect
        zone_mult = 1.0
        for z in self.game.telegraphs:
            if z.in_effect_phase() and z.contains(self.x, self.y):
                zone_mult *= z.dice_period_mult
        self.cool += dt * self.game.speed_mult
        effective_period = self.base_period_sec * self.fire_rate_factor() * zone_mult
        if self.cool >= effective_period:
            self.cool = 0.0
            self.try_fire()

    def fire_rate_factor(self):
        # Combine permanent upgrades with in-game upgrades
        perm_mult = self.game.upgrades.get_fire_rate_mult(self.type)
        ingame_mult = self.game.ingame_upgrades.get_firerate_multiplier()
        # Fire rate multiplier reduces period (faster = smaller period)
        return perm_mult / ingame_mult

    def damage_multiplier(self):
        # Combine permanent upgrades with in-game upgrades
        perm_mult = self.game.upgrades.get_damage_mult(self.type)
        ingame_mult = self.game.ingame_upgrades.get_damage_multiplier()
        return perm_mult * ingame_mult

    def try_fire(self):
        mode = self.game.target_mode
        best = None
        bestv = None
        for e in self.game.enemies:
            if e.dead or e.reached:
                continue
            dx, dy = e.x - self.x, e.y - self.y
            d = (dx*dx + dy*dy) ** 0.5
            if d > self.range:
                continue

            if mode == "nearest":
                v = d; cond = (best is None) or (v < bestv)
            elif mode == "first":
                v = (e.idx, -d); cond = (best is None) or (v > bestv)
            elif mode == "weak":
                v = e.hp; cond = (best is None) or (v < bestv)
            else:
                v = e.hp; cond = (best is None) or (v > bestv)

            if cond:
                best = e; bestv = v

        if best:
            self.fire_at(best)

    def fire_at(self, target):
        base = 2 ** (self.level - 1)
        dmg = base * self.damage_multiplier()
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))


class SingleDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_SINGLE
        
        # Stats:
        # Base: 20 Dmg, 0.45s AS, +10% AS bonus
        # Per Level: +3 Dmg, +2% AS bonus
        self.base_dmg = 20 + (self.level - 1) * 3
        
        base_period = 0.45
        as_bonus = 0.10 + (self.level - 1) * 0.02
        self.base_period_sec = base_period / (1.0 + as_bonus)
        self.base_fire_rate = self.base_period_sec * FPS  # For compatibility

    def set_level(self, lv):
        super().set_level(lv)
        # Recalculate stats
        self.base_dmg = 20 + (self.level - 1) * 3
        base_period = 0.45
        as_bonus = 0.10 + (self.level - 1) * 0.02
        self.base_period_sec = base_period / (1.0 + as_bonus)
        self.base_fire_rate = self.base_period_sec * FPS

    def fire_at(self, target):
        dmg = self.base_dmg * self.damage_multiplier()
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))


class MultiDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_MULTI

    def fire_at(self, target):
        jumps = max(0, self.level - 1)
        base = 2 ** (self.level - 1)
        dmg = base * self.damage_multiplier()
        self.game.bullets.append(ChainBolt(self.game, self.x, self.y, target, dmg, jumps, self.game.enemies, speed_mult_provider=lambda: self.game.speed_mult))


class FreezeDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_FREEZE

    def fire_at(self, target):
        base = 2 ** max(0, self.level - 2)
        dmg = base * self.damage_multiplier()
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))
        target.apply_slow(FREEZE_SLOW_RATIO, FREEZE_DURATION + 0.2 * (self.level - 1))


class WindDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_WIND
        # Wind fires much faster
        self.base_fire_rate = max(6, int(self.base_fire_rate * 0.4))
        self.base_period_sec = self.base_fire_rate / FPS

    def set_level(self, lv):
        super().set_level(lv)
        self.base_fire_rate = max(4, int(self.base_fire_rate * 0.4))
        self.base_period_sec = self.base_fire_rate / FPS


class PoisonDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_POISON

    def fire_at(self, target):
        base = 2 ** (self.level - 1)
        dmg = base * self.damage_multiplier()
        # Initial hit
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))
        # Apply poison: dmg per sec for 3s
        poison_dps = dmg * 0.5
        target.apply_poison(poison_dps, 3.0)


class IronDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_IRON
        
        # Stats:
        # Base: 100 Dmg, 2.0s AS, Boss Dmg x2
        # Per Level: +10 Dmg
        self.base_dmg = 100 + (self.level - 1) * 10
        self.base_period_sec = 2.0
        self.base_fire_rate = self.base_period_sec * FPS

    def set_level(self, lv):
        super().set_level(lv)
        self.base_dmg = 100 + (self.level - 1) * 10
        self.base_period_sec = 2.0
        self.base_fire_rate = self.base_period_sec * FPS

    def try_fire(self):
        # Iron Dice always targets the strongest (Highest HP) enemy
        best = None
        bestv = -1
        for e in self.game.enemies:
            if e.dead or e.reached:
                continue
            dx, dy = e.x - self.x, e.y - self.y
            d = (dx*dx + dy*dy) ** 0.5
            if d > self.range:
                continue
            
            # Target highest HP
            if e.hp > bestv:
                bestv = e.hp
                best = e
        
        if best:
            self.fire_at(best)

    def fire_at(self, target):
        dmg = self.base_dmg * self.damage_multiplier()
        
        # Bonus vs Boss
        from enemy import Boss
        if isinstance(target, Boss):
            dmg *= 2.0
        
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))


class FireDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_FIRE
        
        # Stats:
        # Base: 20 Dmg, 0.8s AS, 20 Splash Dmg
        # Per Level: +3 Dmg, -0.01s AS, +3 Splash Dmg
        self.base_dmg = 20 + (self.level - 1) * 3
        self.splash_dmg = 20 + (self.level - 1) * 3
        
        base_period = 0.8
        period_reduction = (self.level - 1) * 0.01
        self.base_period_sec = max(0.1, base_period - period_reduction)
        self.base_fire_rate = self.base_period_sec * FPS
        self.splash_radius = 80  # Explosion radius

    def set_level(self, lv):
        super().set_level(lv)
        self.base_dmg = 20 + (self.level - 1) * 3
        self.splash_dmg = 20 + (self.level - 1) * 3
        
        base_period = 0.8
        period_reduction = (self.level - 1) * 0.01
        self.base_period_sec = max(0.1, base_period - period_reduction)
        self.base_fire_rate = self.base_period_sec * FPS

    def fire_at(self, target):
        dmg = self.base_dmg * self.damage_multiplier()
        splash = self.splash_dmg * self.damage_multiplier()
        
        self.game.bullets.append(ExplosiveBullet(
            self.game, self.x, self.y, target, 
            dmg, splash, self.splash_radius, 
            speed_mult_provider=lambda: self.game.speed_mult
        ))


def make_die(game, c, r, die_type, level=1):
    if die_type == DIE_MULTI:
        return MultiDice(game, c, r, level)
    elif die_type == DIE_FREEZE:
        return FreezeDice(game, c, r, level)
    elif die_type == DIE_WIND:
        return WindDice(game, c, r, level)
    elif die_type == DIE_POISON:
        return PoisonDice(game, c, r, level)
    elif die_type == DIE_IRON:
        return IronDice(game, c, r, level)
    elif die_type == DIE_FIRE:
        return FireDice(game, c, r, level)
    return SingleDice(game, c, r, level)
