from __future__ import annotations

import copy
import json
import logging
from typing import TYPE_CHECKING, cast

from woodblock.game_logic.constants import (
    LEVEL_BLOCKS,
    LEVEL_BOARDS,
    Block,
    Board,
    BoardUtils,
    CellType,
    IntsBoard,
    Level,
    Piece,
    PieceHand,
    PiecePosition,
    PlayablePieceHand,
)
from woodblock.game_logic.rules import generate_pieces

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)


class GameData:
    """Class to hold the game data."""

    def __init__(self, level: Level = Level.INFINITE, file_path: Path | None = None) -> None:
        self.board = copy.deepcopy(LEVEL_BOARDS[level])
        self.following_pieces = generate_pieces(level)
        self.pieces: PlayablePieceHand = []
        _are_there_more = self.get_more_playable_pieces()
        self.blocks_to_break = LEVEL_BLOCKS[level]

        self.recent_piece: tuple[Piece, PiecePosition] | None = None

        if level == Level.CUSTOM:
            self.load_game_data(file_path)

    def get_more_playable_pieces(self) -> bool:
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
                return False  # No more pieces
            self.pieces = cast("PlayablePieceHand", list(self.following_pieces[0]))
            self.following_pieces = self.following_pieces[1:]
            return True  # New pieces
        return True  # Still has pieces

    def __eq__(self, other: object) -> bool:
        """Determine if two GameData objects are equal."""
        if not isinstance(other, GameData):
            return False

        return (
            self.board == other.board
            and self._normalize_pieces(self.pieces) == self._normalize_pieces(other.pieces)
            and self.following_pieces == other.following_pieces
            and self.blocks_to_break == other.blocks_to_break
            and self.recent_piece == other.recent_piece
        )

    def __hash__(self) -> int:
        """Generate a hash value for the GameData object."""
        return hash(
            (
                # Convert board to a tuple of tuples
                tuple(tuple(row) for row in self.board),
                # Use normalized pieces
                frozenset(self._normalize_pieces(self.pieces)),
                # Handle None in following_pieces and its elements
                tuple(
                    tuple(tuple(piece) if piece is not None else None for piece in group)
                    if group is not None
                    else None
                    for group in self.following_pieces
                ),
                # Integer is already hashable
                self.blocks_to_break,
                # Handle recent_piece
                (tuple(self.recent_piece[0]), self.recent_piece[1]) if self.recent_piece else None,
            ),
        )

    @staticmethod
    def _normalize_pieces(pieces: PlayablePieceHand) -> set[frozenset[Block] | None]:
        """Convert pieces to a set of frozensets, ignoring None.

        Allows for easy comparison and hashing of pieces.

        Args:
            pieces (PlayablePieceHand): The list of pieces to normalize.

        Returns:
            set[frozenset[tuple[int, int]]]: A set of frozensets representing the normalized pieces.

        """
        return {frozenset(piece) if piece is not None else None for piece in pieces}

    def save_game_data(self, file_path: Path | None) -> None:
        """Save the current data of the game to a file (JSON format).

        Args:
            file_path (Path): The path to the file where the game data will be saved.

        """
        if not file_path:
            LOGGER.error("File path is not provided.")
            return

        game_data = {
            "board": BoardUtils.to_int_matrix(self.board),
            "following_pieces": self.following_pieces,
            "pieces": self.pieces,
            "blocks_to_break": self.blocks_to_break,
        }
        with file_path.open("w") as file:
            json.dump(game_data, file)

    def load_board(self, game_data: dict) -> Board | None:
        """Load the board from the game data and validate its structure."""
        loaded_int_matrix: IntsBoard | None = game_data.get("board")
        if loaded_int_matrix is None:
            LOGGER.error("Failed to load board. Please verify the custom game data format.")
            return None
        expected_rows = len(self.board)
        expected_cols = len(self.board[0]) if self.board else 0
        actual_rows = len(loaded_int_matrix)
        actual_cols_set = {len(row) for row in loaded_int_matrix}
        if (
            actual_rows != expected_rows
            or len(actual_cols_set) != 1
            or (len(actual_cols_set) == 1 and next(iter(actual_cols_set)) != expected_cols)
        ):
            raise ValueError(
                f"Inconsistent board dimensions: expected {expected_rows}x{expected_cols}, "
                f"got {actual_rows}x{list(actual_cols_set)}"
                f"{' (different cell numbers per row)' if len(actual_cols_set) > 1 else ''}"
            )
        return BoardUtils.from_int_matrix(loaded_int_matrix)

    def load_following_pieces(self, game_data: dict) -> list[PieceHand] | None:
        """Load following pieces from the game data and validate their structure."""
        loaded_following_pieces: list[PieceHand] | None = game_data.get("following_pieces")
        if loaded_following_pieces is None:
            LOGGER.error(
                "Failed to load following_pieces. Please verify the custom game data format."
            )
            return None
        rows = len(self.board)
        cols = len(self.board[0]) if rows > 0 else 0
        for piece_hand_idx, piece_hand in enumerate(loaded_following_pieces):
            for piece_idx, piece in enumerate(piece_hand):
                for block_idx, block in enumerate(piece):
                    if not (0 <= block[0] < rows and 0 <= block[1] < cols):
                        raise ValueError(
                            f"Block coordinate out of bounds in following_pieces: "
                            f"group {piece_hand_idx}, piece {piece_idx}, block {block_idx}, "
                            f"coord {block}, board size {rows}x{cols}"
                        )
        return [
            [
                [
                    (int(block[0]), int(block[1]))
                    for block in piece
                    if (
                        isinstance(block, (list, tuple))
                        and len(block) == 2
                        and all(isinstance(coord, int) for coord in block)
                    )
                ]
                if piece is not None
                else []
                for piece in piece_hand
            ]
            for piece_hand in loaded_following_pieces
        ]

    def load_pieces(self, game_data: dict) -> PlayablePieceHand | None:
        """Load pieces from the game data and validate their structure."""
        loaded_pieces: PieceHand | None = game_data.get("pieces")
        if loaded_pieces is None:
            LOGGER.error("Failed to load pieces. Please verify the custom game data format.")
            return None
        rows = len(self.board)
        cols = len(self.board[0]) if rows > 0 else 0
        for piece_idx, piece in enumerate(loaded_pieces):
            if piece is not None:
                for block_idx, block in enumerate(piece):
                    if not (0 <= block[0] < rows and 0 <= block[1] < cols):
                        raise ValueError(
                            f"Block coordinate out of bounds in pieces: "
                            f"piece {piece_idx}, block {block_idx}, "
                            f"coord {block}, board size {rows}x{cols}"
                        )
        return [
            [
                (int(block[0]), int(block[1]))
                for block in piece
                if (
                    isinstance(block, (list, tuple))
                    and len(block) == 2
                    and all(isinstance(coord, int) for coord in block)
                )
            ]
            if piece is not None
            else None
            for piece in loaded_pieces
        ]

    def load_blocks_to_break(self, game_data: dict) -> int | None:
        """Load the number of blocks to break from the game data and validate its value."""
        loaded_blocks_to_break: int | None = game_data.get("blocks_to_break")
        if loaded_blocks_to_break is None:
            LOGGER.error(
                "Failed to load blocks_to_break. Please verify the custom game data format."
            )
            return None
        target_blocks_on_board = sum(
            cell.type == CellType.TARGET for row in self.board for cell in row
        )
        if loaded_blocks_to_break > target_blocks_on_board:
            raise ValueError(
                f"Loaded blocks to break ({loaded_blocks_to_break}) exceed target blocks on board "
                f"({target_blocks_on_board})"
            )
        return loaded_blocks_to_break

    def load_game_data(self, file_path: Path | None) -> None:
        """Load the game data from a file."""
        if not file_path:
            LOGGER.error("File path is not provided.")
            return
        if not file_path.exists():
            LOGGER.error("File not found.")
            return

        with file_path.open() as file:
            game_data = json.load(file)

        board = self.load_board(game_data)
        if board is not None:
            self.board = board

        following_pieces = self.load_following_pieces(game_data)
        if following_pieces is not None:
            self.following_pieces = following_pieces

        pieces = self.load_pieces(game_data)
        if pieces is not None:
            self.pieces = pieces

        blocks_to_break = self.load_blocks_to_break(game_data)
        if blocks_to_break is not None:
            self.blocks_to_break = blocks_to_break
