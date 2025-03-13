import pygame
from game_logic.constants import WHITE, BROWN, ORANGE, FONT_PATH, FONT_TITLE_SIZE, FONT_TEXT_SIZE, BACKGROUND_MENU_IMAGE

def draw_menu(screen):
    font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
    title_text_back = font.render('Wood Block', True, BROWN)
    title_text_middle = font.render('Wood Block', True, ORANGE)
    title_text_front = font.render('Wood Block', True, WHITE)
    font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
    play_text = font.render('Play', True, WHITE)
    quit_text = font.render('Quit', True, WHITE)

    title_rect_back = title_text_back.get_rect(center=((screen.get_width() // 2) + 5 , (screen.get_height() // 4) - 5))
    title_rect_middle = title_text_middle.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
    title_rect_front = title_text_front.get_rect(center=((screen.get_width() // 2) - 5 , (screen.get_height() // 4) + 5))
    play_rect = play_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    quit_rect = quit_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.5))

    background = pygame.image.load(BACKGROUND_MENU_IMAGE)
    screen.blit(background, (0, 0))

    mouse_pos = pygame.mouse.get_pos()
    if play_rect.collidepoint(mouse_pos):
        play_text = font.render('Play', True, WHITE)
    else:
        play_text = font.render('Play', True, BROWN)

    if quit_rect.collidepoint(mouse_pos):
        quit_text = font.render('Quit', True, WHITE)
    else:
        quit_text = font.render('Quit', True, BROWN)

    screen.blit(title_text_back, title_rect_back)
    screen.blit(title_text_middle, title_rect_middle)
    screen.blit(title_text_front, title_rect_front)
    screen.blit(play_text, play_rect)
    screen.blit(quit_text, quit_rect)
    pygame.display.flip()

    return play_rect, quit_rect
