class GameState:
    """ Base class for all game states
    """
    # Model stores the game state

    def enter(self, game):
        pass

    # Controller updates the game state
    def update(self, game, events):
        pass

    # View renders the game state
    def render(self, game):
        pass

    def exit(self, game):
        pass


class GameStateManager:
    """ Manages the game state stack
    """
    def __init__(self):
        self.state_stack = []

    def switch_to_base_state(self, new_state):
        while self.state_stack:
            self.state_stack.pop().exit(self)
        new_state.enter(self)
        self.state_stack = [new_state]

    def push_state(self, new_state):
        if self.current_state:
            self.current_state.exit(self)
        self.state_stack.append(new_state)
        print("Pushed state")
        new_state.enter(self)

    def pop_state(self):
        if self.current_state:
            self.state_stack.pop().exit(self)
            print("Popped state")
            if self.current_state:
                self.current_state.enter(self)
            return True
        return False

    @property
    def current_state(self):
        if self.state_stack:
            return self.state_stack[-1]
        return None
