import sys

USAGE = "usage: tinyutils count FILE"


def count(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return len(text.splitlines()), len(text.split())


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help"):
        print(USAGE)
        return 0
    if args[0] == "count" and len(args) == 2:
        lines, words = count(args[1])
        print(f"{lines} lines, {words} words")
        return 0
    print(USAGE, file=sys.stderr)
    return 2
