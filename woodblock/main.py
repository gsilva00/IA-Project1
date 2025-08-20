from __future__ import annotations

import logging

import pygame

from woodblock.game import Game
from woodblock.game_logic.constants import ImageConfig


def main() -> None:
    """Initialize game and run it."""
    logging.basicConfig(level=logging.DEBUG)

    pygame.init()
    pygame.display.set_caption("Wood Block")
    pygame.display.set_icon(pygame.image.load(ImageConfig.APP_GAME_ICON))

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
