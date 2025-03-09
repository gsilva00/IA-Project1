import pygame
from gui.menu import draw_menu
from gui.game import play

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("Infinite")

    while True:
        draw_menu(screen)
        action = play(screen)
        if action == 'menu':
            continue
        elif action == 'play_again':
            continue

if __name__ == "__main__":
    main()
