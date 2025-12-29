class BehaviorFSM:
    def __init__(self):
        self.current_behavior = None

    def reset(self, strategy):
        self.current_behavior = strategy.default_behavior()
        print(f"[BossAI] Behavior Reset to: {self.current_behavior}")

    def update(self, metrics, executor):
        if not self.current_behavior:
            return

        if not executor.is_busy():
            next_behavior = self.current_behavior.decide(metrics)
            if type(next_behavior) != type(self.current_behavior):
                print(f"[BossAI] Behavior Switch: {self.current_behavior} -> {next_behavior}")
                self.current_behavior = next_behavior
                self.current_behavior.enter(executor)
            else:
                # If no transition, re-enter current if executor is free?
                # Actually, behavior should probably only enter once and then wait for next decision
                # or have a loop. For now, if executor is free and no change, re-enter current basic attack.
                self.current_behavior.enter(executor)

    @property
    def current(self):
        return self.current_behavior
