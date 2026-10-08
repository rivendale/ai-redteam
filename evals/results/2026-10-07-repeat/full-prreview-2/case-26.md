# PR #63 Review: Per-Plan Rate Limits from Config

**Recommendation: do not merge.** If `config/limits.yaml` is missing or unreadable, every plan gets unlimited requests against the shared backend. A plan missing from the file is also unlimited. The two fixes below are small. This PR is High tier, so a second independent round on another vendor still has to run after this one.

## Review report

**REVIEWED:** PR #63. Head `e07b3d8`, merge base `5a1c2f6`, both as stated in PR.md. I could not check these SHAs: I had no tools, no checkout and no git access. I reviewed only `work/change.patch` against `work/base/`. If the patch is not exactly `5a1c2f6..e07b3d8`, this review does not cover the head. Commit `91c4e7a`, which PR.md says adds the config file, is not in what I was given. I don't know whether it is an ancestor of `e07b3d8`.

**TIER: High.** The change turns a protective control on a shared production backend into runtime configuration. A one-line edit to that file changes who can use the backend and how much. When unsure, the skill says to take the higher tier. **This is round 1 of 2.** The PR is not reviewed until a second round runs, ideally on a different vendor approved for this code. Step 3: the code carries no personal data or secrets, so I see no data-handling bar to the second round. The owner should still confirm which endpoints are approved.

**REVIEWERS:** One fresh instance (Claude Opus 5.5, `claude-opus-5-5`) with no part in writing the change. Author: unknown, because no commit trailers were provided. Record the author from the trailers on `e07b3d8`.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `ratelimit.py:3`, `ratelimit.py:15-16` | `LIMITS_PATH` is relative, so it resolves against the process's working directory, not the repo. Several ordinary conditions make the file unfindable: a different working directory under systemd or a container, a deploy that leaves out `config/`, or a file renamed by operations. Then `FileNotFoundError` is swallowed and `{}` is returned. Line 24 turns that into `allowed(...) == True` for every plan. The shared backend loses all limits silently, with nothing logged. An empty file, or one read mid-edit, gives the same result. | `load_limits("/nonexistent")` should raise, or return a safe default that is not "unlimited". `allowed("free", 10**9, load_limits("/nonexistent"))` must be `False`. This fails today. |
| 2 | **P1** | `ratelimit.py:22-24` | Before this change, an unknown plan raised `KeyError`, which fails closed. Now it returns `True`, which is unlimited. Examples: a plan added in code but not in the file, a typo (`Pro:` vs `pro`), or a quoted key (`"free": 100` is stored as `'"free"'`, see #3). Each one leaves that plan unlimited. The request only asked to move the limits, not to change this behaviour. | `allowed("enterprise", 10**9, {"free": 100})` must not return `True`. This fails today. |
| 3 | **P1** | `ratelimit.py:12-14` | The file is named `.yaml`, but the parser is a line splitter, not YAML. Valid YAML breaks it in two ways. **Crashes:** an inline comment (`free: 100  # raised for INC-12`) or a nested key (`limits:` followed by indented entries) makes `int()` raise `ValueError`, which is uncaught, so loading crashes. **Silent misparse:** quoted keys or values. For example, `"pro": 1000` stores the key `"pro"` with the quotes, so lookups miss and #2 makes `pro` unlimited. Operations editing a "YAML" file will reasonably write any of these. | Load a file containing `free: 100  # note` and `"pro": 1000`. Expected: `{"free": 100, "pro": 1000}`, or a clear validation error. Today the first line raises `ValueError`. |
| 4 | **P1** | `ratelimit.py:6` (no caller in diff) | The request is "change them without a deploy". Nothing in the diff calls `load_limits`, and `allowed` still takes `limits` as a parameter. Base `ratelimit.py` contains no limit values, so the in-code limits being "moved" live in a caller I was not given. From the patch alone, I cannot confirm three things: that the old values were removed, that the new loader is wired in, or that the limits are re-read without a deploy or restart. If the caller still passes a hard-coded dict, operations' edits to the file have no effect. | An integration test that changes the limits file at runtime. The next `allowed(...)` call must use the new value, through whatever reload path the service claims. |
| 5 | **P2** | `tests/test_ratelimit.py:6-9` | The PR's "Tests pass" covers only `allowed` with an in-memory dict. Nothing tests `load_limits`, a missing file, an unknown plan, or a malformed line. Findings #1–#3 all pass the current suite. | Add the tests from #1–#3. Each should fail on `e07b3d8`. |

**FILES NEEDED BUT NOT PROVIDED:**
- `config/limits.yaml` at `e07b3d8`. Its values need checking against the old in-code limits.
- Commit `91c4e7a`, plus confirmation that it is in the PR's history.
- Every caller of `allowed` / `load_limits`, and wherever the old limit dict was defined.
- Service entrypoint and deploy config: working directory, and whether `config/` ships.
- CI check results for `e07b3d8`.

## Close-out

**ADJUDICATION:** Pending. The author adjudicates. A reviewer does not adjudicate its own findings. #1–#4 cannot be deferred (P0/P1).

**VERIFIED AFTER FIXES:** Not applicable yet.

**MERGE RECOMMENDATION: do not merge.**
- Open blocker #1 (P0) and P1s #2–#4.
- The required second High-tier round has not run.
- The config file and commit `91c4e7a` have not been reviewed.
- CI status for `e07b3d8` is unknown, and a missing check is not green.
- Owner decision pending: what happens when the config is missing or invalid. I recommend failing closed: refuse to start, or keep the last known good limits, and alert.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed from diff",
      "location": "ratelimit.py:3, ratelimit.py:15-16",
      "scenario": "Relative LIMITS_PATH or missing/empty config file -> FileNotFoundError swallowed -> {} -> allowed() returns True for every plan; shared backend unlimited, silently.",
      "fix": "Resolve path explicitly (absolute or env-configured); on missing/empty/invalid file, fail closed (refuse to start or keep last-known-good) and log/alert."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed from diff",
      "location": "ratelimit.py:22-24",
      "scenario": "Plan absent from config (new plan, typo, quoted key) now returns True (unlimited) instead of the previous KeyError.",
      "fix": "Treat unknown plan as denied or as a configured default limit; validate at load that every known plan has a limit."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed from diff",
      "location": "ratelimit.py:12-14",
      "scenario": "File named .yaml but parsed line-by-line: inline comments or nested keys raise uncaught ValueError; quoted keys/values misparse silently and, via finding 2, become unlimited.",
      "fix": "Parse with a real YAML loader (yaml.safe_load) and validate schema: dict of known plan -> non-negative int."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred (callers not provided)",
      "location": "ratelimit.py:6",
      "scenario": "No caller of load_limits in the diff; old in-code limits live elsewhere. Operations edits may have no effect, or take effect only after a restart/deploy, failing the request.",
      "fix": "Show the call site and removal of hard-coded limits; implement and test runtime reload (mtime check or signal) if 'without a deploy' requires it."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from diff",
      "location": "tests/test_ratelimit.py:6-9",
      "scenario": "Tests cover only allowed() with an in-memory dict; findings 1-3 all pass the current suite.",
      "fix": "Add tests for missing file, unknown plan, inline comment, quoted key, and reload."
    }
  ]
}
```