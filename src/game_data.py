import copy

from game_logic.constants import (GRID_SIZE, INFINITE, LEVEL_BLOCKS,
                                  LEVEL_BOARDS)
from game_logic.rules import generate_pieces


class GameData:
    def __init__(self, level=INFINITE):
        self.board = copy.deepcopy(LEVEL_BOARDS[level]) if level != INFINITE else [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.following_pieces = generate_pieces()
        self.pieces = []
        self.getMorePlayablePieces()
        self.blocks_to_break = copy.deepcopy(LEVEL_BLOCKS[level]) if level != INFINITE else 0
        self.recent_piece = None

    def getMorePlayablePieces(self):
        """Get more pieces to play from the already generated pieces

        """

        if not any(self.pieces):
            if not self.following_pieces:
                self.pieces = []
            else:
                self.pieces = self.following_pieces[0]
                self.following_pieces = self.following_pieces[1:]

    def __eq__(self, other):
        """Check if two GameData objects are equal based on their state."""
        if not isinstance(other, GameData):
            return False

        def normalize_pieces(pieces):
            """Convert pieces to a set of frozensets, ignoring None."""
            return set(frozenset(piece) if piece is not None else None for piece in pieces)

        return (
            self.board == other.board and
            normalize_pieces(self.pieces) == normalize_pieces(other.pieces) and
            self.following_pieces == other.following_pieces and
            self.blocks_to_break == other.blocks_to_break and
            self.recent_piece == other.recent_piece
        )

    def __hash__(self):
        """Generate a hash value for the GameData object based on its state."""

        def normalize_pieces(pieces):
            """Convert pieces to a set of frozensets, ignoring None."""
            return set(frozenset(piece) if piece is not None else None for piece in pieces)

        return hash((
            tuple(tuple(row) for row in self.board),  # Convert board to a tuple of tuples
            frozenset(normalize_pieces(self.pieces)),  # Use normalized pieces
            tuple(
                tuple(
                    tuple(piece) if piece is not None else None for piece in group
                ) if group is not None else None for group in self.following_pieces
            ),  # Handle None in following_pieces and its elements
            self.blocks_to_break,  # Integer is already hashable
            (tuple(self.recent_piece[0]), self.recent_piece[1]) if self.recent_piece else None  # Handle recent_piece
        ))

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
