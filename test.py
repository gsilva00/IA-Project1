import random
import pygame

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 800
GRID_SIZE = 10
CELL_SIZE = 40
BOARD_WIDTH = GRID_SIZE * CELL_SIZE
BOARD_HEIGHT = GRID_SIZE * CELL_SIZE
BACKGROUND_COLOR = (30, 30, 30)

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
FILLED_COLOR = (100, 100, 255)

# Shapes: Each shape is a list of (x, y) coordinates
SHAPES = [
    [(0, 0)],
    [(0, 0), (1, 0)],
    [(0, 0), (0, 1)],
    [(0, 0), (1, 0), (0, 1)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],
    [(0, 0), (1, 0), (2, 0), (0, 1)],
    [(0, 0), (1, 0), (2, 0), (2, 1)],
    [(0, 0), (1, 0), (2, 0), (1, 1)],
    [(0, 0), (1, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (1, 1), (1, 2)],
    [(0, 0), (0, 1), (1, 1), (1, 2)],
    [(0, 0), (1, 0), (1, 1), (2, 1)],
    [(0, 0), (1, 0), (1, 1), (2, 0)],
]

# Game initialization
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Block Blast Infinite")

clock = pygame.time.Clock()

# Functions
def draw_board(board):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if board[y][x]:
                pygame.draw.rect(screen, FILLED_COLOR, rect)  # Draw filled cells
            pygame.draw.rect(screen, GRAY, rect, 1)  # Draw grid

def generate_shapes():
    return [random.choice(SHAPES) for _ in range(3)]

def place_shape(board, shape, position):
    px, py = position
    for x, y in shape:
        board[py + y][px + x] = 1

def check_full_lines(board):
    # Check rows
    for y in range(GRID_SIZE):
        if all(board[y]):
            board[y] = [0] * GRID_SIZE

    # Check columns
    for x in range(GRID_SIZE):
        if all(board[y][x] for y in range(GRID_SIZE)):
            for y in range(GRID_SIZE):
                board[y][x] = 0

def is_valid_position(board, shape, position):
    px, py = position
    for x, y in shape:
        if not (0 <= px + x < GRID_SIZE and 0 <= py + y < GRID_SIZE):
            return False
        if board[py + y][px + x]:
            return False
    return True

def draw_shape(shape, position, color):
    px, py = position
    for x, y in shape:
        rect = pygame.Rect((px + x) * CELL_SIZE, (py + y) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)

def main():
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    shapes = generate_shapes()
    selected_shape = None
    shape_origin = None

    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)

        draw_board(board)

        # Get mouse position and snap to grid
        mx, my = pygame.mouse.get_pos()
        px, py = mx // CELL_SIZE, my // CELL_SIZE

        # Draw shape options
        for i, shape in enumerate(shapes):
            draw_shape(shape, (GRID_SIZE + 2, i * 4), WHITE)

        # Draw selected shape preview
        if selected_shape is not None:
            draw_shape(selected_shape, (px, py), WHITE)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Select a shape
                if selected_shape is None:
                    for i, shape in enumerate(shapes):
                        if GRID_SIZE * CELL_SIZE <= mx <= SCREEN_WIDTH and i * 4 * CELL_SIZE <= my <= (i * 4 + 3) * CELL_SIZE:
                            selected_shape = shape
                            shape_origin = (GRID_SIZE + 2, i * 4)
                            break

            if event.type == pygame.MOUSEBUTTONUP:
                if selected_shape is not None:
                    if is_valid_position(board, selected_shape, (px, py)):
                        place_shape(board, selected_shape, (px, py))
                        check_full_lines(board)
                        shapes.remove(selected_shape)
                        if not shapes:
                            shapes = generate_shapes()
                    selected_shape = None

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
