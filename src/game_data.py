import copy
import json

from game_logic.constants import (GRID_SIZE, INFINITE, LEVEL_BLOCKS,
                                  LEVEL_BOARDS)
from game_logic.rules import generate_pieces


class GameData:
    def __init__(self, level=INFINITE):
        self.board = copy.deepcopy(LEVEL_BOARDS[level]) if level != INFINITE else [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.following_pieces = generate_pieces()
        self.pieces = []
        _areThereMore = self.get_more_playable_pieces()
        self.blocks_to_break = copy.deepcopy(LEVEL_BLOCKS[level]) if level != INFINITE else 0
        self.recent_piece = None

    def get_more_playable_pieces(self):
        """Get more pieces to play from the already generated pieces.

        Returns:
            bool: True if there are more pieces to play, False otherwise.

        """

        if not any(self.pieces):
            if len(self.following_pieces) == 0:
                self.pieces = []
                return False # No more pieces to play
            else:
                self.pieces = self.following_pieces[0]
                self.following_pieces = self.following_pieces[1:]
                return True
        else:
            return True

    def __eq__(self, other):
        """Determine if two GameData objects are equal.

        """

        if not isinstance(other, GameData):
            return False

        return (
                self.board == other.board and
                self._normalize_pieces(self.pieces) == self._normalize_pieces(other.pieces) and
                self.following_pieces == other.following_pieces and
                self.blocks_to_break == other.blocks_to_break and
                self.recent_piece == other.recent_piece
        )

    def __hash__(self):
        """Generate a hash value for the GameData object.

        """

        return hash((
            tuple(tuple(row) for row in self.board),  # Convert board to a tuple of tuples
            frozenset(self._normalize_pieces(self.pieces)),  # Use normalized pieces
            tuple(
                tuple(
                    tuple(piece) if piece is not None else None for piece in group
                ) if group is not None else None for group in self.following_pieces
            ),  # Handle None in following_pieces and its elements
            self.blocks_to_break,  # Integer is already hashable
            (tuple(self.recent_piece[0]), self.recent_piece[1]) if self.recent_piece else None  # Handle recent_piece
        ))

    @staticmethod
    def _normalize_pieces(pieces):
        """Convert pieces to a set of frozensets, ignoring None.

        """

        return set(frozenset(piece) if piece is not None else None for piece in pieces)


    def save_game_state(self, file_path):
        """Save the current state of the game to a file (JSON format). The state of the game is NOT TO BE CONFUSED WITH THE STATES FROM THE STATE MACHINE. This is the data of the actual gameplay.

        Args:
            file_path (str): The path to the file where the game state will be saved.

        """
        game_state = {
            'board': self.board,
            'following_pieces': self.following_pieces,
            'pieces': self.pieces,
            'blocks_to_break': self.blocks_to_break
        }
        with open(file_path, 'w') as file:
            json.dump(game_state, file)

    def load_game_state(self, file_path):
        """Load the game state from a file."""
        with open(file_path, 'r') as file:
            game_state = json.load(file)
        self.board = game_state['board']
        self.following_pieces = game_state['following_pieces']
        self.pieces = game_state['pieces']
        self.blocks_to_break = game_state['blocks_to_break']

if __name__ == '__main__':
    visited = set()
    game_data = GameData()
    game_data.board = [[0, 0, 0, 0], [0, 2, 2, 0], [0, 2, 2, 0], [0, 0, 0, 0]]
    game_data.pieces = [[(0, 0), (1, 0), (2, 0)], [(0, 0), (1, 0), (2, 0)], None]
    game_data.following_pieces = [[[(0, 0), (0, 1)], [(0, 0), (1, 0)], [(0, 0), (1, 0)]], [None, None, None]]
    game_data.blocks_to_break = 4
    game_data.recent_piece = ([(0, 0), (1, 0), (2, 0)], (1, 1))

    game_data_copy = GameData()
    game_data_copy.board = [[0, 0, 0, 0], [0, 2, 2, 0], [0, 2, 2, 0], [0, 0, 0, 0]]
    game_data_copy.pieces = [[(0, 0), (1, 0), (2, 0)], None, [(0, 0), (1, 0), (2, 0)]]
    game_data_copy.following_pieces = [[[(0, 0), (0, 1)], [(0, 0), (1, 0)], [(0, 0), (1, 0)]], [None, None, None]]
    game_data_copy.blocks_to_break = 4
    game_data_copy.recent_piece = ([(0, 0), (1, 0), (2, 0)], (1, 1))

    visited.add(game_data)
    visited.add(game_data_copy)

    print(game_data == game_data_copy)  # True
