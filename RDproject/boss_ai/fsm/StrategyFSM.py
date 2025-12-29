from .FSMBase import FSMBase
from ..strategy.ConcreteStrategies import IdleStrategy

class StrategyFSM(FSMBase):
    def __init__(self):
        super().__init__()
        self.current_strategy = IdleStrategy()
        self.state_time = 0.0
        self.min_state_duration = 2.0 # Minimum time to stay in a strategy

    def update(self, metrics, dt):
        self.state_time += dt
        
        if self.state_time < self.min_state_duration:
            return

        next_strategy = self.current_strategy.decide(metrics)
        
        if type(next_strategy) != type(self.current_strategy):
            print(f"[BossAI] Strategy Switch: {self.current_strategy} -> {next_strategy}")
            self.current_strategy = next_strategy
            self.state_time = 0.0

    @property
    def current(self):
        return self.current_strategy
