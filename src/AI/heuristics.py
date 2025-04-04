import copy

from game_logic.rules import (clear_full_lines, no_more_valid_moves, place_piece, is_valid_position)

def greedy_heuristic(node, parent, current):
    score = 0
    (piece, (px, py)) = current.recent_piece
    temp_state = copy.deepcopy(parent)

    # Place the piece temporarily to evaluate the board
    place_piece(temp_state, piece, (px, py))

    # 1º) Reward clearing rows and columns
    _, target_blocks_cleared = clear_full_lines(temp_state.board)
    score += target_blocks_cleared * 20  # Increased weight for clearing lines

    # 2º) Reward proximity to clearing target blocks
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(3 for cell in parent.board[row] if cell == 2)  # Row
        score += sum(3 for row in parent.board if row[col] == 2)  # Column

    # 3º) Reward normal block placement near others for future clears
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
    
    # 6º) Soft inheritance from the parent node
    score += max(0, (500 - node.heuristic_score * 25))

    return (1000 - score) / 50 # Normalize the score

def a_star_heuristic(node, parent, current):
    score = 0
    (piece, (px, py)) = current.recent_piece
    temp_state = copy.deepcopy(parent)

    # Place the piece temporarily to evaluate the board
    place_piece(temp_state, piece, (px, py))

    # 1º) Reward clearing rows and columns
    lines_cleared, target_blocks_cleared = clear_full_lines(temp_state.board)
    clear_bonus = (2 ** (lines_cleared - 1)) * 10  # Exponential bonus for multi-clears
    score += target_blocks_cleared * 20 + clear_bonus

    # 2º) Reward proximity to clearing target blocks
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(3 for cell in parent.board[row] if cell == 2)  # Row proximity
        score += sum(3 for row in parent.board if row[col] == 2)  # Column proximity



    # 4º) Focus on reducing target clusters to speed up game completion
    h_remaining_targets = count_target_clusters(current.board) * 15
    score -= h_remaining_targets  # Higher cost for more clusters

    # 5º) Reward mobility (number of valid placements left)
    mobility_score = count_valid_moves(current.board, current.pieces) * 5
    score += mobility_score

    # 6º) Penalize moves that lead to deadlocks
    if not any(current.pieces):
        if not any(current.following_pieces):
            return float('-inf')  # No possible moves left
        if no_more_valid_moves(current.board, current.following_pieces[0]):
            return float('-inf')  # Deadlock imminent
    else:
        if no_more_valid_moves(current.board, current.pieces):
            return float('-inf')  # Deadlock

    # 7º) Soft inheritance from the parent node
    score += max(0, (500 - node.heuristic_score * 25))

    return (1000 - score) / 50 # Normalize the score

def count_target_clusters(board):
    """Count distinct clusters of target blocks (2s)."""
    visited = set()
    clusters = 0

    def dfs(x, y):
        if (x, y) in visited or board[y][x] != 2:
            return
        visited.add((x, y))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if 0 <= x + dx < len(board[0]) and 0 <= y + dy < len(board):
                dfs(x + dx, y + dy)

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] == 2 and (x, y) not in visited:
                clusters += 1
                dfs(x, y)
    
    return clusters

def count_valid_moves(board, pieces):
    """Count total valid placements for all pieces."""
    count = 0
    for piece in pieces:
        if piece is None:
            continue
        for y in range(len(board)):
            for x in range(len(board[0])):
                if is_valid_position(board, piece, (x, y)):  # Assume function exists
                    count += 1
    return count
