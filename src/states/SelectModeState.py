import sys
import pygame

from game_logic.constants import BACKGROUND_MENU_PATH, BROWN, FONT_PATH, FONT_TEXT_SIZE, FONT_TITLE_SIZE, INFINITE, ORANGE, WHITE
from states import GameState, GameplayState, SelectLevelState


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
