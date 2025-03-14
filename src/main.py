import pygame
import Game

from game_logic.constants import GAME_ICON_PATH


def main():
    pygame.init()
    pygame.display.set_caption("Wood Block")
    pygame.display.set_icon(pygame.image.load(GAME_ICON_PATH))

    game = Game()
    game.run()

if __name__ == "__main__":
    main()
