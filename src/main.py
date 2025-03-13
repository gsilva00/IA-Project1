import pygame
from game_model import GameModel
from gui.menu import draw_menu
from gui.game import draw_game, draw_game_over
from game_controller import GameController, handle_menu_events, handle_game_events, handle_game_over_events
from game_logic.constants import GAME_ICON_PATH


def play_game(screen, game_controller):
    while game_controller.state == 'play':
        draw_game(screen, game_controller.model)
        handle_game_events(game_controller)
        pygame.time.Clock().tick(60)
        pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("Wood Block")
    icon = pygame.image.load(GAME_ICON_PATH)
    pygame.display.set_icon(icon)

    game_model = GameModel()
    game_controller = GameController(game_model)

    while True:
        if game_controller.state == 'menu':
            play_rect, quit_rect = draw_menu(screen)
            handle_menu_events(game_controller, play_rect, quit_rect)
        elif game_controller.state == 'play':
            play_game(screen, game_controller)
        elif game_controller.state == 'game_over':
            play_again_rect, menu_rect = draw_game_over(screen, game_controller.model.score)
            handle_game_over_events(game_controller, play_again_rect, menu_rect)

if __name__ == "__main__":
    main()
