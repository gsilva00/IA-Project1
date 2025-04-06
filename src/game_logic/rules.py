import random

from game_logic.constants import GRID_SIZE, PIECES


def generate_pieces():
    """Generates list of lists with a total of 99 random pieces.

    Returns:
        List[List[int]]: List of 99 pieces (divided in lists of 3), each piece is a list of pairs (x, y), each pair represents a block in the piece.

    """

    return [[random.choice(PIECES) for _ in range(3)] for _ in range(33)]

def place_piece(game_data, piece, position, hint=False):
    """Places a piece on the board.

    Args:
        game_data (GameData): The game data.
        piece (List[Tuple[int, int]]): The piece to place.
        position (Tuple[int, int]): The position to place the piece.
        hint (bool): If True, place the piece as a hint (not permanent and different value to indicate hint and differentiate color).

    """

    game_data.recent_piece = (piece, position)

    px, py = position
    for x, y in piece:
        game_data.board[py + y][px + x] = 1 if not hint else 0.5

def clear_full_lines(board):
    """Clears full lines and columns from the board.

    Args:
        board (List[List[int]]): The game board.

    Returns:
        Tuple[int, int]: The number of lines and columns cleared, and the number of target blocks cleared.

    """

    # Sets to avoid counting the same line/column/block multiple times
    lines_to_clear = set()
    columns_to_clear = set()
    cleared_blocks = set()

    target_blocks_cleared = 0

    # Prepare lines and columns to clear
    for y in range(GRID_SIZE):
        if all(board[y]):
            lines_to_clear.add(y)

    for x in range(GRID_SIZE):
        if all(board[y][x] for y in range(GRID_SIZE)):
            columns_to_clear.add(x)

    # Clear lines
    for y in lines_to_clear:
        for x in range(GRID_SIZE):
            if (y, x) not in cleared_blocks:
                # Player block
                if board[y][x] == 1:
                    board[y][x] = 0
                # Target block
                elif board[y][x] == 2:
                    print("Target block cleared in line")
                    target_blocks_cleared += 1
                    board[y][x] = 0
                # Target block with more than one hit left
                elif board[y][x] > 2:
                    board[y][x] = board[y][x] - 1

                cleared_blocks.add((y, x))

    # Clear columns
    for x in columns_to_clear:
        for y in range(GRID_SIZE):
            if (y, x) not in cleared_blocks:
                # Player block
                if board[y][x] == 1:
                    board[y][x] = 0
                # Target block
                elif board[y][x] == 2:
                    print("Target block cleared in column")
                    target_blocks_cleared += 1
                    board[y][x] = 0
                # Target block with more than one hit left
                elif board[y][x] > 2:
                    board[y][x] = board[y][x] - 1

                cleared_blocks.add((y, x))

    return len(lines_to_clear) + len(columns_to_clear), target_blocks_cleared

def is_valid_position(board, piece, position):
    """Checks if a piece can be placed on the board at the given position.

    Args:
        board (List[List[int]]): The game board.
        piece (List[Tuple[int, int]]): The piece to place.
        position (Tuple[int, int]): The position to place the piece.

    Returns:
        bool: True if the piece can be placed, False otherwise

    """

    px, py = position
    for x, y in piece:
        if not (0 <= px + x < GRID_SIZE and 0 <= py + y < GRID_SIZE):
            return False
        if board[py + y][px + x]:
            return False
    return True

def no_more_valid_moves(board, pieces):
    """Checks if there are no more valid moves for the player.

    Args:
        board (List[List[int]]): The game board.
        pieces (List[List[Tuple[int, int]]]): The list of possible pieces to place.

    Returns:
        bool: True if there are no more valid moves, False otherwise.

    """

    for piece in pieces:
        if piece is not None:
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if is_valid_position(board, piece, (x, y)):
                        return False
    return True
