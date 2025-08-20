from __future__ import annotations

import copy
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from woodblock.ai.algorithms import TreeNode
    from woodblock.game_data import GameData

from woodblock.game_logic.constants import Board, BoardConfig, CellType, PlayablePieceHand
from woodblock.game_logic.rules import clear_full_lines, no_more_valid_moves, place_piece


# Heuristic for greedy best first search algorithm with the option to inherit the score from the parent node
def greedy_heuristic(
    parent: TreeNode,
    current: GameData,
    total_blocks: int,
    *,
    inheritance: bool,
) -> float:
    """Greedy heuristic function for evaluating the state of the game board.

    Args:
        parent (TreeNode): The parent node of the current state.
        current (GameData): The current state of the game board.
        total_blocks (int): The total number of blocks to break in the level.
        inheritance (bool): Flag indicating whether to inherit the score from the parent node.

    Returns:
        float: The heuristic score for the current state.
            The closer-to-zero/more negative the score, the better the state.

    Time Complexity:
        O(p * g^2 * b), where:
        - p is the number of currently playable pieces
        - g is the grid size
        - b is the number of blocks in the piece (very small, between 1 and 4 for the current available pieces).

    """
    # Guaranteed, because current.recent_piece is set when a piece is placed
    # A piece is placed before the heuristic is called (inside child_states())
    assert current.recent_piece is not None

    # Higher score the better until normalization
    score = 0
    (piece, (px, py)) = current.recent_piece
    temp_state = copy.deepcopy(parent.state)

    # Place the piece temporarily to evaluate the board
    place_piece(temp_state, piece, (px, py))

    # 1º) Reward clearing rows and columns
    _, target_blocks_cleared = clear_full_lines(temp_state.board)
    score += target_blocks_cleared * 20  # Increased weight for clearing lines

    # 2º) Reward proximity to clearing target blocks
    # Time Complexity: O(b * 2*g), where b is the number of blocks in the piece (very small, between 1 and 4 for the current available pieces) and g is the grid size
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(3 for cell in parent.state.board[row] if cell.type == CellType.TARGET)  # Row
        score += sum(3 for row in parent.state.board if row[col].type == CellType.TARGET)  # Column

    # 3º) Reward normal block placement near others for future clears
    # Time Complexity: O(b * 2*g), where b is the number of blocks in the piece (very small, between 1 and 4 for the current available pieces) and g is the grid size
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(1 for cell in parent.state.board[row] if cell.type == CellType.PLAYER)  # Row
        score += sum(1 for row in parent.state.board if row[col].type == CellType.PLAYER)  # Column

    # 4º) Focus on reducing target blocks to break
    if current.blocks_to_break <= 0:
        return float("-inf")  # Winning move

    # 5º) Penalize moves that lead to deadlocks
    # Time Complexity: O(<complexity of no_more_valid_moves()>) == O(p * g^2 * b), where:
    if not any(current.pieces):
        if not any(current.following_pieces):
            return float("inf")  # No more moves available
        if no_more_valid_moves(
            current.board,
            cast("PlayablePieceHand", current.following_pieces[0]),
        ):
            return float("inf")  # Deadlock
    elif no_more_valid_moves(current.board, current.pieces):
        return float("inf")  # Deadlock

    # 6º) Inherit target block break score from the parent node
    if inheritance:
        score += (total_blocks - parent.state.blocks_to_break) * 20

    # Normalize the score
    return (10000 - score) / 10


def a_star_heuristic(current: GameData) -> float:
    """Admissible heuristic function for A* algorithm.

    This heuristic estimates the cost to reach the goal state from the current state without overestimating it.
    Overestimating the cost can lead to suboptimal decisions as per the A* algorithm heuristic admissibility criteria.

    The closer to zero the score, the better the state.

    Args:
        current (GameData): The current state of the game board.

    Returns:
        int: The heuristic score for the current state.

    Time Complexity:
        O(g^2), where g is the grid size

    """
    rows_with_targets = set()
    cols_with_targets = set()

    # 1º) Iterate through the board once to identify rows and columns with target blocks
    # Time Complexity: O(g^2), where g is the grid size
    for row_idx, row in enumerate(current.board):
        for col_idx, cell in enumerate(row):
            if cell.type == CellType.TARGET:
                rows_with_targets.add(row_idx)
                cols_with_targets.add(col_idx)

    # 2º) Calculate the number of rows and columns to clear
    line_to_clear = len(rows_with_targets)
    column_to_clear = len(cols_with_targets)

    return min(line_to_clear, column_to_clear)


def infinite_heuristic(parent: TreeNode, current: GameData) -> float:
    """Heuristic function for the infinite game mode.

    Args:
        parent (TreeNode): The parent node of the current state.
        current (GameData): The current state of the game board.

    Returns:
        float: The heuristic score for the current state.
            The closer-to-zero/more negative the score, the better the state.

    """
    assert current.recent_piece is not None

    # Higher score the better until normalization
    score = 0
    (piece, (px, py)) = current.recent_piece
    temp_state = copy.deepcopy(parent.state)

    # Place the piece temporarily to evaluate the board
    place_piece(temp_state, piece, (px, py))

    # 1º) Minimize the number of blocks on the board
    total_blocks = sum(cell != 0 for row in temp_state.board for cell in row)
    score -= total_blocks * 10  # Higher weight for fewer blocks

    # 2º) Minimize the total perimeter of blocks
    def calc_perimeter(board: Board) -> int:
        rows, cols = BoardConfig.ROW_SIZE, BoardConfig.COL_SIZE
        perimeter = 0
        for r in range(rows):
            for c in range(cols):
                if board[r][c].can_hit:
                    perimeter += (
                        (r == 0 or board[r - 1][c].type == CellType.EMPTY)
                        + (r == rows - 1 or board[r + 1][c].type == CellType.EMPTY)
                        + (c == 0 or board[r][c - 1].type == CellType.EMPTY)
                        + (c == cols - 1 or board[r][c + 1].type == CellType.EMPTY)
                    )
        return perimeter

    # Penalize higher perimeters
    score -= calc_perimeter(temp_state.board) * 5

    # 3º) Avoid jagged edges of blocks
    def calc_jaggedness(board: Board) -> int:
        rows, cols = BoardConfig.ROW_SIZE, BoardConfig.COL_SIZE
        jagged = 0
        for r in range(rows - 1):  # Skip the last row
            for c in range(cols):
                if board[r][c].type != CellType.EMPTY and board[r + 1][c].type == CellType.EMPTY:
                    # Block with empty space below
                    jagged += 1
        return jagged

    # Penalize jagged edges
    score -= calc_jaggedness(temp_state.board) * 8

    # 4º) Avoid leaving a single empty space between two blocks
    def calc_single_empty_spaces(board: Board) -> int:
        rows, cols = BoardConfig.ROW_SIZE, BoardConfig.COL_SIZE
        count = 0
        for r in range(rows):
            for c in range(cols):
                if board[r][c].type == CellType.EMPTY:
                    if (
                        0 < c < cols - 1
                        and board[r][c - 1].type != CellType.EMPTY
                        and board[r][c + 1].type != CellType.EMPTY
                    ):
                        count += 1
                    if (
                        0 < r < rows - 1
                        and board[r - 1][c].type != CellType.EMPTY
                        and board[r + 1][c].type != CellType.EMPTY
                    ):
                        count += 1
        return count

    # Heavily penalize single empty spaces
    score -= calc_single_empty_spaces(temp_state.board) * 15

    # Normalize the score
    return (10000 - score) / 10
