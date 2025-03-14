import sys
import pygame

from game_logic.constants import BACKGROUND_MENU_PATH, BROWN, FONT_PATH, FONT_TEXT_SIZE, FONT_TITLE_SIZE, ORANGE, WHITE
from states import GameState, SelectPlayerState


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
