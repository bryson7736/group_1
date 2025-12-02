# -*- coding: utf-8 -*-
from settings import WAVE_BASE_COUNT, WAVE_GROWTH
class Level:
    def __init__(self, name, path_points, difficulty=1.0):
        self.name = name
        self.path = list(path_points)
        self.difficulty = float(difficulty)

class LevelManager:
    def __init__(self):
        self.levels = [
            Level("Meadow",
                [
                    (1280, 125),  # Top Right
                    (500, 125),   # Top Left-ish
                    (500, 650),   # Bottom Left-ish
                    (1280, 650)   # Bottom Right
                ],
                1.0
            ),
            Level("Tundra", 
                [
                    (100, 100),   # Start Top-Left (Left of grid)
                    (100, 650),   # Down (Left of grid)
                    (1200, 650)   # Right (Below grid)
                ], 
                1.2
            ),
            Level("Story Mode",   
                [
                    (1200, 80),   # Start Top-Right (Above grid)
                    (100, 80),    # Left (Above grid)
                    (100, 650),   # Down (Left of grid)
                    (600, 650)    # Right (Below grid)
                ], 
                1.4
            ),
        ]

    def get(self, idx):
        idx = max(0, min(len(self.levels) - 1, idx))
        return self.levels[idx]

    def wave_info(self, wave_idx):
        base = WAVE_BASE_COUNT + wave_idx * (WAVE_GROWTH // 2)  # clarified precedence
        is_boss = (wave_idx > 0 and wave_idx % 5 == 0)
        return base, is_boss
