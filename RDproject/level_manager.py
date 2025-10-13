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
                    (1280, 125),  # 右上角 (4,0)
                    (500, 125),  # 右下角 (4,2)
                    (500, 700),
                    (1280, 700)   # 左下角 (0,2)
                ],
                1.0
            ),
            Level("Tundra", [(100, 360), (480, 360), (480, 120), (1180, 120)], 1.2),
            Level("Lava",   [(100, 520), (520, 520), (520, 200), (1180, 200)], 1.4),
        ]

    def get(self, idx):
        idx = max(0, min(len(self.levels) - 1, idx))
        return self.levels[idx]

    def wave_info(self, wave_idx):
        base = WAVE_BASE_COUNT + wave_idx * (WAVE_GROWTH // 2)  # clarified precedence
        is_boss = (wave_idx > 0 and wave_idx % 5 == 0)
        return base, is_boss
