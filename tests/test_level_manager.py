import pytest
from level_manager import LevelManager, Level
from settings import WAVE_BASE_COUNT, WAVE_GROWTH

def test_level_manager_init():
    lm = LevelManager()
    assert len(lm.levels) > 0
    assert isinstance(lm.levels[0], Level)

def test_level_manager_get():
    lm = LevelManager()
    l0 = lm.get(0)
    assert l0.name == "Meadow"
    
    # Test bounds clamping
    ln = lm.get(999)
    assert ln == lm.levels[-1]

def test_wave_info():
    lm = LevelManager()
    
    # Wave 0
    base, is_boss = lm.wave_info(0)
    assert base == WAVE_BASE_COUNT
    assert is_boss is False
    
    # Wave 1
    base_1, is_boss_1 = lm.wave_info(1)
    assert base_1 == WAVE_BASE_COUNT + (WAVE_GROWTH // 2)
    assert is_boss_1 is False
    
    # Wave 5 (Boss wave logic check: >0 and %5==0)
    _, is_boss_5 = lm.wave_info(5)
    assert is_boss_5 is True
