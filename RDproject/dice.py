# -*- coding: utf-8 -*-
import math, os, pygame, random
from colors import WHITE, DICE_COLORS, BLUE
from settings import BASE_RANGE, BASE_FIRE_RATE, FIRE_RATE_STEP, MAX_DIE_LEVEL, ASSET_FILES, FPS, ASSETS_DIR
from settings import BIG_ENEMY_ZONE_SLOW_DICE, FREEZE_DURATION, FREEZE_SLOW_RATIO
from projectiles import Bullet, ChainBolt, ExplosiveBullet
from ui import draw_pips

DIE_SINGLE = "single"
DIE_MULTI = "multi"
DIE_FREEZE = "freeze"
DIE_WIND = "wind"
DIE_POISON = "poison"
DIE_IRON = "iron"
DIE_FIRE = "fire"
DIE_TYPES = [DIE_SINGLE, DIE_MULTI, DIE_FREEZE, DIE_WIND, DIE_POISON, DIE_IRON, DIE_FIRE]

_dice_images_cache = {}

def get_die_image(die_type):
    if die_type in _dice_images_cache:
        return _dice_images_cache[die_type]
    p = ASSET_FILES.get("dice", {}).get(die_type)
    if p and os.path.exists(os.path.join(ASSETS_DIR, p)):
        img = pygame.image.load(os.path.join(ASSETS_DIR, p)).convert_alpha()
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
        """Effective range."""
        # Base range is constant for now, or could be upgraded
        return self.base_range

    @property
    def x(self):
        return self.game.grid.center_of(self.c, self.r)[0]

    @property
    def y(self):
        return self.game.grid.center_of(self.c, self.r)[1]

    def set_level(self, lv):
        self.level = max(1, min(MAX_DIE_LEVEL, lv))
        # New Proportional Logic: Period = Base / Level
        # Base period from settings: 50/60 = 0.83s at level 1
        base_period_at_lv1 = BASE_FIRE_RATE / FPS
        self.base_period_sec = base_period_at_lv1 / self.level
        self.cool = 0.0

    def can_merge_with(self, other):
        return other and (self.type == other.type) and (self.level == other.level)

    def draw(self, surf, selected):
        rect = self.game.grid.rect_at(self.c, self.r).inflate(-12, -12)
        base_col = DICE_COLORS.get(self.type, (140, 140, 160))
        
        # 1. Background (Glossy Square Style)
        pygame.draw.rect(surf, base_col, rect, border_radius=14)
        
        # Glossy Highlight (Top 40%)
        highlight_rect = pygame.Rect(rect.x, rect.y, rect.w, int(rect.h * 0.4))
        highlight = pygame.Surface((highlight_rect.w, highlight_rect.h), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 45))
        surf.blit(highlight, highlight_rect.topleft)

        # 2. Main Icon
        if not self.image:
            self.image = get_die_image(self.type)
        if self.image:
            ir = self.image.get_rect()
            target_w = rect.w * 0.75
            scale = target_w / ir.w
            img = pygame.transform.smoothscale(self.image, (int(ir.w * scale), int(ir.h * scale)))
            img.set_alpha(180) # Better visibility than before
            surf.blit(img, (rect.centerx - img.get_width() // 2, rect.centery - img.get_height() // 2))

        # 3. Level indicator (Pips/Dots restored for field dice)
        draw_pips(surf, rect, self.level, WHITE)

        # 4. Selection/Border logic
        if selected:
            pygame.draw.rect(surf, BLUE, rect, width=5, border_radius=14)
        else:
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
        
        # In-game upgrade: +10% speed per level
        ingame_level = self.game.ingame_upgrades.get_level(self.type)
        ingame_mult = 1.0 + (ingame_level - 1) * 0.10
        
        return perm_mult / ingame_mult

    def damage_multiplier(self):
        # Combine permanent upgrades with in-game upgrades
        perm_mult = self.game.upgrades.get_damage_mult(self.type)
        
        # In-game upgrade: +20% damage per level
        ingame_level = self.game.ingame_upgrades.get_level(self.type)
        ingame_mult = 1.0 + (ingame_level - 1) * 0.20
        
        return perm_mult * ingame_mult

    def apply_crit(self, dmg):
        crit_rate = self.game.upgrades.get_crit_rate(self.type)
        if random.random() < crit_rate:
            return dmg * 2.0
        return dmg

    def try_fire(self):
        # All dice except Iron: Priority attack frontmost enemy ("first" mode)
        best = None
        bestv = None
        for e in self.game.enemies:
            if e.dead or e.reached:
                continue
            dx, dy = e.x - self.x, e.y - self.y
            d = (dx*dx + dy*dy) ** 0.5
            if d > self.range:
                continue

            # First mode: higher idx = further along path, prioritize frontmost
            v = (e.idx, -d)
            cond = (best is None) or (v > bestv)

            if cond:
                best = e; bestv = v

        if best:
            self.fire_at(best)

    def fire_at(self, target):
        base = 2 ** (self.level - 1)
        dmg = self.apply_crit(base * self.damage_multiplier())
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))


class SingleDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_SINGLE
        
        # Stats:
        # Base: 15 Dmg (nerfed from 20), 0.45s AS, +10% AS bonus
        # Per Level: +3 Dmg, +2% AS bonus
        self.base_dmg = 15 + (self.level - 1) * 3
        
        base_period = 0.45
        as_bonus = 0.10 + (self.level - 1) * 0.02
        # New Logic: Period = 0.45 / level (with small bonus kept? or removed?)
        # Simplest proportional logic:
        self.base_period_sec = base_period / self.level
        # Removing old bonus formula to keep it strictly proportional + upgrades
        self.base_fire_rate = self.base_period_sec * FPS  # For compatibility

    def set_level(self, lv):
        super().set_level(lv)
        # Recalculate stats
        self.base_dmg = 15 + (self.level - 1) * 3
        base_period = 0.45
        self.base_period_sec = base_period / self.level
        self.base_fire_rate = self.base_period_sec * FPS

    def fire_at(self, target):
        dmg = self.apply_crit(self.base_dmg * self.damage_multiplier())
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))


class MultiDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_MULTI

    def fire_at(self, target):
        # Buff: Jumps = level (so Lv1 has 1 jump, hitting 2 targets total)
        jumps = self.level
        # Buff: Base damage starts at 3 instead of 1
        base = 3 * (2 ** (self.level - 1))
        dmg = self.apply_crit(base * self.damage_multiplier())
        self.game.bullets.append(ChainBolt(self.game, self.x, self.y, target, dmg, jumps, self.game.enemies, speed_mult_provider=lambda: self.game.speed_mult))


class FreezeDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_FREEZE

    def fire_at(self, target):
        base = 2 ** max(0, self.level - 2)
        dmg = self.apply_crit(base * self.damage_multiplier())
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))
        target.apply_slow(FREEZE_SLOW_RATIO, FREEZE_DURATION + 0.2 * (self.level - 1))


class WindDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_WIND
        # Wind fires much faster: 0.3s base at level 1
        self.base_period_sec = 0.3 / self.level
        self.base_fire_rate = self.base_period_sec * FPS

    def set_level(self, lv):
        super().set_level(lv)
        # Wind Logic: Base 0.3s / level
        self.base_period_sec = 0.3 / self.level
        self.base_fire_rate = self.base_period_sec * FPS


class PoisonDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_POISON

    def fire_at(self, target):
        base = 2 ** (self.level - 1)
        dmg = self.apply_crit(base * self.damage_multiplier())
        # Initial hit
        self.game.bullets.append(Bullet(self.game, self.x, self.y, target, dmg, speed_mult_provider=lambda: self.game.speed_mult))
        # Apply poison: dmg per sec for 3s (Buffed to 0.6x)
        # In-game upgrade: +10% dot ratio per level
        ingame_level = self.game.ingame_upgrades.get_level(self.type)
        dot_ratio = 0.6 + (ingame_level - 1) * 0.1
        
        poison_dps = dmg * dot_ratio
        target.apply_poison(poison_dps, 3.0)


class IronDice(Die):
    def __init__(self, game, c, r, level=1):
        super().__init__(game, c, r, level)
        self.type = DIE_IRON
        
        # Stats:
        # Base: 100 Dmg, 1.5s AS (Buffed from 2.0s), Boss Dmg x2
        # Per Level: +10 Dmg
        self.base_dmg = 100 + (self.level - 1) * 10
        self.base_period_sec = 1.5 / self.level
        self.base_fire_rate = self.base_period_sec * FPS

    def set_level(self, lv):
        super().set_level(lv)
        self.base_dmg = 100 + (self.level - 1) * 10
        self.base_period_sec = 1.5 / self.level
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
        from enemy import BigEnemy
        from boss import TrueBoss
        if isinstance(target, (BigEnemy, TrueBoss)):
            # Base 2.0x, +0.5x per in-game level
            ingame_level = self.game.ingame_upgrades.get_level(self.type)
            boss_mult = 2.0 + (ingame_level - 1) * 0.5
            dmg *= boss_mult
        
        dmg = self.apply_crit(dmg)
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
        self.base_period_sec = base_period / self.level
        self.base_fire_rate = self.base_period_sec * FPS
        self.splash_radius = 80  # Explosion radius

    def set_level(self, lv):
        super().set_level(lv)
        self.base_dmg = 20 + (self.level - 1) * 3
        self.splash_dmg = 20 + (self.level - 1) * 3
        
        base_period = 0.8
        self.base_period_sec = base_period / self.level
        self.base_fire_rate = self.base_period_sec * FPS

    def fire_at(self, target):
        dmg = self.apply_crit(self.base_dmg * self.damage_multiplier())
        # Splash damage is 75% of main damage (Nerfed from 100%)
        splash = self.splash_dmg * self.damage_multiplier() * 0.75
        
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
