# Review report: PR #63, "limits from config"

**REVIEWED:** PR #63. Head `e07b3d8`, merge base `5a1c2f6`. Both SHAs come from PR.md. I had no tools, so I could not check them against a checkout or a worktree. This review covers only `change.patch` read against `base/ratelimit.py`. Commit `91c4e7a` and `config/limits.yaml` were not provided, so they are **not reviewed**. I cannot confirm that `91c4e7a` is even reachable from `e07b3d8`.

**TIER:** **High.** These limits protect a shared production backend, and this PR moves them into configuration. That is the "network exposure, including its configuration" case. A config value or a missing file now decides whether the backend is protected at all. **This is round 1 of 2.** Until a second independent round runs, ideally on a different vendor, this PR is not reviewed under the skill.

**REVIEWERS:**
- Reviewer: one fresh instance (claude-opus-5-5) with no part in writing the change.
- Author: unknown. No commit trailers were provided, so authorship cannot be recorded.
- Data: the code carries no personal data or secrets. I could not confirm whether this endpoint is approved under Step 3; the owner should confirm that before round 2.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `ratelimit.py` `load_limits`, `except FileNotFoundError: pass`, together with `allowed`, `if limit is None: return True` | Several conditions return `{}`: the deploy lacks `config/limits.yaml`, the file is renamed or mounted elsewhere, or `91c4e7a` is not in the merged history. With `{}`, `allowed()` returns `True` for every plan at any usage. Rate limiting is silently off and the shared backend is unprotected. The docstring presents this as intended ("means no limits are configured"). | `load_limits("/nonexistent")` should raise, or `allowed("free", 10**9, load_limits("/nonexistent"))` should be `False`. Today it returns `{}` and `True`. |
| 2 | **P1** | `ratelimit.py` `allowed`, `limits.get(plan)` and `return True` | Any plan missing from the file gets unlimited requests. Examples: a new plan added in code but not in config, a case or typo mismatch (`Pro:` vs `pro`), or a deleted line. The base code raised `KeyError` here, so this change turns failing loudly into failing open. | `allowed("enterprise", 10**9, {"free": 100})` should be `False` or raise. Today it is `True`. |
| 3 | **P1** | `ratelimit.py` `LIMITS_PATH = "config/limits.yaml"` | The path is relative, so `open()` resolves it against the process working directory, not the repository or module directory. A service started from another directory (systemd, a container `WORKDIR`, a test runner) gets `FileNotFoundError`. Finding 1 then turns that into no limits. | Call `os.chdir(tmpdir)`, then `load_limits()`. It should still find the file, or raise. Today it returns `{}`. |
| 4 | **P1** | `ratelimit.py` `load_limits`, `int(n)` | Operations editing the file is the whole purpose of the request, and normal edits crash the parser with `ValueError`. Examples: an inline comment (`free: 100  # daily`), a quoted value (`free: "100"`), a YAML parent key (`limits:` followed by indented entries, where `int("\n")` fails), or `free: 1e3`. The file is named `.yaml`, but the parser is not YAML. Depending on the unseen caller, this is either a startup or request outage, or an exception path that bypasses limiting. | `load_limits` on a file containing `free: 100  # daily` should return `{"free": 100}` or raise a clear config error naming the line. Today it raises an unhandled `ValueError`. |
| 5 | **P1** (evidence: inferred from absence) | `ratelimit.py` `load_limits`, no caller in the patch | Nothing in the patch calls `load_limits`, and nothing re-reads the file after a change. If the caller still passes the old in-code dict, editing the file has no effect. If the caller loads once at startup, a change still needs a restart. Either way, "change them without a deploy" is not met. I cannot confirm this without the caller. | Edit the limits file while the service runs, then confirm `allowed` sees the new value without a restart. |
| 6 | **P2** | `tests/test_ratelimit.py` | The only test covers `allowed` with an in-memory dict, which is base behaviour. Nothing tests `load_limits`, the missing-file path, an unknown plan, or parsing. "Tests pass" is a claim I could not run, and the tests would pass with findings 1 to 4 present. | Add the tests suggested for findings 1 to 4. Each should fail against the current head. |

**FILES NEEDED BUT NOT PROVIDED:**
- `config/limits.yaml`, to check its real format against the parser in finding 4 and that every plan is present for finding 2.
- Commit `91c4e7a` and confirmation that it is an ancestor of `e07b3d8`.
- Every caller of `allowed` and `load_limits`, and where they get `limits` (finding 5).
- The source of plan names, to compare against the config keys.
- The CI check list and its results for `e07b3d8`.
- Commit trailers, for authorship.

---

**Close-out**

ADJUDICATION: pending. The author must decide each finding, and a reviewer does not adjudicate its own findings. Findings 1 to 5 are P0 or P1, so they cannot be deferred. Each must be fixed with a regression test, or rejected with evidence.

VERIFIED AFTER FIXES: nothing yet. No fixes exist.

MERGE RECOMMENDATION: **Do not merge.**
- **P0 blocker open:** the limiter fails open when the file is missing (finding 1).
- **P1s open:** findings 2 to 5.
- **Round 2 not run:** the second High-tier round is outstanding.
- **Checks unverified:** CI status was not provided, and a missing check is not green.
- **Unreviewed code:** `91c4e7a` and the config file have not been seen.
- **Owner decision pending:** should missing or unknown limits fail closed (deny or error) or fail open? I recommend failing closed, with a clear startup error.

```json
{
  "verdict": "do not merge",
  "findings": [
    {"severity": "P0", "evidence_level": "code-read", "location": "ratelimit.py load_limits (except FileNotFoundError: pass) + allowed (limit is None -> True)", "scenario": "Config file missing, mislocated, or its commit 91c4e7a not merged: load_limits returns {} and allowed() returns True for every plan at any usage; shared backend unprotected.", "fix": "Raise on a missing or unreadable file (fail at startup); never treat absent config as unlimited."},
    {"severity": "P1", "evidence_level": "code-read", "location": "ratelimit.py allowed, limits.get(plan) / return True", "scenario": "Plan absent from config (new plan, typo, case mismatch) gets unlimited requests; base code raised KeyError.", "fix": "Deny or raise for unknown plans; validate at load that every known plan has a limit."},
    {"severity": "P1", "evidence_level": "code-read", "location": "ratelimit.py LIMITS_PATH = \"config/limits.yaml\"", "scenario": "Relative path resolves against the process CWD; started from another directory, the file is not found and finding 1 disables limits.", "fix": "Resolve relative to the module or repo root, or take an absolute path from an env var; fail if not found."},
    {"severity": "P1", "evidence_level": "code-read", "location": "ratelimit.py load_limits, int(n)", "scenario": "Inline comments, quoted values, YAML parent keys or 1e3 raise an unhandled ValueError, so a normal ops edit causes an outage or a limiting bypass.", "fix": "Use a real YAML parser (yaml.safe_load), validate positive ints per plan, report a clear error with the offending key."},
    {"severity": "P1", "evidence_level": "inferred", "location": "ratelimit.py load_limits (no caller in patch)", "scenario": "Nothing calls load_limits or re-reads the file, so edits have no effect or need a restart; the requirement 'change without a deploy' is unmet.", "fix": "Wire the caller to load from config and reload on change or on a TTL, keeping the last good config if a reload fails."},
    {"severity": "P2", "evidence_level": "code-read", "location": "tests/test_ratelimit.py", "scenario": "Tests cover only base allowed() behaviour; load_limits, missing file, unknown plan and parsing are untested, so the suite passes with findings 1-4 present.", "fix": "Add the regression tests listed for findings 1-4."}
  ]
}
```