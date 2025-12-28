import pytest
from projectiles import Bullet, ExplosiveBullet
import math

class MockSoundMgr:
    def play(self, name):
        pass

class MockEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 100
        self.dead = False
        self.damage_history = []
        
    def hit(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True
            
    def apply_poison(self, dmg, duration):
        pass
        
    def apply_slow(self, ratio, duration):
        pass

class MockGame:
    def __init__(self, enemies=None):
        self.enemies = enemies or []
        self.sound_mgr = MockSoundMgr()

def test_bullet_hit():
    target = MockEnemy(100, 0)
    game = MockGame([target])
    # Target is at 100, 0. Bullet at 0, 0. Speed 200.
    # Time 0.5s -> travels 100. Should hit.
    bullet = Bullet(game, 0, 0, target, dmg=10)
    bullet.base_speed = 200
    
    hit = bullet.update(0.5)
    
    assert hit is True
    assert target.hp == 90
    assert bullet.x == 100
    assert bullet.y == 0

def test_bullet_travel():
    target = MockEnemy(200, 0)
    game = MockGame([target])
    bullet = Bullet(game, 0, 0, target, dmg=10)
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
