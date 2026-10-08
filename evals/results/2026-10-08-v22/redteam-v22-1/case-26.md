# Redteam review: PR #63 (limits from config)

**Single-reviewer review, no tools.** I could not run code, open the repository or fetch commit 91c4e7a. Every CONFIRMED finding below comes from tracing the supplied code by hand. The work was not written in this conversation, but no fresh reviewer instance was available.

**VERDICT: REWORK.** The change fails open: if the config file is missing, or a plan name doesn't match, every request is allowed, so the shared backend loses its protection. Nothing tests that path.

**CONFIDENCE: medium.** Three things limit it: no tools to execute anything, `config/limits.yaml` and commit 91c4e7a were not supplied, and the callers of `allowed()` / `load_limits()` were not supplied.

**INPUTS LEDGER**
- Seen: request.md, context.md, PR.md, base/README.md, base/ratelimit.py, change.patch (ratelimit.py and tests/test_ratelimit.py).
- Not seen: `config/limits.yaml`. This matters: its format decides whether the parser works at all.
- Not seen: commit 91c4e7a. This matters: it is unclear whether the commit is in the PR's range (head e07b3d8, base 5a1c2f6). If it is not, the file never ships.
- Not seen: the callers of `allowed()` and the service startup code. This matters: they decide whether `load_limits()` is called at all, from which working directory, and whether limits reload without a deploy.
- Not seen: CI output for "Tests pass". This matters little, because the test cannot detect the change anyway (F3).

**COVERAGE**
- Checked: `ratelimit.py:load_limits`, `ratelimit.py:allowed`, `ratelimit.py:LIMITS_PATH`, `tests/test_ratelimit.py`, base/ratelimit.py, PR.md claims.
- Not checked: `config/limits.yaml`, commit 91c4e7a, callers and startup code, CI run.

**SEATS AND GATE:** I was the only local reviewer. No cross-vendor seats were used (not requested; depth is standard). The sensitivity gate found no personal, credential or confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | B | change.patch `ratelimit.py:15-16`, `22-24`; `LIMITS_PATH` at line 3 | The limiter fails open. `FileNotFoundError` is swallowed and returns `{}`, and `allowed()` returns `True` for any plan not in the dict. The base code raised `KeyError` for an unknown plan. | The service starts from a working directory other than the repo root (`LIMITS_PATH` is relative). Or the file isn't deployed (see S2). Or ops writes `Free:` instead of `free:`. In each case every request from every plan is allowed with no error or log, and the shared backend is unprotected. | Fail closed. Raise (or refuse to start) when the file is missing or empty, and deny or log loudly for an unknown plan. Resolve the path relative to the module or from an env var. **Repro:** `ratelimit.allowed("free", 10**9, ratelimit.load_limits("/nonexistent"))` should be `False` or raise; it returns `True`. | a Y / b Y / c N / d Y |
| F2 | Medium | CONFIRMED | B | change.patch `ratelimit.py:12-14` | The file is named `.yaml` but parsed with a hand-rolled `split(":")` plus `int()`. Inline comments, quoted values, nesting and a top-level key all raise `ValueError` or produce garbage keys. | Ops edits the file to `pro: 1000  # raised for Q4`. `int(" 1000  # raised for Q4\n")` raises `ValueError`, and limit loading crashes. What happens next depends on the unseen caller: either startup fails or the error propagates. Likewise `limits:` followed by an indented `free: 100` makes `int("\n")` raise. | Use `yaml.safe_load` and validate the result: a dict of str to non-negative int. Or rename the format to something that isn't YAML and document it. **Repro:** write `pro: 1000  # note` to a temp file and call `load_limits(tmp)`. Expected: `{"pro": 1000}` or a clear validation error. Observed: `ValueError`. | a Y / b Y / c N / d N |
| F3 | Medium | CONFIRMED | B | change.patch `tests/test_ratelimit.py:7-9` | The only test passes a hand-built dict to `allowed()`. It passes unchanged on the base code, so it cannot detect anything this PR changed. There is no test of `load_limits`, the missing file, an unknown plan or a malformed line. | A regression in `load_limits`, or the fail-open in F1, ships with green CI. "Tests pass" in PR.md gives no assurance about this change. | Add tests: load from a temp file; missing file raises or denies; unknown plan denied; inline comment handled. Before trusting them, check each one goes red on the current patch (rule 5). **Repro:** apply only the test file to base 5a1c2f6; it passes there. Traced: base `used_today < limits[plan]` gives True for 99 and False for 100. | a Y / b Y / c N / d Y |

## NEEDS VALIDATION
- **S1.** Is the change wired in at all? The patch adds `load_limits()` but no shown code calls it, and `allowed()` still takes `limits` as an argument. Even if a caller exists, loading only once at startup still needs a restart for ops to change limits. That would miss the request's "without a deploy" if a restart counts as one. **Settles it:** the call site of `load_limits()`, and whether it reloads per request, on a timer or on a signal.
- **S2.** Does `config/limits.yaml` ship with this PR? PR.md says commit 91c4e7a adds it, but the patch contains no such file. **Settles it:** `git merge-base --is-ancestor 91c4e7a e07b3d8` and `git diff 5a1c2f6 e07b3d8 -- config/limits.yaml`.
- **S3.** Do the values in the file match the limits previously in code (plan names, numbers)? **Settles it:** a diff of the old in-code limits against the new file's contents.

## REFUTED
- **C1: "blank lines or comments crash the parser".** Withdrawn. Blank lines contain no `:`, and full-line `#` comments are skipped at line 12. Only inline comments crash, which is F2.
- **C2: "`allowed()` mis-handles a limit of 0".** Withdrawn. The code checks `limit is None`, not falsiness, so `0` correctly denies.

## WHAT HOLDS UP
- The comparison semantics are unchanged (`used_today < limit`), so a configured plan behaves as before.
- Full-line comments and blank lines are handled.
- A zero limit is respected.
- The change is small and confined to one module.
- I found no instruction aimed at the reviewer inside the work.

## UNVERIFIED CLAIMS
- **"Tests pass".** Confirm from the CI log for head e07b3d8. Even if they pass, F3 still applies.
- **"The file and its values are added in commit 91c4e7a".** Confirm with S2.

## QUESTIONS FOR THE AUTHOR
1. Where is `load_limits()` called, from what working directory, and how often is it re-read?
2. Is 91c4e7a in this PR's range, and what does the file contain?
3. Was failing open on a missing or unknown entry intended? If so, who signed off on unprotected backend traffic?

## DECISION-MAKER SUMMARY
Do not merge yet. As written, a missing config file or a mistyped plan name silently removes every request limit on the production shared backend, and the tests cannot catch it. Require fail-closed behaviour, a real YAML parser and tests of the loader; merging now risks backend overload with no alarm.

## OWNER SUMMARY
This change moves request limits into a settings file, but if that file is missing or has a typo, the system quietly stops limiting anyone. The included test doesn't check the new behaviour, so this would not be caught before release. It should be fixed to refuse to run without valid limits and given proper tests before it goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "change.patch", "status": "seen", "matters": true},
    {"item": "base/ratelimit.py", "status": "seen", "matters": true},
    {"item": "base/README.md", "status": "seen", "matters": false},
    {"item": "config/limits.yaml", "status": "not_seen", "matters": true},
    {"item": "commit 91c4e7a", "status": "not_seen", "matters": true},
    {"item": "callers of allowed()/load_limits()", "status": "not_seen", "matters": true},
    {"item": "CI output for e07b3d8", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-single-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "ratelimit.py", "kind": "file"},
      {"unit": "ratelimit.py:load_limits", "kind": "function"},
      {"unit": "ratelimit.py:allowed", "kind": "function"},
      {"unit": "tests/test_ratelimit.py", "kind": "file"},
      {"unit": "base/ratelimit.py", "kind": "file"},
      {"unit": "PR.md", "kind": "file"},
      {"unit": "base/README.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "config/limits.yaml", "reason": "not supplied"},
      {"unit": "commit 91c4e7a", "reason": "not supplied"},
      {"unit": "callers of allowed()/load_limits()", "reason": "not supplied"},
      {"unit": "CI run", "reason": "no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "change.patch ratelimit.py:15-16, 22-24 (LIMITS_PATH line 3)",
     "scenario": "When config/limits.yaml is absent at the cwd-relative path, or a plan name in it does not match exactly, load_limits returns no entry for the plan and allowed() returns True for every request, silently removing all limits on the shared backend.",
     "fix": "Fail closed: raise or refuse to start on a missing or empty file, deny and log unknown plans, and resolve the path from the module location or an env var.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "ratelimit.allowed('free', 10**9, ratelimit.load_limits('/nonexistent')); expected False or an exception, observed True."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "change.patch ratelimit.py:12-14",
     "scenario": "When ops adds an inline comment ('pro: 1000  # note') or any nested or quoted YAML, int() raises ValueError and limit loading crashes.",
     "fix": "Parse with yaml.safe_load and validate that the result maps str to non-negative int, with a clear error.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Write 'pro: 1000  # note' to a temp file and call load_limits(path); expected {'pro': 1000} or a validation error, observed ValueError."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "change.patch tests/test_ratelimit.py:7-9",
     "scenario": "The only test passes on the base code, so a broken load_limits or the fail-open path in F1 ships with green CI.",
     "fix": "Add tests for load_limits from a temp file, a missing file, an unknown plan and an inline comment; confirm each fails on the current patch.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Apply only tests/test_ratelimit.py to base 5a1c2f6 and run it; it passes, so it cannot detect this change."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "change.patch ratelimit.py:6 (load_limits has no shown caller)",
     "suspicion": "load_limits may never be called, or only at startup, so limits still require a deploy or restart to change.",
     "unresolved_fact": "The call site of load_limits() and whether it reloads without a restart."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "PR.md line 4 (commit 91c4e7a)",
     "suspicion": "config/limits.yaml may not be part of this PR's diff, so it may not ship with the code.",
     "unresolved_fact": "Whether 91c4e7a is between 5a1c2f6 and e07b3d8, and the contents of the file at e07b3d8."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "config/limits.yaml",
     "suspicion": "The config values may not match the limits previously defined in code.",
     "unresolved_fact": "A diff of the old in-code limits against the new file's plan names and numbers."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Blank lines or full-line comments crash the parser.",
     "evidence": "Blank lines contain no ':' and lines starting with '#' are skipped at ratelimit.py:12."},
    {"id": "C2", "candidate": "A limit of 0 is treated as no limit.",
     "evidence": "allowed() checks 'limit is None', not falsiness, so 0 denies."}
  ]
}
```