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

    def getMorePlayablePieces(self):
        """Get more pieces to play from the already generated pieces

        """

        if not any(self.pieces):
            if not self.following_pieces:
                self.pieces = []
            else:
                self.pieces = self.following_pieces[0]
                self.following_pieces = self.following_pieces[1:]
