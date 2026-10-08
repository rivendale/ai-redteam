#!/usr/bin/env bash
# Run one skill version over every eval case in a sealed, tool-less headless Claude session.
# usage: run_reviews.sh SKILL.md OUTDIR [PARALLEL]   (ONLY=case-06,case-07 to run a subset; APPLIES=pr-review or plain for the cases that target it;
# for the plain prompt pass prompts/adversarial-review.md as SKILL.md)
# Each reviewer sees only: the skill text, the case's request/context/work (from tools/prepare.py), and the same
# output-format note for every version. It never sees expected.json. No tools, no MCP servers, no settings files.
set -u
skill=$(realpath "$1"); out=$(realpath -m "$2"); par=${3:-3}
here=$(cd "$(dirname "$0")/../.." && pwd)
prep=$(mktemp -d); mkdir -p "$out/_meta"
python3 "$here/evals/tools/prepare.py" "$prep" ${ONLY:+--only "$ONLY"} ${APPLIES:+--applies "$APPLIES"} >/dev/null
export INVOCATION_ID= SKILL="$skill" OUT="$out"
review() {
  d=$1; c=$(basename "$d")
  [ -s "$OUT/$c.md" ] && return 0
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
    echo "json block with \"verdict\" and \"findings\" (each: severity, evidence_level, location, scenario, fix)."
  } > "$OUT/$c.prompt"
  # --output-format json carries the report text plus model and token usage; the report is written unchanged to
  # case-NN.md and the raw output and usage to _meta/ (score.py reads case-NN.json in preference to the .md, so
  # nothing named case-*.json may sit beside the reports), so runs stay comparable and every result can state its cost.
  timeout 900 claude -p --output-format json --tools "" --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
    --setting-sources "" --permission-mode dontAsk --disallowedTools "Bash,Write,Edit,Read,WebFetch,WebSearch" \
    < "$OUT/$c.prompt" > "$OUT/_meta/$c.claude.json" 2> "$OUT/$c.err" || echo "$c failed rc=$?" >> "$OUT/failures.txt"
  python3 - "$OUT/_meta/$c.claude.json" "$OUT/$c.md" "$OUT/_meta/$c.usage.json" <<'PYX' || { echo "$c failed: unparsable json or run error" >> "$OUT/failures.txt"; rm -f "$OUT/$c.md"; }
import json, sys
d = json.load(open(sys.argv[1]))
# A failed run can still exit 0 (is_error true, or a non-success subtype): record it as a failure, never as a report,
# or the case scores as a total miss and reads like a recall regression (second read of #13).
if d.get("is_error") or d.get("subtype", "success") != "success":
    sys.exit(f"run error: subtype={d.get('subtype')} is_error={d.get('is_error')}")
open(sys.argv[2], "w").write(d.get("result", ""))
json.dump({"models": list((d.get("modelUsage") or {}).keys()), "usage": d.get("usage"),
           "total_cost_usd": d.get("total_cost_usd"), "duration_ms": d.get("duration_ms"),
           "num_turns": d.get("num_turns")}, open(sys.argv[3], "w"), indent=1)
PYX
}
export -f review
ls -d "$prep"/case-* | xargs -P "$par" -I{} bash -c 'review "$@"' _ {}
echo "reports: $(ls "$out"/case-*.md 2>/dev/null | wc -l) of $(ls -d "$prep"/case-* | wc -l)"
rm -rf "$prep"
