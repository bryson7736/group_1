# -*- coding: utf-8 -*-
"""
In-Game Upgrade System
Players can spend money during gameplay to upgrade specific dice types.
"""

class InGameUpgrades:
    """Manages in-game upgrades purchased with money during a run."""
    
    # Cost progression for each upgrade level (Level 1 -> 2, etc.)
    UPGRADE_COSTS = {
        1: 100,
        2: 200,
        3: 400,
        4: 700,
        5: 0 # Max level
    }
    
    MAX_LEVEL = 5
    
    def __init__(self):
        """Initialize upgrades."""
        # Dictionary to track level of each dice type: {'single': 1, 'fire': 1, ...}
        self.levels = {}
    
    def reset(self):
        """Reset all upgrades to level 1 (for new game)."""
        self.levels = {}
    
    def get_level(self, die_type: str) -> int:
        """Get current level of specified dice type (default 1)."""
        return self.levels.get(die_type, 1)
    
    def get_upgrade_cost(self, die_type: str) -> int:
        """Get cost for next level of specified dice type."""
        current_level = self.get_level(die_type)
        if current_level >= self.MAX_LEVEL:
            return 0
        return self.UPGRADE_COSTS.get(current_level, 0)
    
    def can_upgrade(self, die_type: str) -> bool:
        """Check if upgrade is available."""
        current_level = self.get_level(die_type)
        return current_level < self.MAX_LEVEL
    
    def purchase_upgrade(self, die_type: str, current_money: int) -> tuple:
        """
        Attempt to purchase an upgrade.
        Returns (success: bool, new_money: int, message: str)
        """
        current_level = self.get_level(die_type)
        
        if current_level >= self.MAX_LEVEL:
            return (False, current_money, f"{die_type} MAX!")
        
        cost = self.get_upgrade_cost(die_type)
        if current_money < cost:
            return (False, current_money, f"Need ${cost}")
        
        # Purchase
        self.levels[die_type] = current_level + 1
        return (True, current_money - cost, f"{die_type} Lv{current_level + 1}!")
