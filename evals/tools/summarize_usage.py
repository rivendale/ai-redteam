#!/usr/bin/env python3
"""Sum token usage and cost over a run directory written by run_reviews.sh.
usage: summarize_usage.py RUN_DIR [RUN_DIR ...]"""
import glob, json, sys
for d in sys.argv[1:]:
    rows = [json.load(open(f)) for f in sorted(glob.glob(f"{d}/case-*.usage.json"))]
    if not rows:
        print(f"{d}: no usage files"); continue
    tok = lambda k: sum((r.get("usage") or {}).get(k, 0) or 0 for r in rows)
    cost = sum(r.get("total_cost_usd") or 0 for r in rows)
    secs = sum(r.get("duration_ms") or 0 for r in rows) / 1000
    models = sorted({m for r in rows for m in r.get("models", [])})
    print(f"{d}: {len(rows)} reviews, models {models}, input {tok('input_tokens')}, cache read "
          f"{tok('cache_read_input_tokens')}, cache write {tok('cache_creation_input_tokens')}, output "
          f"{tok('output_tokens')}, list-price cost ${cost:.2f} (${cost/len(rows):.3f}/review), {secs/len(rows):.0f}s/review")
