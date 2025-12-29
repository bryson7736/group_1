from abc import ABC, abstractmethod

class Behavior(ABC):
    @abstractmethod
    def decide(self, metrics):
        """Decide next behavior."""
        pass

    @abstractmethod
    def enter(self, executor):
        """Called when entering this behavior."""
        pass

    def update(self, dt):
        """Optional update logic."""
        pass

    def __repr__(self):
        return self.__class__.__name__
