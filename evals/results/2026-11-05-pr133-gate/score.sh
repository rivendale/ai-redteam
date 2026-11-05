#!/usr/bin/env bash
# Score every finished run dir: map pr-review severities, then score.py (cases at 0b6eb30); writes scores/<run>.{json,txt}.
set -u
R=$(cd "$(dirname "$0")" && pwd); A=<scratch>/art
mkdir -p "$R/scores" "$R/mapped"
for d in "$R"/runs/r[0-9]-pr-review-*; do
  [ -d "$d" ] || continue; n=$(basename "$d")
  python3 "$A/evals/tools/map_pr_severity.py" "$d" "$R/mapped/$n" >/dev/null
  python3 "$A/evals/score.py" --cases "$A/evals/cases" --reports "$R/mapped/$n" --skill pr-review --json "$R/scores/$n.json" > "$R/scores/$n.txt" 2>&1
  echo "$n: $(grep -E '^(TOTAL|Total|recall)' "$R/scores/$n.txt" | tail -1)"
done
