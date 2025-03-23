import pygame

from game_logic.constants import CELL_SIZE, DARK_WOOD_PATH, FONT_PATH, FONT_TEXT_SMALL_SIZE, GRAY, GRID_OFFSET_X, GRID_OFFSET_Y, GRID_SIZE, LIGHT_WOOD_PATH, RED_WOOD_PATH, WHITE, WOOD_PATH


def draw_board(screen, board):
    """Draw the board

    Args:
        screen (pygame.Surface): The screen to draw on
        board (List[List[int]]): The board to draw
    """

    wood_dark = pygame.image.load(DARK_WOOD_PATH)
    wood_target = pygame.image.load(RED_WOOD_PATH)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if board[y][x] == 0.5:
                # Create a semi-transparent red surface
                red_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                red_surface.fill((255, 0, 0, 128))  # RGBA with alpha value 128 for transparency
                screen.blit(red_surface, (GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE))
            elif board[y][x] == 1:
                screen.blit(wood_dark, (GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE))
            elif board[y][x] == 2:
                screen.blit(wood_target, (GRID_OFFSET_X + x * CELL_SIZE, (y + GRID_OFFSET_Y) * CELL_SIZE))
            pygame.draw.rect(screen, GRAY, rect, 1)

def draw_piece(screen, piece, position, is_selected, offset_y=0):
    """Draw a piece on the board

    Args:
        screen (pygame.Surface): The screen to draw on
        piece (List[Tuple[int, int]]): The piece to draw
        position (Tuple[int, int]): The position to draw the piece
        is_selected (bool): Whether the piece is selected
        offset_y (int, optional): The vertical (y) offset to draw the piece. Defaults to 0.
    """

    wood = pygame.image.load(WOOD_PATH)
    wood_light = pygame.image.load(LIGHT_WOOD_PATH)

    px, py = position
    for x, y in piece:
        rect = pygame.Rect((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        if is_selected:
            screen.blit(wood_light, ((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE))
        else:
            screen.blit(wood, ((px + x) * CELL_SIZE, (py + y + offset_y) * CELL_SIZE))
        pygame.draw.rect(screen, GRAY, rect,1)

def draw_score(screen, score):
    """Draw the score on the screen

    Args:
        screen (pygame.Surface): The screen to draw on
        score (int): The score to draw
    """

    font = pygame.font.Font(FONT_PATH, FONT_TEXT_SMALL_SIZE)
    text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(text, (10, 10))
