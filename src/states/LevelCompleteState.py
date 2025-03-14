import pygame
from game_logic.constants import BROWN, FONT_PATH, FONT_TEXT_SMALL_SIZE, FONT_TITLE_SIZE, ORANGE, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from states import GameState


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
        for event in events:
            if event.type == pygame.QUIT:
                game.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.next_level_rect.collidepoint(event.pos) or self.play_next_rect.collidepoint(event.pos):
                    game.change_state(self.level)
                if self.back_rect.collidepoint(event.pos):
                    game.change_state('menu')

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
