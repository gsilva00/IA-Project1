import sys
import pygame

from game_logic.constants import BROWN, FONT_PATH, FONT_TEXT_SMALL_SIZE, FONT_TITLE_SIZE, ORANGE, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from states import GameState, GameplayState


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
