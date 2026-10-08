#!/usr/bin/env bash
# Run one skill over the eval cases with OpenAI Codex as the reviewer (the opt-in cross-vendor seat).
# usage: run_reviews_codex.sh SKILL.md OUTDIR [PARALLEL]   (ONLY=case-06,case-07 for a subset; APPLIES=pr-review or plain
# for the cases that target it; CODEX_MODEL to pin)
# Codex keeps a shell even in read-only mode, so unlike the claude lane it COULD read files. Guards: an empty working
# directory, a stripped environment (no secrets in variables), --ephemeral, read-only sandbox, and every report is
# scanned by tools/scan_secrets.py before it may be published. A canary test (an injected "read this file and run
# env") leaked nothing on codex-cli 0.161.0, 2026-10-07; that is model judgment, not a sandbox guarantee.
# HOME points at an empty temporary directory, so ~ holds nothing; only CODEX_HOME (auth) is real. The read-only
# sandbox can still read absolute paths, so run injection cases only where nothing sensitive is readable.
# Each run also writes _meta/<case>.usage.json (CLI version, model, tokens) with no paths; the raw log stays local.
set -u
skill=$(realpath "$1"); out=$(realpath -m "$2"); par=${3:-2}
here=$(cd "$(dirname "$0")/../.." && pwd)
prep=$(mktemp -d); mkdir -p "$out/_meta"
python3 "$here/evals/tools/prepare.py" "$prep" ${ONLY:+--only "$ONLY"} ${APPLIES:+--applies "$APPLIES"} >/dev/null
export SKILL="$skill" OUT="$out"
review() {
  d=$1; c=$(basename "$d"); [ -s "$OUT/$c.md" ] && return 0
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
  w=$(mktemp -d); h=$(mktemp -d)
  env -i HOME="$h" PATH="$PATH" CODEX_HOME="${CODEX_HOME:-$HOME/.codex}" \
    timeout 900 codex exec -s read-only --ephemeral --skip-git-repo-check -C "$w" ${CODEX_MODEL:+-m "$CODEX_MODEL"} \
    -o "$OUT/$c.md" < "$OUT/$c.prompt" > "$OUT/_meta/$c.codex.log" 2>&1 || { echo "$c failed rc=$?" >> "$OUT/failures.txt"; rm -f "$OUT/$c.md"; }
  python3 - "$OUT/_meta/$c.codex.log" "$OUT/_meta/$c.usage.json" <<'PY2'
import json, re, sys
t = open(sys.argv[1], errors="replace").read()
v = re.search(r"OpenAI Codex v([0-9.]+)", t); m = re.search(r"^model: (\S+)", t, re.M)
k = re.search(r"tokens used\s*\n\s*([0-9,]+)", t)
json.dump({"cli": "codex", "cli_version": v and v.group(1), "model": m and m.group(1),
           "tokens": int(k.group(1).replace(",", "")) if k else None}, open(sys.argv[2], "w"))
PY2
  rm -rf "$w" "$h"
}
export -f review
ls -d "$prep"/case-* | xargs -P "$par" -I{} bash -c 'review "$@"' _ {}
echo "reports: $(ls "$out"/case-*.md 2>/dev/null | wc -l) of $(ls -d "$prep"/case-* | wc -l)"
python3 "$here/evals/tools/scan_secrets.py" "$out" || echo "SECRET SCAN FAILED: do not publish $out"
rm -rf "$prep"
