#!/usr/bin/env python3
"""Copy pr-review reports to OUT with P0-P3 severities mapped to the scorer's Critical/High/Medium/Low.
usage: map_pr_severity.py IN_DIR OUT_DIR. Only the "severity" values in the final json block change."""
import json, pathlib, re, sys
MAP = {"P0": "Critical", "P1": "High", "P2": "Medium", "P3": "Low"}
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
for f in sorted(src.glob("case-*.md")):
    t = f.read_text()
    t = re.sub(r'("severity"\s*:\s*")(P[0-3])(")', lambda m: m.group(1) + MAP[m.group(2)] + m.group(3), t)
    (out / f.name).write_text(t)
print("mapped", len(list(out.glob("case-*.md"))))
