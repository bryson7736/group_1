from .BehaviorBase import Behavior

class BasicAttack(Behavior):
    def decide(self, metrics):
        if metrics.merge_rate > 2 and Disrupt.ready():
            return Disrupt()
        if AOEAttack.ready():
            return AOEAttack()
        return self

    def enter(self, executor):
        executor.cast("BasicAttack", duration=4.0)

    @staticmethod
    def ready():
        return True # Placeholder for actual cooldown check

class AOEAttack(Behavior):
    def decide(self, metrics):
        return BasicAttack()

    def enter(self, executor):
        executor.cast("AOEAttack", duration=4.0)

    @staticmethod
    def ready():
        return True 

class Disrupt(Behavior):
    def decide(self, metrics):
        return BasicAttack()

    def enter(self, executor):
        executor.cast("Disrupt", duration=4.0)

    @staticmethod
    def ready():
        return True
