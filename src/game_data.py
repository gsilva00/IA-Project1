import copy
import json

from game_logic.constants import (CUSTOM, GRID_SIZE, INFINITE, LEVEL_BLOCKS,
                                  LEVEL_BOARDS)
from game_logic.rules import generate_pieces


class GameData:
    def __init__(self, level=INFINITE, file_path=None):
        self.board = copy.deepcopy(LEVEL_BOARDS[level if level != CUSTOM else 1]) if level != INFINITE else [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.following_pieces = generate_pieces(level)
        self.pieces = []
        _areThereMore = self.get_more_playable_pieces()
        self.blocks_to_break = copy.deepcopy(LEVEL_BLOCKS[level if level != CUSTOM else 1]) if level != INFINITE else 0
        self.recent_piece = None

        if level == CUSTOM and file_path is not None:
            self.load_game_data(file_path)


    def get_more_playable_pieces(self):
        """Get more pieces to play from the already generated pieces.

        Returns:
            bool: True if there are more pieces to play, False otherwise.

        Time Complexity:
            if there are no more pieces to play - O(1) since it will return immediately.
            if there are more pieces to play - O(f + 3) == O(f), where f is the number of following_pieces elements (between 1 and 33) and 3 is the number of pieces to play.

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


    def save_game_data(self, file_path):
        """Save the current data of the game to a file (JSON format).

        Args:
            file_path (str): The path to the file where the game data will be saved.

        """

        game_data = {
            'board': self.board,
            'following_pieces': self.following_pieces,
            'pieces': self.pieces,
            'blocks_to_break': self.blocks_to_break
        }
        with open(file_path, 'w') as file:
            json.dump(game_data, file)

    def load_game_data(self, file_path):
        """Load the game data from a file.

        """

        with open(file_path, 'r') as file:
            game_data = json.load(file)

        # Use get() to avoid KeyError if the key is not present, using the default (already initialized) game_data values
        # Special case for following_pieces and pieces, due to the JSON format not preserving the tuple structure of each square in the piece
        self.board = game_data.get('board', self.board)
        self.following_pieces = [
            [
                [tuple(square) for square in piece] if piece is not None else None
                for piece in three_piece_group
            ]
            for three_piece_group in game_data.get('following_pieces', self.following_pieces)
        ]
        self.pieces = [
            [tuple(square) for square in piece] if piece is not None else None
            for piece in game_data.get('pieces', self.pieces)
        ]
        self.blocks_to_break = game_data.get('blocks_to_break', self.blocks_to_break)
