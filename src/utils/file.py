import csv
import os
from datetime import datetime

from game_logic.constants import DATA_PATH


def stats_to_file(filename, elapsed_time, memory_used, states_generated, num_moves):
    """Store statistics to a CSV file

    Args:
        filename (str): The name of the file to store the stats
        elapsed_time (float): The elapsed time in seconds
        memory_used (int): The memory used in bytes
        states_generated (int): The number of states generated
        num_moves (int): The number of moves made

    """

    full_path = os.path.join(DATA_PATH, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    file_exists = os.path.isfile(full_path)
    with open(full_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(['Timestamp', 'Elapsed Time', 'Memory Used', 'States Generated', 'Number of Moves'])

        writer.writerow([datetime.now().isoformat(), elapsed_time, memory_used, states_generated, num_moves])

    print(f'Stored stats to {full_path}')


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
