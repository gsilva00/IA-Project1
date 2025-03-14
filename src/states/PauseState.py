import sys
import pygame

from game_logic.constants import BROWN, FONT_PATH, FONT_TEXT_SMALL_SIZE, FONT_TITLE_SIZE, ORANGE, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from states import GameState, MainMenuState


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
