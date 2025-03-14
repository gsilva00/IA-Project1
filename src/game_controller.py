import sys
import pygame
from game_logic.constants import CELL_SIZE, GRID_OFFSET_Y
from game_logic.rules import generate_pieces, place_piece, check_full_lines, is_valid_position, no_more_valid_moves


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


def handle_menu_events(game_controller, levels_rect, infinite_rect, quit_rect):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if levels_rect.collidepoint(event.pos):
                game_controller.state = 'select_level'
            elif infinite_rect.collidepoint(event.pos):
                game_controller.state = 'infinite'
            elif quit_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

def handle_select_level_events(game_controller, level_1_rect, level_2_rect, level_3_rect, menu_rect):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if level_1_rect.collidepoint(event.pos):
                game_controller.model.level = 1
                game_controller.state = 'level_1'
            elif level_2_rect.collidepoint(event.pos):
                game_controller.model.level = 2
                game_controller.state = 'level_2'
            elif level_3_rect.collidepoint(event.pos):
                game_controller.model.level = 3
                game_controller.state = 'level_3'
            elif menu_rect.collidepoint(event.pos):
                game_controller.state = 'menu'

def handle_game_events(game_controller):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_controller.model.selected_piece is None:
                mx, my = pygame.mouse.get_pos()
                for i, piece in enumerate(game_controller.model.pieces):
                    piece_x_start = (i * 5 + 2) * CELL_SIZE
                    piece_x_end = piece_x_start + 4 * CELL_SIZE
                    piece_y_start = 10 * CELL_SIZE
                    piece_y_end = piece_y_start + 4 * CELL_SIZE
                    if piece_x_start <= mx <= piece_x_end and piece_y_start <= my <= piece_y_end:
                        game_controller.model.selected_piece = piece
                        game_controller.model.selected_index = i
                        game_controller.model.pieces_visible[i] = False # Mark the piece as not visible
                        break

        if event.type == pygame.MOUSEBUTTONUP:
            if game_controller.model.selected_piece is not None:
                mx, my = pygame.mouse.get_pos()
                px, py = mx // CELL_SIZE, (my // CELL_SIZE) - GRID_OFFSET_Y
                if is_valid_position(game_controller.model.board, game_controller.model.selected_piece, (px-4, py)):
                    place_piece(game_controller.model.board, game_controller.model.selected_piece, (px-4, py))
                    lines_cleared, target_blocks_cleared = check_full_lines(game_controller.model.board)

                    if game_controller.state != 'infinite':
                        game_controller.model.blocks_to_break -= target_blocks_cleared
                        game_controller.model.score += target_blocks_cleared

                        if game_controller.model.blocks_to_break <= 0:
                            game_controller.state = 'game_over'

                    else:
                        game_controller.model.score += lines_cleared

                    # All pieces placed, generate new ones
                    if all(not visible for visible in game_controller.model.pieces_visible):
                        game_controller.model.pieces = generate_pieces()
                        game_controller.model.pieces_visible = [True] * len(game_controller.model.pieces)

                    if no_more_valid_moves(game_controller.model.board, game_controller.model.pieces, game_controller.model.pieces_visible):
                        game_controller.state = 'game_over'
                else:
                    game_controller.model.pieces_visible[game_controller.model.selected_index] = True # Restore visibility if not placed

                game_controller.model.selected_piece = None
                game_controller.model.selected_index = None

def handle_game_over_events(game_controller, play_again_rect, menu_rect):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_again_rect.collidepoint(event.pos):
                game_controller.model.reset()
                game_controller.state = 'infinite'
            elif menu_rect.collidepoint(event.pos):
                game_controller.model.reset()
                game_controller.state = 'menu'
