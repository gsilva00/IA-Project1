import copy

from game_logic.rules import (clear_full_lines, no_more_valid_moves, place_piece, is_valid_position)

# Heuristic for greedy best first search algorithm with the option to inherit the score from the parent node
def greedy_heuristic(parent, current, total_blocks, inheritance):
    score = 0
    (piece, (px, py)) = current.recent_piece
    temp_state = copy.deepcopy(parent.state)

    # Place the piece temporarily to evaluate the board
    place_piece(temp_state, piece, (px, py))

    # 1º) Reward clearing rows and columns
    _, target_blocks_cleared = clear_full_lines(temp_state.board)
    score += target_blocks_cleared * 20  # Increased weight for clearing lines

    # 2º) Reward proximity to clearing target blocks
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(3 for cell in parent.state.board[row] if cell == 2)  # Row
        score += sum(3 for row in parent.state.board if row[col] == 2)  # Column

    # 3º) Reward normal block placement near others for future clears
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(1 for cell in parent.state.board[row] if cell == 1)  # Row
        score += sum(1 for row in parent.state.board if row[col] == 1)  # Column

    # 4º) Focus on reducing target blocks to break
    if current.blocks_to_break <= 0:
        return float('-inf')  # Winning move

    # 5º) Penalize moves that lead to deadlocks
    if not any(current.pieces):
        if not any(current.following_pieces):
            return float('inf')
        if no_more_valid_moves(current.board, current.following_pieces[0]):
            return float('inf')  # Deadlock
    else:
        if no_more_valid_moves(current.board, current.pieces):
            return float('inf')  # Deadlock
    
    # 6º) Inherit target block break score from the parent node
    if (inheritance):
        score += (total_blocks - parent.state.blocks_to_break) * 20

    return (10000 - score) / 10 # Normalize the score

# Admissible heuristic for A* algorithm
#Never overestimates the cost to reach the goal state from the current state
def a_star_heuristic(current):
    rows_with_targets = set()
    cols_with_targets = set()

    # 1º) Iterate through the board once to identify rows and columns with target blocks
    for row_idx, row in enumerate(current.board):
        for col_idx, cell in enumerate(row):
            if cell == 2:
                rows_with_targets.add(row_idx)
                cols_with_targets.add(col_idx)

    # 2º) Calculate the number of rows and columns to clear
    line_to_clear = len(rows_with_targets)
    column_to_clear = len(cols_with_targets)

    return min(line_to_clear, column_to_clear)

def infinite_heuristic(parent, current):
    score = 0
    (piece, (px, py)) = current.recent_piece
    temp_state = copy.deepcopy(parent.state)

    # Place the piece temporarily to evaluate the board
    place_piece(temp_state, piece, (px, py))

    # 1º) Minimize the number of blocks on the board
    total_blocks = sum(cell != 0 for row in temp_state.board for cell in row)
    score -= total_blocks * 10  # Higher weight for fewer blocks

    # 2º) Minimize the total perimeter of blocks
    perimeter = 0
    for row_idx, row in enumerate(temp_state.board):
        for col_idx, cell in enumerate(row):
            if cell != 0:
                # Check the four neighbors
                if row_idx == 0 or temp_state.board[row_idx - 1][col_idx] == 0:
                    perimeter += 1
                if row_idx == len(temp_state.board) - 1 or temp_state.board[row_idx + 1][col_idx] == 0:
                    perimeter += 1
                if col_idx == 0 or temp_state.board[row_idx][col_idx - 1] == 0:
                    perimeter += 1
                if col_idx == len(row) - 1 or temp_state.board[row_idx][col_idx + 1] == 0:
                    perimeter += 1
    score -= perimeter * 5  # Penalize higher perimeters

    # 3º) Avoid jagged edges of blocks
    jaggedness = 0
    for row_idx, row in enumerate(temp_state.board[:-1]):  # Skip the last row
        for col_idx, cell in enumerate(row):
            if cell != 0 and temp_state.board[row_idx + 1][col_idx] == 0:  # Block with empty space below
                jaggedness += 1
    score -= jaggedness * 8  # Penalize jagged edges

    # 4º) Avoid leaving a single empty space between two blocks
    single_empty_spaces = 0
    for row_idx, row in enumerate(temp_state.board):
        for col_idx, cell in enumerate(row):
            if cell == 0:
                # Check if surrounded by blocks horizontally
                if col_idx > 0 and col_idx < len(row) - 1 and temp_state.board[row_idx][col_idx - 1] != 0 and temp_state.board[row_idx][col_idx + 1] != 0:
                    single_empty_spaces += 1
                # Check if surrounded by blocks vertically
                if row_idx > 0 and row_idx < len(temp_state.board) - 1 and temp_state.board[row_idx - 1][col_idx] != 0 and temp_state.board[row_idx + 1][col_idx] != 0:
                    single_empty_spaces += 1
    score -= single_empty_spaces * 15  # Heavily penalize single empty spaces

    return (10000 - score) / 10 # Normalize the score
