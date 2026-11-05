"""Print the next high and low tide for a station from a local CSV table."""
import csv
import sys


def next_tides(path, after):
    """Return (high, low) rows from the table at path whose time is after `after` (ISO text)."""
    high = low = None
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row["time"] <= after:
                continue
            if row["kind"] == "H" and high is None:
                high = row
            if row["kind"] == "L" and low is None:
                low = row
    return high, low


if __name__ == "__main__":
    print(next_tides(sys.argv[1], sys.argv[2]))
