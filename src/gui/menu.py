import pygame
from game_logic.constants import SCREEN_WIDTH, SCREEN_HEIGHT

def draw_menu(screen):
    pygame.init()
    font = pygame.font.Font(None, 74)
    title_text = font.render('Wood Block', True, (255, 255, 255))
    
    play_text = font.render('Play', True, (255, 255, 255))
    quit_text = font.render('Quit', True, (255, 255, 255))

    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 4))
    play_rect = play_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    quit_rect = quit_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 1.5))

    running = True
    while running:
        screen.fill((0, 0, 0))

        mouse_pos = pygame.mouse.get_pos()

        if play_rect.collidepoint(mouse_pos):
            play_text = font.render('Play', True, (255, 0, 0))
        else:
            play_text = font.render('Play', True, (255, 255, 255))

        if quit_rect.collidepoint(mouse_pos):
            quit_text = font.render('Quit', True, (255, 0, 0))
        else:
            quit_text = font.render('Quit', True, (255, 255, 255))

        screen.blit(title_text, title_rect)
        screen.blit(play_text, play_rect)
        screen.blit(quit_text, quit_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(event.pos):
                    print("Play button clicked")
                    running = False
                elif quit_rect.collidepoint(event.pos):
                    print("Quit button clicked")
                    pygame.quit()
                    exit()

    pygame.quit()