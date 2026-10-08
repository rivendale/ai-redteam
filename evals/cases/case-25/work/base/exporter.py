"""Customer export."""
import csv


def load_people(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))
