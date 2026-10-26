#!/usr/bin/env bash
# #122 targeted ship check. One overall cap across every output folder; pairs (BASE, NEW) start only when both fit.
set -u
R=$(cd "$(dirname "$0")" && pwd)
LANE=$HOME/work/icf/ai-redteam/evals/tools/run_reviews.sh
CAP=30; EST=0.35; PAIR_EST=0.25
export MODEL=claude-opus-5-5
spent() { python3 - "$R" <<'PY'
import glob, json, math, sys
t = 0.0
for f in glob.glob(sys.argv[1] + "/runs/*/_meta/*.usage.json"):
    try:
        c = json.load(open(f)).get("total_cost_usd")
    except (OSError, ValueError):
        c = None
    t += c if isinstance(c, (int, float)) and math.isfinite(c) and c >= 0 else 0.35
print(f"{t:.4f}")
PY
}
one() {  # skill text cases-dir applies only run
  local skill=$1 text=$2 cases=$3 applies=$4 only=$5 tag=$6
  local out=$R/runs/$tag-$skill-$text
  local left; left=$(python3 -c "print(max(0.0, $CAP - $(spent)))")
  mkdir -p "$out"
  (cd "$(mktemp -d)" && MAX_COST_USD=$left EST_REVIEW_USD=$EST CASES=$cases APPLIES=$applies ONLY=$only \
     bash "$LANE" "$R/skills/$skill-$text.md" "$out" 3) > "$out.log" 2>&1
  echo "$(date -u +%FT%TZ) $tag $skill $text exit=$? spent=$(spent)"
}
pair() {  # skill cases applies only tag ncases
  local need; need=$(python3 -c "print(2 * $6 * $PAIR_EST)")
  local left; left=$(python3 -c "print($CAP - $(spent))")
  if python3 -c "import sys; sys.exit(0 if $left >= $need else 1)"; then
    one "$1" base "$2" "$3" "$4" "$5"; one "$1" new "$2" "$3" "$4" "$5"
  else
    echo "$(date -u +%FT%TZ) SKIPPED pair $5 $1: need \$$need, left \$$left"
  fi
}
RP=$R/cases/rp
BL=$HOME/work/icf/ai-redteam/evals/cases
pair redteam   "$RP" ""         "" rp1 10
pair pr-review "$RP" pr-review  "" rp1 10
pair redteam   "$BL" ""         case-14,case-15,case-68,case-69,case-28,case-29,case-30 bl1 7
pair pr-review "$BL" pr-review  "" bl1 13
for n in 2 3; do
  pair redteam   "$RP" ""        "" rp$n 10
  pair pr-review "$RP" pr-review "" rp$n 10
done
echo "done spent=$(spent)"
