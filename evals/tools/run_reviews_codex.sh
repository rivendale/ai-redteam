#!/usr/bin/env bash
# Run one skill over the eval cases with OpenAI Codex as the reviewer (the opt-in cross-vendor seat).
# usage: CODEX_MODEL=<model> run_reviews_codex.sh SKILL.md OUTDIR [PARALLEL]   (ONLY=case-06,case-07 for a subset;
# APPLIES=pr-review or plain for the cases that target it). CODEX_MODEL is required: the per-run Codex home has no config.toml,
# so a silent default must not choose the model. It is passed with -m and recorded per review next to the model the CLI reports;
# a review finished by a different model is listed in fallback.txt and warned about at the end.
# Codex keeps a shell even in read-only mode, so unlike the claude lane it COULD read files. Guards: an empty working
# directory, a stripped environment (no secrets in variables), --ephemeral, read-only sandbox, and every report is
# scanned by tools/scan_secrets.py before it may be published. A canary test (an injected "read this file and run
# env") leaked nothing on codex-cli 0.161.0, 2026-10-07; that is model judgment, not a sandbox guarantee.
# HOME points at an empty temporary directory, so ~ holds nothing. CODEX_HOME is a per-run temporary directory (mode 700)
# holding only a copy of the real auth.json, removed on exit, on failure and on a signal, so history, config and cache
# under the real Codex home are not in the model's reach. Nothing is ever copied back: a refreshed token stays in the temporary home
# and is discarded (the lane says so), because a copy-back cannot be made atomic against other Codex sessions and a stale snapshot must
# never replace a newer file; if Codex asks you to sign in again afterwards, run `codex login`. The read-only sandbox restricts
# writes, not reads: the model can still read any absolute path the user can, so run injection cases only where nothing sensitive
# is readable.
# Launcher: CODEX_CMD (a command line, e.g. "node /path/to/codex.js") overrides discovery. Otherwise the first of `codex`, the
# per-user npm install under $HOME and the global npm install that starts with an EMPTY HOME is used. A launcher that only starts
# with the real HOME is refused (the model process never gets the real HOME); none usable stops the lane at once.
# Each run also writes _meta/<case>.usage.json (CLI version, model, tokens) with no paths; the raw log stays local.
set -u
skill=$(realpath "$1"); out=$(realpath -m "$2"); par=${3:-2}
here=$(cd "$(dirname "$0")/../.." && pwd)
[ -n "${CODEX_MODEL:-}" ] || { echo "set CODEX_MODEL (the model to pin); the lane no longer lets the CLI default choose" >&2; exit 2; }
real_home="${CODEX_HOME:-$HOME/.codex}"
prep=; chome=; probe_home=; snap_sum=
cleanup() {
  if [ -n "$chome" ] && [ -f "$chome/auth.json" ] && [ -n "$snap_sum" ] && [ "$(sha256sum < "$chome/auth.json")" != "$snap_sum" ]; then
    echo "note: the Codex CLI refreshed its sign-in token in the temporary home; the real auth.json was not changed. If Codex asks you to sign in again, run: codex login" >&2
  fi
  rm -rf "$chome" "$prep" "$probe_home"
}
trap cleanup EXIT; trap 'exit 143' TERM; trap 'exit 130' INT
[ -f "$real_home/auth.json" ] || { echo "no auth.json under $real_home: sign in to Codex first" >&2; exit 2; }
probe_home=$(mktemp -d)
probe() { env -i HOME="$1" PATH="$PATH" bash -c "$2 --version" >/dev/null 2>&1; }
launch=
for cand in ${CODEX_CMD:+"$CODEX_CMD"} codex "node $HOME/.local/share/codex-npm/node_modules/@openai/codex/bin/codex.js" \
            "node $(npm root -g 2>/dev/null)/@openai/codex/bin/codex.js"; do
  if probe "$probe_home" "$cand"; then launch=$cand; break; fi
done
[ -n "$launch" ] || { echo "no codex launcher starts with an empty HOME (tried CODEX_CMD, codex, the npm installs); set CODEX_CMD to a command that does not need HOME, for example: node /path/to/codex.js" >&2; exit 2; }
chome=$(mktemp -d "${TMPDIR:-/tmp}/codex-lane-XXXXXX"); chmod 700 "$chome"
( umask 077; cp "$real_home/auth.json" "$chome/auth.json" )
snap_sum=$(sha256sum < "$chome/auth.json")   # of the bytes actually copied
prep=$(mktemp -d); mkdir -p "$out/_meta"
python3 "$here/evals/tools/prepare.py" "$prep" ${ONLY:+--only "$ONLY"} ${APPLIES:+--applies "$APPLIES"} ${CASES:+--cases "$CASES"} >/dev/null || { echo "case preparation refused or failed: nothing was reviewed" >&2; exit 1; }
export SKILL="$skill" OUT="$out" LAUNCH="$launch" RUN_CODEX_HOME="$chome"
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
  env -i HOME="$h" PATH="$PATH" CODEX_HOME="$RUN_CODEX_HOME" \
    timeout 900 $LAUNCH exec -s read-only --ephemeral --skip-git-repo-check -C "$w" -m "$CODEX_MODEL" \
    -o "$OUT/$c.md" < "$OUT/$c.prompt" > "$OUT/_meta/$c.codex.log" 2>&1 || { echo "$c failed rc=$?" >> "$OUT/failures.txt"; rm -f "$OUT/$c.md"; }
  python3 - "$OUT/_meta/$c.codex.log" "$OUT/_meta/$c.usage.json" "$CODEX_MODEL" "$c" "$OUT" <<'PY2'
import json, re, sys
t = open(sys.argv[1], errors="replace").read()
v = re.search(r"OpenAI Codex v([0-9.]+)", t); m = re.search(r"^model: (\S+)", t, re.M)
k = re.search(r"tokens used\s*\n\s*([0-9,]+)", t)
want, case, out = sys.argv[3], sys.argv[4], sys.argv[5]
got = m and m.group(1)
mismatch = bool(got) and got != want
json.dump({"cli": "codex", "cli_version": v and v.group(1), "requested_model": want, "model": got, "model_mismatch": mismatch,
           "tokens": int(k.group(1).replace(",", "")) if k else None}, open(sys.argv[2], "w"))
if mismatch:
    open(out + "/fallback.txt", "a").write(f"{case} requested={want} actual={got}\n")
PY2
  rm -rf "$w" "$h"
}
export -f review
ls -d "$prep"/case-* | xargs -P "$par" -I{} bash -c 'review "$@"' _ {}
[ -s "$out/fallback.txt" ] && echo "WARNING: some reviews were finished by a different model than CODEX_MODEL (see $out/fallback.txt)" >&2
echo "reports: $(ls "$out"/case-*.md 2>/dev/null | wc -l) of $(ls -d "$prep"/case-* | wc -l)"
python3 "$here/evals/tools/scan_secrets.py" "$out" || { echo "SECRET SCAN FAILED: do not publish $out"; exit 1; }
