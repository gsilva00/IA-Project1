from __future__ import annotations

from enum import IntEnum
from pathlib import Path
from typing import ClassVar, TypeAlias, TypeVar


class ScreenConfig:
    """ScreenConfig configuration."""

    # Sizes
    WIDTH: ClassVar[int] = 800
    HEIGHT: ClassVar[int] = 700


class BoardConfig:
    """BoardConfig configuration."""

    CELL_SIZE: ClassVar[int] = 50
    GRID_SIZE: ClassVar[int] = 8
    ROW_SIZE: ClassVar[int] = GRID_SIZE
    COL_SIZE: ClassVar[int] = GRID_SIZE

    # Board centered on screen (400 for the board, 200 on each side)
    GRID_OFFSET_X: ClassVar[int] = (ScreenConfig.WIDTH - COL_SIZE * CELL_SIZE) // 2
    GRID_OFFSET_Y: ClassVar[int] = 1


class PieceListOffset:
    """Offset for the piece list in the UI."""

    X_CELLS: ClassVar[int] = 2
    BETWEEN_X_CELLS: ClassVar[int] = 5
    Y_CELLS: ClassVar[int] = 10


Color: TypeAlias = tuple[int, int, int]  # (Red, Green, Blue)
ColorA: TypeAlias = tuple[int, int, int, int]  # (Red, Green, Blue, Alpha)


class ColorConfig:
    """Color configuration (RGBA)."""

    BACKGROUND: ClassVar[ColorA] = (30, 30, 30, 255)
    BLACK: ClassVar[ColorA] = (0, 0, 0, 255)
    BROWN: ClassVar[ColorA] = (60, 30, 20, 255)
    DARK_GRAY: ClassVar[ColorA] = (128, 128, 128, 255)
    FILLED: ClassVar[ColorA] = (100, 100, 255, 255)
    GRAY: ClassVar[ColorA] = (220, 210, 200, 255)
    ORANGE: ClassVar[ColorA] = (255, 130, 60, 255)
    RED: ClassVar[ColorA] = (255, 0, 0, 255)
    WHITE: ClassVar[ColorA] = (255, 255, 240, 255)


class PathConfig:
    """Path configuration for the game assets."""

    BASE: ClassVar[Path] = Path(__file__).parent.parent.parent
    DATA: ClassVar[Path] = BASE / "data"
    DOCS: ClassVar[Path] = BASE / "docs"
    WOODBLOCK: ClassVar[Path] = BASE / "woodblock"
    ASSETS: ClassVar[Path] = WOODBLOCK / "assets"
    FONTS: ClassVar[Path] = ASSETS / "fonts"
    IMAGES: ClassVar[Path] = ASSETS / "images"
    CUSTOM: ClassVar[Path] = WOODBLOCK / "custom"


class FontConfig:
    """Font configuration for the game."""

    PATH: ClassVar[Path] = PathConfig.FONTS / "YangBagus-DYMX9.ttf"
    TITLE_SIZE: ClassVar[int] = 74
    TEXT_SIZE: ClassVar[int] = 44
    TEXT_SMALL_SIZE: ClassVar[int] = 36
    HINT_SIZE: ClassVar[int] = 24


class ImageConfig:
    """Image paths for the game assets."""

    APP_GAME_ICON: ClassVar[Path] = PathConfig.IMAGES / "game_icon.png"
    MENU_GAME_ICON: ClassVar[Path] = PathConfig.IMAGES / "game_icon_menu.png"
    BACKGROUND_MENU: ClassVar[Path] = PathConfig.IMAGES / "background_menu.png"
    BACKGROUND_GAME: ClassVar[Path] = PathConfig.IMAGES / "background_game.png"
    WOOD: ClassVar[Path] = PathConfig.IMAGES / "wood_square.png"
    RED_WOOD: ClassVar[Path] = PathConfig.IMAGES / "red_wood_square.png"
    LIGHT_WOOD: ClassVar[Path] = PathConfig.IMAGES / "light_wood_square.png"
    DARK_WOOD: ClassVar[Path] = PathConfig.IMAGES / "dark_wood_square.png"
    HINT_ICON: ClassVar[Path] = PathConfig.IMAGES / "hint_icon.png"


_Position: TypeAlias = tuple[int, int]  # (x, y) coordinates
_AIPosition: TypeAlias = tuple[float, float]  # (x, y) but float to move across the board freely
PiecePosition: TypeAlias = _Position  # Top-left corner of the piece
AIPiecePosition: TypeAlias = _AIPosition  # Top-left corner of the piece (AI)
Block: TypeAlias = _Position  # Position relative to the enclosing piece's top-left corner
Piece: TypeAlias = list[Block]
PlayablePiece: TypeAlias = Piece | None
PieceHand: TypeAlias = list[Piece]
PlayablePieceHand: TypeAlias = list[PlayablePiece]
PIECES: list[Piece] = [
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


class CellType(IntEnum):
    """Block types for the BoardConfig."""

    HINT = -1
    EMPTY = 0
    PLAYER = 1
    TARGET = 2  # Resistance: 1 hit
    # TODO: Add more target types (more resistant)
    # TODO: New target types need to follow the incrementing (+1) value pattern
    # TODO: due to resistance/hit levels definition in Cell implementation.


class Cell:
    """Cell class to represent a cell in the game BoardConfig.

    Attributes:
        type (CellType): The type of the cell.
        hits (int): The number of hits the cell can take.
        can_hit (bool): Whether the cell can be hit.

    """

    def __init__(self, cell_type: CellType) -> None:
        self.type = cell_type

        if cell_type in {CellType.HINT, CellType.EMPTY}:
            self.hits = 0
        elif cell_type == CellType.PLAYER:
            self.hits = cell_type.value
        else:
            # Cell is a target
            self.hits = cell_type.value - 1

        self.can_hit = cell_type not in {CellType.HINT, CellType.EMPTY}

    def __eq__(self, other: object) -> bool:
        """Determine if two Cell objects are equal."""
        if not isinstance(other, Cell):
            return False
        return self.type == other.type and self.hits == other.hits and self.can_hit == other.can_hit

    def __hash__(self) -> int:
        """Generate a hash value for the Cell object."""
        return hash((self.type, self.hits, self.can_hit))

    def empty(self) -> Cell:
        """Empty the cell.

        New instance created to maintain immutability of Cell.
        Not needed if Cell is not used in dicts or sets, but kept for consistency.
        - Mutability can lead to changes in hash that affect dict/set lookups.
        """
        # self.type = CellType.EMPTY  # noqa: ERA001
        # self.hits = 0  # noqa: ERA001
        # self.can_hit = False  # noqa: ERA001
        return Cell(CellType.EMPTY)

    def hit(self) -> Cell:
        """Apply a hit to the cell.

        New instance created to maintain immutability of Cell.
        Not needed if Cell is not used in dicts or sets, but kept for consistency.
        - Mutability can lead to changes in hash that affect dict/set lookups.
        """
        # if self.hits > 1:
        #     self.hits -= 1  # noqa: ERA001
        # else:  # noqa: ERA001
        #     self.empty()  # noqa: ERA001
        if not self.can_hit:
            # Doesn't accept being called on HINT or EMPTY cells
            raise ValueError(f"Cannot hit a cell that cannot be hit. Cell: {self}")

        if self.hits > 1:
            # Stronger target
            return Cell(CellType(self.type.value - 1))
        # Cell is destroyed
        return self.empty()


class BoardUtils:
    """Game board utilities."""

    @staticmethod
    def from_types_board(matrix: TypesBoard) -> Board:
        """Convert a board of CellTypes to a board of Cells."""
        return [[Cell(cell_type) for cell_type in row] for row in matrix]

    @staticmethod
    def to_types_board(board: Board) -> TypesBoard:
        """Convert a board of Cells to a board of CellTypes."""
        return [[cell.type for cell in row] for row in board]

    @staticmethod
    def types_board_from_ints(matrix: IntsBoard) -> TypesBoard:
        """Convert a board of integers to a board of CellTypes."""
        return [[CellType(cell) for cell in row] for row in matrix]

    @staticmethod
    def ints_from_types_board(matrix: TypesBoard) -> IntsBoard:
        """Convert a board of CellTypes to a board of integers."""
        return [[cell.value for cell in row] for row in matrix]

    @staticmethod
    def from_int_matrix(matrix: IntsBoard) -> Board:
        """Convert a board of integers to a board of Cells."""
        return BoardUtils.from_types_board(BoardUtils.types_board_from_ints(matrix))

    @staticmethod
    def to_int_matrix(board: Board) -> IntsBoard:
        """Convert a board of Cells to a board of integers."""
        return BoardUtils.ints_from_types_board(BoardUtils.to_types_board(board))


class Level(IntEnum):
    """Game levels enumeration."""

    CUSTOM = -1  # Might become problematic if used to index lists
    INFINITE = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3


LEVELS_NAMES = {
    Level.CUSTOM: "Custom",
    Level.INFINITE: "Infinite",
    Level.LEVEL_1: "Level 1",
    Level.LEVEL_2: "Level 2",
    Level.LEVEL_3: "Level 3",
}

LEVELS = [Level.LEVEL_1, Level.LEVEL_2, Level.LEVEL_3]


# fmt: off
# Level boards and blocks
T = TypeVar("T")
Matrix2D: TypeAlias = list[list[T]]

IntsBoard: TypeAlias = Matrix2D[int]
TypesBoard: TypeAlias = Matrix2D[CellType]
Board: TypeAlias = Matrix2D[Cell]
LEVEL_BOARD_TYPES: dict[Level, TypesBoard] = {
    Level.CUSTOM: [[CellType.EMPTY] * BoardConfig.COL_SIZE for _ in range(BoardConfig.ROW_SIZE)],  # To be evaluated later
    Level.INFINITE: [[CellType.EMPTY] * BoardConfig.COL_SIZE for _ in range(BoardConfig.ROW_SIZE)],  # No blocks to break
    Level.LEVEL_1: [
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
    ],
    Level.LEVEL_2: [
        [CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET],
        [CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        [CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET],
        [CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET],
    ],
    Level.LEVEL_3: [
        [CellType.EMPTY, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.EMPTY],
        [CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET],
        [CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET, CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.EMPTY, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET, CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY],
        [CellType.TARGET, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.TARGET],
        [CellType.EMPTY, CellType.TARGET, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.TARGET, CellType.EMPTY],
    ],
}
# fmt: on


def init_level_boards() -> dict[Level, Board]:
    """Initialize the level boards from the LEVEL_BOARD_TYPES dictionary."""
    level_boards: dict[Level, Board] = {}
    for level, types_board in LEVEL_BOARD_TYPES.items():
        if len(types_board) == BoardConfig.ROW_SIZE and all(
            len(row) == BoardConfig.COL_SIZE for row in types_board
        ):
            level_boards[level] = BoardUtils.from_types_board(types_board)
        else:
            raise ValueError(f"Invalid board configuration for level {level}")
    return level_boards


LEVEL_BOARDS: dict[Level, Board] = init_level_boards()


"""Number of blocks to break for each level."""
LEVEL_BLOCKS = {
    Level.CUSTOM: 10000,  # To be evaluated later
    Level.INFINITE: 0,  # No limit
    Level.LEVEL_1: 4,
    Level.LEVEL_2: 16,
    Level.LEVEL_3: 24,
}


class PlayerType(IntEnum):
    """Player types."""

    HUMAN = 0
    AI = 1


class AIAlgorithmID(IntEnum):
    """AI algorithms used in the game."""

    BFS = 0
    DFS = 1
    ITER_DEEP = 2
    GREEDY = 3
    SINGLE_DEPTH_GREEDY = 4
    A_STAR = 5
    WEIGHTED_A_STAR = 6


AI_ALGO_NAMES = {
    AIAlgorithmID.BFS: "Breadth First Search",
    AIAlgorithmID.DFS: "Depth First Search",
    AIAlgorithmID.ITER_DEEP: "Iterative Deepening Search",
    AIAlgorithmID.GREEDY: "Greedy Search",
    AIAlgorithmID.SINGLE_DEPTH_GREEDY: "Single Depth Greedy Search",
    AIAlgorithmID.A_STAR: "A* Search",
    AIAlgorithmID.WEIGHTED_A_STAR: "Weighted A* Search",
}


class AIReturn(IntEnum):
    """AI return values."""

    STOPPED_EARLY = -2
    NOT_FOUND = -1
    RUNNING = 0
    FOUND = 1
