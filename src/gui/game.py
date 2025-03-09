import pygame
from game_logic.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, CELL_SIZE, BACKGROUND_COLOR, WHITE, RED, GRAY, FILLED_COLOR
from game_logic.rules import generate_shapes, place_piece, check_full_lines, is_valid_position, no_more_valid_moves

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

    running = True
    while running:
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    return 'play_again'
                elif menu_rect.collidepoint(event.pos):
                    return 'menu'

    pygame.quit()

def play(screen):
    clock = pygame.time.Clock()

    while True:
        board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        shapes = generate_shapes()
        selected_shape = None
        score = 0
        grid_offset_y = 2

        running = True
        game_over = False
        while running:
            screen.fill(BACKGROUND_COLOR)

            if game_over:
                action = draw_game_over(screen, score)
                if action == 'play_again':
                    break
                elif action == 'menu':
                    return 'menu'
            else:
                draw_board(screen, board, grid_offset_y)

                mx, my = pygame.mouse.get_pos()
                px, py = mx // CELL_SIZE, (my // CELL_SIZE) - grid_offset_y

                for i, shape in enumerate(shapes):
                    draw_shape(screen, shape, (GRID_SIZE + 2, i * 5), WHITE)

                if selected_shape is not None:
                    draw_shape(screen, selected_shape, (px, py), WHITE, grid_offset_y)

                draw_score(screen, score)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if selected_shape is None:
                            for i, shape in enumerate(shapes):
                                if GRID_SIZE * CELL_SIZE <= mx <= SCREEN_WIDTH and i * 5 * CELL_SIZE <= my <= (i * 5 + 4) * CELL_SIZE:
                                    selected_shape = shape
                                    break

                    if event.type == pygame.MOUSEBUTTONUP:
                        if selected_shape is not None:
                            if is_valid_position(board, selected_shape, (px, py)):
                                place_piece(board, selected_shape, (px, py))
                                lines_cleared = check_full_lines(board)
                                score += lines_cleared
                                shapes.remove(selected_shape)
                                if not shapes:
                                    shapes = generate_shapes()
                                if no_more_valid_moves(board, shapes):
                                    game_over = True
                            selected_shape = None

            pygame.display.flip()
            clock.tick(60)

        if not running:
            break

    pygame.quit()
    return 'menu'