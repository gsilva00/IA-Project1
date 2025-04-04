import csv
import os
from datetime import datetime

from game_logic.constants import DATA_PATH


def stats_to_file(filename, elapsed_time, memory_used, states_generated, num_moves):
    full_path = os.path.join(DATA_PATH, filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    file_exists = os.path.isfile(full_path)
    with open(full_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(['Timestamp', 'Elapsed Time', 'Memory Used', 'States Generated', 'Number of Moves'])

        writer.writerow([datetime.now().isoformat(), elapsed_time, memory_used, states_generated, num_moves])

    print(f'Stored stats to {full_path}')
