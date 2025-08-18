import csv
import os

from game_logic.constants import DATA_PATH


def stats_to_file(filename, irl_timestamp, level_name, finished, elapsed_time, memory_used, states_generated, num_moves):
    """Store statistics to a CSV file

    Args:
        filename (str): The name of the file to write to.
        irl_timestamp (str): The timestamp of the game.
        level_name (str): The name of the level.
        finished (bool): Whether the game was finished.
        elapsed_time (float): The time taken to finish the game.
        memory_used (int): The memory used during the game.
        states_generated (int): The number of states generated during the game.
        num_moves (int): The number of moves made during the game.

    """

    full_path = os.path.join(DATA_PATH, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    file_exists = os.path.isfile(full_path)
    with open(full_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(['Timestamp', 'Level', 'Finished', 'Elapsed Time (s)', 'Memory Used (bytes)', 'States Generated', 'Number of Moves'])

        writer.writerow([irl_timestamp, level_name, finished, elapsed_time, memory_used, states_generated, num_moves])

    print(f'Stored stats to {full_path}')


def moves_to_file(filename, irl_timestamp, level_name, elapsed_time, num_moves, moves):
    """Writes the moves to a CSV file with all moves in a single line.

    Args:
        filename (str): The name of the file to write to.
        irl_timestamp (str): The timestamp of the execution.
        level_name (str): The name of the level.
        elapsed_time (float): The time taken to compute the moves.
        moves (list): The list of moves, where each move is a tuple (piece, position).

    """

    full_path = os.path.join(DATA_PATH, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    file_exists = os.path.isfile(full_path)
    with open(full_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(['Timestamp', 'Level', 'Elapsed Time (s)', 'Number of Moves', 'Moves'])

        # Combine all moves into a single string
        moves_str = "; ".join([f"Piece {piece} to {position}" for piece, position in moves])
        writer.writerow([irl_timestamp, level_name, elapsed_time, num_moves, moves_str])

    print(f'Stored moves to {full_path}')


def get_recent_files(folder, count):
    """Get the most recent files from a folder

    Args:
        folder (str): The folder to search for files
        count (int): The number of recent files to return

    Returns:
        List[str]: The list of recent file names

    """

    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
    return files[:count]
