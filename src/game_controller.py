import sys
import pygame
from game_logic.constants import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, GRID_SIZE
from game_logic.rules import generate_shapes, place_piece, check_full_lines, is_valid_position, no_more_valid_moves

class GameController:
    def __init__(self, game_model):
        self._state = 'menu'
        self._model = game_model

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, value):
        self._model = value


def handle_menu_events(game_controller, play_rect, quit_rect):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_rect.collidepoint(event.pos):
                game_controller.state = 'play'
            elif quit_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

def handle_game_events(game_controller):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_controller.model.selected_shape is None:
                mx, my = pygame.mouse.get_pos()
                for i, shape in enumerate(game_controller.model.shapes):
                    if GRID_SIZE * CELL_SIZE <= mx <= SCREEN_WIDTH and i * 5 * CELL_SIZE <= my <= (i * 5 + 4) * CELL_SIZE:
                        game_controller.model.selected_shape = shape
                        game_controller.model.selected_index = i
                        game_controller.model.shapes_visible[i] = False # Mark the shape as not visible
                        break

        if event.type == pygame.MOUSEBUTTONUP:
            if game_controller.model.selected_shape is not None:
                mx, my = pygame.mouse.get_pos()
                px, py = mx // CELL_SIZE, (my // CELL_SIZE) - game_controller.model.grid_offset_y
                if is_valid_position(game_controller.model.board, game_controller.model.selected_shape, (px, py)):
                    place_piece(game_controller.model.board, game_controller.model.selected_shape, (px, py))
                    lines_cleared = check_full_lines(game_controller.model.board)
                    game_controller.model.score += lines_cleared

                    if all(not visible for visible in game_controller.model.shapes_visible):
                        game_controller.model.shapes = generate_shapes()
                        game_controller.model.shapes_visible = [True] * len(game_controller.model.shapes)

                    if no_more_valid_moves(game_controller.model.board, game_controller.model.shapes):
                        game_controller.state = 'game_over'
                else:
                    game_controller.model.shapes_visible[game_controller.model.selected_index] = True # Restore visibility if not placed

                game_controller.model.selected_shape = None
                game_controller.model.selected_index = None

def handle_game_over_events(game_controller, play_again_rect, menu_rect):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_again_rect.collidepoint(event.pos):
                game_controller.model.reset()
                game_controller.state = 'play'
            elif menu_rect.collidepoint(event.pos):
                game_controller.state = 'menu'
