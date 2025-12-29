from .BehaviorBase import Behavior

class Shield(Behavior):
    def decide(self, metrics):
        if metrics.threat_score < 0.6:
            from .AggressiveBehaviors import BasicAttack
            return BasicAttack()
        return self

    def enter(self, executor):
        executor.cast("Shield", duration=3.0)

class DamageReduction(Behavior):
    def decide(self, metrics):
        return self

    def enter(self, executor):
        executor.cast("DamageReduction", duration=5.0)
