import pytest
from upgrades import UpgradeState

@pytest.fixture
def upgrades():
    return UpgradeState()

def test_initial_state(upgrades):
    assert upgrades.coins == 0
    assert upgrades.ingame_damage_mult == {}

def test_add_coin_and_spend(upgrades):
    upgrades.add_coin(100)
    assert upgrades.coins == 100
    
    success = upgrades.spend(50)
    assert success is True
    assert upgrades.coins == 50
    
    fail = upgrades.spend(60)
    assert fail is False
    assert upgrades.coins == 50

def test_ingame_upgrade(upgrades):
    upgrades.add_coin(200)
    
    # Test damage upgrade
    # Default cost 100
    t = "TestType"
    upgrades.upgrade_ingame_damage(t, step=0.1, cost=100)
    
    assert upgrades.coins == 100
    assert upgrades.ingame_damage_mult[t] == 1.1

    # Second upgrade
    upgrades.upgrade_ingame_damage(t, step=0.1, cost=100)
    # 1.1 * 1.1 = 1.21
    assert abs(upgrades.ingame_damage_mult[t] - 1.21) < 0.0001
    assert upgrades.coins == 0

def test_reset_ingame(upgrades):
    upgrades.add_coin(100)
    upgrades.upgrade_ingame_damage("Test", cost=100)
    
    assert upgrades.ingame_damage_mult["Test"] > 1.0
    
    upgrades.reset_ingame()
    assert upgrades.ingame_damage_mult == {}
    # Coins should persist? 
    # Based on code: coins are self.coins, reset_ingame only clears dicts.
    assert upgrades.coins == 0 # we spent them
