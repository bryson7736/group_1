# -*- coding: utf-8 -*-
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Global settings
SCREEN_W, SCREEN_H = 1280, 768
FPS = 60

# Grid
GRID_COLS, GRID_ROWS = 5, 3
CELL_SIZE = 140
GRID_X = 575
GRID_Y = 175

PANEL_W = 360

# Economy & base
DIE_COST = 10
MERGE_REFUND = 3
START_MONEY = 100
BASE_HP = 10
MAX_DIE_LEVEL = 7

# Dice balance
BASE_RANGE = 1000  # Increased from 200 for better coverage
BASE_FIRE_RATE = 50  # smaller = faster (frame-equivalent ticks)
FIRE_RATE_STEP = 4

# Enemies
ENEMY_SIZE = 30
WAVE_BASE_COUNT = 25
WAVE_GROWTH = 1

# Big Enemy
BIG_ENEMY_HP_MULT = 6.0
BIG_ENEMY_SPAWN_WAVE = 5           # every Nth wave is a big enemy wave
BIG_ENEMY_TELEGRAPH_WARN = 1.0     # seconds warning before ability
BIG_ENEMY_DEBUFF_DURATION = 3.0    # seconds slow/debuff duration
BIG_ENEMY_DESTROY_RADIUS = 1       # tiles Manhattan radius (1 = 3x3)
BIG_ENEMY_ZONE_SLOW_ENEMY = 0.6    # enemies speed multiplier inside zone
BIG_ENEMY_ZONE_SLOW_DICE = 1.2     # dice fire period multiplier (>1 = slower)

# Projectiles
BULLET_SPEED = 660.0
CHAIN_MAX_DISTANCE = 220      # Multi chain max distance

# Slow effect (Freeze dice)
FREEZE_SLOW_RATIO = 0.65      # 35% slow (higher value = less slow)
FREEZE_DURATION = 2.0

# UI
TITLE = "Random Dice Tower Defense v2.3a (RDpro7a)"

# Game speed presets (affects enemy move, fire rate, and projectile motion)
GAME_SPEEDS = [0.5, 1.0, 2.0, 4.0, 8.0]
DEFAULT_SPEED_INDEX = 1

# Asset files (optional, looked up in assets/)
ASSET_FILES = {
    "trash": "trash.png",
    "dice": {
        "single": "dice_single.png",
        "multi": "dice_multi.png",
        "freeze": "dice_freeze.png",
        "wind": "dice_wind.png",
        "poison": "dice_poison.png",
        "iron": "dice_iron.png",
        "fire": "dice_fire.png"
    }
}
