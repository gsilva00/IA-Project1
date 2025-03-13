import os

# Constants for the game:

# For screen size
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700

# For the board
CELL_SIZE = 50
GRID_SIZE = 8

# Colors
BACKGROUND_COLOR = (30, 30, 30)
BROWN = (60, 30, 20)
ORANGE = (255, 130, 60)
WHITE = (255, 255, 240)
RED = (255, 0, 0)
GRAY = (220, 210, 200)
FILLED_COLOR = (100, 100, 255)

# Font
FONT_PATH = os.path.join(os.path.dirname(__file__), '../images', 'YangBagus-DYMX9.ttf')
FONT_TITLE_SIZE = 74
FONT_TEXT_SIZE = 64
FONT_TEXT_SMALL_SIZE = 36

# Images
BACKGROUND_MENU_IMAGE = os.path.join(os.path.dirname(__file__), '../images', 'background3.png')

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
