import time
from collections import deque

class SlidingWindow:
    def __init__(self, duration_s):
        self.duration = duration_s
        self.data = deque() # (timestamp, value)

    def add(self, value):
        now = time.time()
        self.data.append((now, value))
        self._cleanup(now)

    def _cleanup(self, now):
        while self.data and now - self.data[0][0] > self.duration:
            self.data.popleft()

    def average(self):
        self._cleanup(time.time())
        if not self.data:
            return 0
        total = sum(v for t, v in self.data)
        return total / self.duration

    def count(self):
        self._cleanup(time.time())
        return len(self.data)

class PlayerMetrics:
    def __init__(self):
        self.damage_window = SlidingWindow(5.0)
        self.merge_window = SlidingWindow(5.0)
        
        self.damage_rate = 0.0
        self.merge_rate = 0.0
        self.dice_count = 0
        self.boss_hp_pct = 1.0
        
        self.threat_score = 0.0

    def record_damage(self, amount):
        self.damage_window.add(amount)

    def record_merge(self):
        self.merge_window.add(1)

    def update(self, dt, game_state):
        """
        game_state should contain:
        - dice_count: total number of dice on player grid
        - boss_hp_pct: boss current hp / max hp
        """
        self.damage_rate = self.damage_window.average()
        self.merge_rate = self.merge_window.count()
        self.dice_count = game_state.get('dice_count', 0)
        self.boss_hp_pct = game_state.get('boss_hp_pct', 1.0)

        # Normalize metrics for threat score (rough normalization)
        # Assuming damage_rate of 500/s is "high" (normalized to 1.0)
        # Assuming merge_rate of 3/5s is "high" (normalized to 1.0)
        # Assuming dice_count of 15 is "high" (normalized to 1.0)
        
        norm_damage = min(1.0, self.damage_rate / 500.0)
        norm_merge = min(1.0, self.merge_rate / 3.0)
        norm_dice = min(1.0, self.dice_count / 15.0)

        self.threat_score = (
            norm_damage * 0.6 +
            norm_merge * 0.3 +
            norm_dice * 0.1
        )
