#!/usr/bin/env bash
# Run one skill version over every eval case in a sealed, tool-less headless Claude session.
# usage: run_reviews.sh SKILL.md OUTDIR [PARALLEL]   (ONLY=case-06,case-07 to run a subset; APPLIES=pr-review or plain for the cases that target it;
# for the plain prompt pass prompts/adversarial-review.md as SKILL.md; CASES=evals/assess/cases with NOTE=assess for the
# assess skill, whose output note asks for its own JSON block)
# MODEL=<id> pins the reviewer model with --model (recommended: the lane passes --setting-sources "", so a model pinned in the user's settings is ignored and the account default is used).
# Start it from an empty working directory (cd "$(mktemp -d)"), so no project instruction file in the current directory is loaded into the sealed session.
# COST CAP (optional): MAX_COST_USD=<cap> EST_REVIEW_USD=<pessimistic cost of one review>. Before EVERY review the lane adds the money
# already recorded in OUTDIR/_meta, the reviews in flight (each at the estimate, so parallel workers cannot overshoot together) and
# this review's estimate; if that crosses the cap the review is not started, it is listed in OUTDIR/cost_cap_skipped.txt and the lane
# exits 3. A cap without an estimate is refused. A review that fails without a usage record is charged at the estimate. Set the
# estimate above the dearest review you have seen (the redteam family cost up to $0.64 each on 2026-10-22); an actual cost above
# the estimate is reported at the end. The cap bounds spending only as far as the estimate is honest.
# Each reviewer sees only: the skill text, the case's request/context/work (from tools/prepare.py), and the same
# output-format note for every version. It never sees expected.json. No tools, no MCP servers, no settings files.
set -u
skill=$(realpath "$1"); out=$(realpath -m "$2"); par=${3:-3}
here=$(cd "$(dirname "$0")/../.." && pwd)
if [ -n "${MAX_COST_USD:-}" ] && [ -z "${EST_REVIEW_USD:-}" ]; then echo "MAX_COST_USD needs EST_REVIEW_USD (a pessimistic cost of one review): an unknown cost cannot be bounded" >&2; exit 2; fi
prep=$(mktemp -d); mkdir -p "$out/_meta/.inflight" "$out/_meta/.charged"; rm -f "$out/cost_cap_skipped.txt"
python3 "$here/evals/tools/prepare.py" "$prep" ${ONLY:+--only "$ONLY"} ${APPLIES:+--applies "$APPLIES"} ${CASES:+--cases "$CASES"} >/dev/null || { echo "case preparation refused or failed: nothing was reviewed" >&2; exit 1; }
export INVOCATION_ID= SKILL="$skill" OUT="$out" NOTE="${NOTE:-}" MAX_COST_USD="${MAX_COST_USD:-}" EST_REVIEW_USD="${EST_REVIEW_USD:-}"
review() {
  d=$1; c=$(basename "$d")
  [ -s "$OUT/$c.md" ] && return 0
  if [ -n "$MAX_COST_USD" ]; then
    exec 9> "$OUT/_meta/.cost.lock"; flock 9
    go=$(python3 - "$OUT" "$c" <<'PYC'
import glob, json, os, sys
out, case = sys.argv[1:3]
cap, est = float(os.environ["MAX_COST_USD"]), float(os.environ["EST_REVIEW_USD"])
spent = 0.0
for f in glob.glob(out + "/_meta/*.usage.json"):
    try:
        cost = json.load(open(f)).get("total_cost_usd")
    except (OSError, ValueError):
        cost = None
    spent += cost if isinstance(cost, (int, float)) else est        # a usage file without a cost is charged at the estimate
spent += est * len(glob.glob(out + "/_meta/.charged/*"))             # failed reviews with no usage record
spent += est * len(glob.glob(out + "/_meta/.inflight/*"))            # reviews running now
if spent + est > cap + 1e-9:
    print("stop")
else:
    open(out + "/_meta/.inflight/" + case, "w").close(); print("go")
PYC
)
    flock -u 9; exec 9>&-
    if [ "$go" != go ]; then echo "$c" >> "$OUT/cost_cap_skipped.txt"; return 0; fi
  fi
  {
    echo "You are running the following skill. Follow it exactly."
    echo; echo "=== SKILL ==="; cat "$SKILL"
    echo; echo "=== INPUTS ==="
    echo "--- ORIGINAL REQUEST (request.md) ---"; cat "$d/request.md"
    echo "--- CONTEXT (context.md) ---"; cat "$d/context.md"
    echo "--- WORK UNDER REVIEW ---"
    find "$d/work" -type f | sort | while read -r f; do echo "### file: ${f#$d/work/}"; cat "$f"; echo; done
    echo; echo "=== OUTPUT NOTE (same for every version) ==="
    echo "You have no tools in this session: you cannot run code or open links. After your report, append one fenced"
    if [ "${NOTE:-}" = assess ]; then
      echo "json block in the format the skill specifies. The item is a saved snapshot (work/snapshot.md, dated in work/meta.json);"
      echo "the context file is work/context_file.md when present."
    else
      echo "json block with \"verdict\" and \"findings\" (each: severity, evidence_level, location, scenario, fix)."
    fi
  } > "$OUT/$c.prompt"
  # --output-format json carries the report text plus model and token usage; the report is written unchanged to
  # case-NN.md and the raw output and usage to _meta/ (score.py reads case-NN.json in preference to the .md, so
  # nothing named case-*.json may sit beside the reports), so runs stay comparable and every result can state its cost.
  timeout 900 claude -p ${MODEL:+--model "$MODEL"} --output-format json --tools "" --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
    --setting-sources "" --permission-mode dontAsk --disallowedTools "Bash,Write,Edit,Read,WebFetch,WebSearch" \
    < "$OUT/$c.prompt" > "$OUT/_meta/$c.claude.json" 2> "$OUT/$c.err" || echo "$c failed rc=$?" >> "$OUT/failures.txt"
  python3 - "$OUT/_meta/$c.claude.json" "$OUT/$c.md" "$OUT/_meta/$c.usage.json" <<'PYX' || { echo "$c failed: unparsable json or run error" >> "$OUT/failures.txt"; rm -f "$OUT/$c.md"; }
import json, os, sys
d = json.load(open(sys.argv[1]))
# A failed run can still exit 0 (is_error true, or a non-success subtype): record it as a failure, never as a report,
# or the case scores as a total miss and reads like a recall regression (second read of #13).
if d.get("is_error") or d.get("subtype", "success") != "success":
    sys.exit(f"run error: subtype={d.get('subtype')} is_error={d.get('is_error')}")
open(sys.argv[2], "w").write(d.get("result", ""))
# After a safety stop the CLI can silently finish the review with a DIFFERENT model (seen on 2026-10-22: Opus 4.8 wrote most of
# the output of reviews that were pinned to Opus 5.5). Record which model produced how many output tokens and flag such a review,
# so a mixed-model report is never scored as if the pinned model had written it.
usage_by_model = d.get("modelUsage") or {}
out_by_model = {m: (u or {}).get("outputTokens", 0) for m, u in usage_by_model.items()}
wanted = os.environ.get("MODEL") or os.environ.get("ANTHROPIC_MODEL") or ""
producers = sorted(m for m, t in out_by_model.items() if t)         # every model that actually produced output tokens
# With a pinned model, anything else that produced output is a fallback. Without one (the account default), the requested identity is
# unknown, but two producers are still observable and the review is mixed: never report a mixed review as a single-model result.
other = sorted(m for m in producers if m != wanted) if wanted else (producers if len(producers) > 1 else [])
mixed = bool(other) if wanted else len(producers) > 1
flagged = mixed or bool(d.get("safety_stops"))
json.dump({"models": list(usage_by_model.keys()), "output_tokens_by_model": out_by_model, "requested_model": wanted or None,
           "requested_model_known": bool(wanted), "producers": producers, "single_model": len(producers) == 1,
           "fallback_models": other, "safety_stops": d.get("safety_stops") or 0, "mixed_model": mixed,
           "usage": d.get("usage"),
           "total_cost_usd": d.get("total_cost_usd"), "duration_ms": d.get("duration_ms"),
           "num_turns": d.get("num_turns")}, open(sys.argv[3], "w"), indent=1)
if flagged:
    with open(os.path.join(os.path.dirname(os.path.dirname(sys.argv[3])), "fallback.txt"), "a") as f:
        f.write(f"{os.path.basename(sys.argv[2])[:-3]} safety_stops={d.get('safety_stops') or 0} fallback_models={','.join(other) or '-'} requested_model_known={'yes' if wanted else 'no'}\n")
PYX
  if [ -n "$MAX_COST_USD" ]; then
    rm -f "$OUT/_meta/.inflight/$c"
    [ -f "$OUT/_meta/$c.usage.json" ] || touch "$OUT/_meta/.charged/$c"
  fi
}
export -f review
ls -d "$prep"/case-* | xargs -P "$par" -I{} bash -c 'review "$@"' _ {}
echo "reports: $(ls "$out"/case-*.md 2>/dev/null | wc -l) of $(ls -d "$prep"/case-* | wc -l)"
[ -s "$out/fallback.txt" ] && echo "WARNING: $(wc -l < "$out/fallback.txt") review(s) had a safety stop or were finished by a different model (see $out/fallback.txt); do not score them as the pinned model without saying so"
if [ -n "$MAX_COST_USD" ]; then
  python3 - "$out" <<'PYS'
import glob, json, os, sys
out = sys.argv[1]; est = float(os.environ["EST_REVIEW_USD"]); cap = float(os.environ["MAX_COST_USD"])
costs = []
for f in glob.glob(out + "/_meta/*.usage.json"):
    try:
        c = json.load(open(f)).get("total_cost_usd")
    except (OSError, ValueError):
        c = None
    if isinstance(c, (int, float)):
        costs.append(c)
print(f"cost: ${sum(costs):.3f} recorded over {len(costs)} review(s), cap ${cap:.2f}, estimate ${est:.2f} per review")
over = [c for c in costs if c > est]
if over:
    print(f"WARNING: {len(over)} review(s) cost above the estimate (largest ${max(over):.3f}); the estimate was too low, raise EST_REVIEW_USD", file=sys.stderr)
PYS
fi
rm -rf "$prep"
if [ -s "$out/cost_cap_skipped.txt" ]; then
  echo "COST CAP: $(wc -l < "$out/cost_cap_skipped.txt") review(s) not started because the next one could cross \$$MAX_COST_USD (see $out/cost_cap_skipped.txt)" >&2
  exit 3
fi
