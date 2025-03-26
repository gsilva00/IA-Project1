import copy

from game_logic.constants import GRID_SIZE
from game_logic.rules import clear_full_lines, is_valid_position, no_more_valid_moves, place_piece


_num_states = 0
def get_num_states():
    """Get the total number of states generated in another module

    Returns:
        int: The number of states generated
    """

    return _num_states

def child_states(game_data):
    """Generate all possible child states from the current state of the game being played

    Args:
        game_data (GameData): The current game state (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE). This is the data that the AI will use to make its decision while actually playing the game on the board.
    """

    global _num_states
    new_states = []

    # Avoid having to return a new gameplay state (GameData) with no pieces to play
    if not any(game_data.pieces):
        if game_data.get_more_playable_pieces():
            new_states = child_states(game_data)
        else:
            return new_states
    else:
        for i, piece in enumerate(game_data.pieces):
            if piece is not None:
                for y in range(GRID_SIZE):
                    for x in range(GRID_SIZE):
                        if is_valid_position(game_data.board, piece, (x, y)):
                            new_data = copy.deepcopy(game_data)
                            place_piece(new_data, piece, (x, y))
                            _, target_blocks_cleared = clear_full_lines(new_data.board)
                            new_data.blocks_to_break -= target_blocks_cleared
                            new_data.pieces[i] = None

                            _num_states += 1
                            new_states.append(new_data)

    return new_states

def goal_state(game_data):
    """Check if the current game state is a goal state (no more blocks to break)

    Args:
        game_data (GameData): The current game state
    """

    # For when the number of blocks to break is lower than the number of blocks that can be broken
    return game_data.blocks_to_break <= 0
