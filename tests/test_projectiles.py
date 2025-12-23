import pytest
from projectiles import Bullet, ExplosiveBullet
import math

class MockEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100
        self.dead = False
        
    def hit(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True

class MockGame:
    def __init__(self, enemies):
        self.enemies = enemies

def test_bullet_hit():
    target = MockEnemy(100, 0)
    # Target is at 100, 0. Bullet at 0, 0. Speed 200.
    # Time 0.5s -> travels 100. Should hit.
    bullet = Bullet(None, 0, 0, target, dmg=10)
    bullet.base_speed = 200
    
    hit = bullet.update(0.5)
    
    assert hit is True
    assert target.hp == 90
    assert bullet.x == 100
    assert bullet.y == 0

def test_bullet_travel():
    target = MockEnemy(200, 0)
    bullet = Bullet(None, 0, 0, target, dmg=10)
    bullet.base_speed = 100
    
    # 0.5s -> 50 units
    hit = bullet.update(0.5)
    
    assert hit is False
    assert target.hp == 100
    assert bullet.x == 50
    assert bullet.y == 0

def test_explosive_bullet():
    target = MockEnemy(100, 0)
    nearby_enemy = MockEnemy(105, 0) # Distance 5
    far_enemy = MockEnemy(200, 0)    # Far away
    
    game = MockGame([target, nearby_enemy, far_enemy])
    
    bullet = ExplosiveBullet(
        game, 0, 0, target, 
        dmg=10, splash_dmg=5, splash_radius=20
    )
    bullet.base_speed = 200
    
    # Hit target
    bullet.update(0.5)
    
    assert target.hp == 90
    assert nearby_enemy.hp == 95 # Took splash
    assert far_enemy.hp == 100   # Too far
