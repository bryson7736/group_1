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

# =============================================================================
# FSM States
# =============================================================================
STATE_IDLE = "idle"
STATE_DEFENSE = "defense"
STATE_ATTACK = "attack"
STATE_HEAL = "heal"

# =============================================================================
# Boss Settings (Configurable)
# =============================================================================
BOSS_SIZE_MULT = 3          # Boss is 3x larger than normal enemy
BOSS_MONEY_DROP = 200.0     # Money reward for killing boss
BOSS_SPEED_MULT = 0.7       # Boss moves slower than normal enemies

# Boss HP Formula Settings
BOSS_BASE_HP = 5000.0      # Base HP for boss
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

# Global Skill Cooldown (shared by all skills)
GLOBAL_SKILL_COOLDOWN = 5.0     # Cooldown after using any skill
INITIAL_SKILL_COOLDOWN = 2.0    # Initial cooldown at spawn

# Skill Durations (seconds)
SKILL_DURATION = {
    STATE_DEFENSE: 3.0,
    STATE_ATTACK: 1.0,  # Cast time
    STATE_HEAL: 2.0,
}

# Defense settings
DEFENSE_DAMAGE_REDUCTION = 0.5  # 50% damage reduction
DEFENSE_MOVE_SPEED_MULT = 0.5   # Move at 50% speed while defending

# Heal settings
HEAL_HP_PERCENT_PER_SEC = 0.05  # 5% max HP per second
HEAL_TRIGGER_THRESHOLD = 0.8   # Heal when HP < 80%

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
        
        # FSM State
        self.state = STATE_IDLE
        self.state_timer = 0.0
        
        # Skill cooldowns and durations
        self.durations = dict(SKILL_DURATION)
        # Per-state cooldown timers (tested via boss.timers[STATE_X])
        self.timers = {
            STATE_DEFENSE: INITIAL_SKILL_COOLDOWN,
            STATE_ATTACK: INITIAL_SKILL_COOLDOWN,
            STATE_HEAL: INITIAL_SKILL_COOLDOWN,
        }

    def hit(self, dmg):
        """Override hit to apply defense damage reduction."""
        if self.state == STATE_DEFENSE:
            dmg *= DEFENSE_DAMAGE_REDUCTION
        super().hit(dmg)

    def update(self, dt, speed_mult=1.0, zone_mult=1.0):
        """FSM update logic."""
        if self.dead or self.reached:
            return

        # Update per-state cooldown timers
        for state in self.timers:
            self.timers[state] = max(0, self.timers[state] - dt * speed_mult)
            
        # State Machine timer
        self.state_timer = max(0, self.state_timer - dt * speed_mult)
        
        if self.state == STATE_IDLE:
            self._state_idle(dt, speed_mult, zone_mult)
        elif self.state == STATE_DEFENSE:
            self._state_defense(dt, speed_mult, zone_mult)
        elif self.state == STATE_ATTACK:
            self._state_attack(dt, speed_mult, zone_mult)
        elif self.state == STATE_HEAL:
            self._state_heal(dt, speed_mult, zone_mult)

    # -------------------------------------------------------------------------
    # State Handlers
    # -------------------------------------------------------------------------
    def _state_idle(self, dt, speed_mult, zone_mult):
        """IDLE: Move normally, try to pick a skill."""
        super().update(dt, speed_mult, zone_mult)
        self._try_skill()
    
    def _state_defense(self, dt, speed_mult, zone_mult):
        """DEFENSE: Move slowly, reduce damage taken."""
        super().update(dt, speed_mult * DEFENSE_MOVE_SPEED_MULT, zone_mult)
        if self.state_timer <= 0:
            self._reset_all_timers()
            self.state = STATE_IDLE

    def _state_attack(self, dt, speed_mult, zone_mult):
        """ATTACK: Stop moving, cast attack when timer ends."""
        if self.state_timer <= 0:
            self._cast_attack()
            self._reset_all_timers()
            self.state = STATE_IDLE

    def _state_heal(self, dt, speed_mult, zone_mult):
        """HEAL: Stop moving, regenerate HP."""
        heal_rate = HEAL_HP_PERCENT_PER_SEC * self.max_hp
        self.hp = min(self.max_hp, self.hp + heal_rate * dt * speed_mult)
        
        if self.state_timer <= 0:
            self._reset_all_timers()
            self.state = STATE_IDLE

    # -------------------------------------------------------------------------
    # Skill Logic
    # -------------------------------------------------------------------------
    def _try_skill(self):
        """Attempt to activate a skill based on priority."""
        # Check global cooldown - if ANY timer > 0, all skills are on cooldown
        if any(t > 0 for t in self.timers.values()):
            return
        
        # Priority: Heal (if low HP) > Defense > Attack
        if self.hp < self.max_hp * HEAL_TRIGGER_THRESHOLD:
            self._enter_state(STATE_HEAL)
            return

        # Random choice between Defense and Attack
        import random
        if random.random() < 0.5:
            self._enter_state(STATE_DEFENSE)
        else:
            self._enter_state(STATE_ATTACK)

    def _reset_all_timers(self):
        """Reset all skill timers to global cooldown (shared cooldown)."""
        for state in self.timers:
            self.timers[state] = GLOBAL_SKILL_COOLDOWN

    def _enter_state(self, new_state):
        """Transition to a new state."""
        self.state = new_state
        self.state_timer = self.durations[new_state]

    def _cast_attack(self):
        """Destroy random dice on the player's grid."""
        if not self.game or not self.game.grid:
            return
            
        filled = []
        for c in range(self.game.grid.cols):
            for r in range(self.game.grid.rows):
                if self.game.grid.get(c, r):
                    filled.append((c, r))
        
        if filled:
            for _ in range(min(ATTACK_DESTROY_DICE_COUNT, len(filled))):
                c, r = random.choice(filled)
                self.game.grid.remove(c, r)
                filled.remove((c, r))

    # -------------------------------------------------------------------------
    # Drawing
    # -------------------------------------------------------------------------
    def draw(self, surf, font):
        """Override draw to show current state visually."""
        r = pygame.Rect(int(self.x - self.size/2), int(self.y - self.size/2), self.size, self.size)
        color = ORANGE
        border_color = None
        border_width = 0
        
        if self.state == STATE_DEFENSE:
            color = BLUE
            border_color = WHITE
            border_width = 4
        elif self.state == STATE_HEAL:
            color = GREEN
            border_color = WHITE
            border_width = 4
        elif self.state == STATE_ATTACK:
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

        hp_txt = font.render(str(max(0, int(self.hp + 0.5))), True, WHITE)
        surf.blit(hp_txt, (r.centerx - hp_txt.get_width()//2, r.centery - hp_txt.get_height()//2))
