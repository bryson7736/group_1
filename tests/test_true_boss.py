import pytest
import random
from boss import TrueBoss, STATE_IDLE, STATE_DEFENSE, STATE_ATTACK, STATE_HEAL

class MockSoundMgr:
    def play(self, name):
        pass

class MockGrid:
    def __init__(self):
        self.cols = 5
        self.rows = 3
        self.cells = {}
    
    def get(self, c, r):
        return self.cells.get((c, r))
    
    def remove(self, c, r):
        if (c, r) in self.cells:
            del self.cells[(c, r)]
            
class MockGame:
    def __init__(self):
        self.grid = MockGrid()
        self.sound_mgr = MockSoundMgr()

@pytest.fixture
def boss():
    game = MockGame()
    path = [(0, 0), (100, 0)]
    return TrueBoss(path, hp=1000, speed=10, game=game)

def test_true_boss_initial_state(boss):
    assert boss.state == STATE_IDLE
    # Check timers are initialized (not zero)
    assert boss.timers[STATE_DEFENSE] > 0
    assert boss.timers[STATE_ATTACK] > 0
    assert boss.timers[STATE_HEAL] > 0

def test_true_boss_defense(boss):
    # Force all cooldowns ready
    for s in boss.timers:
        boss.timers[s] = 0
    
    # Force defense state for deterministic testing
    boss.state = STATE_DEFENSE
    boss.state_timer = 3.0
    
    # Check damage reduction
    boss.hit(100)
    assert boss.hp == 1000 - 50 # 50% reduction

def test_true_boss_heal(boss):
    boss.hp = 400 # Injured
    for s in boss.timers:
        boss.timers[s] = 0
    
    boss.update(0.1)
    assert boss.state == STATE_HEAL
    
    # Base healing rate is 5% of max HP (50) per sec
    # dt=0.1 -> +5 HP
    boss.update(0.1)
    assert boss.hp > 400

def test_true_boss_attack(boss):
    # Clear and setup grid
    boss.game.grid.cells = {(2, 1): "Dice"}
    
    # Reset cooldowns
    for s in boss.timers:
        boss.timers[s] = 0
    
    # Force attack state
    boss.state = STATE_ATTACK
    boss.state_timer = 0 # Force execution on next update
    
    # Initial state check
    assert (2, 1) in boss.game.grid.cells
    
    # Trigger cast - state_timer is 0, so update should call _cast_attack immediately
    boss.update(0.1)
    
    # Should be back to IDLE and dice removed
    assert boss.state == STATE_IDLE
    assert (2, 1) not in boss.game.grid.cells
