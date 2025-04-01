import os

# Constants for the organization and structure of the game:

# For screen size
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700

# For the board
CELL_SIZE = 50
GRID_SIZE = 8
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2  # Board centered on screen (400 for the board, 200 on each side)
GRID_OFFSET_Y = 1

PIECES_LIST_OFFSET_X_CELLS = 2
PIECES_LIST_BETWEEN_OFFSET_X_CELLS = 5
PIECES_LIST_OFFSET_Y_CELLS = 10

# Colors (RGBA)
BACKGROUND_COLOR = (30, 30, 30, 255)
BROWN = (60, 30, 20, 255)
ORANGE = (255, 130, 60, 255)
WHITE = (255, 255, 240, 255)
RED = (255, 0, 0, 255)
GRAY = (220, 210, 200, 255)
FILLED_COLOR = (100, 100, 255, 255)

# Paths
_BASE_PATH = os.path.join(os.path.dirname(__file__), '../../')
_SRC_PATH = os.path.join(_BASE_PATH, 'src')
_ASSETS_PATH = os.path.join(_BASE_PATH, 'assets')
_FONTS_PATH = os.path.join(_ASSETS_PATH, 'fonts')
_IMAGES_PATH = os.path.join(_ASSETS_PATH, 'images')

DATA_PATH = os.path.join(_BASE_PATH, 'data')

# Font
FONT_PATH = os.path.join(_FONTS_PATH, 'YangBagus-DYMX9.ttf')
FONT_TITLE_SIZE = 74
FONT_TEXT_SIZE = 44
FONT_TEXT_SMALL_SIZE = 36
FONT_HINT_SIZE = 24

# Images
GAME_ICON_PATH = os.path.join(_IMAGES_PATH, 'game_icon.png')
GAME_ICON_MENU_PATH = os.path.join(_IMAGES_PATH, 'game_icon_menu.png')
BACKGROUND_MENU_PATH = os.path.join(_IMAGES_PATH, 'background_menu.png')
BACKGROUND_GAME_PATH = os.path.join(_IMAGES_PATH, 'background_game.png')
WOOD_PATH = os.path.join(_IMAGES_PATH, 'wood_square.png')
RED_WOOD_PATH = os.path.join(_IMAGES_PATH, 'red_wood_square.png')
LIGHT_WOOD_PATH = os.path.join(_IMAGES_PATH, 'light_wood_square.png')
DARK_WOOD_PATH = os.path.join(_IMAGES_PATH, 'dark_wood_square.png')
HINT_ICON_PATH = os.path.join(_IMAGES_PATH, 'hint_icon.png')


# --------------------------------------------------------------
# Constants for the game:

"""
    Pieces for the pieces in the game:

    Each piece is a list of (x, y) coordinates
    The origin (0, 0) is the top-left corner of the piece
"""
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

# For player type
HUMAN = 0
AI = 1

# For AI algorithm type
BFS = 0
DFS = 1
ITER_DEEP = 2
GREEDY = 3
A_STAR = 4
WEIGHTED_A_STAR = 5

# For levels
INFINITE = 0
LEVEL_1 = 1
LEVEL_2 = 2
LEVEL_3 = 3

LEVELS = [LEVEL_1, LEVEL_2, LEVEL_3]

# For level 1:
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

# For level 2:
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

# For level 3:
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

# --------------------------------------------------------------
# Constants for return values:

AI_NOT_FOUND = -1
AI_RUNNING = 0
AI_FOUND = 1
