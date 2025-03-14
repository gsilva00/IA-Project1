import copy
import sys
import pygame

from game_logic.constants import (A_STAR, AI, BACKGROUND_GAME_PATH, BACKGROUND_MENU_PATH, BFS, BROWN, CELL_SIZE, DARK_WOOD_PATH,
                                  DFS, FONT_PATH, FONT_TEXT_SIZE, FONT_TEXT_SMALL_SIZE, FONT_TITLE_SIZE, GRAY, GREEDY, GRID_OFFSET_X, GRID_OFFSET_Y,
                                  GRID_SIZE, INFINITE, ITER_DEEP, LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_BLOCKS, LEVEL_BOARDS, LIGHT_WOOD_PATH, ORANGE, PLAYER,
                                  SCREEN_HEIGHT, SCREEN_WIDTH, UNIFORM_COST, WEIGHTED_A_STAR, WHITE, WOOD_PATH)
from game_logic.rules import check_full_lines, generate_pieces, is_valid_position, no_more_valid_moves, place_piece


class GameStateManager:
    """ Manages the game states' stack
    """
    def __init__(self):
        self.state_stack = []

    def switch_to_base_state(self, new_state):
        while self.state_stack:
            self.state_stack.pop().exit(self)
        new_state.enter(self)
        self.state_stack = [new_state]

    def push_state(self, new_state):
        if self.current_state:
            self.current_state.exit(self)
        self.state_stack.append(new_state)
        print("Pushed state")
        new_state.enter(self)

    def pop_state(self):
        if self.current_state:
            self.state_stack.pop().exit(self)
            print("Popped state")
            if self.current_state:
                self.current_state.enter(self)
            return True
        return False

    @property
    def current_state(self):
        if self.state_stack:
            return self.state_stack[-1]
        return None


class GameState:
    """ Base class for all game states
    """
    # Model stores the game state

    def enter(self, game):
        pass

    # Controller updates the game state
    def update(self, game, events):
        pass

    # View renders the game state
    def render(self, game):
        pass

    def exit(self, game):
        pass

# ========================================
# Concrete Game States
# ========================================
class MainMenuState(GameState):
    def __init__(self):
        self.alpha = 255  # For transition effect

    def enter(self, game):
        print("Entering Main Menu")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.state_manager.switch_to_base_state(SelectPlayerState())

    def render(self, game):
        font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        title_text_back = font.render('Wood Block', True, BROWN)
        title_text_middle = font.render('Wood Block', True, ORANGE)
        title_text_front = font.render('Wood Block', True, WHITE)
        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        start_text = font.render('Click Anywhere to Start', True, WHITE)

        background = pygame.image.load(BACKGROUND_MENU_PATH)
        game.screen.blit(background, (0, 0))

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))
        start_rect = start_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.5))

        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(start_text, start_rect)
        pygame.display.flip()

    def exit(self, game):
        print("Exiting Main Menu")
        # while self.alpha > 0:
        #     game.state_manager.current_state.render(game)
        #     fade_surface = pygame.Surface((game.screen.get_width(), game.screen.get_height()))
        #     fade_surface.fill((0, 0, 0))
        #     fade_surface.set_alpha(self.alpha)
        #     game.screen.blit(fade_surface, (0, 0))
        #     pygame.display.flip()
        #     self.alpha -= 5  # Adjust the speed of the fade-out effect
        # self.alpha = 255  # Reset alpha for next time

class SelectPlayerState(GameState):
    def __init__(self):
        self.player_rect = None
        self.ai_rect = None
        self.back_rect = None

    def enter(self, game):
        print("Entering Select Player Menu")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.player_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectAIAlgorithmState(PLAYER))
                elif self.ai_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectAIAlgorithmState(AI))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()

    def render(self, game):
        font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        title_text_back = font.render('Wood Block', True, BROWN)
        title_text_middle = font.render('Wood Block', True, ORANGE)
        title_text_front = font.render('Wood Block', True, WHITE)

        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        player_text = font.render('Player', True, WHITE)
        ai_text = font.render('AI', True, WHITE)
        back_text = font.render('Go Back', True, WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))

        # Interactable rectangles
        self.player_rect = player_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2.5))
        self.ai_rect = ai_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2))
        self.back_rect = back_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.5))

        background = pygame.image.load(BACKGROUND_MENU_PATH)
        game.screen.blit(background, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        if self.player_rect.collidepoint(mouse_pos):
            player_text = font.render('Player', True, WHITE)
        else:
            player_text = font.render('Player', True, BROWN)
        if self.ai_rect.collidepoint(mouse_pos):
            ai_text = font.render('AI', True, WHITE)
        else:
            ai_text = font.render('AI', True, BROWN)
        if self.back_rect.collidepoint(mouse_pos):
            back_text = font.render('Go Back', True, WHITE)
        else:
            back_text = font.render('Go Back', True, BROWN)

        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(player_text, self.player_rect)
        game.screen.blit(ai_text, self.ai_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()


    def exit(self, game):
        print("Exiting Select Player Menu")

class SelectAIAlgorithmState(GameState):
    def __init__(self, player):
        self.player = player

        # TODO: Define all rectangles for AI algorithm selection
        self.bfs_rect = None
        self.dfs_rect = None
        self.iter_deep_rect = None
        self.uniform_cost_rect = None
        self.greedy_rect = None
        self.a_star_rect = None
        self.weighted_a_star_rect = None
        self.back_rect = None

    def enter(self, game):
        print("Entering Select AI Algorithm Menu")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.bfs_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, BFS))
                elif self.dfs_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, DFS))
                elif self.iter_deep_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, ITER_DEEP))
                elif self.uniform_cost_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, UNIFORM_COST))
                elif self.greedy_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, GREEDY))
                elif self.a_star_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, A_STAR))
                elif self.weighted_a_star_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, WEIGHTED_A_STAR))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop()

    def render(self, game):
        font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        title_text_back = font.render('Wood Block', True, BROWN)
        title_text_middle = font.render('Wood Block', True, ORANGE)
        title_text_front = font.render('Wood Block', True, WHITE)

        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        bfs_text = font.render('Breath First Search', True, WHITE)
        dfs_text = font.render('Depth First Search', True, WHITE)
        iter_deep_text = font.render('Iterative Deepening', True, WHITE)
        uniform_cost_text = font.render('Uniform Cost Search', True, WHITE)
        greedy_text = font.render('Greedy Search', True, WHITE)
        a_star_text = font.render('A*', True, WHITE)
        weighted_a_star_text = font.render('Weighted A*', True, WHITE)
        back_text = font.render('Go Back', True, WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))

        # Interactable rectangles
        self.bfs_rect = bfs_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2.5))
        self.dfs_rect = dfs_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2))
        self.iter_deep_rect = iter_deep_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.8))
        self.uniform_cost_rect = uniform_cost_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.6))
        self.greedy_rect = greedy_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.4))
        self.a_star_rect = a_star_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.2))
        self.weighted_a_star_rect = weighted_a_star_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1))
        self.back_rect = back_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.5))

        background = pygame.image.load(BACKGROUND_MENU_PATH)
        game.screen.blit(background, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        if self.bfs_rect.collidepoint(mouse_pos):
            bfs_text = font.render('Breath First Search', True, WHITE)
        else:
            bfs_text = font.render('Breath First Search', True, BROWN)
        if self.dfs_rect.collidepoint(mouse_pos):
            dfs_text = font.render('Depth First Search', True, WHITE)
        else:
            dfs_text = font.render('Depth First Search', True, BROWN)
        if self.iter_deep_rect.collidepoint(mouse_pos):
            iter_deep_text = font.render('Iterative Deepening', True, WHITE)
        else:
            iter_deep_text = font.render('Iterative Deepening', True, BROWN)
        if self.uniform_cost_rect.collidepoint(mouse_pos):
            uniform_cost_text = font.render('Uniform Cost Search', True, WHITE)
        else:
            uniform_cost_text = font.render('Uniform Cost Search', True, BROWN)
        if self.greedy_rect.collidepoint(mouse_pos):
            greedy_text = font.render('Greedy Search', True, WHITE)
        else:
            greedy_text = font.render('Greedy Search', True, BROWN)
        if self.a_star_rect.collidepoint(mouse_pos):
            a_star_text = font.render('A*', True, WHITE)
        else:
            a_star_text = font.render('A*', True, BROWN)
        if self.weighted_a_star_rect.collidepoint(mouse_pos):
            weighted_a_star_text = font.render('Weighted A*', True, WHITE)
        else:
            weighted_a_star_text = font.render('Weighted A*', True, BROWN)
        if self.back_rect.collidepoint(mouse_pos):
            back_text = font.render('Go Back', True, WHITE)
        else:
            back_text = font.render('Go Back', True, BROWN)

        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(bfs_text, self.bfs_rect)
        game.screen.blit(dfs_text, self.dfs_rect)
        game.screen.blit(iter_deep_text, self.iter_deep_rect)
        game.screen.blit(uniform_cost_text, self.uniform_cost_rect)
        game.screen.blit(greedy_text, self.greedy_rect)
        game.screen.blit(a_star_text, self.a_star_rect)
        game.screen.blit(weighted_a_star_text, self.weighted_a_star_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self, game):
        print("Exiting Select AI Algorithm Menu")

class SelectModeState(GameState):
    def __init__(self, player, ai_algorithm):
        self.player = player
        self.ai_algorithm = ai_algorithm
        self.levels_rect = None
        self.infinite_rect = None
        self.quit_rect = None

    def get_menu_rects(self):
        return self.levels_rect, self.infinite_rect, self.quit_rect

    def enter(self, game):
        print("Entering Select Mode Menu")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.levels_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectLevelState(self.player, self.ai_algorithm))
                elif self.infinite_rect.collidepoint(event.pos):
                    game.state_manager.switch_to_base_state(GameplayState(self.player, self.ai_algorithm, INFINITE))
                elif self.quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    def render(self, game):
        font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        title_text_back = font.render('Wood Block', True, BROWN)
        title_text_middle = font.render('Wood Block', True, ORANGE)
        title_text_front = font.render('Wood Block', True, WHITE)

        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        levels_text = font.render('Levels', True, WHITE)
        infinite_text = font.render('Infinite', True, WHITE)
        quit_text = font.render('Quit', True, WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))

        # Interactable rectangles
        self.levels_rect = levels_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2.5))
        self.infinite_rect = infinite_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2))
        self.quit_rect = quit_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.5))

        background = pygame.image.load(BACKGROUND_MENU_PATH)
        game.screen.blit(background, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        if self.levels_rect.collidepoint(mouse_pos):
            levels_text = font.render('Levels', True, WHITE)
        else:
            levels_text = font.render('Levels', True, BROWN)

        if self.infinite_rect.collidepoint(mouse_pos):
            infinite_text = font.render('Infinite', True, WHITE)
        else:
            infinite_text = font.render('Infinite', True, BROWN)

        if self.quit_rect.collidepoint(mouse_pos):
            quit_text = font.render('Quit', True, WHITE)
        else:
            quit_text = font.render('Quit', True, BROWN)

        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(levels_text, self.levels_rect)
        game.screen.blit(infinite_text, self.infinite_rect)
        game.screen.blit(quit_text, self.quit_rect)
        pygame.display.flip()

    def exit(self, game):
        print("Exiting Main Menu")

class SelectLevelState(GameState):
    def __init__(self, player, ai_algorithm):
        self.player = player
        self.ai_algorithm = ai_algorithm
        self.level_1_rect = None
        self.level_2_rect = None
        self.level_3_rect = None
        self.back_rect = None

    def enter(self, game):
        print("Entering Select Level")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.level_1_rect.collidepoint(event.pos):
                    game.state_manager.push_state(GameplayState(player=self.player, ai_algorithm=self.ai_algorithm, level=LEVEL_1))
                elif self.level_2_rect.collidepoint(event.pos):
                    game.state_manager.push_state(GameplayState(player=self.player, ai_algorithm=self.ai_algorithm, level=LEVEL_2))
                elif self.level_3_rect.collidepoint(event.pos):
                    game.state_manager.push_state(GameplayState(player=self.player, ai_algorithm=self.ai_algorithm, level=LEVEL_3))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()

    def render(self, game):
        font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        title_text_back = font.render('Level Select', True, BROWN)
        title_text_middle = font.render('Level Select', True, ORANGE)
        title_text_front = font.render('Level Select', True, WHITE)

        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        level_1_text = font.render('Level 1', True, WHITE)
        level_2_text = font.render('Level 2', True, WHITE)
        level_3_text = font.render('Level 3', True, WHITE)
        back_text = font.render('Go Back', True, WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))

        # Interactable rectangles
        self.level_1_rect = level_1_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2.5))
        self.level_2_rect = level_2_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2))
        self.level_3_rect = level_3_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.5))
        self.back_rect = back_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.2))

        background = pygame.image.load(BACKGROUND_MENU_PATH)
        game.screen.blit(background, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        if self.level_1_rect.collidepoint(mouse_pos):
            level_1_text = font.render('Level 1', True, WHITE)
        else:
            level_1_text = font.render('Level 1', True, BROWN)

        if self.level_2_rect.collidepoint(mouse_pos):
            level_2_text = font.render('Level 2', True, WHITE)
        else:
            level_2_text = font.render('Level 2', True, BROWN)

        if self.level_3_rect.collidepoint(mouse_pos):
            level_3_text = font.render('Level 3', True, WHITE)
        else:
            level_3_text = font.render('Level 3', True, BROWN)

        if self.back_rect.collidepoint(mouse_pos):
            back_text = font.render('Go Back', True, WHITE)
        else:
            back_text = font.render('Go Back', True, BROWN)

        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(level_1_text, self.level_1_rect)
        game.screen.blit(level_2_text, self.level_2_rect)
        game.screen.blit(level_3_text, self.level_3_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self, game):
        print("Exiting Select Level")


class GameData:
    def __init__(self, level=INFINITE):
        self.board = copy.deepcopy(LEVEL_BOARDS[level]) if level != INFINITE else [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.pieces = generate_pieces() # TODO: Change this
        self.following_pieces = generate_pieces() # TODO: Change this
        self.blocks_to_break = copy.deepcopy(LEVEL_BLOCKS[level]) if level != INFINITE else 0

    # Review this
    # def reset(self):
    #     self.board = copy.deepcopy(LEVEL_BOARDS[self.level]) if self.level != INFINITE else [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    #     self.pieces = generate_pieces()
    #     self.following_pieces = generate_pieces()

class GameplayState(GameState):
    def __init__(self, player, ai_algorithm, level=INFINITE):
        self.player = player
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

class PauseState(GameState):
    def __init__(self):
        self.resume_rect = None
        self.exit_rect = None

    def enter(self, game):
        print("Game Paused")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.state_manager.pop_state()
                elif event.key == pygame.K_ESCAPE:
                    game.state_manager.pop_state()
                    game.state_manager.pop_state()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.resume_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
                elif self.exit_rect.collidepoint(event.pos):
                    game.state_manager.switch_to_base_state(MainMenuState())

    def render(self, game):
        font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        pause_text = font.render('Pause', True, WHITE)

        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)
        resume_text = font.render('Press R to Resume', True, WHITE)
        exit_text = font.render('Press ESC to Exit', True, WHITE)

        # Non-interactable rectangles
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        # Interactable rectangles
        self.resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.5))
        self.exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        game.screen.fill(BROWN)

        mouse_pos = pygame.mouse.get_pos()

        if self.resume_rect.collidepoint(mouse_pos):
            resume_text = font.render('Press R to Resume', True, ORANGE)
        else:
            resume_text = font.render('Press R to Resume', True, WHITE)
        if self.exit_rect.collidepoint(mouse_pos):
            exit_text = font.render('Press ESC to Exit', True, ORANGE)
        else:
            exit_text = font.render('Press ESC to Exit', True, WHITE)

        game.screen.blit(pause_text, pause_rect)
        game.screen.blit(resume_text, self.resume_rect)
        game.screen.blit(exit_text, self.exit_rect)
        pygame.display.flip()

    def exit(self, game):
        print("Exiting Pause")

class GameOverState(GameState):
    def __init__(self, level, score):
        self.level = level
        self.score = score
        self.play_again_rect = None
        self.back_rect = None

    def enter(self, game):
        print("Game Over")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_again_rect.collidepoint(event.pos):
                    game.state_manager.switch_to_base_state(GameplayState(self.level))
                elif self.back_rect.collidepoint(event.pos):
                    # Pop the GameOverState and the GameplayState
                    game.state_manager.pop_state()
                    game.state_manager.pop_state()

    def render(self, game):
        font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        game_over_text = font.render('Game Over', True, WHITE)

        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)
        score_text = font.render(f'Score: {self.score}', True, ORANGE)
        play_again_text = font.render('Play Again', True, WHITE)
        back_text = font.render('Go Back', True, WHITE)

        # Non-interactable rectangles
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.5))

        # Interactable rectangles
        play_again_rect = play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.7))
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.4))

        game.screen.fill(BROWN)

        mouse_pos = pygame.mouse.get_pos()
        if play_again_rect.collidepoint(mouse_pos):
            play_again_text = font.render('Play Again', True, ORANGE)
        else:
            play_again_text = font.render('Play Again', True, WHITE)

        if back_rect.collidepoint(mouse_pos):
            back_text = font.render('Go Back', True, ORANGE)
        else:
            back_text = font.render('Go Back', True, WHITE)

        game.screen.blit(game_over_text, game_over_rect)
        game.screen.blit(score_text, score_rect)
        game.screen.blit(play_again_text, play_again_rect)
        game.screen.blit(back_text, back_rect)
        pygame.display.flip()

        return play_again_rect, back_rect

    def exit(self, game):
        print("Exiting Game Over")

class LevelCompleteState(GameState):
    def __init__(self, level, score):
        self.level = level
        self.score = score
        self.next_level_rect = None
        self.play_next_rect = None
        self.back_rect = None

    def enter(self, game):
        print("Level Complete")

    def update(self, game, events):
        # TODO: Create a level complete screen
        return NotImplementedError

    def render(self, game):
        font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        level_complete_text = font.render('Level Complete', True, WHITE)

        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)
        score_text = font.render(f'Score: {self.score}', True, ORANGE)
        next_level_text = font.render('Next Level', True, WHITE)
        play_next_text = font.render('Play Next', True, WHITE)
        back_text = font.render('Go Back', True, WHITE)

        # Non-interactable rectangles
        level_complete_rect = level_complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.5))

        # Interactable rectangles
        self.next_level_rect = next_level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.7))
        self.play_next_rect = play_next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
        self.back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.3))

        game.screen.fill(BROWN)

        mouse_pos = pygame.mouse.get_pos()
        if self.next_level_rect.collidepoint(mouse_pos):
            next_level_text = font.render('Next Level', True, ORANGE)
        else:
            next_level_text = font.render('Next Level', True, WHITE)
        if self.play_next_rect.collidepoint(mouse_pos):
            play_next_text = font.render('Play Next', True, ORANGE)
        else:
            play_next_text = font.render('Play Next', True, WHITE)
        if self.back_rect.collidepoint(mouse_pos):
            back_text = font.render('Go Back', True, ORANGE)
        else:
            back_text = font.render('Go Back', True, WHITE)

        game.screen.blit(level_complete_text, level_complete_rect)
        game.screen.blit(score_text, score_rect)
        game.screen.blit(next_level_text, self.next_level_rect)
        game.screen.blit(play_next_text, self.play_next_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()


    def exit(self, game):
        print("Exiting Level Complete")
