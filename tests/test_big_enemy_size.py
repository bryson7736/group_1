
import pytest
from enemy import Enemy, BigEnemy
from settings import ENEMY_SIZE

@pytest.fixture
def basic_path():
    return [(0, 0), (100, 0)]

def test_enemy_default_size(basic_path):
    e = Enemy(basic_path, hp=100, speed=10)
    assert e.size == ENEMY_SIZE

def test_big_enemy_larger_size(basic_path):
    b = BigEnemy(basic_path, hp=1000, speed=10)
    assert b.size == ENEMY_SIZE * 3
    assert b.size > ENEMY_SIZE
