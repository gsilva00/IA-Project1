import pygame
from game_logic.constants import WHITE, BROWN, ORANGE, FONT_PATH, FONT_TITLE_SIZE, FONT_TEXT_SIZE, BACKGROUND_MENU_PATH


def draw_select_level(screen):
    font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
    title_text_back = font.render('Level Select', True, BROWN)
    title_text_middle = font.render('Level Select', True, ORANGE)
    title_text_front = font.render('Level Select', True, WHITE)
    font = pygame.font.Font(FONT_PATH, FONT_TEXT_SIZE)
    level_1_text = font.render('Level 1', True, WHITE)
    level_2_text = font.render('Level 2', True, WHITE)
    level_3_text = font.render('Level 3', True, WHITE)
    menu_text = font.render('Go Back', True, WHITE)

    title_rect_back = title_text_back.get_rect(center=((screen.get_width() // 2) + 5 , (screen.get_height() // 4) - 5))
    title_rect_middle = title_text_middle.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
    title_rect_front = title_text_front.get_rect(center=((screen.get_width() // 2) - 5 , (screen.get_height() // 4) + 5))
    level_1_rect = level_1_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2.5))
    level_2_rect = level_2_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    level_3_rect = level_3_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.5))
    menu_rect = menu_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.2))

    background = pygame.image.load(BACKGROUND_MENU_PATH)
    screen.blit(background, (0, 0))

    mouse_pos = pygame.mouse.get_pos()
    if level_1_rect.collidepoint(mouse_pos):
        level_1_text = font.render('Level 1', True, WHITE)
    else:
        level_1_text = font.render('Level 1', True, BROWN)
    
    if level_2_rect.collidepoint(mouse_pos):
        level_2_text = font.render('Level 2', True, WHITE)
    else:
        level_2_text = font.render('Level 2', True, BROWN)

    if level_3_rect.collidepoint(mouse_pos):
        level_3_text = font.render('Level 3', True, WHITE)
    else:
        level_3_text = font.render('Level 3', True, BROWN)

    if menu_rect.collidepoint(mouse_pos):
        menu_text = font.render('Go Back', True, ORANGE)
    else:
        menu_text = font.render('Go Back', True, WHITE)

    screen.blit(title_text_back, title_rect_back)
    screen.blit(title_text_middle, title_rect_middle)
    screen.blit(title_text_front, title_rect_front)
    screen.blit(level_1_text, level_1_rect)
    screen.blit(level_2_text, level_2_rect)
    screen.blit(level_3_text, level_3_rect)
    screen.blit(menu_text, menu_rect)
    pygame.display.flip()

    return level_1_rect, level_2_rect, level_3_rect, menu_rect
