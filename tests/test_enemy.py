import pytest
from enemy import Enemy

@pytest.fixture
def basic_enemy():
    # Simple straight line path
    path = [(0, 0), (100, 0)]
    return Enemy(path, hp=100, speed=10)

def test_enemy_initialization(basic_enemy):
    assert basic_enemy.hp == 100
    assert basic_enemy.max_hp == 100
    assert basic_enemy.speed == 10
    assert basic_enemy.dead is False
    assert basic_enemy.x == 0
    assert basic_enemy.y == 0

def test_enemy_hit(basic_enemy):
    basic_enemy.hit(10)
    assert basic_enemy.hp == 90
    assert basic_enemy.dead is False
    
    basic_enemy.hit(90)
    assert basic_enemy.hp <= 0
    assert basic_enemy.dead is True

def test_enemy_poison(basic_enemy):
    basic_enemy.apply_poison(dmg=10, duration=1.0)
    assert basic_enemy.poison_dmg == 10
    assert basic_enemy.poison_timer == 1.0
    
    # Simulate update
    dt = 0.5
    basic_enemy.update(dt)
    
    # Should have taken damage: 10 * 0.5 = 5
    assert basic_enemy.hp == 95
    assert basic_enemy.poison_timer == 0.5

def test_enemy_slow(basic_enemy):
    basic_enemy.apply_slow(ratio=0.5, duration=1.0)
    assert basic_enemy.slow_ratio == 0.5
    assert basic_enemy.slow_timer == 1.0
    
    # Movement update
    # Distance to travel: speed * slow * dt = 10 * 0.5 * 0.5 = 2.5
    dt = 0.5
    basic_enemy.update(dt)
    
    assert basic_enemy.x == 2.5
    assert basic_enemy.slow_timer == 0.5
    
    # Update again to expire it
    basic_enemy.update(0.5)
    assert basic_enemy.x == 2.5 + (10 * 1.0 * 0.5) # Now full speed (5.0) -> total 7.5
    assert basic_enemy.slow_timer == 0.0
    assert basic_enemy.slow_ratio == 1.0
