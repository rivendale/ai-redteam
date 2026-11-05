#!/usr/bin/env bash
# ai-redteam #133 rule-3 gate: pr-review BASE (main + cases 88-92, 0b6eb30) vs NEW (same + #133's two commits), 18 pr-review cases,
# 3 repeats each side, claude-sonnet-5-5, sealed lane run_reviews.sh from an empty cwd. Run in stages: STAGE=1|2|3 runs repeat N
# (one BASE lane and one NEW lane, 36 reviews); the caller checks the account's weekly usage between stages.
# Published copy: run directories sit directly beside this script (the original wrote them under runs/), and SR replaces a
# local scratch path.
set -u
R=$(cd "$(dirname "$0")" && pwd)
SR="${SR:?set SR to the folder holding two worktrees: art (BASE, 0b6eb30) and art-new (0b6eb30 + #133)}"
CAP=20; EST=0.30
export MODEL=claude-sonnet-5-5 GATE_RULE='evals/README.md#gate-rule (rivendale/ai-redteam, as of main 2026-11-05)' GATE_MARGIN=4 GATE_FA_MARGIN=3
n=${STAGE:?STAGE=1, 2 or 3}
spent() { python3 - "$R" <<'PY'
import glob, json, math, sys
t = 0.0
for f in glob.glob(sys.argv[1] + "/r[0-9]-*/_meta/*.usage.json"):
    try:
        c = json.load(open(f)).get("total_cost_usd")
    except (OSError, ValueError):
        c = None
    t += c if isinstance(c, (int, float)) and math.isfinite(c) and c >= 0 else 0.30
print(f"{t:.4f}")
PY
}
for text in base new; do
  wt=$SR/art; [ "$text" = new ] && wt=$SR/art-new   # each side uses its own worktree's runner, cases and skill (evals/ is identical)
  skill=$wt/skills/pr-review/SKILL.md; LANE=$wt/evals/tools/run_reviews.sh; CASES=$wt/evals/cases
  out=$R/r$n-pr-review-$text; mkdir -p "$out"
  left=$(python3 -c "print(max(0.0, $CAP - $(spent)))")
  (cd "$(mktemp -d)" && MAX_COST_USD=$left EST_REVIEW_USD=$EST CASES=$CASES APPLIES=pr-review bash "$LANE" "$skill" "$out" 2) > "$out.log" 2>&1
  echo "$(date -u +%FT%TZ) r$n $text exit=$? spent=$(spent)"
done
