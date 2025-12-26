# -*- coding: utf-8 -*-
class UpgradeState:
    """Session-lifetime upgrades and coins."""
    def __init__(self):
        self.coins = 0
        # In-game upgrades (reset per run)
        self.ingame_damage_mult = {}
        self.ingame_fire_rate_mult = {}
        self.ingame_cost_mult = {}
        
        # Class upgrades (persistent-ish)
        self.class_damage_mult = {}
        self.class_fire_rate_mult = {}
        self.class_crit_rate = {}

    def reset_ingame(self):
        self.ingame_damage_mult = {}
        self.ingame_fire_rate_mult = {}
        self.ingame_cost_mult = {}

    def ensure_type(self, t):
        self.ingame_damage_mult.setdefault(t, 1.0)
        self.ingame_fire_rate_mult.setdefault(t, 1.0)
        self.ingame_cost_mult.setdefault(t, 1.0)
        
        self.class_damage_mult.setdefault(t, 1.0)
        self.class_fire_rate_mult.setdefault(t, 1.0)

    def get_damage_mult(self, t):
        self.ensure_type(t)
        return self.ingame_damage_mult[t] * self.class_damage_mult[t]

    def get_fire_rate_mult(self, t):
        self.ensure_type(t)
        return self.ingame_fire_rate_mult[t] * self.class_fire_rate_mult[t]
        
    def get_cost_mult(self, t):
        self.ensure_type(t)
        return self.ingame_cost_mult[t]

    def add_coin(self, n=1):
        self.coins += n

    def spend(self, cost):
        if self.coins >= cost:
            self.coins -= cost
            return True
        return False

    # --- In-Game Upgrades ---
    def upgrade_ingame_damage(self, t, *, step=0.10, cost=100):
        self.ensure_type(t)
        if self.spend(cost):
            self.ingame_damage_mult[t] *= (1.0 + step)
            return True
        return False

    def upgrade_ingame_fire(self, t, *, step=0.08, cost=100):
        self.ensure_type(t)
        if self.spend(cost):
            self.ingame_fire_rate_mult[t] *= (1.0 - step)
            return True
        return False
        
    # --- Class Upgrades (Lobby) ---
    def upgrade_class_damage(self, t, *, step=0.10, cost=50):
        self.ensure_type(t)
        if self.spend(cost):
            self.class_damage_mult[t] *= (1.0 + step)
            return True
        return False

    def upgrade_class_fire_rate(self, t, *, step=0.05, cost=50):
        self.ensure_type(t)
        if self.spend(cost):
            # Reduces delay, so multiplier < 1.0
            self.class_fire_rate_mult[t] *= (1.0 - step)
            return True
        return False

    def upgrade_class_crit_rate(self, t, *, step=0.05, cost=50):
        self.ensure_type(t)
        self.class_crit_rate.setdefault(t, 0.0)
        if self.class_crit_rate[t] >= 0.50: # Cap at 50%
            return False
        if self.spend(cost):
            self.class_crit_rate[t] += step
            return True
        return False

    def get_crit_rate(self, t):
        self.ensure_type(t)
        return self.class_crit_rate.get(t, 0.0)
