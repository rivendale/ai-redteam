# PR Review: PR #63, "limits from config"

## Review report

**REVIEWED:** PR #63. Head `e07b3d8`, merge base `5a1c2f6`. Both SHAs come from PR.md as asserted. I had no tools, so I could not check out the head in a throwaway worktree or confirm that `change.patch` equals `5a1c2f6..e07b3d8`. This review covers the patch as given, applied to `base/`. It does not cover the head SHA itself.

**TIER: High.** The limits protect a shared production backend. This change moves an availability and abuse control into configuration and changes its failure behaviour. Step 2 covers this case: "config that alters who can access what" is High. When in doubt, the skill says to take the higher tier. **This is round 1 of 2. Until a second round runs, preferably on a different vendor, the PR is not reviewed.**

**DATA (Step 3):** The patch carries no secrets or personal data. Sending it to a reviewer endpoint raises no data concerns.

**REVIEWERS:** Claude Opus 5.5 (`claude-opus-5-5`), a fresh instance that did not write this change. I don't know the author: commit trailers were not provided.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `ratelimit.py` `load_limits` (`except FileNotFoundError: pass`) together with `allowed` (`if limit is None: return True`) | If the config file is missing, `load_limits()` returns `{}` and `allowed()` returns `True` for every plan. Rate limiting switches off silently and the shared backend loses its protection. This happens in three realistic cases: (a) `LIMITS_PATH` is relative, so the process starts from any other working directory; (b) commit `91c4e7a` is not in the merged range, or the file is left out of the deploy artefact; (c) operations rename or move the file. Nothing logs or alerts. Before this change, an unknown plan raised `KeyError` (fail-closed). | `load_limits("/nonexistent")` should raise, or the service should refuse to start. `allowed("free", 10**9, load_limits("/nonexistent"))` must not return `True`. Fails today. |
| 2 | **P0** | `ratelimit.py` `allowed`, `limits.get(plan)` → `return True` | Any plan name absent from the file gets unlimited requests. Examples: a typo, a newly added plan, a case mismatch (`Free` vs `free`), or a quoted YAML key (`"pro": 1000` is parsed as key `"pro"` with the quotes kept, so lookups for `pro` miss). A single editing mistake by operations removes the limit for a whole plan. | `allowed("pro", 10**9, load_limits(<file containing '"pro": 1000'>))` should be `False`, and `allowed("unknown", 10**9, {"free": 100})` should be `False` or raise. Both return `True` today. |
| 3 | **P1** | `ratelimit.py` `load_limits`, the `int(n)` line | The file is named `.yaml`, but the parser only handles flat `key: int` lines. Ordinary YAML that operations will plausibly write raises an uncaught `ValueError` at load: `free: 100  # daily` (inline comment), `free: "100"`, or nested `plans:\n  free: 100` (where `int("")` fails on the `plans:` line). Depending on the unseen caller, this either crashes startup or crashes at request time. Duplicate keys silently take the last value. | Load a file containing `free: 100  # daily` and assert the result is `{"free": 100}`, or assert a clear config error naming the line. Today it raises a bare `ValueError`. |
| 4 | **P1** | `tests/test_ratelimit.py` (whole file) | The claim "Tests pass" says nothing about this change. The only test calls `allowed()` with a hand-built dict and would pass against the base code unchanged. Nothing tests `load_limits`, the missing-file path, the missing-plan path, or the comment and whitespace handling. Findings 1–3 all ship undetected. I did not run the test. | The tests from findings 1–3. Also add a round-trip test on the real `config/limits.yaml` asserting each plan's value equals the previous in-code value. |
| 5 | **P1** (scope, against the request) | `ratelimit.py` `LIMITS_PATH` / `load_limits`; no caller in the diff | The request is that operations can change limits *without a deploy*. Nothing in the diff calls `load_limits`, and there is no reload mechanism. If the caller loads once at import or startup, a change needs a restart, and if the file ships inside the build artefact, it needs a redeploy. Either way the requirement is not met. The patch also does not remove the in-code limits. `base/ratelimit.py` has none, so they live in an unseen caller and may now be a second source of truth. | An integration test that edits the config file while the service is running and asserts that the new limit takes effect without a restart. Fails, or cannot be written, against this diff. |

### FILES NEEDED BUT NOT PROVIDED

- `config/limits.yaml`. I cannot check its values against the previous limits, or check its format against the parser (finding 3).
- Commit `91c4e7a`. I cannot confirm it lies between `5a1c2f6` and `e07b3d8`. If it does not, finding 1 happens on the first deploy.
- Every caller of `allowed()` and `load_limits()`, and wherever the in-code limits currently live (findings 1, 3, 5).
- The CI check results for `e07b3d8`. "Tests pass" is an assertion; I saw no check output.
- The commit log with trailers, for authorship.

## Close-out

*Not written by the reviewer.* The skill says a reviewer never adjudicates its own findings. The author must give each finding a decision. Findings 1, 2, 4 and 5 are P0 or P1, so none of them can be deferred.

**ADJUDICATION:** pending, with the author.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.**

- Two P0 fail-open paths are open. A missing file or a missing plan means no rate limit on a shared production backend.
- The High tier needs a second review round, and it has not run.
- The head SHA was not frozen or confirmed, and `91c4e7a` is unverified.
- No CI checks were seen. A missing check is not green.
- An owner decision is pending on fail-open vs fail-closed for missing or invalid config. My recommendation: fail closed (refuse to start, or keep the last known good limits) and alert.
- A design decision is pending on how a reload happens without a deploy.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by reading the patch; not executed",
      "location": "ratelimit.py load_limits (except FileNotFoundError: pass) + allowed (limit is None -> True)",
      "scenario": "config/limits.yaml is missing: relative LIMITS_PATH with a different working directory, commit 91c4e7a not in the merged range, or file left out of the deploy. load_limits returns {} and allowed returns True for every plan, so rate limiting is silently disabled on the shared backend.",
      "fix": "Fail closed: raise or refuse to start on a missing or unreadable file (or keep the last known good limits), resolve the path from config or relative to the module rather than the working directory, and log or alert."
    },
    {
      "severity": "P0",
      "evidence_level": "confirmed by reading the patch; not executed",
      "location": "ratelimit.py allowed, limits.get(plan) -> return True",
      "scenario": "A plan absent from the file (typo, new plan, case mismatch, quoted YAML key like \"pro\": 1000 kept with its quotes) gets unlimited requests. Previously this raised KeyError.",
      "fix": "Treat an unknown plan as denied or as an error, validate at load that every known plan has a limit, and strip quotes or use a real YAML parser."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading the patch; not executed",
      "location": "ratelimit.py load_limits, int(n)",
      "scenario": "Valid YAML such as 'free: 100  # daily', 'free: \"100\"' or nested 'plans:' raises an uncaught ValueError, crashing startup or requests depending on the unseen caller. Duplicate keys silently take the last value.",
      "fix": "Parse with a real YAML loader and a schema (plan -> positive int), rejecting invalid config with an error that names the offending line."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading the patch; tests not run",
      "location": "tests/test_ratelimit.py",
      "scenario": "The only test exercises allowed() with a literal dict and passes on the base code too. load_limits, missing-file, missing-plan and parse cases are untested, so 'Tests pass' does not cover this change.",
      "fix": "Add tests for the missing file, unknown plan, inline comments and quoted keys, plus a test that config/limits.yaml values equal the previous in-code limits."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred: callers and config not provided",
      "location": "ratelimit.py LIMITS_PATH / load_limits; no caller in the diff",
      "scenario": "The request requires changing limits without a deploy. Nothing calls load_limits and there is no reload, so changes likely need a restart or redeploy. The in-code limits in the unseen caller are not removed, which may leave two sources of truth.",
      "fix": "Show the caller, add a reload mechanism (mtime check or signal) with validation before swapping in new limits, and remove the old in-code limits."
    }
  ]
}
```