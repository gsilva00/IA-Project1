import copy

from game_logic.rules import (clear_full_lines, no_more_valid_moves, place_piece)

def greedy_heuristic(root, parent, current):
    score = 0
    (piece, (px, py)) = current.recent_piece
    temp_state = copy.deepcopy(parent)

    # Place the piece temporarily to evaluate the board
    place_piece(temp_state, piece, (px, py))

    # 1º) Iterate through the rows and columns containing the placed piece
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(1 for cell in parent.board[row] if cell == 2)  # Row
        score += sum(1 for row in parent.board if row[col] == 2)  # Column

    # 2º) Check if a line or column containing target blocks is cleared
    _, target_blocks_cleared = clear_full_lines(temp_state.board)
    score += target_blocks_cleared * 10

    # 3º) Check if the play clears enough space to make room for upcoming pieces
    if no_more_valid_moves(parent.board, current.pieces):
        if not no_more_valid_moves(current.board, current.pieces):
            score += 25

    # 4º) Check if the play results in target_blocks <= 0
    if current.blocks_to_break <= 0:
        return float('inf')

    # 5º) Check if the play results in a loss due to no valid moves for the next blocks
    if no_more_valid_moves(current.board, current.pieces):
        return float('-inf')
    
    # 6º) Add the score of the parent state
    score += (root.blocks_to_break - parent.blocks_to_break) * 10

    return score
