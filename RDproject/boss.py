# -*- coding: utf-8 -*-
"""
Boss Module - TrueBoss with FSM
Separated for easier expansion of boss mechanics and skills.
"""
import random
import pygame
from colors import WHITE, ORANGE, RED, GREEN, BLUE
from settings import ENEMY_SIZE
from enemy import Enemy
from boss_ai.BossAIController import BossAIController

# =============================================================================
# Boss Settings (Configurable)
# =============================================================================
BOSS_SIZE_MULT = 3          # Boss is 3x larger than normal enemy
BOSS_MONEY_DROP = 200.0     # Money reward for killing boss
BOSS_SPEED_MULT = 0.7       # Boss moves slower than normal enemies

# Boss HP Formula Settings
BOSS_BASE_HP = 2500.0      # Base HP for boss
BOSS_HP_PER_WAVE = 500.0    # Additional HP per wave
BOSS_HP_DIFFICULTY_SCALE = 3  # Difficulty scaling exponent


def calculate_boss_hp(wave: int, difficulty: float = 1.0) -> float:
    """
    Calculate Boss HP based on wave and difficulty.
    Formula: (BASE_HP + wave * HP_PER_WAVE) * (difficulty ^ DIFFICULTY_SCALE)
    """
    base = BOSS_BASE_HP + wave * BOSS_HP_PER_WAVE
    return base * (difficulty ** BOSS_HP_DIFFICULTY_SCALE)


def calculate_boss_speed(base_speed: float) -> float:
    """Calculate Boss movement speed."""
    return base_speed * BOSS_SPEED_MULT


# Defense settings
DEFENSE_DAMAGE_REDUCTION = 0.5  # 50% damage reduction
DEFENSE_MOVE_SPEED_MULT = 0.5   # Move at 50% speed while defending

# Attack settings
ATTACK_DESTROY_DICE_COUNT = 1  # Number of dice to destroy per attack


# =============================================================================
# TrueBoss Class
# =============================================================================
class TrueBoss(Enemy):
    """
    True Boss with FSM-based skills:
    - IDLE: Normal movement, checks for available skills
    - DEFENSE: Reduces incoming damage, moves slowly
    - ATTACK: Stops to cast, destroys player dice
    - HEAL: Stops to regenerate HP
    """
    
    def __init__(self, path_points, hp, speed, game=None):
        super().__init__(path_points, hp, speed, size=ENEMY_SIZE * BOSS_SIZE_MULT)
        self.game = game
        self.money_drop = BOSS_MONEY_DROP
        
        # New Boss AI Controller
        self.ai_controller = BossAIController(self, game)
        
        self.attack_targets = [] # List of (c, r) tuples for targeted dice

    @property
    def state(self):
        """Map HFSM skill names back to legacy state names for UI compatibility."""
        skill = self.ai_controller.executor.current_skill
        if skill in ["Shield", "DamageReduction"]:
            return "defense"
        elif skill in ["BasicAttack", "AOEAttack", "Disrupt"]:
            return "attack"
        elif skill == "Heal":
            return "heal"
        return "idle"

    def hit(self, dmg):
        """Override hit to apply defense damage reduction and track damage."""
        # Use AI controller state for damage reduction logic
        if self.ai_controller.executor.current_skill == "Shield":
            dmg *= DEFENSE_DAMAGE_REDUCTION
        
        super().hit(dmg)
        self.ai_controller.record_damage(dmg)

    def update(self, dt, speed_mult=1.0, zone_mult=1.0):
        """FSM update logic."""
        if self.dead or self.reached:
            return

        # Delegate update to AI controller
        self.ai_controller.update(dt * speed_mult)
        
        # Movement logic based on current state/skill
        current_skill = self.ai_controller.executor.current_skill
        
        if current_skill in ["Shield", "DamageReduction"]:
            # Move slowly during defense
            super().update(dt, speed_mult * DEFENSE_MOVE_SPEED_MULT, zone_mult)
        elif current_skill in ["AOEAttack", "Heal", "SummonMinion"]:
            # Stop moving during casting/healing
            pass 
        else:
            # Move normally (Idle or BasicAttack)
            super().update(dt, speed_mult, zone_mult)

    # -------------------------------------------------------------------------
    # Bridge for SkillExecutor
    # -------------------------------------------------------------------------
    def on_skill_start(self, skill_name):
        """Called when a skill starts (animation trigger)."""
        self.attack_targets = []
        if skill_name in ["BasicAttack", "AOEAttack", "Disrupt"]:
            # Selection of targets happens when skill starts
            if self.game and self.game.grid:
                filled = []
                for c in range(self.game.grid.cols):
                    for r in range(self.game.grid.rows):
                        if self.game.grid.get(c, r):
                            filled.append((c, r))
                
                if filled:
                    count = min(ATTACK_DESTROY_DICE_COUNT, len(filled))
                    self.attack_targets = random.sample(filled, count)

    def apply_skill_effect(self, skill_name):
        """Called when a skill durationEnds (execution trigger)."""
        if skill_name in ["BasicAttack", "AOEAttack", "Disrupt"]:
            self._cast_attack()
        elif skill_name == "Heal":
            self.hp = min(self.max_hp, self.hp + self.max_hp * 0.2) # Heal 20%
        elif skill_name == "SummonMinion":
            # Implementation of summon minion could go here
            pass

    def _cast_attack(self):
        """Destroy targeted dice on the player's grid."""
        if not self.game or not self.game.grid:
            return
            
        for c, r in self.attack_targets:
            # Verify die still exists there (it might have been merged/trashed)
            if self.game.grid.get(c, r):
                self.game.grid.remove(c, r)
        
        self.attack_targets = []

    # -------------------------------------------------------------------------
    # Drawing
    # -------------------------------------------------------------------------
    def draw(self, surf, font):
        """Override draw to show current state visually."""
        r = pygame.Rect(int(self.x - self.size/2), int(self.y - self.size/2), self.size, self.size)
        color = ORANGE
        border_color = None
        border_width = 0
        
        current_skill = self.ai_controller.executor.current_skill
        
        if current_skill == "Shield":
            color = BLUE
            border_color = WHITE
            border_width = 4
        elif current_skill == "Heal":
            color = GREEN
            border_color = WHITE
            border_width = 4
        elif current_skill in ["BasicAttack", "AOEAttack", "Disrupt"]:
            color = RED
            border_color = (255, 255, 0)
            border_width = 4
        
        pygame.draw.rect(surf, color, r, border_radius=10)
        if border_color:
            pygame.draw.rect(surf, border_color, r, width=border_width, border_radius=10)
        
        # Debuff indicators
        if self.poison_timer > 0:
            pygame.draw.rect(surf, (180, 50, 255), r, width=2, border_radius=10)
        elif self.slow_timer > 0:
            pygame.draw.rect(surf, (100, 100, 255), r, width=2, border_radius=10)

        # Health Bar
        bar_w = self.size
        bar_h = 8
        bar_x = int(self.x - bar_w / 2)
        bar_y = int(self.y - self.size / 2 - bar_h - 6)
        
        # Background (Red/Dark)
        pygame.draw.rect(surf, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        
        # Foreground (Green)
        if self.max_hp > 0:
            pct = max(0.0, min(1.0, self.hp / self.max_hp))
            fill_w = int(bar_w * pct)
            pygame.draw.rect(surf, (0, 255, 0), (bar_x, bar_y, fill_w, bar_h))

        hp_txt = font.render(str(max(0, int(self.hp + 0.5))), True, WHITE)
        surf.blit(hp_txt, (r.centerx - hp_txt.get_width()//2, r.centery - hp_txt.get_height()//2))

        # Draw Target Indicators on Grid
        if self.ai_controller.executor.current_skill in ["BasicAttack", "AOEAttack", "Disrupt"] and self.attack_targets:
            for c, r in self.attack_targets:
                if self.game and self.game.grid:
                    rect = self.game.grid.rect_at(c, r)
                    # Draw a crosshair or target symbol
                    cx, cy = rect.centerx, rect.centery
                    # Pulsing effect
                    pulse = (pygame.time.get_ticks() % 500) / 500.0
                    radius = 20 + int(pulse * 10)
                    
                    # Red circle
                    pygame.draw.circle(surf, (255, 0, 0), (cx, cy), radius, width=3)
                    # Cross
                    pygame.draw.line(surf, (255, 0, 0), (cx - radius, cy), (cx + radius, cy), 3)
                    pygame.draw.line(surf, (255, 0, 0), (cx, cy - radius), (cx, cy + radius), 3)
