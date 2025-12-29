from .BehaviorBase import Behavior

class HealSelf(Behavior):
    def decide(self, metrics):
        if metrics.boss_hp_pct > 0.4:
            from .DefensiveBehaviors import Shield
            return Shield()
        return self

    def enter(self, executor):
        executor.cast("Heal", duration=3.0)

class SummonMinion(Behavior):
    def decide(self, metrics):
        return HealSelf()

    def enter(self, executor):
        executor.cast("SummonMinion", duration=1.0)
