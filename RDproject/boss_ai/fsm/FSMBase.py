class FSMBase:
    """Base class for Finite State Machines."""
    def __init__(self):
        self.current_state = None

    def update(self, metrics, dt):
        if self.current_state:
            self.current_state.update(metrics, dt)

    def transition_to(self, next_state):
        if self.current_state:
            self.current_state.exit()
        self.current_state = next_state
        if self.current_state:
            self.current_state.enter()
