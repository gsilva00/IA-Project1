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
        self.getMorePlayablePieces()
        self.blocks_to_break = copy.deepcopy(LEVEL_BLOCKS[level]) if level != INFINITE else 0

    def getMorePlayablePieces(self):
        """Get more pieces to play from the already generated pieces

        """

        if not any(self.pieces):
            if len(self.following_pieces) == 0:
                self.pieces = []
            else:
                self.pieces = self.following_pieces[0]
                self.following_pieces = self.following_pieces[1:]

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
