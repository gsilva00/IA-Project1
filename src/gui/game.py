import pygame
from game_logic.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, CELL_SIZE, BACKGROUND_COLOR, WHITE, RED, GRAY, FILLED_COLOR

def draw_board(screen, board, offset_y):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, (y + offset_y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if board[y][x]:
                pygame.draw.rect(screen, FILLED_COLOR, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_shape(screen, shape, position, color, offset_y=0):
    px, py = position
    for x, y in shape:
        rect = pygame.Rect((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)

def draw_score(screen, score):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))

def draw_game_over(screen, score):
    font = pygame.font.Font(None, 74)
    game_over_text = font.render('Game Over', True, WHITE)
    score_text = font.render(f'Score: {score}', True, WHITE)

    play_again_text = font.render('Play Again', True, WHITE)
    menu_text = font.render('Menu', True, WHITE)

    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    play_again_rect = play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5))
    menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.2))

    screen.fill(BACKGROUND_COLOR)

    mouse_pos = pygame.mouse.get_pos()

    if play_again_rect.collidepoint(mouse_pos):
        play_again_text = font.render('Play Again', True, RED)
    else:
        play_again_text = font.render('Play Again', True, WHITE)

    if menu_rect.collidepoint(mouse_pos):
        menu_text = font.render('Go Back', True, RED)
    else:
        menu_text = font.render('Go Back', True, WHITE)

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(play_again_text, play_again_rect)
    screen.blit(menu_text, menu_rect)
    pygame.display.flip()

    return play_again_rect, menu_rect

def draw_game(screen, game_model):
    screen.fill(BACKGROUND_COLOR)
    draw_board(screen, game_model.board, game_model.grid_offset_y)

    mx, my = pygame.mouse.get_pos()
    px, py = mx // CELL_SIZE, (my // CELL_SIZE) - game_model.grid_offset_y

    for i, shape in enumerate(game_model.shapes):
        if game_model.shapes_visible[i] and (game_model.selected_shape is None or i != game_model.selected_index):
            draw_shape(screen, shape, (GRID_SIZE + 2, i * 5), WHITE)

    if game_model.selected_shape is not None:
        draw_shape(screen, game_model.selected_shape, (px, py), WHITE, game_model.grid_offset_y)

    draw_score(screen, game_model.score)
