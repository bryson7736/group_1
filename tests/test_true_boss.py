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
    # Initial state should be mapped to "idle"
    assert boss.state == STATE_IDLE
    # Metrics should be empty
    assert boss.ai_controller.metrics.damage_window.average() == 0

def test_true_boss_defense(boss):
    # Force the boss into a defensive skill
    boss.ai_controller.executor.cast("Shield", duration=3.0)
    assert boss.state == STATE_DEFENSE
    
    # Check damage reduction
    boss.hit(100)
    assert boss.hp == 1000 - 50 # 50% reduction from DEFENSE_DAMAGE_REDUCTION

def test_true_boss_heal(boss):
    # Setup condition for Heal (Low HP)
    boss.hp = 300 
    boss.ai_controller.metrics.boss_hp_pct = 0.3
    
    # Update AI but ignore if it casted anything (like Idle)
    boss.ai_controller.update(0.1)
    boss.ai_controller.executor.cancel_current_skill()
    boss.ai_controller.executor.cooldown_timer = 0 # Also reset GCD
    
    # Manually forcing a cast for reliable testing of state mapping and effect
    boss.ai_controller.executor.cast("Heal", duration=3.0)
    assert boss.state == STATE_HEAL
    
    # Test apply effect
    boss.apply_skill_effect("Heal")
    assert boss.hp > 300

def test_true_boss_attack(boss):
    # Setup grid targets
    boss.game.grid.cells[(2, 1)] = "Dice"
    
    # Cast attack
    boss.ai_controller.executor.cast("BasicAttack", duration=4.0)
    assert boss.state == STATE_ATTACK
    
    # Verify target selection from bridge
    assert len(boss.attack_targets) > 0
    
    # Force effect application
    boss.apply_skill_effect("BasicAttack")
    
    # Should remove something (MockGrid logic)
    assert (2, 1) not in boss.game.grid.cells
