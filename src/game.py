import pygame

from states import GameStateManager, MainMenuState

class Game:
    """Main game class.
    """

    def __init__(self):
        self.state_manager = GameStateManager()
        self.state_manager.switch_to_base_state(MainMenuState())
        self.screen = pygame.display.set_mode((800, 700))
        self.clock = pygame.time.Clock()

    def update(self):
        """Update the game state.

        """

        events = pygame.event.get()
        self.state_manager.current_state.update(self, events)

    def render(self):
        """Render the game state.

        """

        self.state_manager.current_state.render(self)

    def run(self):
        while True:
            self.update()
            self.render()
            self.clock.tick(60)
