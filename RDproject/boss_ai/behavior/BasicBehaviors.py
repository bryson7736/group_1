from .BehaviorBase import Behavior

class IdleBehavior(Behavior):
    def decide(self, metrics):
        return self

    def enter(self, executor):
        executor.cast("Idle", duration=0.5)
