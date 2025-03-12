import pygame
import os #para importar imagem
from gui.menu import draw_menu
from gui.game import play

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 700))
    pygame.display.set_caption("Wood Block")
    
    #Add Icon
    icon_path = os.path.join(os.path.dirname(__file__), 'images', 'game_icon.png')
    icon = pygame.image.load(icon_path)
    pygame.display.set_icon(icon)

    while True:
        draw_menu(screen)
        action = play(screen)
        if action == 'menu':
            continue
        elif action == 'play_again':
            continue

if __name__ == "__main__":
    main()
