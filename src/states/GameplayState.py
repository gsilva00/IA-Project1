import sys
import pygame
import GameData

from game_logic.constants import (BACKGROUND_GAME_PATH, CELL_SIZE, DARK_WOOD_PATH, FONT_PATH, FONT_TEXT_SMALL_SIZE,
                                  GRAY, GRID_OFFSET_X, GRID_OFFSET_Y, GRID_SIZE, INFINITE, LIGHT_WOOD_PATH, WHITE, WOOD_PATH
                                  )
from game_logic.rules import check_full_lines, generate_pieces, is_valid_position, no_more_valid_moves, place_piece
from main import GameOverState, LevelCompleteState, PauseState
from states import GameState


class GameplayState(GameState):
    def __init__(self, player, ai_algorithm, level=INFINITE):
        self.player = player
        self.ai_algorithm = ai_algorithm
        self.level = level
        self.game_data = GameData(level)
        self.score = 0
        self.selected_piece = None
        self.selected_index = None
        self.pieces_visible = [True] * len(self.game_data.pieces)

    def enter(self, game):
        print("Starting Gameplay")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.selected_piece is None:
                    mx, my = pygame.mouse.get_pos()
                    for i, piece in enumerate(self.game_data.pieces):
                        piece_x_start = (i * 5 + 2) * CELL_SIZE
                        piece_x_end = piece_x_start + 4 * CELL_SIZE
                        piece_y_start = 10 * CELL_SIZE
                        piece_y_end = piece_y_start + 4 * CELL_SIZE
                        if piece_x_start <= mx <= piece_x_end and piece_y_start <= my <= piece_y_end:
                            self.selected_piece = piece
                            self.selected_index = i
                            self.pieces_visible[i] = False # Mark the piece as not visible
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.selected_piece is not None:
                    mx, my = pygame.mouse.get_pos()
                    px, py = mx // CELL_SIZE, (my // CELL_SIZE) - GRID_OFFSET_Y
                    if is_valid_position(self.game_data.board, self.selected_piece, (px-4, py)):
                        place_piece(self.game_data.board, self.selected_piece, (px-4, py))
                        lines_cleared, target_blocks_cleared = check_full_lines(self.game_data.board)

                        # Not infinite mode
                        if self.level != INFINITE:
                            self.game_data.blocks_to_break -= target_blocks_cleared
                            self.score += target_blocks_cleared

                            if self.game_data.blocks_to_break <= 0:
                                game.state_manager.switch_to_base_state(LevelCompleteState(self.score))

                        else:
                            self.score += lines_cleared

                        # All pieces placed, generate new ones
                        if all(not visible for visible in self.pieces_visible):
                            self.game_data.pieces = generate_pieces()
                            self.pieces_visible = [True] * len(self.game_data.pieces)

                        if no_more_valid_moves(self.game_data.board, self.game_data.pieces, self.pieces_visible):
                            game.state_manager.switch_to_base_state(GameOverState(self.score))
                    else:
                        # Restore visibility if not placed
                        self.pieces_visible[self.selected_index] = True

                    self.selected_piece = None
                    self.selected_index = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    game.state_manager.push_state(PauseState())

    def render(self, game):
        def draw_board(screen, board):
            wood_dark = pygame.image.load(DARK_WOOD_PATH)
            wood_target = pygame.image.load(WOOD_PATH)

            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    if board[y][x] == 1:
                        screen.blit(wood_dark, (GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE))
                    elif board[y][x] == 2:
                        screen.blit(wood_target, (GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE))
                    pygame.draw.rect(screen, GRAY, rect, 1)

        def draw_piece(screen, piece, position, is_selected, offset_y=0):
            wood = pygame.image.load(WOOD_PATH)
            wood_light = pygame.image.load(LIGHT_WOOD_PATH)

            px, py = position
            for x, y in piece:
                rect = pygame.Rect((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if is_selected:
                    screen.blit(wood_light, ((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE))
                else:
                    screen.blit(wood, ((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE))
                pygame.draw.rect(screen, GRAY, rect,1)

        def draw_score(screen, score):
            font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)
            text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(text, (10, 10))


        background = pygame.image.load(BACKGROUND_GAME_PATH)
        game.screen.blit(background, (0, 0))

        draw_board(game.screen, self.game_data.board)
        mx, my = pygame.mouse.get_pos()
        px, py = mx // CELL_SIZE, (my // CELL_SIZE) - GRID_OFFSET_Y

        for i, piece in enumerate(self.game_data.pieces):
            if self.pieces_visible[i] and (self.selected_piece is None or i != self.selected_index):
                draw_piece(game.screen, piece, (i*5+2, 10), False)

        if self.selected_piece is not None:
            draw_piece(game.screen, self.selected_piece, (px, py), True, GRID_OFFSET_Y)

        draw_score(game.screen, self.score)
        pygame.display.flip()

    def exit(self, game):
        print("Exiting Gameplay")
