import csv
import os

class Logger:
    def __init__(self, filename="ml_logs.csv"):
        self.filename = filename

        # Create file with header if not exists
        if not os.path.exists(filename):
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["diff", "speed", "distance", "label", "prediction"])

    def log(self, diff, speed, distance, label, prediction):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([diff, speed, distance, label, prediction])