#!/usr/bin/env bash
# Re-score the six published runs: map pr-review severities, then score.py with the cases at 0b6eb30.
#   A=<an ai-redteam checkout at 0b6eb30 or later with cases 88-92> [OUT=dir] ./score.sh
# Writes OUT/<run>.{json,txt} (default: ./rescored, so the published scores/ are not overwritten) and exits 1 unless all
# six runs were found and scored. Compare with scores/: the JSON should be identical.
set -u
R=$(cd "$(dirname "$0")" && pwd)
A="${A:?set A to an ai-redteam checkout that has cases 88-92}"
OUT="${OUT:-$R/rescored}"
mkdir -p "$OUT/mapped"
n=0
for d in "$R"/r[0-9]-pr-review-*/; do
  [ -d "$d" ] || continue; b=$(basename "$d")
  python3 "$A/evals/tools/map_pr_severity.py" "$d" "$OUT/mapped/$b" >/dev/null || { echo "map failed: $b" >&2; exit 1; }
  python3 "$A/evals/score.py" --cases "$A/evals/cases" --reports "$OUT/mapped/$b" --skill pr-review --json "$OUT/$b.json" > "$OUT/$b.txt" 2>&1
  echo "$b: $(grep -E '^recall' "$OUT/$b.txt" | tail -1)"; n=$((n + 1))
done
[ "$n" -eq 6 ] || { echo "scored $n runs, expected 6" >&2; exit 1; }
