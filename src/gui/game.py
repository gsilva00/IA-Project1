import pygame
from game_logic.constants import *


def draw_board(screen, board):
    wood_dark = pygame.image.load(DARK_WOOD_PATH)
    wood_target = pygame.image.load(WOOD_PATH)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if board[y][x] == 1:
                screen.blit(wood_dark, (GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE))
            elif board[y][x] == 2:
                screen.blit(wood_target, (GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE))
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_shape(screen, shape, position, is_selected, offset_y=0):
    wood = pygame.image.load(WOOD_PATH)
    wood_light = pygame.image.load(LIGHT_WOOD_PATH)

    px, py = position
    for x, y in shape:
        rect = pygame.Rect((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if is_selected:
            screen.blit(wood_light, ((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE))
        else:
            screen.blit(wood, ((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE))
        pygame.draw.rect(screen, GRAY, rect,1)

def draw_score(screen, score):
    font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

def draw_game_over(screen, score):
    font = pygame.font.Font(FONT_PATH, FONT_TITLE_SIZE)
    game_over_text = font.render('Game Over', True, WHITE)
    font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)
    score_text = font.render(f'Score: {score}', True, ORANGE)
    play_again_text = font.render('Play Again', True, WHITE)
    menu_text = font.render('Go Back', True, WHITE)

    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.5))
    play_again_rect = play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.7))
    menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.4))

    screen.fill(BROWN)

    mouse_pos = pygame.mouse.get_pos()
    if play_again_rect.collidepoint(mouse_pos):
        play_again_text = font.render('Play Again', True, ORANGE)
    else:
        play_again_text = font.render('Play Again', True, WHITE)

    if menu_rect.collidepoint(mouse_pos):
        menu_text = font.render('Go Back', True, ORANGE)
    else:
        menu_text = font.render('Go Back', True, WHITE)

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(play_again_text, play_again_rect)
    screen.blit(menu_text, menu_rect)
    pygame.display.flip()

    return play_again_rect, menu_rect

def draw_game(screen, game_model, level_number=0):
    background = pygame.image.load(BACKGROUND_GAME_PATH)

    screen.blit(background, (0, 0))

    draw_board(screen, game_model.board)
    mx, my = pygame.mouse.get_pos()
    px, py = mx // CELL_SIZE, (my // CELL_SIZE) - GRID_OFFSET_Y

    for i, shape in enumerate(game_model.shapes):
        if game_model.shapes_visible[i] and (game_model.selected_shape is None or i != game_model.selected_index):
            draw_shape(screen, shape, (i*5+2, 10), False)

    if game_model.selected_shape is not None:
        draw_shape(screen, game_model.selected_shape, (px, py), True, GRID_OFFSET_Y)

    draw_score(screen, game_model.score)
