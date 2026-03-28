import csv
import os

class DatasetLogger:
    def __init__(self, filename="dataset.csv"):
        self.filename = filename

        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "diff", "speed", "distance",
                    "acceleration", "jerk",
                    "attack_type"
                ])

    def log(self, diff, speed, distance, acc, jerk, attack):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([diff, speed, distance, acc, jerk, attack])