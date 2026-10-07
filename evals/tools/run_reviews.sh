#!/usr/bin/env bash
# Run one skill version over every eval case in a sealed, tool-less headless Claude session.
# usage: run_reviews.sh SKILL.md OUTDIR [PARALLEL]   (ONLY=case-06,case-07 to run a subset)
# Each reviewer sees only: the skill text, the case's request/context/work (from tools/prepare.py), and the same
# output-format note for every version. It never sees expected.json. No tools, no MCP servers, no settings files.
set -u
skill=$(realpath "$1"); out=$(realpath -m "$2"); par=${3:-3}
here=$(cd "$(dirname "$0")/../.." && pwd)
prep=$(mktemp -d); mkdir -p "$out"
python3 "$here/evals/tools/prepare.py" "$prep" ${ONLY:+--only "$ONLY"} >/dev/null
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
  timeout 900 claude -p --tools "" --strict-mcp-config --mcp-config '{"mcpServers":{}}' \
    --setting-sources "" --permission-mode dontAsk --disallowedTools "Bash,Write,Edit,Read,WebFetch,WebSearch" \
    < "$OUT/$c.prompt" > "$OUT/$c.md" 2> "$OUT/$c.err" || echo "$c failed rc=$?" >> "$OUT/failures.txt"
}
export -f review
ls -d "$prep"/case-* | xargs -P "$par" -I{} bash -c 'review "$@"' _ {}
echo "reports: $(ls "$out"/case-*.md 2>/dev/null | wc -l) of $(ls -d "$prep"/case-* | wc -l)"
rm -rf "$prep"
