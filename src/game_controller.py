import sys
import pygame
from game_logic.constants import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, GRID_SIZE
from game_logic.rules import generate_shapes, place_piece, check_full_lines, is_valid_position, no_more_valid_moves

class GameController:
    def __init__(self, game_model):
        self.state = 'menu'
        self.model = game_model

    def set_state(self, state):
        self.state = state


def handle_menu_events(game_controller, play_rect, quit_rect):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_rect.collidepoint(event.pos):
                game_controller.set_state('play')
            elif quit_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

def handle_game_events(game_controller):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            print('mouse down')
            if game_controller.model.selected_shape is None:
                mx, my = pygame.mouse.get_pos()
                print(f"mx: {mx}, my: {my}")
                for i, shape in enumerate(game_controller.model.shapes):
                    print(f"i: {i}, shape: {shape}")
                    if GRID_SIZE * CELL_SIZE <= mx <= SCREEN_WIDTH and i * 5 * CELL_SIZE <= my <= (i * 5 + 4) * CELL_SIZE:
                        print('shape selected')
                        game_controller.model.selected_shape = shape
                        break

        if event.type == pygame.MOUSEBUTTONUP:
            print('mouse up')
            if game_controller.model.selected_shape is not None:
                mx, my = pygame.mouse.get_pos()
                px, py = mx // CELL_SIZE, (my // CELL_SIZE) - game_controller.model.grid_offset_y
                if is_valid_position(game_controller.model.board, game_controller.model.selected_shape, (px, py)):
                    place_piece(game_controller.model.board, game_controller.model.selected_shape, (px, py))
                    lines_cleared = check_full_lines(game_controller.model.board)
                    game_controller.model.score += lines_cleared
                    game_controller.model.shapes.remove(game_controller.model.selected_shape)
                    if not game_controller.model.shapes:
                        game_controller.model.shapes = generate_shapes()
                    if no_more_valid_moves(game_controller.model.board, game_controller.model.shapes):
                        game_controller.set_state('game_over')
                game_controller.model.selected_shape = None

def handle_game_over_events(game_controller, play_again_rect, menu_rect):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_again_rect.collidepoint(event.pos):
                game_controller.model.reset()
                game_controller.set_state('play')
            elif menu_rect.collidepoint(event.pos):
                game_controller.set_state('menu')
