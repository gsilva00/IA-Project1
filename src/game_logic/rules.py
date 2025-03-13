import random
from game_logic.constants import GRID_SIZE, PIECES


def generate_shapes():
    return [random.choice(PIECES) for _ in range(3)]

def place_piece(board, shape, position):
    px, py = position
    for x, y in shape:
        board[py + y][px + x] = 1

def check_full_lines(board):
    lines_cleared = 0

    for y in range(GRID_SIZE):
        if all(board[y]):
            board[y] = [0] * GRID_SIZE
            lines_cleared += 1

    for x in range(GRID_SIZE):
        if all(board[y][x] for y in range(GRID_SIZE)):
            for y in range(GRID_SIZE):
                board[y][x] = 0
            lines_cleared += 1

    return lines_cleared

def is_valid_position(board, shape, position):
    px, py = position
    for x, y in shape:
        if not (0 <= px + x < GRID_SIZE and 0 <= py + y < GRID_SIZE):
            return False
        if board[py + y][px + x]:
            return False
    return True

def no_more_valid_moves(board, shapes):
    for shape in shapes:
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if is_valid_position(board, shape, (x, y)):
                    return False
    return True
