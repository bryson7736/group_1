from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def decide(self, metrics):
        """Decide next strategy."""
        pass

    @abstractmethod
    def default_behavior(self):
        """Return the default behavior for this strategy."""
        pass

    def __repr__(self):
        return self.__class__.__name__
