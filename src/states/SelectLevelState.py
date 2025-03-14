import sys
import pygame

from game_logic.constants import BACKGROUND_MENU_PATH, BROWN, FONT_PATH, FONT_TEXT_SIZE, FONT_TITLE_SIZE, LEVEL_1, LEVEL_2, LEVEL_3, ORANGE, WHITE
from states import GameState, GameplayState


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
