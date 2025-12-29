from .StrategyBase import Strategy

class IdleStrategy(Strategy):
    def decide(self, metrics):
        if metrics.boss_hp_pct < 0.3:
            return RecoveryStrategy()
        if metrics.threat_score > 0.7:
            return DefensiveStrategy()
        if metrics.threat_score > 0.4:
            return AggressiveStrategy()
        return self

    def default_behavior(self):
        from ..behavior.BasicBehaviors import IdleBehavior
        return IdleBehavior()

class AggressiveStrategy(Strategy):
    def decide(self, metrics):
        if metrics.boss_hp_pct < 0.3:
            return RecoveryStrategy()
        if metrics.threat_score > 0.8:
            return DefensiveStrategy()
        if metrics.threat_score < 0.2:
            return IdleStrategy()
        return self

    def default_behavior(self):
        from ..behavior.AggressiveBehaviors import BasicAttack
        return BasicAttack()

class DefensiveStrategy(Strategy):
    def decide(self, metrics):
        if metrics.boss_hp_pct < 0.2:
            return RecoveryStrategy()
        if metrics.threat_score < 0.5:
            return AggressiveStrategy()
        return self

    def default_behavior(self):
        from ..behavior.DefensiveBehaviors import Shield
        return Shield()

class RecoveryStrategy(Strategy):
    def decide(self, metrics):
        if metrics.boss_hp_pct > 0.5:
            return DefensiveStrategy()
        return self

    def default_behavior(self):
        from ..behavior.RecoveryBehaviors import HealSelf
        return HealSelf()
