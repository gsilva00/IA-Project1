import copy

from game_logic.constants import GRID_SIZE, INFINITE, LEVEL_BLOCKS, LEVEL_BOARDS
from game_logic.rules import generate_pieces


class GameData:
    def __init__(self, level=INFINITE):
        self.board = copy.deepcopy(LEVEL_BOARDS[level]) if level != INFINITE else [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.pieces = generate_pieces() # TODO: Change this
        self.following_pieces = generate_pieces() # TODO: Change this
        self.blocks_to_break = copy.deepcopy(LEVEL_BLOCKS[level]) if level != INFINITE else 0

    # Review this
    # def reset(self):
    #     self.board = copy.deepcopy(LEVEL_BOARDS[self.level]) if self.level != INFINITE else [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    #     self.pieces = generate_pieces()
    #     self.following_pieces = generate_pieces()
