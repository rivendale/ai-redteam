# Changelogs from commit trailers, step by step  (post, 2026-09-17)

A commit-msg hook adds a `Change:` trailer to each commit from the first word of its subject (`Fix the retry` becomes `Change: fixed`), so nobody
types one. A 21-line script reads `git log` since the last tag, groups lines by trailer type and writes the markdown. The whole script:

```python
import subprocess
from collections import defaultdict

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout

tag = git("describe", "--tags", "--abbrev=0").strip()
log = git("log", f"{tag}..HEAD", "--format=%h%n%s%n%(trailers:key=Change,valueonly)%x00")
groups = defaultdict(list)
for entry in log.split("\0"):
    parts = entry.strip().split("\n")
    if len(parts) < 3 or not parts[2].strip():
        continue
    groups[parts[2].strip().lower()].append(f"{parts[1]} ({parts[0]})")
out = [f"## Changes since {tag}", ""]
for kind in ("added", "changed", "fixed", "removed"):
    if groups[kind]:
        out += [f"### {kind.title()}", ""]
        out += [f"- {line}" for line in groups[kind]]
        out.append("")
print("\n".join(out))
```

Run on the post's sample repository it prints `## Changes since v0.3.0`, then `### Added` and `### Fixed` lists, one line per commit.
