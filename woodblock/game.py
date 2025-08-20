from __future__ import annotations

import logging
import sys

import pygame

from woodblock.assets.assets import Assets
from woodblock.states import GameStateManager, MainMenuState
from woodblock.utils.misc import QuitGameException

LOGGER = logging.getLogger(__name__)


class Game:
    """Main game class."""

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((800, 700))
        self.clock = pygame.time.Clock()
        self.state_manager = GameStateManager()
        self.state_manager.switch_to_base_state(MainMenuState())

        Assets.load()

    def update(self) -> None:
        """Update the game state.

        This method handles the game state updates and events.

        Raises:
            QuitGameException: If the game is requested to quit.

        """
        current_state = self.state_manager.current_state
        events = pygame.event.get()
        if current_state is not None:
            current_state.update(self, events)

    def render(self) -> None:
        """Render the game state."""
        current_state = self.state_manager.current_state
        if current_state is not None:
            current_state.render(self.screen)

    def run(self) -> None:
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
            LOGGER.info("=== Quitting game... ===")
            self.state_manager.clear_states()
            pygame.quit()
            sys.exit()
        except Exception:
            LOGGER.exception("An error occurred.")
            self.state_manager.clear_states()
            pygame.quit()
            sys.exit()
