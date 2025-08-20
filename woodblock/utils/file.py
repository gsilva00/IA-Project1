from __future__ import annotations

import csv
import logging
from pathlib import Path

from woodblock.game_logic.constants import PathConfig, Piece, PiecePosition

LOGGER = logging.getLogger(__name__)


def stats_to_file(
    filename: Path,
    irl_timestamp: str,
    level_name: str,
    elapsed_time: float,
    memory_used: int,
    states_generated: int,
    num_moves: int,
    *,
    finished: bool,
) -> None:
    """Store statistics to a CSV file.

    Args:
        filename (Path): The name of the file to write to.
        irl_timestamp (str): The timestamp of the game.
        level_name (str): The name of the level.
        elapsed_time (float): The time taken to finish the game.
        memory_used (int): The memory used during the game.
        states_generated (int): The number of states generated during the game.
        num_moves (int): The number of moves made during the game.
        finished (bool): Whether the game was finished.

    """
    full_path = Path(PathConfig.DATA) / filename
    full_path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = full_path.is_file()
    with full_path.open(mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(
                [
                    "Timestamp",
                    "Level",
                    "Finished",
                    "Elapsed Time (s)",
                    "Memory Used (bytes)",
                    "States Generated",
                    "Number of Moves",
                ],
            )

        writer.writerow(
            [
                irl_timestamp,
                level_name,
                finished,
                elapsed_time,
                memory_used,
                states_generated,
                num_moves,
            ],
        )

    LOGGER.info(f"Stored stats to {full_path}")


def moves_to_file(
    filename: Path,
    irl_timestamp: str,
    level_name: str,
    elapsed_time: float,
    num_moves: int,
    moves: list[tuple[Piece, PiecePosition]],
) -> None:
    """Write the moves to a CSV file with all moves in a single line.

    Args:
        filename (Path): The name of the file to write to.
        irl_timestamp (str): The timestamp of the execution.
        level_name (str): The name of the level.
        elapsed_time (float): The time taken to compute the moves.
        num_moves (int): The number of moves made.
        moves (list): The list of moves, where each move is a tuple (piece, position).

    """
    full_path = Path(PathConfig.DATA) / filename
    full_path.parent.mkdir(parents=True, exist_ok=True)

    file_exists = full_path.is_file()
    with full_path.open(mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Timestamp", "Level", "Elapsed Time (s)", "Number of Moves", "Moves"])

        # Combine all moves into a single string
        moves_str = "; ".join([f"Piece {piece} to {position}" for piece, position in moves])
        writer.writerow([irl_timestamp, level_name, elapsed_time, num_moves, moves_str])

    LOGGER.info(f"Stored moves to {full_path}")


def get_recent_files(folder: Path, count: int) -> list[Path]:
    """Get the most recent files from a folder.

    Args:
        folder (Path): The folder to search for files.
        count (int): The number of recent files to return.

    Returns:
        list[Path]: The list of recent file paths.

    """
    files = [f for f in folder.iterdir() if f.is_file()]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files[:count]
