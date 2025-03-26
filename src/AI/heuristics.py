import copy

from game_logic.rules import (clear_full_lines, no_more_valid_moves, place_piece)


def greedy_heuristic(node, parent, current):
    score = 0
    (piece, (px, py)) = current.recent_piece
    temp_state = copy.deepcopy(parent)

    # Place the piece temporarily to evaluate the board
    place_piece(temp_state, piece, (px, py))

    # 1º) Reward clearing rows and columns
    _, target_blocks_cleared = clear_full_lines(temp_state.board)
    score += target_blocks_cleared * 20  # Increased weight for clearing lines

    # 1º) Iterate through the rows and columns containing the placed piece
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(3 for cell in parent.board[row] if cell == 2)  # Row
        score += sum(3 for row in parent.board if row[col] == 2)  # Column

    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(1 for cell in parent.board[row] if cell == 1)  # Row
        score += sum(1 for row in parent.board if row[col] == 1)  # Column

    # 4º) Focus on reducing target blocks to break
    if current.blocks_to_break <= 0:
        return float('inf')  # Winning move

    # 5º) Penalize moves that lead to deadlocks
    if not any(current.pieces):
        if not any(current.following_pieces):
            return float('-inf')
        if no_more_valid_moves(current.board, current.following_pieces[0]):
            return float('-inf')  # Deadlock
    else:
        if no_more_valid_moves(current.board, current.pieces):
            return float('-inf')  # Deadlock
    
    # 6º) Inherit the score from the parent node
    if (score + node.heuristic_score) <= 0:
        score = 0
    else:
        score += node.heuristic_score

    return score
