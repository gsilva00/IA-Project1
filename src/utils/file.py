import os
import csv
from datetime import datetime
from game_logic.constants import _BASE_PATH

def save_to_file(filename, data):
    full_path = os.path.join(_BASE_PATH, 'data', filename)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    file_exists = os.path.isfile(full_path)
    with open(full_path, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(['Timestamp', 'Elapsed Time'])

        writer.writerow([datetime.now().isoformat(), data])
