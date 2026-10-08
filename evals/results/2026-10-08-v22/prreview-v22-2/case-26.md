# PR #63 review: limits from config

**This review is incomplete.** The change is High tier, which needs two rounds, and only this one has run. On this round's findings alone, the recommendation is **do not merge**: the patch removes the shared backend's protection in two common situations without any error.

## Review report

**REVIEWED:** PR #63. Head `e07b3d8`, merge base `5a1c2f6`, both taken from PR.md. I had no tools, so I could not resolve either SHA, check out the head in a worktree, or confirm that `change.patch` matches `5a1c2f6..e07b3d8`. This round reviewed the supplied patch against `base/ratelimit.py`, nothing more.

**TIER:** High. The limits exist to protect a shared production backend, and this change moves that control into an operator-edited config file and changes what happens when the limit is missing. That is protective configuration that governs exposure. Where the tier was unclear, the skill says to take the higher one. High needs two rounds, preferably from two different vendors. Only round 1 has run, so the PR is not yet reviewed.

**DATA:** The patch contains no personal data, secrets or credentials. Reviewing it in this session is acceptable.

**REVIEWERS:** Round 1 is this instance (Claude Opus 5.5, `claude-opus-5-5`). It did not write the change and has no authoring context. The author is unknown: no commit trailers were supplied. Round 2 has not run.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `ratelimit.py:3`, `ratelimit.py:15-16`, `ratelimit.py:23-24` | **Missing config file removes all limits.** `LIMITS_PATH` is the relative path `"config/limits.yaml"`, so it is resolved against the process working directory. Any of these leaves the file unfound: the service starts from another directory, the file is not shipped in the deploy artifact, or commit 91c4e7a is not in the head's history. In each case `FileNotFoundError` is swallowed and `{}` is returned. Then `allowed()` returns `True` for every plan. Every plan becomes unlimited against the shared backend, with no error or log line. | `load_limits("/nonexistent/limits.yaml")` must raise (or the service must refuse to start). `allowed("free", 10**9, load_limits(missing))` must not return `True`. Both fail today. |
| 2 | P1 | `ratelimit.py:22-24` | **Unknown plan becomes unlimited.** In base, `limits[plan]` raised `KeyError` for an unconfigured plan. Now `limits.get(plan)` returning `None` gives `True`. Examples: a typo in the YAML (`Free: 100`), a quoted key (see #3), or a new plan added in code but not in the config. That plan then gets unlimited requests, silently. The request was only to move the limits, so this change in semantics is beyond what was asked. | `allowed("enterprise", 10**9, {"free": 100})` must not return `True` (raise, or apply a default deny). Fails today. |
| 3 | P1 | `ratelimit.py:12-14` | **Valid YAML is misparsed.** The file is named `.yaml` but read with a `split(":")` / `int()` line parser. Some valid YAML crashes it: `free: 100  # daily` raises `ValueError` from `int(" 100  # daily\n")`, and a nested `limits:` header gives `int("")`, which raises at load. Other valid YAML is read silently wrong: `"pro": 1000` is stored under the key `'"pro"'`, so `pro` hits finding #2 and becomes unlimited. Negative and zero values are accepted without any check. | Write a fixture YAML with an inline comment, a quoted key, and a nested map. Assert either that it parses to `{"free": 100, "pro": 1000}` or that a clear validation error is raised. Today the comment case crashes and the quoted-key case returns the wrong key. |
| 4 | P1 | `ratelimit.py:6` (new `load_limits`, no caller in the diff) | **The request is not delivered.** Nothing in the patch calls `load_limits`. `allowed()` still takes `limits` from its caller, which is where the current in-code limits live, and that caller is unchanged and not provided. An operator who edits `config/limits.yaml` would see no change in behavior. Nothing shows when the file is reread either, which matters because the request is "without a deploy". *Inferred: the caller files were not provided.* | An integration test that changes the config file and asserts that the request path enforces the new limit without a code change. That cannot pass while nothing calls `load_limits`. |

**Claims not verified:**
- "Tests pass" was not run.
- The only test exercises `allowed()` with an in-memory dict. Nothing tests `load_limits`, a missing file, an unknown plan, or real YAML, which are exactly the cases in findings 1–3.

**FILES NEEDED BUT NOT PROVIDED:**
- `config/limits.yaml` (the values, and whether it is shipped with the deploy)
- commit `91c4e7a`, and whether it is an ancestor of `e07b3d8`
- the caller(s) of `allowed()` and the current in-code limits dict
- how the deploy sets the working directory
- the CI check results

## Close-out

Not written here. The author adjudicates these findings and whoever closes the PR writes the close-out; a reviewer does not adjudicate its own findings. For the closer:
- Findings 1–4 are P0/P1, so each must be **Accepted** with a regression test or **Rejected** with evidence. None can be deferred.
- Round 2 is required before merge, preferably from another vendor approved for this code.

**MERGE RECOMMENDATION:** Do not merge. What is still open:
- **Round 2:** the High tier requires it and it has not run.
- **Blockers:** P0 #1 and P1 #2–#4 are unresolved.
- **Design decision:** whether missing or unknown limits should fail closed or deny by default.
- **Checks:** the CI results were not provided, so they cannot be confirmed green.
- **Config commit:** `91c4e7a` is not confirmed to be in the head.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "read in diff",
      "location": "ratelimit.py:3, ratelimit.py:15-16, ratelimit.py:23-24",
      "scenario": "Relative LIMITS_PATH not found (other cwd, file not shipped, or 91c4e7a not in head): FileNotFoundError swallowed, {} returned, allowed() returns True for every plan, so the shared backend is unprotected with no error.",
      "fix": "Fail closed: raise or refuse to start when the config is missing; resolve the path from config/env rather than cwd; log the loaded limits."
    },
    {
      "severity": "P1",
      "evidence_level": "read in diff",
      "location": "ratelimit.py:22-24",
      "scenario": "Plan absent from config (typo, quoted key, new plan) now gets unlimited requests; base raised KeyError. Semantic change beyond the request.",
      "fix": "Keep the failure (raise) or deny by default for unknown plans; validate at load that every known plan has a limit."
    },
    {
      "severity": "P1",
      "evidence_level": "read in diff",
      "location": "ratelimit.py:12-14",
      "scenario": "Hand-rolled parser on a .yaml file: inline comment or nested map raises ValueError at load; quoted key \"pro\" stored as '\"pro\"' and becomes unlimited; negative/zero values accepted.",
      "fix": "Parse with a YAML library (safe_load), validate the schema (plan names, positive ints), and test with realistic files."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred (caller not provided)",
      "location": "ratelimit.py:6",
      "scenario": "load_limits has no caller in the diff; allowed() still receives the caller's in-code limits, so editing config/limits.yaml changes nothing and no reload path exists for 'without a deploy'.",
      "fix": "Wire load_limits into the request path, remove the in-code limits, define the reload behavior, and add an integration test."
    }
  ]
}
```