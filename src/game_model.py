from game_logic.constants import GRID_SIZE
from game_logic.rules import generate_pieces


class GameModel:
    def __init__(self):
        self._board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self._pieces = generate_pieces()
        self._pieces_visible = [True] * len(self._pieces)
        self._selected_piece = None
        self._selected_index = None
        self._score = 0
        self._blocks_to_break = 0

    def reset(self):
        self._board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self._pieces = generate_pieces()
        self._pieces_visible = [True] * len(self._pieces)
        self._selected_piece = None
        self._selected_index = None
        self._score = 0
        self._blocks_to_break = 0

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, value):
        self._board = value

    @property
    def pieces(self):
        return self._pieces

    @pieces.setter
    def pieces(self, value):
        self._pieces = value

    @property
    def pieces_visible(self):
        return self._pieces_visible

    @pieces_visible.setter
    def pieces_visible(self, value):
        self._pieces_visible = value

    @property
    def selected_piece(self):
        return self._selected_piece

    @selected_piece.setter
    def selected_piece(self, value):
        self._selected_piece = value

    @property
    def selected_index(self):
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value):
        self._selected_index = value

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @property
    def blocks_to_break(self):
        return self._blocks_to_break

    @blocks_to_break.setter
    def blocks_to_break(self, value):
        self._blocks_to_break = value
