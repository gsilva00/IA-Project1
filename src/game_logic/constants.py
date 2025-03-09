# Constants for the game:

# Constant variables for screen size
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700

# Constant variables for the board
CELL_SIZE = 50
GRID_SIZE = 8

# Colors
BACKGROUND_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GRAY = (200, 200, 200)
FILLED_COLOR = (100, 100, 255)

'''
    Shapes for the pieces in the game:

    Each shape is a list of (x, y) coordinates
    The origin (0, 0) is the top-left corner of the piece
'''
PIECES = [
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
    [(0, 0), (1, 0), (1, 1), (2, 0)]
]
