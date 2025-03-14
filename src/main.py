import pygame, re, copy
from game_model import GameModel
from gui.menu import draw_menu
from gui.select_level import draw_select_level
from gui.game import draw_game, draw_game_over
from game_controller import GameController, handle_menu_events, handle_game_events, handle_game_over_events, handle_select_level_events
from game_logic.constants import GAME_ICON_PATH, LEVEL_BOARDS, LEVEL_BLOCKS


def play_game(screen, game_controller):
    while game_controller.state == 'infinite':
        draw_game(screen, game_controller.model)
        handle_game_events(game_controller)
        pygame.time.Clock().tick(60)
        pygame.display.flip()

def start_level(screen, game_controller, level_number):
    game_controller.model.board = copy.deepcopy(LEVEL_BOARDS[level_number])
    game_controller.model.blocks_to_break = copy.deepcopy(LEVEL_BLOCKS[level_number])

    while game_controller.state == f'level_{level_number}':
        draw_game(screen, game_controller.model, level_number)
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
            levels_rect, infinite_rect, quit_rect = draw_menu(screen)
            handle_menu_events(game_controller, levels_rect, infinite_rect, quit_rect)
        elif game_controller.state == 'select_level':
            level_1_rect, level_2_rect, level_3_rect, menu_rect = draw_select_level(screen)
            handle_select_level_events(game_controller, level_1_rect, level_2_rect, level_3_rect, menu_rect)
        elif game_controller.state == 'infinite':
            play_game(screen, game_controller)
        elif game_controller.state == 'game_over':
            play_again_rect, menu_rect = draw_game_over(screen, game_controller.model.score)
            handle_game_over_events(game_controller, play_again_rect, menu_rect)
        else:
            match = re.match(r'level_(\d+)', game_controller.state)
            if match:
                level_number = int(match.group(1))
                start_level(screen, game_controller, level_number)

if __name__ == "__main__":
    main()
