# -*- coding: utf-8 -*-
"""
In-Game Upgrade System
Players can spend money during gameplay to upgrade global attributes.
"""

class InGameUpgrades:
    """Manages in-game upgrades purchased with money during a run."""
    
    # Cost progression for each upgrade level
    UPGRADE_COSTS = {
        1: 50,   # Level 1 -> 2
        2: 100,  # Level 2 -> 3
        3: 200,  # Level 3 -> 4
        4: 400,  # Level 4 -> 5
    }
    
    # Effect per level
    DAMAGE_PER_LEVEL = 0.20   # +20% per level
    FIRERATE_PER_LEVEL = 0.15  # +15% per level
    RANGE_PER_LEVEL = 0.15     # +15% per level
    
    MAX_LEVEL = 5
    
    def __init__(self):
        """Initialize all upgrades at level 1."""
        self.damage_level = 1
        self.firerate_level = 1
        self.range_level = 1
    
    def reset(self):
        """Reset all upgrades to level 1 (for new game)."""
        self.damage_level = 1
        self.firerate_level = 1
        self.range_level = 1
    
    def get_damage_multiplier(self) -> float:
        """Get the current damage multiplier."""
        return 1.0 + (self.damage_level - 1) * self.DAMAGE_PER_LEVEL
    
    def get_firerate_multiplier(self) -> float:
        """Get the current fire rate multiplier (higher = faster)."""
        # Fire rate multiplier affects period inversely
        # Level 1: 1.0, Level 2: 1.15, Level 3: 1.30, etc.
        return 1.0 + (self.firerate_level - 1) * self.FIRERATE_PER_LEVEL
    
    def get_range_multiplier(self) -> float:
        """Get the current range multiplier."""
        return 1.0 + (self.range_level - 1) * self.RANGE_PER_LEVEL
    
    def get_upgrade_cost(self, upgrade_type: str) -> int:
        """Get cost for next level of specified upgrade."""
        current_level = self._get_level(upgrade_type)
        if current_level >= self.MAX_LEVEL:
            return 0  # Max level, no more upgrades
        return self.UPGRADE_COSTS.get(current_level, 0)
    
    def can_upgrade(self, upgrade_type: str) -> bool:
        """Check if upgrade is available (not at max level)."""
        current_level = self._get_level(upgrade_type)
        return current_level < self.MAX_LEVEL
    
    def purchase_upgrade(self, upgrade_type: str, current_money: int) -> tuple:
        """
        Attempt to purchase an upgrade.
        Returns (success: bool, new_money: int, message: str)
        """
        current_level = self._get_level(upgrade_type)
        
        # Check if at max level
        if current_level >= self.MAX_LEVEL:
            return (False, current_money, f"{upgrade_type} is already at MAX level!")
        
        # Check cost
        cost = self.get_upgrade_cost(upgrade_type)
        if current_money < cost:
            return (False, current_money, f"Not enough money! Need ${cost}")
        
        # Purchase upgrade
        self._set_level(upgrade_type, current_level + 1)
        new_money = current_money - cost
        return (True, new_money, f"{upgrade_type} upgraded to Level {current_level + 1}!")
    
    def _get_level(self, upgrade_type: str) -> int:
        """Get current level of specified upgrade."""
        if upgrade_type == "damage":
            return self.damage_level
        elif upgrade_type == "firerate":
            return self.firerate_level
        elif upgrade_type == "range":
            return self.range_level
        return 1
    
    def _set_level(self, upgrade_type: str, level: int):
        """Set level of specified upgrade."""
        level = max(1, min(self.MAX_LEVEL, level))
        if upgrade_type == "damage":
            self.damage_level = level
        elif upgrade_type == "firerate":
            self.firerate_level = level
        elif upgrade_type == "range":
            self.range_level = level
