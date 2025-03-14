import random

from game_logic.constants import GRID_SIZE, PIECES


def generate_pieces():
    return [random.choice(PIECES) for _ in range(3)]

def place_piece(board, piece, position):
    px, py = position
    for x, y in piece:
        board[py + y][px + x] = 1

def check_full_lines(board):
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
                    target_blocks_cleared += 1
                    board[y][x] = 0
                # Target block with more than
                elif board[y][x] > 2:
                    board[y][x] = board[y][x] - 1

                cleared_blocks.add((y, x))

    return len(lines_to_clear) + len(columns_to_clear), target_blocks_cleared

def is_valid_position(board, piece, position):
    px, py = position
    for x, y in piece:
        if not (0 <= px + x < GRID_SIZE and 0 <= py + y < GRID_SIZE):
            return False
        if board[py + y][px + x]:
            return False
    return True

def no_more_valid_moves(board, pieces, visible):
    for i, piece in enumerate(pieces):
        if visible[i]:
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    if is_valid_position(board, piece, (x, y)):
                        return False
    return True
