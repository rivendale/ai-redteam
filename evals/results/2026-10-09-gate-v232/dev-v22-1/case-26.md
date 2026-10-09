# Redteam review: PR #63, "limits from config"

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing was run. Every trace below comes from reading the patch.

**VERDICT: REWORK.** If the config file is missing, or a plan is missing from it, the change silently removes all request limits on the shared backend these limits exist to protect.

**CONFIDENCE: medium.** Three things limit it: no tools (traces were not executed), a single reviewer, and missing inputs (`config/limits.yaml`, commit 91c4e7a, and the callers of `allowed`/`load_limits`).

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, base/README.md, base/ratelimit.py, change.patch (ratelimit.py and tests/test_ratelimit.py).
- **Not seen: `config/limits.yaml`.** This matters: whether it is well-formed and its values are correct is unknown.
- **Not seen: commit 91c4e7a.** This matters: it is unknown whether 91c4e7a lies between merge base 5a1c2f6 and head e07b3d8. If it does not, the merge ships with no config file, which triggers F1.
- **Not seen: callers of `load_limits` and `allowed`, and the old hardcoded limits.** This matters: base/ratelimit.py contains no limit values, so the "code" being replaced lives elsewhere and was not supplied.
- **Not seen: CI output behind "Tests pass".** This matters, though it is outweighed by F3.

**COVERAGE**
- **Checked:** `ratelimit.py:load_limits` and `ratelimit.py:allowed` (main path plus hostile inputs: missing file, unknown plan, YAML comments, quoted keys, nested YAML, negative/duplicate values), the test file, and PR.md's claims.
- **Not checked:** config/limits.yaml, commit 91c4e7a, callers, deploy and config-distribution mechanism, CI.

**SEATS AND GATE:** One reviewer (this session). No cross-vendor seats were requested or available. The sensitivity gate passed: no personal, financial or credential data is present. No instructions addressed to the reviewer were found in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | ratelimit.py:3, 15-16, 22-24 | A missing config file is swallowed and becomes `{}`, and `allowed` returns True for every plan. `LIMITS_PATH` is relative to the process CWD. | The service starts with a CWD other than the repo root, or 91c4e7a is not in the merged branch, or ops deletes or renames the file. `load_limits()` then returns `{}` with no error or log, every request is allowed, and the shared backend is unprotected. Nobody notices until the backend degrades. | Fail closed. Raise on a missing file at startup (or keep the last known-good limits on reload), resolve the path relative to the module or from an env var, and log the loaded limits. **Repro:** in an empty temp dir, `import ratelimit; ratelimit.allowed("free", 10**9, ratelimit.load_limits())`. Expected: False or an exception. By trace: True. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | B | ratelimit.py:22-24 | An unknown plan now means unlimited. Base code raised `KeyError` for an unknown plan; the new code allows it. | A config key that does not match the plan string the caller uses gives that plan unlimited requests silently. Examples: `Pro` vs `pro`, a quoted YAML key `"free": 100` (parsed as the key `"free"` including quotes, line 13), or a plan added in code but not in config. | Treat an unknown plan as deny, or as an explicit default limit, and log it. Validate at load time that every known plan has a limit. **Repro:** `allowed("free", 10**9, {'"free"': 100})` returns True. Expected: False or an error. | a✓ b✓ c✓ d✓ |
| F3 | High | CONFIRMED | B | tests/test_ratelimit.py:6-9 | The only test exercises `allowed` with a literal dict, and it passes on the base code too. `load_limits`, the missing-file path, the unknown-plan path and the "pro" limit are untested. "Tests pass" says nothing about this change. | A regression in parsing or in the fail-open default (F1, F2) ships with green CI. | Add tests for parsing a sample file, for missing-file behaviour, for an unknown plan, for comments and quoted keys, and for a malformed value. **Mutation:** delete `load_limits` entirely, or revert `allowed` to base. The existing test stays green, which shows it guards nothing new. | a✓ b✓ c✗ d✓ |
| F4 | High | CONFIRMED | B | ratelimit.py:12-14 | A hand-rolled `key: int` parser reads a file named `.yaml`, so ops will write YAML it cannot parse. | `free: 100  # raised for Q4` (inline comment), `"1000"` (quoted value), or a `limits:` header with indented children all raise `ValueError` from `int(...)`. An ops edit made "without a deploy" then crashes whatever calls `load_limits`, at startup or on reload. | Use `yaml.safe_load` and validate the schema (a mapping of str to non-negative int). On a reload error, keep the old limits. **Repro:** write `free: 100  # note` to the file and call `load_limits(path)`. Observed by trace: ValueError. | a✓ b✓ c✗ d✓ |
| F5 | Low | CONFIRMED | B | ratelimit.py:13-14 | Values are not validated. Negative or zero values are accepted, and duplicate keys are resolved last-wins silently. | A typo of `-100` blocks a whole plan. A duplicated key overrides the intended value without warning. | Reject negative values and duplicate keys at load time, with a clear error. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1, requirement fit.** The patch changes no caller. It is unknown whether anything calls `load_limits`, and whether limits are re-read without a restart or deploy. If nothing calls it, limits still come from code (drift from the request). If it is called once at import, a change needs a restart. Settle this by showing the call site and its reload behaviour.
- **S2.** It is unknown whether commit 91c4e7a is an ancestor of e07b3d8 and a descendant of 5a1c2f6, and whether its values equal the old hardcoded limits. Settle this with `git merge-base --is-ancestor` and a diff of the values against the old dict.
- **S3, requirement fit.** If `config/limits.yaml` is committed to the repo and shipped with the build, changing it still requires a deploy, which defeats the request. Settle this by stating how the file reaches production hosts.
- **S4.** The CWD the service runs with in production is unknown, and it decides whether F1 triggers on day one. Settle this from the service unit or container `WORKDIR`.

## REFUTED
- **"`int(n)` fails on the trailing newline."** Refuted: `int()` strips surrounding whitespace, so `int(" 100\n") == 100`.
- **"Values with colons are mis-split."** Refuted as a separate defect: `split(":", 1)` keeps the key intact. A value containing a colon fails `int()`, which is already covered by F4.

## WHAT HOLDS UP
- Comment lines starting with `#` are skipped correctly.
- `split(":", 1)` and `.strip()` handle ordinary `key: value` lines.
- The comparison `used_today < limit` keeps the base semantics.
- Errors other than `FileNotFoundError` (permission errors, bad ints) propagate rather than being swallowed.

## UNVERIFIED CLAIMS
- **"Tests pass."** No CI output was supplied. Confirm with the CI run for e07b3d8.
- **"The file and its values are added in commit 91c4e7a."** Not supplied. Confirm with S2.

## QUESTIONS FOR THE AUTHOR
1. Where is `load_limits` called, and how does an ops edit take effect without a deploy?
2. Is 91c4e7a in this PR's history, and do its values match the old limits?
3. Was fail-open on a missing file or unknown plan intended? If so, who signed off, given that the limits protect a shared backend?

## DECISION-MAKER SUMMARY
Do not merge. A missing or mismatched config file silently turns off rate limiting for the shared backend (F1, F2), and the tests do not exercise any of the new code (F3). Fail closed, use a real YAML parser with validation, add tests for these paths, and show the caller and reload mechanism. Merging as is risks an unthrottled production backend with no alert.

## OWNER SUMMARY
The change moves request limits into a settings file, but if that file is missing or a plan name in it is misspelled, the system quietly stops limiting requests at all. That could let traffic overwhelm the shared backend the limits are meant to protect. It should be changed to refuse or alert in those cases, and tested, before it goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "change.patch", "status": "seen", "matters": true},
    {"item": "base/ratelimit.py", "status": "seen", "matters": true},
    {"item": "base/README.md", "status": "seen", "matters": false},
    {"item": "config/limits.yaml", "status": "not_seen", "matters": true},
    {"item": "commit 91c4e7a", "status": "not_seen", "matters": true},
    {"item": "callers of load_limits/allowed and old hardcoded limits", "status": "not_seen", "matters": true},
    {"item": "CI output for e07b3d8", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"},
      {"unit": "base/ratelimit.py", "kind": "file"},
      {"unit": "change.patch", "kind": "file"},
      {"unit": "ratelimit.py:load_limits", "kind": "function"},
      {"unit": "ratelimit.py:allowed", "kind": "function"},
      {"unit": "tests/test_ratelimit.py", "kind": "file"},
      {"unit": "PR.md: Tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "config/limits.yaml", "reason": "not supplied"},
      {"unit": "commit 91c4e7a", "reason": "not supplied"},
      {"unit": "callers of load_limits and allowed", "reason": "not supplied"},
      {"unit": "CI run", "reason": "not supplied; no tools to run tests"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "ratelimit.py:3,15-16,22-24",
     "scenario": "Service starts with a CWD other than the repo root, or config/limits.yaml is absent from the merged branch; load_limits returns {} silently and allowed() returns True for every request, leaving the shared backend unthrottled.",
     "fix": "Fail closed: raise on a missing file at startup or keep last known-good limits on reload; resolve the path relative to the module or from an env var; log the loaded limits.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "In an empty temp dir: import ratelimit; ratelimit.allowed('free', 10**9, ratelimit.load_limits()). Expected False or an exception; by trace returns True."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "ratelimit.py:22-24",
     "scenario": "A config key that does not match the caller's plan string (case, quoted YAML key parsed with its quotes, plan missing from the file) makes that plan unlimited with no error; base code raised KeyError.",
     "fix": "Deny or apply an explicit default limit for unknown plans, log it, and validate at load time that every known plan has a limit.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "allowed('free', 10**9, {'\"free\"': 100}) returns True; expected False or an error."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "tests/test_ratelimit.py:6-9",
     "scenario": "The only test passes on the base code as well and never calls load_limits, so regressions in parsing or the fail-open defaults ship with green CI.",
     "fix": "Add tests for file parsing, missing file, unknown plan, comments, quoted keys and malformed values.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Delete load_limits or revert allowed() to the base version; the existing test still passes."},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "ratelimit.py:12-14",
     "scenario": "Ops writes valid YAML such as 'free: 100  # note', a quoted value, or a nested 'limits:' block; int() raises ValueError and the caller of load_limits crashes on startup or reload.",
     "fix": "Parse with yaml.safe_load, validate a str-to-non-negative-int mapping, and keep previous limits on a reload error.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Write 'free: 100  # note' to a file and call load_limits(path); by trace raises ValueError."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "ratelimit.py:13-14",
     "scenario": "A value of -100 blocks a plan entirely; a duplicated key silently overrides the earlier value.",
     "fix": "Reject negative values and duplicate keys at load time with a clear error.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "load_limits on a file with 'free: -1' then allowed('free', 0, limits) returns False; a file with 'free: 1' then 'free: 2' yields {'free': 2} with no warning."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "change.patch (no caller changed)",
     "suspicion": "Nothing may call load_limits, or it may be read only once, so limits still need code or a restart to change.",
     "unresolved_fact": "The call site of load_limits and whether it reloads without a deploy or restart."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "PR.md: commit 91c4e7a",
     "suspicion": "The config file may not be in the merged branch, or its values may differ from the old hardcoded limits.",
     "unresolved_fact": "Whether 91c4e7a is between 5a1c2f6 and e07b3d8, and a diff of its values against the old limits."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "ratelimit.py:3",
     "suspicion": "If config/limits.yaml ships inside the repo build, changing it still requires a deploy, which defeats the request.",
     "unresolved_fact": "How config/limits.yaml reaches production hosts."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "ratelimit.py:3",
     "suspicion": "The production CWD may not be the repo root, which would trigger F1 immediately.",
     "unresolved_fact": "The service's working directory in production (unit file or container WORKDIR)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "int(n) fails on the trailing newline of each line.",
     "evidence": "int() strips surrounding whitespace; int(' 100\\n') == 100."},
    {"id": "C2", "candidate": "Values containing colons are mis-split into the wrong key.",
     "evidence": "split(':', 1) keeps the key intact; a colon in the value fails int() and is covered by F4."}
  ]
}
```