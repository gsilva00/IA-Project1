from game_logic.constants import GRID_SIZE
from game_logic.rules import generate_shapes

class GameModel:
    def __init__(self):
        self.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.shapes = generate_shapes()
        self.selected_shape = None
        self.score = 0
        self.grid_offset_y = 2

    def reset(self):
        self.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.shapes = generate_shapes()
        self.selected_shape = None
        self.score = 0
        self.grid_offset_y = 2

    # def set_board(self, board):
    #     self.board = board

    # def set_shapes(self, shapes):
    #     self.shapes = shapes

    # def set_selected_shape(self, selected_shape):
    #     self.selected_shape = selected_shape

    # def set_score(self, score):
    #     self.score = score

    # def set_grid_offset_y(self, grid_offset_y):
    #     self.grid_offset_y = grid_offset_y
