# pr-review: PR #63, limits from config

## Review report

**REVIEWED:** PR #63, head `e07b3d8`, merge base `5a1c2f6`. Both SHAs are as stated in PR.md. I could not check them because this session has no tools and no checkout. I reviewed `change.patch` against `base/ratelimit.py`. I could not confirm that this patch is exactly `git diff 5a1c2f6...e07b3d8`. The PR says the config file comes from commit `91c4e7a`, which I was not given. I could not tell whether that commit is between the merge base and the head, so I do not know if it is part of this PR at all.

**TIER: High.** The diff is small, but these limits protect a shared production backend. The change moves control over how much each plan can use into a config file and changes what happens when that config is missing or incomplete. That is access control and availability for a shared resource, so I treat it like permissions config. The skill says to take the higher tier when unsure. **This is round 1 of 2.** A High-tier PR is not reviewed until a second round, ideally from a different vendor, has run.

**Data:** The material is code and invented sample data only, with no personal data or secrets. Nothing left this session.

**REVIEWERS:** Claude Opus 5.5 (`claude-opus-5-5`), a fresh session with no part in writing the change. Author: no commit trailers were provided, so authorship cannot be read and is **not recorded**.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `ratelimit.py:15-16` with `ratelimit.py:22-24` | If `config/limits.yaml` is absent, `load_limits` catches `FileNotFoundError` and returns `{}`. Then `allowed()` returns `True` for every plan. Causes include a deploy without the file, a renamed file, or a missing volume mount. Every customer becomes unlimited, the shared backend is unprotected, and nothing is logged. The base code failed closed: `limits[plan]` raised. The docstring says this is intended ("a missing file means no limits"), but it is not what the request asked for. | `load_limits("/nonexistent")` must raise, or must return limits that deny. Today it returns `{}` and `allowed("free", 10**9, {})` is `True`. |
| 2 | **P1** | `ratelimit.py:3`, `ratelimit.py:10` | `LIMITS_PATH` is relative, so it is resolved against the process working directory, not the module or repo. If the service starts from `/` or from a systemd unit with a different `WorkingDirectory`, the file is not found. That leads straight to Finding 1: all limits are silently disabled. | Run `load_limits()` with the working directory set to a temp dir while the real config exists. It should find the config or fail loudly. Today it returns `{}`. |
| 3 | **P1** | `ratelimit.py:22-24` | Any plan not in the file is unlimited. Examples: a billing plan the YAML does not list yet, such as `enterprise`, or a key typo such as `Pro:` vs `pro`. An ops edit that drops a line removes that plan's limit. The base code raised `KeyError` for unknown plans. This new behavior was not requested ("all of it, and nothing extra"). | `allowed("enterprise", 10**9, {"free": 100})` should be `False` or raise. Today it is `True`. |
| 4 | **P1** | `ratelimit.py:12-14` | The file is named `.yaml`, but the parser only handles bare `key: int` lines. Ordinary YAML an operator would write raises `ValueError` from `int(n)`. Examples: `free: 100  # daily cap`, `free: "100"`, or a nested `limits:` block (`int("\n")`). The process then fails at load, or on every request, depending on the call site, which is not shown. So a routine ops edit can take the service down. | Load a file containing `free: 100  # cap` and `limits:\n  pro: 1000`. It should parse, or be rejected with a clear validation error at startup. Today it raises a bare `ValueError`. |
| 5 | **P2** | `ratelimit.py:6` (no caller in diff) | The request says ops should change limits "without a deploy". No code in the diff calls `load_limits`, re-reads the file, or watches it. If the file is loaded once at startup, as is typical, an ops edit has no effect until a restart. I cannot confirm the caller (see FILES NEEDED). | Integration test: start the app, edit the config, send a request. The new limit applies, or the documented reload path is exercised. |
| 6 | **P2** | `tests/test_ratelimit.py:6-9` | The only test passes a hand-built dict to `allowed()`. It would pass on the base code too. Nothing tests `load_limits`, a missing file, an unknown plan or malformed lines, so Findings 1-4 all ship green. "Tests pass" is a claim I have not seen evidenced or run. | The tests listed for Findings 1-4. |
| 7 | P3 | `ratelimit.py:14` | Duplicate keys win silently by last occurrence. With `free: 100` … `free: 100000`, the later line applies and nothing warns. | A file with a duplicate key should be rejected. Today the last value is used. |

### FILES NEEDED BUT NOT PROVIDED

- `config/limits.yaml`: its values, the plans it lists, and whether it is in this PR at all.
- Commit `91c4e7a`: is it an ancestor of `e07b3d8` and a descendant of `5a1c2f6`?
- The callers of `allowed()` and `load_limits()`: when the file is loaded, whether it is reloaded, and how a `ValueError` would surface.
- The billing/plan source of truth, to check that every live plan has an entry.
- CI results for `e07b3d8`.
- Commit trailers, for authorship.

## Close-out

Not written. The author adjudicates these findings, and I do not adjudicate my own. The table is left for them:

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1-7 | *pending author* | |

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.**
- **Blocker:** Finding 1 (P0, fail-open) is unresolved. Findings 2-4 (P1) cannot be deferred.
- **Tier:** High requires a second review round, which has not run.
- **Checks:** none were shown, and a missing check is not green.
- **Owner decision pending:** when config is missing or incomplete, should the service fail closed (deny or refuse to start) or fail open? I recommend refusing to start on a missing or invalid file, and denying unknown plans.
- **Scope:** I could not confirm that the config file and `91c4e7a` are part of the reviewed head.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {"severity": "P0", "evidence_level": "confirmed_in_code", "location": "ratelimit.py:15-16, ratelimit.py:22-24", "scenario": "config/limits.yaml missing -> load_limits returns {} -> allowed() returns True for every plan; shared backend unprotected, silently", "fix": "Fail closed: raise on missing file (refuse to start) or deny when no limits are loaded; log loudly"},
    {"severity": "P1", "evidence_level": "confirmed_in_code", "location": "ratelimit.py:3, ratelimit.py:10", "scenario": "Relative LIMITS_PATH resolves against process cwd; service started elsewhere does not find the file and falls into finding 1", "fix": "Resolve path from an env var or module/app root; validate it exists at startup"},
    {"severity": "P1", "evidence_level": "confirmed_in_code", "location": "ratelimit.py:22-24", "scenario": "Plan absent from config (new plan, key typo, deleted line) gets unlimited requests; base code raised KeyError", "fix": "Deny or raise for unknown plans; validate config covers all known plans at load"},
    {"severity": "P1", "evidence_level": "confirmed_in_code", "location": "ratelimit.py:12-14", "scenario": "Valid YAML such as 'free: 100  # cap', quoted values or nested keys raise ValueError from int(); an ops edit can break the service", "fix": "Use a real YAML parser with schema validation (positive ints, known plans) and reject bad config with a clear error at load"},
    {"severity": "P2", "evidence_level": "inferred_caller_not_provided", "location": "ratelimit.py:6", "scenario": "No reload path in the diff; if loaded once at startup, ops edits need a restart, contrary to 'change without a deploy'", "fix": "Show/implement the reload mechanism (periodic re-read or signal) with last-known-good fallback"},
    {"severity": "P2", "evidence_level": "confirmed_in_code", "location": "tests/test_ratelimit.py:6-9", "scenario": "Test only exercises allowed() with a literal dict and passes on base code; load_limits, missing file, unknown plan and malformed input are untested", "fix": "Add tests for findings 1-4"},
    {"severity": "P3", "evidence_level": "confirmed_in_code", "location": "ratelimit.py:14", "scenario": "Duplicate plan keys: last value wins silently", "fix": "Reject duplicate keys at load"}
  ]
}
```