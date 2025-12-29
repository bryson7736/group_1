import time
from .metrics.PlayerMetrics import PlayerMetrics
from .fsm.StrategyFSM import StrategyFSM
from .fsm.BehaviorFSM import BehaviorFSM
from .action.SkillExecutor import SkillExecutor

class BossAIController:
    def __init__(self, boss, game):
        self.boss = boss
        self.game = game
        self.metrics = PlayerMetrics()
        self.strategy_fsm = StrategyFSM()
        self.behavior_fsm = BehaviorFSM()
        self.executor = SkillExecutor(boss, game)
        
        # Initial setup
        self.behavior_fsm.reset(self.strategy_fsm.current)

    def update(self, dt):
        # 1. Update Metrics
        game_state = {
            'dice_count': self._get_player_dice_count(),
            'boss_hp_pct': self.boss.hp / self.boss.max_hp if self.boss.max_hp > 0 else 1.0
        }
        self.metrics.update(dt, game_state)

        # 2. Update Strategy (Low Frequency - could optimize with timer)
        prev_strategy = self.strategy_fsm.current
        self.strategy_fsm.update(self.metrics, dt)

        # 3. Handle Strategy Change
        if type(self.strategy_fsm.current) != type(prev_strategy):
            self.behavior_fsm.reset(self.strategy_fsm.current)
            self.executor.cancel_current_skill()

        # 4. Update Behavior
        self.behavior_fsm.update(self.metrics, self.executor)

        # 5. Update Executor
        self.executor.update(dt)
        
        # Logging Debug info (Throttled)
        if not hasattr(self, '_last_log_time'): self._last_log_time = 0
        if time.time() - self._last_log_time > 1.0:
            print(f"[BossAI] Strategy: {self.strategy_fsm.current} | Behavior: {self.behavior_fsm.current} | Threat: {self.metrics.threat_score:.2f}")
            self._last_log_time = time.time()

    def _get_player_dice_count(self):
        if not self.game or not self.game.grid:
            return 0
        count = 0
        for c in range(self.game.grid.cols):
            for r in range(self.game.grid.rows):
                if self.game.grid.get(c, r):
                    count += 1
        return count

    def record_damage(self, amount):
        self.metrics.record_damage(amount)

    def record_merge(self):
        self.metrics.record_merge()
