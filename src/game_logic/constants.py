import os

# Constants for the game:

# For screen size
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700

# For the board
CELL_SIZE = 50
GRID_SIZE = 8
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 1

# Colors
BACKGROUND_COLOR = (30, 30, 30)
BROWN = (60, 30, 20)
ORANGE = (255, 130, 60)
WHITE = (255, 255, 240)
RED = (255, 0, 0)
GRAY = (220, 210, 200)
FILLED_COLOR = (100, 100, 255)

# Paths
_BASE_PATH = os.path.join(os.path.dirname(__file__), '../../')
_SRC_PATH = os.path.join(_BASE_PATH, 'src')
_ASSETS_PATH = os.path.join(_BASE_PATH, 'assets')
_FONT_PATH = os.path.join(_ASSETS_PATH, 'fonts')
_IMAGES_PATH = os.path.join(_ASSETS_PATH, 'images')

# Font
FONT_PATH = os.path.join(_FONT_PATH, 'YangBagus-DYMX9.ttf')
FONT_TITLE_SIZE = 74
FONT_TEXT_SIZE = 64
FONT_TEXT_SMALL_SIZE = 36

# Images
GAME_ICON_PATH = os.path.join(_IMAGES_PATH, 'game_icon.png')
BACKGROUND_MENU_PATH = os.path.join(_IMAGES_PATH, 'background_menu.png')
BACKGROUND_GAME_PATH = os.path.join(_IMAGES_PATH, 'background_game.png')
WOOD_PATH = os.path.join(_IMAGES_PATH, 'wood_square.png')
LIGHT_WOOD_PATH = os.path.join(_IMAGES_PATH, 'light_wood_square.png')
DARK_WOOD_PATH = os.path.join(_IMAGES_PATH, 'dark_wood_square.png')

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

# --------------------------------------------------------------

# Constants for the game:

# Constants for level 1:

LEVEL_1_BLOCKS = 4

LEVEL_1_BOARD = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,2,2,0,0,0],
    [0,0,0,2,2,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0]
]

# Constants for level 2:

LEVEL_2_BLOCKS = 16

LEVEL_2_BOARD = [
    [2,2,0,0,0,0,2,2],
    [2,0,0,0,0,0,0,2],
    [0,0,0,0,0,0,0,0],
    [0,0,0,2,2,0,0,0],
    [0,0,0,2,2,0,0,0],
    [0,0,0,0,0,0,0,0],
    [2,0,0,0,0,0,0,2],
    [2,2,0,0,0,0,2,2]
]

# Constants for level 3:

LEVEL_3_BLOCKS = 24

LEVEL_3_BOARD = [
    [0,2,0,0,0,0,2,0],
    [2,2,0,0,0,0,2,2],
    [0,0,2,2,2,2,0,0],
    [0,0,2,0,0,2,0,0],
    [0,0,2,0,0,2,0,0],
    [0,0,2,2,2,2,0,0],
    [2,2,0,0,0,0,2,2],
    [0,2,0,0,0,0,2,0]
]

LEVEL_BOARDS = {
    1: LEVEL_1_BOARD,
    2: LEVEL_2_BOARD,
    3: LEVEL_3_BOARD
}

LEVEL_BLOCKS = {
    1: LEVEL_1_BLOCKS,
    2: LEVEL_2_BLOCKS,
    3: LEVEL_3_BLOCKS
}
