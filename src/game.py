import sys

import pygame

from states import GameStateManager, MainMenuState
from utils.misc import QuitGameException


class Game:
    """Main game class.

    """

    def __init__(self):
        self.screen = pygame.display.set_mode((800, 700))
        self.clock = pygame.time.Clock()
        self.state_manager = GameStateManager(self.screen)
        self.state_manager.switch_to_base_state(MainMenuState())

    def update(self):
        """Update the game state.

        """

        events = pygame.event.get()
        self.state_manager.current_state.update(self, events)

    def render(self):
        """Render the game state.

        """

        self.state_manager.current_state.render(self.screen)

    def run(self):
        try:
            while True:
                self.update()
                self.render()
                self.clock.tick(60)
        except QuitGameException:
            print("=== Quitting game... ===")
            self.state_manager.clear_states()
            pygame.quit()
            sys.exit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.state_manager.clear_states()
            pygame.quit()
            sys.exit()
