import copy

from game_logic.constants import GRID_SIZE
from game_logic.rules import clear_full_lines, is_valid_position, place_piece


_num_states = 0
def get_num_states():
    """Get the total number of states generated in another module

    Returns:
        int: The number of states generated

    """

    return _num_states

def child_states(game_state):
    """Generate all possible child states from the current state of the game being played

    Args:
        game_state (GameData): The current game state (NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE). This is the data that the AI will use to make its decision while actually playing the game on the board.

    """

    global _num_states
    new_states = []

    # Avoid having to return a new gameplay state (GameData) with no pieces to play
    if not any(game_state.pieces):
        if game_state.get_more_playable_pieces():
            new_states = child_states(game_state)
        else:
            return new_states
    else:
        for i, piece in enumerate(game_state.pieces):
            if piece is not None:
                for y in range(GRID_SIZE):
                    for x in range(GRID_SIZE):
                        if is_valid_position(game_state.board, piece, (x, y)):
                            new_state = copy.deepcopy(game_state)
                            place_piece(new_state, piece, (x, y))
                            _, target_blocks_cleared = clear_full_lines(new_state.board)
                            new_state.blocks_to_break -= target_blocks_cleared
                            new_state.pieces[i] = None

                            _num_states += 1
                            new_states.append(new_state)

    return new_states

def goal_state(game_state):
    """Check if the current game state is a goal state (no more blocks to break)

    Args:
        game_state (GameData): The current game state

    """

    # For when the number of blocks to break is lower than the number of blocks that can be broken
    return game_state.blocks_to_break <= 0
