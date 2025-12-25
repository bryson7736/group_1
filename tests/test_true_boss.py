
import pytest
from boss import TrueBoss, STATE_IDLE, STATE_DEFENSE, STATE_ATTACK, STATE_HEAL

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
    # Force defense ready
    boss.timers[STATE_DEFENSE] = 0
    boss.timers[STATE_HEAL] = 10 
    boss.timers[STATE_ATTACK] = 10
    
    boss.update(0.1)
    assert boss.state == STATE_DEFENSE
    
    # Check damage reduction
    boss.hit(100)
    assert boss.hp == 1000 - 50 # 50% reduction

def test_true_boss_heal(boss):
    boss.hp = 500 # Injured
    boss.timers[STATE_HEAL] = 0
    boss.timers[STATE_DEFENSE] = 10
    boss.timers[STATE_ATTACK] = 10
    
    boss.update(0.1)
    assert boss.state == STATE_HEAL
    
    # Update again to trigger one tick of healing
    boss.update(0.1)
    
    # Check healing occurred
    # rate is 5% of 1000 = 50 per sec
    # dt = 0.1 -> +5 HP
    expected = 500 + 5
    assert abs(boss.hp - expected) < 0.1

def test_true_boss_attack(boss):
    boss.game.grid.cells[(2, 1)] = "Dice"
    
    boss.timers[STATE_ATTACK] = 0
    boss.timers[STATE_DEFENSE] = 10
    boss.timers[STATE_HEAL] = 10
    
    # Enter attack state
    boss.update(0.1)
    assert boss.state == STATE_ATTACK
    
    # Wait for cast duration (1.0s)
    boss.state_timer = 0
    boss.update(0.1)
    
    # Should be back to IDLE
    assert boss.state == STATE_IDLE
    # Dice should be gone
    assert (2, 1) not in boss.game.grid.cells
