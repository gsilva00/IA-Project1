from game_logic.constants import GRID_SIZE
from game_logic.rules import generate_shapes


class GameModel:
    def __init__(self):
        self._board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self._shapes = generate_shapes()
        self._shapes_visible = [True] * len(self._shapes)
        self._selected_shape = None
        self._selected_index = None
        self._score = 0
        self._blocks_to_break = 0

    def reset(self):
        self._board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self._shapes = generate_shapes()
        self._shapes_visible = [True] * len(self._shapes)
        self._selected_shape = None
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
    def shapes(self):
        return self._shapes

    @shapes.setter
    def shapes(self, value):
        self._shapes = value

    @property
    def shapes_visible(self):
        return self._shapes_visible

    @shapes_visible.setter
    def shapes_visible(self, value):
        self._shapes_visible = value

    @property
    def selected_shape(self):
        return self._selected_shape

    @selected_shape.setter
    def selected_shape(self, value):
        self._selected_shape = value

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
