"""Fail when the dependency report lists an advisory that is not in .audit-ignore."""
import json
import sys


def blocking(report_path, ignore_path=".audit-ignore"):
    """Advisory ids in the report that are not ignored."""
    try:
        ignored = {l.strip() for l in open(ignore_path) if l.strip() and not l.startswith("#")}
    except FileNotFoundError:
        ignored = set()
    report = json.load(open(report_path))
    return sorted(a["id"] for a in report["advisories"] if a["id"] not in ignored)


if __name__ == "__main__":
    left = blocking(sys.argv[1])
    print("\n".join(left))
    sys.exit(1 if left else 0)
