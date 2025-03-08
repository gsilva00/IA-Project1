import pygame
from gui.menu import draw_menu

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    draw_menu(screen)

if __name__ == "__main__":
    main()
