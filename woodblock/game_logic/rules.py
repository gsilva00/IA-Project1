from __future__ import annotations

import logging
import secrets
from typing import TYPE_CHECKING

from woodblock.game_logic.constants import (
    PIECES,
    Board,
    BoardConfig,
    Cell,
    CellType,
    Level,
    Piece,
    PieceHand,
    PiecePosition,
    PlayablePieceHand,
)

if TYPE_CHECKING:
    from woodblock.game_data import GameData

LOGGER = logging.getLogger(__name__)


def generate_pieces(level: Level) -> list[PieceHand]:
    """Generate list of lists with a total of 99 random pieces.

    Returns:
        list[PieceHand]: A list of lists containing the generated pieces:
        - 99 pieces (divided in inner playable lists of 3) if level is not infinite
        - 333 pieces (divided in inner playable lists of 3) if level is infinite

    """
    return [
        [secrets.choice(PIECES) for _ in range(3)]
        for _ in range(33 if level != Level.INFINITE else 333)
    ]


def place_piece(
    game_data: GameData,
    piece: Piece,
    position: PiecePosition,
    *,
    is_hint: bool = False,
) -> None:
    """Places a piece on the BoardConfig.

    Args:
        game_data (GameData): The game data.
        piece (list[Tuple[int, int]]): The piece to place.
        position (Tuple[int, int]): The position to place the piece.
        is_hint (bool): If True, place the piece as a hint (not permanent and different value to indicate hint and differentiate color).

    Time Complexity:
        O(b), where b is the number of blocks in the piece (very small, between 1 and 4 for the current available pieces).
        - Even in the extreme case where a piece is the whole grid, it would be O(g^2) where g is the grid size).
        - Still, the grid size is always small (8x8). It also wouldn't be able to be expanded much more than that, due to this project being about developing search algorithms and them being needed to run in a reasonable time.
        - The time complexity of this function is O(1) in practice, since the number of blocks in the piece is very small.

    """
    game_data.recent_piece = (piece, position)

    px, py = position
    for x, y in piece:
        game_data.board[py + y][px + x] = (
            Cell(CellType.PLAYER) if not is_hint else Cell(CellType.HINT)
        )


def clear_full_lines(board: Board) -> tuple[int, int]:
    """Clear full lines and columns from the BoardConfig.

    Args:
        board (Board): The game BoardConfig.

    Returns:
        tuple[int, int]: The number of lines and columns cleared, and the number of target blocks cleared.

    Time Complexity:
        O(g^2), where g is the size of the grid

    """
    # Sets to avoid counting the same line/column/block multiple times
    # Prepare lines and columns to clear
    # Time Complexity: O(g^2) each
    lines_to_clear = {
        y for y in range(BoardConfig.ROW_SIZE) if all(cell.can_hit for cell in board[y])
    }
    columns_to_clear = {
        x
        for x in range(BoardConfig.COL_SIZE)
        if all(board[y][x].can_hit for y in range(BoardConfig.ROW_SIZE))
    }
    cleared_blocks = set()
    target_blocks_cleared = 0

    def clear_block(x: int, y: int) -> None:
        nonlocal target_blocks_cleared
        block = board[y][x]
        if block.type == CellType.TARGET and block.hits == 1:
            target_blocks_cleared += 1
        board[y][x] = block.hit()

    # Time Complexity: O(n^2), where n is the number of lines to clear (n <= g)
    for y in lines_to_clear:
        for x in range(BoardConfig.COL_SIZE):
            if (x, y) not in cleared_blocks:
                clear_block(x, y)
                cleared_blocks.add((x, y))

    # Time Complexity: O(n^2), where n is the number of columns to clear (n <= g)
    for x in columns_to_clear:
        for y in range(BoardConfig.ROW_SIZE):
            if (x, y) not in cleared_blocks:
                clear_block(x, y)
                cleared_blocks.add((x, y))

    return len(lines_to_clear) + len(columns_to_clear), target_blocks_cleared


def is_valid_position(
    board: Board,
    piece: Piece,
    position: PiecePosition,
) -> bool:
    """Check if a piece can be placed on the board at the given position.

    Args:
        board (Board): The game BoardConfig.
        piece (Piece): The piece to place.
        position (PiecePosition): The position to place the piece.

    Returns:
        bool: True if the piece can be placed, False otherwise

    Time Complexity:
        O(b), where b is the number of blocks in the piece (very small, between 1 and 4 for the current available pieces.
        Even in the extreme case where a piece is the whole grid, it would be O(g^2) where g is the grid size).
        Still, the grid size is always small (8x8). It also wouldn't be able to be expanded much more than that, due to this project being about developing search algorithms and them being needed to run in a reasonable time.
        The time complexity of this function is O(1) in practice, since the number of blocks in the piece is very small.

    """
    px, py = position
    for x, y in piece:
        if not (0 <= px + x < BoardConfig.COL_SIZE and 0 <= py + y < BoardConfig.ROW_SIZE):
            return False
        if board[py + y][px + x].can_hit:
            return False
    return True


def no_more_valid_moves(board: Board, pieces: PlayablePieceHand) -> bool:
    """Check if there are no more valid moves for the player.

    Args:
        board (Board): The game BoardConfig.
        pieces (PlayablePieceHand): The list of possible pieces to place.

    Returns:
        bool: True if there are no more valid moves, False otherwise.

    Time Complexity:
        O(p * g^2 * <complexity of is_valid_position()>) == O(p * g^2 * b), where:
        - p is the number of pieces to place
        - g is the grid size
        - b is the number of blocks in the piece (very small, between 1 and 4 for the current available pieces).

    """
    for piece in pieces:
        if piece is not None:
            for y in range(BoardConfig.ROW_SIZE):
                for x in range(BoardConfig.COL_SIZE):
                    if is_valid_position(board, piece, (x, y)):
                        return False
    return True
