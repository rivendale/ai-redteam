#!/usr/bin/env python3
"""Copy what a reviewer may see (request.md, context.md, work/) into OUT/<case id>/, leaving expected.json behind.

    python3 evals/tools/prepare.py OUT [--only ID,...]
"""
import argparse, pathlib, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "cases"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    ids = [x for x in a.only.split(",") if x]
    out = pathlib.Path(a.out)
    n = 0
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        if ids and not any(d.name.startswith(i) for i in ids):
            continue
        dst = out / d.name
        if dst.exists():
            shutil.rmtree(dst)
        dst.mkdir(parents=True)
        for f in ("request.md", "context.md"):
            shutil.copy2(d / f, dst / f)
        shutil.copytree(d / "work", dst / "work", ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
        n += 1
    left = [p for p in out.rglob("expected.json")] + [p for p in out.rglob("*.pyc")] + [p for p in out.rglob("__pycache__")]
    if left:
        print("not for reviewers, found in the output:", left[0]); return 1
    print(f"{n} case(s) prepared in {out} (no expected.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
