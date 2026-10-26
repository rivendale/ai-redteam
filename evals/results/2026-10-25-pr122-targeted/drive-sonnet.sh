#!/usr/bin/env bash
# #122 follow-up: pr-review cases 35 and 61 on Sonnet, BASE and NEW, 3 runs; overall cap = what is left of the $30 line.
set -u
R=$(cd "$(dirname "$0")" && pwd)
LANE=$HOME/work/icf/ai-redteam/evals/tools/run_reviews.sh
CAP=4.30; EST=0.45; PAIR_EST=0.40
export MODEL=claude-sonnet-5-5
spent() { python3 - "$R" <<'PY'
import glob, json, math, sys
t = 0.0
for f in glob.glob(sys.argv[1] + "/runs/s[0-9]-*/_meta/*.usage.json"):
    try:
        c = json.load(open(f)).get("total_cost_usd")
    except (OSError, ValueError):
        c = None
    t += c if isinstance(c, (int, float)) and math.isfinite(c) and c >= 0 else 0.45
print(f"{t:.4f}")
PY
}
for n in 1 2 3; do
  left=$(python3 -c "print($CAP - $(spent))")
  if ! python3 -c "import sys; sys.exit(0 if $left >= 4 * $PAIR_EST else 1)"; then echo "SKIPPED pair s$n: left \$$left"; continue; fi
  for text in base new; do
    out=$R/runs/s$n-pr-review-$text; mkdir -p "$out"
    left=$(python3 -c "print(max(0.0, $CAP - $(spent)))")
    (cd "$(mktemp -d)" && MAX_COST_USD=$left EST_REVIEW_USD=$EST CASES=$HOME/work/icf/ai-redteam/evals/cases APPLIES=pr-review \
       ONLY=case-35,case-61 bash "$LANE" "$R/skills/pr-review-$text.md" "$out" 2) > "$out.log" 2>&1
    echo "$(date -u +%FT%TZ) s$n $text exit=$? spent=$(spent)"
  done
done
echo "done spent=$(spent)"
