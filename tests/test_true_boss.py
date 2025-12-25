
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
    # Force all cooldowns ready (shared cooldown)
    boss.timers[STATE_DEFENSE] = 0
    boss.timers[STATE_HEAL] = 0
    boss.timers[STATE_ATTACK] = 0
    
    # Force defense by ensuring HP is full (so heal won't trigger)
    boss.hp = boss.max_hp
    # Seed random to get defense
    import random
    random.seed(0)
    
    boss.update(0.1)
    # With seeded random, check if state changed from idle
    # If not defense, try again with different seed
    if boss.state != STATE_DEFENSE:
        boss.state = STATE_IDLE
        boss.timers[STATE_DEFENSE] = 0
        boss.timers[STATE_HEAL] = 0
        boss.timers[STATE_ATTACK] = 0
        random.seed(1)
        boss.update(0.1)
    
    # Directly force defense state for deterministic testing
    boss.state = STATE_DEFENSE
    boss.state_timer = 3.0  # Defense duration
    
    # Check damage reduction
    boss.hit(100)
    assert boss.hp == 1000 - 50 # 50% reduction

def test_true_boss_heal(boss):
    boss.hp = 500 # Injured (< 80% of max, will trigger heal)
    # All timers must be 0 for shared cooldown
    boss.timers[STATE_HEAL] = 0
    boss.timers[STATE_DEFENSE] = 0
    boss.timers[STATE_ATTACK] = 0
    
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
    
    # All timers must be 0 for shared cooldown
    boss.timers[STATE_ATTACK] = 0
    boss.timers[STATE_DEFENSE] = 0
    boss.timers[STATE_HEAL] = 0
    
    # Force attack state directly for deterministic testing
    boss.state = STATE_ATTACK
    boss.state_timer = 1.0  # Attack duration
    boss.update(0.1)
    assert boss.state == STATE_ATTACK
    
    # Wait for cast duration (1.0s)
    boss.state_timer = 0
    boss.update(0.1)
    
    # Should be back to IDLE
    assert boss.state == STATE_IDLE
    # Dice should be gone
    assert (2, 1) not in boss.game.grid.cells
