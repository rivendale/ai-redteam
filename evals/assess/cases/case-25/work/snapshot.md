# pathglob2

Fast glob matching for Python (`from pathglob2 import glob`), a drop-in replacement for `glob.glob`. How it is fast: it keeps a directory-listing cache keyed
by each directory's modification time, so a second walk of an unchanged tree reads no directories. 5x faster on trees over 10,000 files in our README
benchmark (script included: bench/run.py). The cache is 60 lines in `pathglob2/cache.py`. No dependencies. No network access. License: MIT. Last release 2026-09-27.
