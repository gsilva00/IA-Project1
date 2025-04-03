import copy
import math
import time

import pygame

from AI.algorithm_registry import get_ai_algorithm, get_ai_algorithm_id
from AI.algorithms import (AIAlgorithm, AStarAlgorithm, BFSAlgorithm,
                           DFSAlgorithm, GreedySearchAlgorithm,
                           IterDeepAlgorithm, WeightedAStarAlgorithm)
from game_data import GameData
from game_logic.constants import (A_STAR, AI, AI_FOUND, AI_NOT_FOUND,
                                  BACKGROUND_GAME_PATH, BACKGROUND_MENU_PATH,
                                  BFS, BROWN, CELL_SIZE, DFS, FONT_HINT_SIZE,
                                  FONT_PATH, FONT_TEXT_SIZE,
                                  FONT_TEXT_SMALL_SIZE, FONT_TITLE_SIZE,
                                  GAME_ICON_MENU_PATH, GRAY, GREEDY,
                                  GRID_OFFSET_X, GRID_OFFSET_Y, HINT_ICON_PATH,
                                  HUMAN, INFINITE, ITER_DEEP, LEVEL_1, LEVEL_2,
                                  LEVEL_3, LEVELS, ORANGE,
                                  PIECES_LIST_BETWEEN_OFFSET_X_CELLS,
                                  PIECES_LIST_OFFSET_X_CELLS,
                                  PIECES_LIST_OFFSET_Y_CELLS, SCREEN_HEIGHT,
                                  SCREEN_WIDTH, WEIGHTED_A_STAR, WHITE)
from game_logic.rules import (clear_full_lines, is_valid_position,
                              no_more_valid_moves, place_piece)
from utils.misc import QuitGameException, ScreenWrapper
from utils.ui import draw_board, draw_piece, draw_score


class GameStateManager:
    """Manages the game states' stack

    """

    def __init__(self, screen):
        self.state_stack = []
        self.screen = screen

    def switch_to_base_state(self, new_state):
        """Switch to a new state and remove all previous states

        Args:
            new_state (GameState): The new state to switch to
        """

        self.clear_states()
        new_state.enter(self.screen)
        self.state_stack = [new_state]

    def push_state(self, new_state):
        """Push a new state to the stack

        Args:
            new_state (GameState): The new state to push
        """

        if self.current_state is not None:
            self.current_state.exit(self.screen)
        self.state_stack.append(new_state)
        print("Pushed state")
        new_state.enter(self.screen)

    def pop_state(self, times=1):
        """Pop the current state

        Args:
            times (int): The number of times to pop the state

        Returns:
            bool: True if the state was popped, False otherwise
        """
        popped = False
        for _ in range(times):
            if self.current_state is not None:
                self.state_stack.pop().exit(self.screen)
                print("Popped state")
                popped = True
            else:
                break

        if self.current_state is not None:
            self.current_state.enter(self.screen)

        return popped

    def peek_state(self):
        """Get the state at the top of the stack

        Returns:
            GameState: The state at the top of the stack
        """

        if self.state_stack:
            print("The peeked state is:", self.state_stack[-1])
            return self.state_stack[-1]
        return None

    def subst_below_switch_to(self, new_state):
        """Switch to a new state and remove the previous state

        Args:
            new_state (GameState): The new state to switch to

        Returns:
            bool: True if the state was switched, False otherwise
        """

        if len(self.state_stack) > 1:
            self.state_stack[-2].exit(self.screen)
            self.state_stack[-2] = new_state
            self.state_stack.pop().exit(self.screen)
            new_state.enter(self.screen)
            return True
        return False

    def clear_states(self):
        """Clear all states

        """

        while self.state_stack:
            self.state_stack.pop().exit(self.screen)

    @property
    def current_state(self):
        """Get the current state

        Returns:
            GameState: The current state
        """

        if self.state_stack:
            return self.state_stack[-1]
        return None


class GameState:
    """ Base class for all game states

    """
    # Each subclass stores its Model

    def enter(self, screen):
        """Called when the game state is entered
        Used for debugging, possible transition effects and other initializations separate from the constructor

        Args:
            screen (pygame.Surface): The screen to render on
        """
        pass

    def update(self, game, events):
        """Controller that updates the game state

        Args:
            game (Game): The Game object
            events (List[pygame.event.Event]): The events that have occurred
        """
        pass

    def render(self, game):
        """View that renders the game state

        Args:
            game (Game): The Game object
        """
        pass

    def exit(self, screen):
        """Called when the game state is exited
        Used for debugging, possible transition effects and other clean-up operations

        Args:
            screen (pygame.Surface): The screen to render on
        """
        pass

# ========================================
# Concrete Game States
# ========================================
class MainMenuState(GameState):
    """Main menu of the game

    """

    def enter(self, screen):
        print("Entering Main Menu")

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                raise QuitGameException()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                game.state_manager.push_state(SelectPlayerState())

    def render(self, game):
        background = pygame.image.load(BACKGROUND_MENU_PATH)
        icon_menu = pygame.image.load(GAME_ICON_MENU_PATH)
        title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        text_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)

        title_text_back = title_font.render('Wood Block', True, BROWN)
        title_text_middle = title_font.render('Wood Block', True, ORANGE)
        title_text_front = title_font.render('Wood Block', True, WHITE)
        start_text = text_font.render('* Click Anywhere to Start *', True, WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))
        start_rect = start_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.35))

        game.screen.blit(background, (0, 0))
        game.screen.blit(icon_menu, (SCREEN_WIDTH / 2 - 100, SCREEN_HEIGHT / 2 - 100))
        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(start_text, start_rect)
        pygame.display.flip()

    def exit(self, screen):
        print("Exiting Main Menu")

class SelectPlayerState(GameState):
    """Menu to select either player mode or AI mode

    """

    def __init__(self):
        self.keyboard_active = False
        self.selected_option = None
        self.player_rect = None
        self.ai_rect = None
        self.back_rect = None

    def enter(self, screen):
        print("Entering Select Player Menu")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                raise QuitGameException()
            # Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.player_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectAIAlgorithmState(HUMAN))
                elif self.ai_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectAIAlgorithmState(AI))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                    self.keyboard_active = True

                if event.key == pygame.K_BACKSPACE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 3
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 3
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.push_state(SelectAIAlgorithmState(HUMAN))
                    elif self.selected_option == 1:
                        game.state_manager.push_state(SelectAIAlgorithmState(AI))
                    elif self.selected_option == 2:
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.player_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.ai_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 2
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, game):
        background = pygame.image.load(BACKGROUND_MENU_PATH)
        title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        subtitle_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        # text_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)

        title_text_back = title_font.render('Wood Block', True, BROWN)
        title_text_middle = title_font.render('Wood Block', True, ORANGE)
        title_text_front = title_font.render('Wood Block', True, WHITE)
        subtitle_text = subtitle_font.render('Select The Player', True, BROWN)
        player_text = subtitle_font.render('Human', True, ORANGE if self.selected_option == 0 else WHITE)
        ai_text = subtitle_font.render('AI', True, ORANGE if self.selected_option == 1 else WHITE)
        back_text = subtitle_font.render('Go Back', True, ORANGE if self.selected_option == 2 else WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))
        subtitle_rect = subtitle_text.get_rect(center=(game.screen.get_width() // 2 , game.screen.get_height() // 2.65 ))

        # Interactable rectangles
        self.player_rect = player_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2.1))
        self.ai_rect = ai_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.7))
        self.back_rect = back_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.20))

        game.screen.blit(background, (0, 0))
        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(subtitle_text,subtitle_rect)
        game.screen.blit(player_text, self.player_rect)
        game.screen.blit(ai_text, self.ai_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()


    def exit(self, screen):
        print("Exiting Select Player Menu")

class SelectAIAlgorithmState(GameState):
    """Menu to select the AI algorithm (for player mode's hints or for AI mode)

    """

    def __init__(self, player):
        self.player = player

        self.keyboard_active = False
        self.selected_option = None
        self.bfs_rect = None
        self.dfs_rect = None
        self.iter_deep_rect = None
        self.greedy_rect = None
        self.a_star_rect = None
        self.weighted_a_star_rect = None
        self.back_rect = None

    def enter(self, screen):
        print("Entering Select AI Algorithm Menu")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                raise QuitGameException()
            # Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.bfs_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, BFS))
                elif self.dfs_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, DFS))
                elif self.iter_deep_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, ITER_DEEP))
                elif self.greedy_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, GREEDY))
                elif self.a_star_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, A_STAR))
                elif self.weighted_a_star_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectModeState(self.player, WEIGHTED_A_STAR))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                    self.keyboard_active = True

                if event.key == pygame.K_BACKSPACE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 7
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 7
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.push_state(SelectModeState(self.player, BFS))
                    elif self.selected_option == 1:
                        game.state_manager.push_state(SelectModeState(self.player, DFS))
                    elif self.selected_option == 2:
                        game.state_manager.push_state(SelectModeState(self.player, ITER_DEEP))
                    elif self.selected_option == 3:
                        game.state_manager.push_state(SelectModeState(self.player, GREEDY))
                    elif self.selected_option == 4:
                        game.state_manager.push_state(SelectModeState(self.player, A_STAR))
                    elif self.selected_option == 5:
                        game.state_manager.push_state(SelectModeState(self.player, WEIGHTED_A_STAR))
                    elif self.selected_option == 6:
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.bfs_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.dfs_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif self.iter_deep_rect.collidepoint(mouse_pos):
            self.selected_option = 2
        elif self.greedy_rect.collidepoint(mouse_pos):
            self.selected_option = 3
        elif self.a_star_rect.collidepoint(mouse_pos):
            self.selected_option = 4
        elif self.weighted_a_star_rect.collidepoint(mouse_pos):
            self.selected_option = 5
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 6
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, game):
        background = pygame.image.load(BACKGROUND_MENU_PATH)
        title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        subtitle_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        text_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)

        title_text_back = title_font.render('Wood Block', True, BROWN)
        title_text_middle = title_font.render('Wood Block', True, ORANGE)
        title_text_front = title_font.render('Wood Block', True, WHITE)
        subtitle_text = subtitle_font.render('Select The AI Algorithm', True, BROWN)
        bfs_text = text_font.render('Breadth First Search', True, ORANGE if self.selected_option == 0 else WHITE)
        dfs_text = text_font.render('Depth First Search', True, ORANGE if self.selected_option == 1 else WHITE)
        iter_deep_text = text_font.render('Iterative Deepening', True, ORANGE if self.selected_option == 2 else WHITE)
        greedy_text = text_font.render('Greedy Search', True, ORANGE if self.selected_option == 3 else WHITE)
        a_star_text = text_font.render('A*', True, ORANGE if self.selected_option == 4 else WHITE)
        weighted_a_star_text = text_font.render('Weighted A*', True, ORANGE if self.selected_option == 5 else WHITE)
        back_text = subtitle_font.render('Go Back', True, ORANGE if self.selected_option == 6 else WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))
        subtitle_rect = subtitle_text.get_rect(center=(game.screen.get_width() // 2 , game.screen.get_height() // 2.65 ))

        # Interactable rectangles
        self.bfs_rect = bfs_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2.1))
        self.dfs_rect = dfs_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.85))
        self.iter_deep_rect = iter_deep_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.67))
        self.greedy_rect = greedy_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.52))
        self.a_star_rect = a_star_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.4))
        self.weighted_a_star_rect = weighted_a_star_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.3))
        self.back_rect = back_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.17))

        game.screen.blit(background, (0, 0))
        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(subtitle_text,subtitle_rect)
        game.screen.blit(bfs_text, self.bfs_rect)
        game.screen.blit(dfs_text, self.dfs_rect)
        game.screen.blit(iter_deep_text, self.iter_deep_rect)
        game.screen.blit(greedy_text, self.greedy_rect)
        game.screen.blit(a_star_text, self.a_star_rect)
        game.screen.blit(weighted_a_star_text, self.weighted_a_star_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self, screen):
        print("Exiting Select AI Algorithm Menu")

class SelectModeState(GameState):
    """Menu to select the game mode (Levels or Infinite)

    """

    def __init__(self, player, ai_algorithm):
        self.player = player
        self.ai_algorithm = ai_algorithm

        self.keyboard_active = False
        self.selected_option = None
        self.levels_rect = None
        self.infinite_rect = None
        self.quit_rect = None

    def get_menu_rects(self):
        return self.levels_rect, self.infinite_rect, self.quit_rect

    def enter(self, screen):
        print("Entering Select Mode Menu")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                raise QuitGameException()
            # Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.levels_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectLevelState(self.player, self.ai_algorithm))
                elif self.infinite_rect.collidepoint(event.pos):
                    game.state_manager.push_state(GameplayState(self.player, self.ai_algorithm, INFINITE))
                elif self.quit_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                    self.keyboard_active = True

                if event.key == pygame.K_BACKSPACE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 3
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 3
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.push_state(SelectLevelState(self.player, self.ai_algorithm))
                    elif self.selected_option == 1:
                        game.state_manager.push_state(GameplayState(self.player, self.ai_algorithm, INFINITE))
                    elif self.selected_option == 2:
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.levels_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.infinite_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif self.quit_rect.collidepoint(mouse_pos):
            self.selected_option = 2
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, game):
        background = pygame.image.load(BACKGROUND_MENU_PATH)
        title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        subtitle_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        text_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)

        title_text_back = title_font.render('Wood Block', True, BROWN)
        title_text_middle = title_font.render('Wood Block', True, ORANGE)
        title_text_front = title_font.render('Wood Block', True, WHITE)
        subtitle_text = subtitle_font.render('Select The Game Mode', True, BROWN)
        levels_text = text_font.render('Levels', True, ORANGE if self.selected_option == 0 else WHITE)
        infinite_text = text_font.render('Infinite', True, ORANGE if self.selected_option == 1 else WHITE)
        back_text = subtitle_font.render('Go Back', True, ORANGE if self.selected_option == 2 else WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))
        subtitle_rect = subtitle_text.get_rect(center=(game.screen.get_width() // 2 , game.screen.get_height() // 2.65 ))

        # Interactable rectangles
        self.levels_rect = levels_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2.1))
        self.infinite_rect = infinite_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.7))
        self.quit_rect = back_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.20))

        game.screen.blit(background, (0, 0))
        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(subtitle_text,subtitle_rect)
        game.screen.blit(levels_text, self.levels_rect)
        game.screen.blit(infinite_text, self.infinite_rect)
        game.screen.blit(back_text, self.quit_rect)
        pygame.display.flip()

    def exit(self, screen):
        print("Exiting Main Menu")

class SelectLevelState(GameState):
    """Menu to select the game level for the Levels mode

    """

    def __init__(self, player, ai_algorithm):
        self.player = player
        self.ai_algorithm = ai_algorithm

        self.keyboard_active = False
        self.selected_option = None
        self.level_1_rect = None
        self.level_2_rect = None
        self.level_3_rect = None
        self.back_rect = None

    def enter(self, screen):
        print("Entering Select Level")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                raise QuitGameException()
            # Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.level_1_rect.collidepoint(event.pos):
                    game.state_manager.push_state(GameplayState(self.player, self.ai_algorithm, LEVEL_1))
                elif self.level_2_rect.collidepoint(event.pos):
                    game.state_manager.push_state(GameplayState(self.player, self.ai_algorithm, LEVEL_2))
                elif self.level_3_rect.collidepoint(event.pos):
                    game.state_manager.push_state(GameplayState(self.player, self.ai_algorithm, LEVEL_3))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                    self.keyboard_active = True

                if event.key == pygame.K_BACKSPACE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 4
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 4
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.push_state(GameplayState(self.player, self.ai_algorithm, LEVEL_1))
                    elif self.selected_option == 1:
                        game.state_manager.push_state(GameplayState(self.player, self.ai_algorithm, LEVEL_2))
                    elif self.selected_option == 2:
                        game.state_manager.push_state(GameplayState(self.player, self.ai_algorithm, LEVEL_3))
                    elif self.selected_option == 3:
                        game.state_manager.pop_state()

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.level_1_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.level_2_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif self.level_3_rect.collidepoint(mouse_pos):
            self.selected_option = 2
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 3
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, game):
        background = pygame.image.load(BACKGROUND_MENU_PATH)
        title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        subtitle_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        text_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)

        title_text_back = title_font.render('Wood Block', True, BROWN)
        title_text_middle = title_font.render('Wood Block', True, ORANGE)
        title_text_front = title_font.render('Wood Block', True, WHITE)
        subtitle_text = subtitle_font.render('Select The Game Level', True, BROWN)
        level_1_text = text_font.render('Level 1', True, ORANGE if self.selected_option == 0 else WHITE)
        level_2_text = text_font.render('Level 2', True, ORANGE if self.selected_option == 1 else WHITE)
        level_3_text = text_font.render('Level 3', True, ORANGE if self.selected_option == 2 else WHITE)
        back_text = subtitle_font.render('Go Back', True, ORANGE if self.selected_option == 3 else WHITE)

        # Non-interactable rectangles
        title_rect_back = title_text_back.get_rect(center=((game.screen.get_width() // 2) + 5 , (game.screen.get_height() // 4) - 5))
        title_rect_middle = title_text_middle.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 4))
        title_rect_front = title_text_front.get_rect(center=((game.screen.get_width() // 2) - 5 , (game.screen.get_height() // 4) + 5))
        subtitle_rect = subtitle_text.get_rect(center=(game.screen.get_width() // 2 , game.screen.get_height() // 2.65 ))

        # Interactable rectangles
        self.level_1_rect = level_1_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 2.1))
        self.level_2_rect = level_2_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.7))
        self.level_3_rect = level_3_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.42))
        self.back_rect = back_text.get_rect(center=(game.screen.get_width() // 2, game.screen.get_height() // 1.2))

        game.screen.blit(background, (0, 0))
        game.screen.blit(title_text_back, title_rect_back)
        game.screen.blit(title_text_middle, title_rect_middle)
        game.screen.blit(title_text_front, title_rect_front)
        game.screen.blit(subtitle_text,subtitle_rect)
        game.screen.blit(level_1_text, self.level_1_rect)
        game.screen.blit(level_2_text, self.level_2_rect)
        game.screen.blit(level_3_text, self.level_3_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self, screen):
        print("Exiting Select Level")


class GameplayState(GameState):
    """Gameplay state of the game

    """

    def __init__(self, player, ai_algorithm, level=INFINITE):
        self.player = player
        self.ai_algorithm = get_ai_algorithm(ai_algorithm, level)
        self.level = level

        # custom_game_data = GameData(level=1)
        # custom_game_data.board = [
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [0, 0, 0, 0, 0, 0, 0, 0],
        #     [2, 1, 1, 1, 1, 1, 1, 0],
        # ]

        # custom_game_data.pieces = [[(0, 0)]]  # A single block piece
        # custom_game_data.following_pieces = []
        # custom_game_data.blocks_to_break = 1
        # self.game_data = custom_game_data
        self.game_data = GameData(self.level)
        self.score = 0
        self.selected_index = None
        self.selected_piece = None

        self.hint_button = None
        self.hint_pressed = False
        self.ai_hint_index = None
        self.ai_hint_position = None

        self.ai_running_start_time = None
        self.ai_initial_pos = None
        self.ai_current_pos = None
        self.ai_target_pos = None

        self.done = None

    def _toggle_ai_running_time(self):
        """Toggle the AI running time to stop or start the timer

        """

        if self.ai_running_start_time is None:
            self.ai_running_start_time = time.time()
        else:
            self.ai_running_start_time = None

    def _on_ai_algo_done(self, status, piece_index, piece_position):
        """Callback function for AI algorithm to notify/update state when it has finished

        Args:
            status (int): Status of the AI algorithm (AI_FOUND or AI_NOT_FOUND)
            piece_index (int): Index of the piece in the game_data.pieces list
            piece_position (Tuple[int, int]): Position where the piece should be placed
        """

        if status == AI_FOUND:
            print("AI found a move")

            if self.player == HUMAN:
                self.ai_hint_index = piece_index
                self.ai_hint_position = piece_position

            else:
                self.selected_index = piece_index
                self.selected_piece = self.game_data.pieces[self.selected_index]
                self.ai_target_pos = (GRID_OFFSET_X + piece_position[0] * CELL_SIZE, (GRID_OFFSET_Y + piece_position[1]) * CELL_SIZE)

                for i, piece in enumerate(self.game_data.pieces):
                    if piece == self.selected_piece:
                        # Convert from cell-based coordinates to screen-based coordinates
                        self.ai_initial_pos = ((i * PIECES_LIST_BETWEEN_OFFSET_X_CELLS + PIECES_LIST_OFFSET_X_CELLS) * CELL_SIZE, PIECES_LIST_OFFSET_Y_CELLS * CELL_SIZE)
                        self.ai_current_pos = self.ai_initial_pos
                        break

                self.game_data.pieces[self.selected_index] = None

        elif status == AI_NOT_FOUND:
            print("AI didn't find a move")


    def enter(self, screen):
        print("Starting Gameplay")

        # Start running the AI algorithm AS SOON AS WE ENTER THE GAMEPLAY STATE (but avoid recomputing if there are results already)
        if (
            (self.player == HUMAN and (not self.ai_hint_index or not self.ai_hint_position)) or
            (self.player == AI and (not self.ai_initial_pos or not self.ai_current_pos or not self.ai_target_pos))
        ):
            self.ai_algorithm.get_next_move(self.game_data, self._toggle_ai_running_time, self._on_ai_algo_done)

    def update(self, game, events):
        if self.player == HUMAN:
            self.update_player(game, events)
        else:
            self.update_ai(game, events)

    def update_player(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                self.ai_algorithm.stop()
                raise QuitGameException()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    # Stop the AI algorithm running in the background (if it is)
                    game.state_manager.push_state(PauseState())

                if event.key == pygame.K_h:
                    # Callback function will handle assigning the AI's move to the corresponding variables
                    # Check how those variables are used in the events above
                    self.hint_pressed = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.selected_piece is None:
                    mx, my = pygame.mouse.get_pos()
                    for i, piece in enumerate(self.game_data.pieces):
                        if piece is not None:
                            piece_x_start = (i * 5 + 2) * CELL_SIZE
                            piece_x_end = piece_x_start + 4 * CELL_SIZE
                            piece_y_start = 10 * CELL_SIZE
                            piece_y_end = piece_y_start + 4 * CELL_SIZE
                            if piece_x_start <= mx <= piece_x_end and piece_y_start <= my <= piece_y_end:
                                self.selected_index = i
                                self.selected_piece = piece
                                self.game_data.pieces[i] = None
                                break

                    # Mouse wasn't on any piece, check if hint button was pressed
                    if self.selected_piece is None and self.hint_button.collidepoint(mx, my):
                        self.hint_pressed = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.selected_piece is not None:
                    mx, my = pygame.mouse.get_pos()
                    px, py = mx // CELL_SIZE, (my // CELL_SIZE) - GRID_OFFSET_Y
                    if is_valid_position(self.game_data.board, self.selected_piece, (px-4, py)):
                        place_piece(self.game_data, self.selected_piece, (px-4, py))
                        lines_cleared, target_blocks_cleared = clear_full_lines(self.game_data.board)

                        # Levels mode
                        if self.level != INFINITE:
                            self.game_data.blocks_to_break -= target_blocks_cleared
                            self.score += target_blocks_cleared

                            if self.game_data.blocks_to_break <= 0:
                                self.ai_algorithm.stop()
                                self.done = True

                                # push_state() will call exit() of this state, which EXCEPTIONALLY calls render() to render the final state, so these variables need to be reset early
                                self.selected_index = None
                                self.selected_piece = None
                                self.hint_pressed = False
                                self.ai_hint_index = None
                                self.ai_hint_position = None

                                game.state_manager.push_state(LevelCompleteState(self.score, self.player, get_ai_algorithm_id(self.ai_algorithm), self.level))

                        else:
                            self.score += lines_cleared

                        if not self.done:
                            # Player made move, so state changed, then prepare next hint
                            if (
                                    self.ai_running_start_time is None and self.ai_hint_index is not None and self.ai_hint_position is not None and
                                    self.selected_index == self.ai_hint_index and px-4 == self.ai_hint_position[0] and py == self.ai_hint_position[1]
                            ):
                                # Hinted piece was placed, get the next hint (if available, as some algorithms may not compute more than one hint)
                                self.ai_algorithm.get_next_move(self.game_data, self._toggle_ai_running_time, self._on_ai_algo_done)
                            elif (
                                    self.ai_running_start_time is None and self.ai_hint_index is not None and self.ai_hint_position is not None and
                                    (self.selected_index != self.ai_hint_index or px-4 != self.ai_hint_position[0] or py != self.ai_hint_position[1])
                            ):
                                # Hinted piece was not placed, so we need to get a new hint (even if the AI computed more than one hint)
                                self.ai_algorithm.get_next_move(self.game_data, self._toggle_ai_running_time, self._on_ai_algo_done, True)

                            # All pieces placed (all None), generate new ones
                            if not any(self.game_data.pieces):
                                _areThereMore = self.game_data.get_more_playable_pieces()

                            if no_more_valid_moves(self.game_data.board, self.game_data.pieces):
                                self.ai_algorithm.stop()
                                self.done = True

                                # push_state() will call exit() of this state, which EXCEPTIONALLY calls render() to render the final state, so these variables need to be reset early
                                self.selected_index = None
                                self.selected_piece = None
                                self.hint_pressed = False
                                self.ai_hint_index = None
                                self.ai_hint_position = None

                                game.state_manager.push_state(GameOverState(self.score, self.player, get_ai_algorithm_id(self.ai_algorithm), self.level))

                        # Clear the current hint
                        self.hint_pressed = False
                        self.ai_hint_index = None
                        self.ai_hint_position = None
                    else:
                        # Restore visibility if not placed
                        for i, piece in enumerate(self.game_data.pieces):
                            if self.selected_index == i and piece is None:
                                self.game_data.pieces[i] = self.selected_piece

                    self.selected_index = None
                    self.selected_piece = None
                    self.done = False

    def update_ai(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                self.ai_algorithm.stop()
                raise QuitGameException()

        # Callback function will handle assigning the AI's move to the corresponding variables

        # If algorithm isn't running (finished), handle its move
        if self.ai_running_start_time is None:
            if self.selected_piece is not None:
                # If the algorithm found a move, handle it
                if self.ai_current_pos == self.ai_target_pos:
                    px, py = (self.ai_target_pos[0] - GRID_OFFSET_X) // CELL_SIZE, (self.ai_target_pos[1] // CELL_SIZE) - GRID_OFFSET_Y
                    place_piece(self.game_data, self.selected_piece, (px, py))
                    lines_cleared, target_blocks_cleared = clear_full_lines(self.game_data.board)
                    # time.sleep(0.3)  # Add a small delay to better visualize the AI's move

                    # Levels mode
                    if self.level != INFINITE:
                        self.game_data.blocks_to_break -= target_blocks_cleared
                        self.score += target_blocks_cleared

                        if self.game_data.blocks_to_break <= 0:
                            self.ai_algorithm.stop()
                            self.done = True

                            # push_state() will call exit() of this state, which EXCEPTIONALLY calls render() to render the final state, so these variables need to be reset early
                            self.selected_piece = None
                            self.ai_initial_pos = None
                            self.ai_current_pos = None
                            self.ai_target_pos = None

                            game.state_manager.push_state(LevelCompleteState(self.score, self.player, get_ai_algorithm_id(self.ai_algorithm), self.level))

                    else:
                        self.score += lines_cleared

                    if not self.done:
                        # All pieces placed (all None), generate new ones
                        if not any(self.game_data.pieces):
                            _areThereMore = self.game_data.get_more_playable_pieces()

                        if no_more_valid_moves(self.game_data.board, self.game_data.pieces):
                            self.ai_algorithm.stop()
                            self.done = True

                            # push_state() will call exit() of this state, which EXCEPTIONALLY calls render() to render the final state, so these variables need to be reset early
                            self.selected_piece = None
                            self.ai_initial_pos = None
                            self.ai_current_pos = None
                            self.ai_target_pos = None

                            game.state_manager.push_state(GameOverState(self.score, self.player, get_ai_algorithm_id(self.ai_algorithm), self.level))

                    self.selected_piece = None
                    self.ai_initial_pos = None
                    self.ai_current_pos = None
                    self.ai_target_pos = None

                    if not self.done:
                        self.ai_algorithm.get_next_move(self.game_data, self._toggle_ai_running_time, self._on_ai_algo_done)

                    self.done = False
            else:
                # AI didn't find a move (DONT KNOW WHAT TO DO HERE) TODO
                game.state_manager.push_state(GameOverState(self.score, self.player, get_ai_algorithm_id(self.ai_algorithm), self.level))
                pass
        else:
            # Do nothing, the AI is still running
            pass

    def render(self, game):
        if self.player == HUMAN:
            self.render_player(game)
        else:
            self.render_ai(game)

    def render_player(self, game):
        background = pygame.image.load(BACKGROUND_GAME_PATH)
        hint_icon = pygame.image.load(HINT_ICON_PATH).convert_alpha() # With transparency
        font = pygame.font.Font(FONT_PATH, FONT_HINT_SIZE)

        hint_text = font.render('H', True, WHITE)
        hint_icon = pygame.transform.scale(hint_icon, (60, 60)) # Resize the hint icon

        game.screen.blit(background, (0, 0))

        # Draw the hint piece
        if self.ai_hint_index is not None and self.ai_hint_position is not None and self.hint_pressed:
            game_data = copy.deepcopy(self.game_data)
            piece = self.game_data.pieces[self.ai_hint_index] if self.game_data.pieces[self.ai_hint_index] is not None else self.selected_piece
            place_piece(game_data, piece, self.ai_hint_position, True)
            draw_board(game.screen, game_data.board)
        else:
            draw_board(game.screen, self.game_data.board)

        mx, my = pygame.mouse.get_pos()
        px, py = mx // CELL_SIZE, (my // CELL_SIZE) - GRID_OFFSET_Y

        # Draw the list of pieces
        for i, piece in enumerate(self.game_data.pieces):
            if piece is not None:
                draw_piece(game.screen, piece, (i*PIECES_LIST_BETWEEN_OFFSET_X_CELLS+PIECES_LIST_OFFSET_X_CELLS, PIECES_LIST_OFFSET_Y_CELLS), False)

        if self.selected_piece is not None:
            draw_piece(game.screen, self.selected_piece, (px, py), True, GRID_OFFSET_Y)

        # Hint button
        if self.ai_hint_index is None or self.ai_hint_position is None:
            # If no hint is available, grey out the hint button
            self.hint_button = pygame.draw.circle(game.screen, (128, 128, 128), (SCREEN_WIDTH - 50, 50), 30)
            greyed_hint_icon = hint_icon.copy()
            greyed_hint_icon.fill(GRAY, special_flags=pygame.BLEND_RGBA_MULT)
            greyed_hint_text = font.render('H', True, GRAY)
            game.screen.blit(greyed_hint_icon, self.hint_button.topleft)
            game.screen.blit(greyed_hint_text, (self.hint_button.right - 18, self.hint_button.bottom - 18))
        elif self.hint_button.collidepoint(mx, my):
            self.hint_button = pygame.draw.circle(game.screen, BROWN, (SCREEN_WIDTH - 50, 50), 30)
            game.screen.blit(hint_icon, self.hint_button.topleft)
            game.screen.blit(hint_text, (self.hint_button.right - 18, self.hint_button.bottom - 18))

        draw_score(game.screen, self.score)
        pygame.display.flip()

    def render_ai(self, game):
        background = pygame.image.load(BACKGROUND_GAME_PATH)
        font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)

        game.screen.blit(background, (0, 0))

        draw_board(game.screen, self.game_data.board)

        # Draw the list of pieces
        for i, piece in enumerate(self.game_data.pieces):
            if piece is not None:
                draw_piece(game.screen, piece, (i*PIECES_LIST_BETWEEN_OFFSET_X_CELLS+PIECES_LIST_OFFSET_X_CELLS, PIECES_LIST_OFFSET_Y_CELLS), False)

        if self.selected_piece is not None:
            if self.ai_current_pos != self.ai_target_pos:
                px, py = self.ai_current_pos[0] / CELL_SIZE, self.ai_current_pos[1] / CELL_SIZE
                draw_piece(game.screen, self.selected_piece, (px, py), True)

                cx, cy = self.ai_current_pos
                tx, ty = self.ai_target_pos
                distance = math.sqrt((tx - cx) ** 2 + (ty - cy) ** 2)
                speed = 20
                if distance < speed:
                    self.ai_current_pos = self.ai_target_pos
                else:
                    # Calculate the direction vector
                    direction_x = tx - self.ai_initial_pos[0]
                    direction_y = ty - self.ai_initial_pos[1]

                    norm = math.sqrt(direction_x ** 2 + direction_y ** 2)
                    direction_x /= norm
                    direction_y /= norm

                    step_x = speed * direction_x
                    step_y = speed * direction_y

                    self.ai_current_pos = (cx + step_x, cy + step_y)


        # The AI is running, show the time elapsed
        if self.ai_running_start_time is not None:
            elapsed_time = time.time() - self.ai_running_start_time
            elapsed_time_text = font.render(f'Time Elapsed: {elapsed_time:.3f} seconds', True, WHITE)
            elapsed_time_rect = elapsed_time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)  # Set transparency level (0-255)
            overlay.fill((128, 128, 128))  # Grey color
            game.screen.blit(overlay, (0, 0))
            game.screen.blit(elapsed_time_text, elapsed_time_rect)

        draw_score(game.screen, self.score)
        pygame.display.flip()

    def exit(self, screen):
        print("Exiting Gameplay")

        # If the game is done, show the final state for a while, then move to the next state
        if self.done:
            screen_wrapper = ScreenWrapper(screen)
            self.render(screen_wrapper)
            time.sleep(0.8)


        # Stop the AI algorithm running in the background
        # This way, it also stops when the game is paused (which is kind of a waste of time)
        # self.ai_algorithm.stop()

class PauseState(GameState):
    """Pause menu

    """

    def __init__(self):
        self.keyboard_active = False
        self.selected_option = None
        self.resume_rect = None
        self.exit_rect = None

    def enter(self, screen):
        print("Game Paused")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                # Get the GameplayState and stop the AI algorithm
                game.state_manager.pop_state()
                game.state_manager.peek_state().ai_algorithm.stop()
                raise QuitGameException()
            # Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.resume_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
                elif self.exit_rect.collidepoint(event.pos):
                    game.state_manager.pop_state()
                    game.state_manager.peek_state().ai_algorithm.stop()
                    game.state_manager.switch_to_base_state(MainMenuState())
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                    self.keyboard_active = True

                if event.key in [pygame.K_r, pygame.K_ESCAPE, pygame.K_p]:
                    game.state_manager.pop_state()
                elif event.key == pygame.K_BACKSPACE:
                    game.state_manager.pop_state()
                    game.state_manager.peek_state().ai_algorithm.stop()
                    game.state_manager.switch_to_base_state(MainMenuState())
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 2
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 2
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.pop_state()
                    elif self.selected_option == 1:
                        game.state_manager.pop_state()
                        game.state_manager.peek_state().ai_algorithm.stop()
                        game.state_manager.switch_to_base_state(MainMenuState())

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.resume_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.exit_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, game):
        title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        text_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)

        pause_text = title_font.render('Pause', True, WHITE)
        resume_text = text_font.render('Resume', True, ORANGE if self.selected_option == 0 else WHITE)
        exit_text = text_font.render('Quit', True, ORANGE if self.selected_option == 1 else WHITE)

        # Non-interactable rectangles
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        # Interactable rectangles
        self.resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.5))
        self.exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        game.screen.fill(BROWN)
        game.screen.blit(pause_text, pause_rect)
        game.screen.blit(resume_text, self.resume_rect)
        game.screen.blit(exit_text, self.exit_rect)
        pygame.display.flip()

    def exit(self, screen):
        print("Exiting Pause")

class GameOverState(GameState):
    """Game Over menu

    """

    def __init__(self, score, player, ai_algorithm, level):
        self.score = score
        self.player = player
        self.ai_algorithm = ai_algorithm
        self.level = level

        self.keyboard_active = False
        self.selected_option = None
        self.play_again_rect = None
        self.back_rect = None

    def enter(self, screen):
        print("Entering Game Over")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                raise QuitGameException()
            # Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.play_again_rect.collidepoint(event.pos):
                    game.state_manager.subst_below_switch_to(GameplayState(self.player, self.ai_algorithm, self.level))
                elif self.back_rect.collidepoint(event.pos):
                    # Pop the GameOverState and the GameplayState
                    game.state_manager.pop_state(2)
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                    self.keyboard_active = True

                if event.key == pygame.K_BACKSPACE:
                    game.state_manager.pop_state(2)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % 2
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % 2
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0:
                        game.state_manager.subst_below_switch_to(GameplayState(self.player, self.ai_algorithm, self.level))
                    elif self.selected_option == 1:
                        game.state_manager.pop_state(2)

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.play_again_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 1
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, game):
        title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        subtitle_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
        text_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)

        game_over_text = title_font.render('Game Over', True, WHITE)
        score_text = subtitle_font.render(f'Score: {self.score}', True, ORANGE)
        play_again_text = text_font.render('Play Again', True, ORANGE if self.selected_option == 0 else WHITE)
        back_text = text_font.render('Go Back', True, ORANGE if self.selected_option == 1 else WHITE)

        # Non-interactable rectangles
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.5))

        # Interactable rectangles
        self.play_again_rect = play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.7))
        self.back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.4))

        game.screen.fill(BROWN)
        game.screen.blit(game_over_text, game_over_rect)
        game.screen.blit(score_text, score_rect)
        game.screen.blit(play_again_text, self.play_again_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self, screen):
        print("Exiting Game Over")

class LevelCompleteState(GameState):
    """Level Complete menu

    """

    def __init__(self, score, player, ai_algorithm, level):
        self.score = score
        self.player = player
        self.ai_algorithm = ai_algorithm
        self.level = level

        self.keyboard_active = False
        self.selected_option = None
        self.next_level_rect = None
        self.play_next_rect = None
        self.back_rect = None

    def enter(self, screen):
        print("Entering Level Complete")
        self.keyboard_active = False
        self.selected_option = None

    def update(self, game, events):
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_q)):
                raise QuitGameException()
            # Mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.level != LEVELS[-1] and self.next_level_rect is not None and self.next_level_rect.collidepoint(event.pos):
                    game.state_manager.subst_below_switch_to(GameplayState(self.player, self.ai_algorithm, self.level + 1))
                elif self.play_next_rect.collidepoint(event.pos):
                    game.state_manager.subst_below_switch_to(GameplayState(self.player, self.ai_algorithm, self.level))
                elif self.back_rect.collidepoint(event.pos):
                    game.state_manager.pop_state(2)
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s]:
                    self.keyboard_active = True

                if event.key == pygame.K_BACKSPACE:
                    game.state_manager.pop_state()
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option - 1) % (3 if self.level != LEVELS[-1] else 2)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    if self.selected_option is None:
                        self.selected_option = 0
                    else:
                        self.selected_option = (self.selected_option + 1) % (3 if self.level != LEVELS[-1] else 2)
                elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    if self.selected_option == 0 and self.level != LEVELS[-1]:
                        game.state_manager.subst_below_switch_to(GameplayState(self.player, self.ai_algorithm, self.level + 1))
                    elif (self.selected_option == 1 and self.level != LEVELS[-1]) or (self.selected_option == 0 and self.level == LEVELS[-1]):
                        game.state_manager.subst_below_switch_to(GameplayState(self.player, self.ai_algorithm, self.level))
                    elif (self.selected_option == 2 and self.level != LEVELS[-1]) or (self.selected_option == 1 and self.level == LEVELS[-1]):
                        game.state_manager.pop_state(2)

        # Update selected option based on mouse position
        # Must be after the keyboard events to avoid overriding the selected option (mouse has priority)
        mouse_pos = pygame.mouse.get_pos()
        if self.level != LEVELS[-1] and self.next_level_rect is not None and self.next_level_rect.collidepoint(mouse_pos):
            self.selected_option = 0
        elif self.play_next_rect.collidepoint(mouse_pos):
            self.selected_option = 1 if self.level != LEVELS[-1] else 0
        elif self.back_rect.collidepoint(mouse_pos):
            self.selected_option = 2 if self.level != LEVELS[-1] else 1
        elif not self.keyboard_active:
            self.selected_option = None

    def render(self, game):
        title_font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
        text_font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)

        level_complete_text = title_font.render('Level Complete', True, WHITE)
        score_text = text_font.render(f'Score: {self.score}', True, ORANGE)
        if self.level != LEVELS[-1]:
            next_level_text = text_font.render('Next Level', True, ORANGE if self.selected_option == 0 else WHITE)
            play_next_text = text_font.render('Retry Level', True, ORANGE if self.selected_option == 1 else WHITE)
            back_text = text_font.render('Go Back', True, ORANGE if self.selected_option == 2 else WHITE)
        else:
            play_next_text = text_font.render('Retry Level', True, ORANGE if self.selected_option == 0 else WHITE)
            back_text = text_font.render('Go Back', True, ORANGE if self.selected_option == 1 else WHITE)

        # Non-interactable rectangles
        level_complete_rect = level_complete_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.5))

        # Interactable rectangles
        if self.level != LEVELS[-1]:
            self.next_level_rect = next_level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.7))
        self.play_next_rect = play_next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
        self.back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.3))

        game.screen.fill(BROWN)
        game.screen.blit(level_complete_text, level_complete_rect)
        game.screen.blit(score_text, score_rect)
        if self.level != LEVELS[-1]:
            game.screen.blit(next_level_text, self.next_level_rect)
        game.screen.blit(play_next_text, self.play_next_rect)
        game.screen.blit(back_text, self.back_rect)
        pygame.display.flip()

    def exit(self, screen):
        print("Exiting Level Complete")
