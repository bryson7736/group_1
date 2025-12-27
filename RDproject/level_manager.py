# -*- coding: utf-8 -*-
from settings import WAVE_BASE_COUNT, WAVE_GROWTH
class Level:
    def __init__(self, name, path_points, difficulty=1.0, path_color=(80, 85, 100), bg_type=None): # Default GRAY from colors.py
        self.name = name
        self.path = list(path_points)
        self.difficulty = float(difficulty)
        self.path_color = path_color
        self.bg_type = bg_type

class LevelManager:
    def __init__(self):
        self.levels = [
            Level("Infinite: Space",
                [
                    (1280, 125),  # Top Right
                    (500, 125),   # Top Left-ish
                    (500, 650),   # Bottom Left-ish
                    (1280, 650)   # Bottom Right
                ],
                1.0,
                path_color=(100, 120, 255),
                bg_type="space"
            ),
        ]

    def get(self, idx):
        idx = max(0, min(len(self.levels) - 1, idx))
        return self.levels[idx]

    def wave_info(self, wave_idx):
        base = WAVE_BASE_COUNT + wave_idx * WAVE_GROWTH
        is_boss = (wave_idx > 0 and wave_idx % 5 == 0)
        true_boss = (wave_idx > 0 and wave_idx % 10 == 0)
        return base, is_boss, true_boss
