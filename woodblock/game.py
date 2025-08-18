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
        This method handles the game state updates and events.

        Raises:
            QuitGameException: If the game is requested to quit.

        """

        events = pygame.event.get()
        self.state_manager.current_state.update(self, events)

    def render(self):
        """Render the game state.

        """

        self.state_manager.current_state.render(self.screen)

    def run(self):
        """Run the main game loop at 60 frames per second.
        Handles the game state updates and rendering.
        Handles quitting the game when a QuitGameException is raised.
        The game loop will also handle any exceptions that occur during the game.

        """

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
