import pygame
from game_logic.constants import WHITE, RED, BACKGROUND_COLOR

def draw_menu(screen):
    font = pygame.font.Font(None, 74)
    title_text = font.render('Wood Block', True, WHITE)

    play_text = font.render('Play', True, WHITE)
    quit_text = font.render('Quit', True, WHITE)

    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
    play_rect = play_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    quit_rect = quit_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.5))

    screen.fill(BACKGROUND_COLOR)

    mouse_pos = pygame.mouse.get_pos()

    if play_rect.collidepoint(mouse_pos):
        play_text = font.render('Play', True, RED)
    else:
        play_text = font.render('Play', True, WHITE)

    if quit_rect.collidepoint(mouse_pos):
        quit_text = font.render('Quit', True, RED)
    else:
        quit_text = font.render('Quit', True, WHITE)

    screen.blit(title_text, title_rect)
    screen.blit(play_text, play_rect)
    screen.blit(quit_text, quit_rect)
    pygame.display.flip()

    return play_rect, quit_rect
