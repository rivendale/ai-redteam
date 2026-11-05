# PR #63 Review Report: limits from config

**REVIEWED:** PR #63, head `e07b3d8`, merge base `5a1c2f6`. Both SHAs are taken from PR.md. I could not check them against a repository, and I did not review commit `91c4e7a`.

**TIER:** High. The limits protect a shared production backend, so they are an access and availability control. A change to how they load or fail is a security-relevant change. The tier calls for two rounds, ideally on two vendors. This is round one. **Round two has not run, so under Step 2 this PR is not reviewed.**

**REVIEWERS:** Sonnet 5.5, a fresh instance with no part in writing the change. The author is unknown because no commit trailers were supplied. I ran no code and sent nothing outside this session. Whether a second approved endpoint exists is not stated.

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `ratelimit.py` `load_limits` (`except FileNotFoundError: pass`) and `allowed` (`if limit is None: return True`) | The limit file is missing, misnamed, or not shipped in the image. `load_limits` returns `{}`, and `allowed` then returns True for every plan with no log or error. The old code raised `KeyError` and failed closed. Now all traffic is unlimited against the shared backend. | `allowed("free", 10**9, load_limits("/nonexistent"))` must not return True. Missing config should raise or refuse to start. |
| 2 | P1 | `ratelimit.py` `allowed` (`limits.get(plan)` returns None → True) | An unknown, new, or misspelled plan name (`"enterprise"`, `"Pro"`) is silently unlimited. Before, it was a loud `KeyError`. | `allowed("unknown", 5, {"free": 100})` must deny or raise. |
| 3 | P1 | `ratelimit.py` `load_limits` (`plan.strip()`) | Valid YAML such as `"free": 100` or `'pro': 1000` produces the keys `'"free"'` and `"'pro'"`. These never match `"free"` or `"pro"`, so by #2 those plans become unlimited. Nothing warns. | Load a file containing `"free": 100` and assert `limits["free"] == 100`, or that loading fails. |
| 4 | P2 | `ratelimit.py` `load_limits` (hand-rolled parser) | The parser is not YAML, though the file is named `.yaml`. `free: 100  # trial` raises an uncaught `ValueError` from `int()`. Nested keys, a bare `free:`, and indented children also crash or mis-parse. Duplicate keys silently take the last value. Negative or zero values are accepted without validation. A bad edit by operations is the exact scenario this change enables. | Table test for inline comment, blank value, duplicate key, negative, and non-numeric. Each should give a clear error naming the line, or defined behavior. |
| 5 | P1 | `ratelimit.py` (whole patch), UNVERIFIED | Nothing in the patch calls `load_limits`. `allowed` still takes `limits` from its caller, and the callers were not provided. If limits are loaded once at startup, changing the file needs a restart or redeploy. That contradicts "without a deploy". The relative `LIMITS_PATH` also depends on the process working directory, which feeds #1. | An integration test that edits the file at runtime and checks the new limit applies without a restart. Another that starts the process from a different cwd. |
| 6 | P2 | `tests/test_ratelimit.py` | The only test passes a dict directly to `allowed`, which the old code already did. `load_limits`, the missing-file path, the unknown-plan path, and malformed input are untested. "Tests pass" is a claim and I have not seen a run. | The tests listed in #1–#4. Each must fail on the current head. |
| 7 | P1 | PR.md claims, UNVERIFIED | The PR cites `config/limits.yaml` and commit `91c4e7a`, and I could not open either. I can't confirm the shipped values match the limits previously in code. The base `ratelimit.py` holds none, so the old values are in callers I wasn't given. I also can't confirm that `91c4e7a` is an ancestor of `e07b3d8`. A wrong value, such as a typo adding a zero, would go straight to production. | Diff the old in-code values against the YAML values, and assert in a test that every known plan has an entry. |

PR.md and the diff contain no text aimed at the reviewer.

**FILES NEEDED BUT NOT PROVIDED:**
- `config/limits.yaml`
- Commit `91c4e7a`
- Callers of `allowed` and any startup or reload code
- The previous in-code limit values
- CI results for `e07b3d8`
- Commit trailers

## Close-out

Not yet written. The author must adjudicate, and the reviewer does not adjudicate its own findings.

**MERGE RECOMMENDATION: do not merge.**
- #1 is a P0 and cannot be deferred.
- #2, #3, #5 and #7 are P1 and also cannot be deferred.
- The required second High-tier round has not run.
- The limits file and its values are unseen, and CI status is unknown.
- No written rule was provided that overrides these gates.

After fixes, verify them with a targeted read of the correction diff and its tests, not another full round.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "read-from-diff",
      "location": "ratelimit.py load_limits / allowed",
      "scenario": "Missing config file yields an empty dict and allowed() returns True for every plan, so all rate limits silently disappear on a shared production backend (previously a KeyError).",
      "fix": "Fail closed: raise or refuse to start when the file is missing or empty; add a test that a missing file does not allow unlimited requests."
    },
    {
      "severity": "P1",
      "evidence_level": "read-from-diff",
      "location": "ratelimit.py allowed (limits.get(plan) is None -> True)",
      "scenario": "Unknown or misspelled plan names are unlimited instead of erroring.",
      "fix": "Deny or raise for plans with no configured limit; test an unknown plan."
    },
    {
      "severity": "P1",
      "evidence_level": "read-from-diff",
      "location": "ratelimit.py load_limits (plan.strip())",
      "scenario": "Quoted YAML keys like \"free\": 100 become '\"free\"' and never match, so by the unknown-plan path that plan is unlimited.",
      "fix": "Use a real YAML parser (yaml.safe_load) with schema validation, or strip quotes and reject unknown shapes."
    },
    {
      "severity": "P2",
      "evidence_level": "read-from-diff",
      "location": "ratelimit.py load_limits",
      "scenario": "Hand-rolled parser crashes with ValueError on inline comments or blank values, and accepts duplicate, negative or zero values without validation.",
      "fix": "Parse with safe_load, validate positive ints, error on duplicates, and add table tests for malformed input."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "ratelimit.py (no call site; LIMITS_PATH relative)",
      "scenario": "load_limits is not wired in by this patch, so runtime change without a deploy is not shown; if loaded once at startup a restart is needed, and the relative path depends on the working directory.",
      "fix": "Show the call site, define a reload mechanism, resolve the path absolutely or from an environment variable, and test runtime change and a different cwd."
    },
    {
      "severity": "P2",
      "evidence_level": "read-from-diff",
      "location": "tests/test_ratelimit.py",
      "scenario": "Only the pre-existing allowed() behavior is tested; loader, missing-file, unknown-plan and malformed paths have no coverage, and 'Tests pass' is unverified.",
      "fix": "Add tests for each path above that fail on the current head."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "PR.md (config/limits.yaml, commit 91c4e7a)",
      "scenario": "The config file, its values and the cited commit were not provided; values may differ from the previous in-code limits, which would go directly to production.",
      "fix": "Provide the file and commit, diff old values against new, and add a test that every known plan has an entry."
    }
  ]
}
```