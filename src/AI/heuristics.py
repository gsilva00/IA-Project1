from game_logic.rules import (check_full_lines, is_valid_position,
                              no_more_valid_moves, place_piece)


def greedy_heuristic(board, piece, position, game_data):
    score = 0
    px, py = position

    # Place the piece temporarily to evaluate the board
    temp_board = [row[:] for row in board]
    place_piece(temp_board, piece, position)

    temp_visible_pieces = game_data.pieces_visible.copy()
    temp_visible_pieces[game_data.pieces.index(piece)] = False

    # 1º) Iterate through the rows and columns containing the placed piece
    for x, y in piece:
        row = py + y
        col = px + x
        score += sum(1 for cell in temp_board[row] if cell == 2)  # Row
        score += sum(1 for row in temp_board if row[col] == 2)  # Column

    # 2º) Check if a line or column containing target blocks is cleared
    _, target_blocks_cleared = check_full_lines(temp_board)
    score += target_blocks_cleared * 10

    # 3º) Check if the play clears enough space to make room for upcoming pieces
    visible_pieces_count = sum(game_data.pieces_visible)
    if visible_pieces_count > 1:
        if no_more_valid_moves(board, game_data.pieces, temp_visible_pieces):
            if not no_more_valid_moves(temp_board, game_data.pieces, temp_visible_pieces):
                score += 100
    else:
        if no_more_valid_moves(board, game_data.following_pieces[0], [True, True, True]):
            if not no_more_valid_moves(temp_board, game_data.following_pieces[0], [True, True, True]):
                score += 100

    # 4º) Check if the play results in target_blocks <= 0
    if game_data.blocks_to_break - target_blocks_cleared <= 0:
        return float('inf')

    # 5º) Check if the play results in a loss due to no valid moves for the next blocks
    if no_more_valid_moves(temp_board, game_data.pieces, temp_visible_pieces):
        return float('-inf')

    return score