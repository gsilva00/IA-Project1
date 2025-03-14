import sys
import pygame

from game_logic.constants import (AI, BACKGROUND_MENU_PATH, BROWN, FONT_PATH, FONT_TEXT_SIZE, FONT_TITLE_SIZE, ORANGE, PLAYER, WHITE)
from states import GameState, SelectAIAlgoState


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
                    game.state_manager.push_state(SelectAIAlgoState(PLAYER))
                elif self.ai_rect.collidepoint(event.pos):
                    game.state_manager.push_state(SelectAIAlgoState(AI))
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
