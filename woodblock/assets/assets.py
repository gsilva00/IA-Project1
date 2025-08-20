from __future__ import annotations

from typing import ClassVar

import pygame

from woodblock.game_logic.constants import FontConfig, ImageConfig


class Assets:
    """Class to manage game assets such as images, fonts, and sounds.

    This class is responsible for loading and providing access to all game assets.

    Singleton pattern is used to ensure that only one instance of this class exists.

    Needed due to the global nature of game assets and the need for consistent access across different parts of the game,
    to avoid duplication of function parameters and arguments, asset loading and management logic.
    While needing pygame to be initialized before loading some assets.
    """

    # TODO: Careful about the use of singleton pattern

    initialized: ClassVar[bool] = False
    backgrounds: ClassVar[dict[str, pygame.Surface]] = {}
    icons: ClassVar[dict[str, pygame.Surface]] = {}
    fonts: ClassVar[dict[str, pygame.font.Font]] = {}
    blocks: ClassVar[dict[str, pygame.Surface]] = {}

    @classmethod
    def load(cls) -> None:
        """Load all game assets."""
        if cls.initialized:
            return
        cls.backgrounds = {
            "menu": pygame.image.load(ImageConfig.BACKGROUND_MENU),
            "game": pygame.image.load(ImageConfig.BACKGROUND_GAME),
        }
        cls.icons = {
            "menu_game": pygame.image.load(ImageConfig.MENU_GAME_ICON),
            "hint": pygame.image.load(ImageConfig.HINT_ICON).convert_alpha(),
        }
        cls.fonts = {
            "title": pygame.font.Font(FontConfig.PATH, FontConfig.TITLE_SIZE),
            "subtitle": pygame.font.Font(FontConfig.PATH, FontConfig.TEXT_SIZE),
            "text": pygame.font.Font(FontConfig.PATH, FontConfig.TEXT_SMALL_SIZE),
            "hint": pygame.font.Font(FontConfig.PATH, FontConfig.HINT_SIZE),
        }
        cls.blocks = {
            "block": pygame.image.load(ImageConfig.WOOD),
            "selected": pygame.image.load(ImageConfig.LIGHT_WOOD),
            "player": pygame.image.load(ImageConfig.DARK_WOOD),
            "target": pygame.image.load(ImageConfig.RED_WOOD),
        }
        cls.initialized = True
