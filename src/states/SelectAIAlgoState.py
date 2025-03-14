import sys
import pygame

from game_logic.constants import A_STAR, BACKGROUND_MENU_PATH, BFS, BROWN, DFS, FONT_PATH, FONT_TEXT_SIZE, FONT_TITLE_SIZE, GREEDY, ITER_DEEP, ORANGE, UNIFORM_COST, WEIGHTED_A_STAR, WHITE
from states import GameState, SelectModeState


class SelectAIAlgoState(GameState):
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
