# pr-review report: PR #63 "limits from config"

**REVIEWED:** PR #63, head `e07b3d8`, merge base `5a1c2f6`. I read `change.patch`, `PR.md` and `base/` only. I could not run anything and have no other access in this session.

**TIER:** High, for two reasons.
- Per-plan limits are an access control on a shared production backend.
- The change alters what happens when the limits are absent, and I take the higher tier when unsure.

Only one round has run here, so under Step 2 the review is **not complete**. A second round, ideally on a different vendor, is still required. I also could not confirm that this endpoint is approved for the data the code can carry (Step 3).

**REVIEWERS:** this report comes from a single fresh instance (Sonnet 5.5) with no memory of the change. The author is unknown because no commit trailers were provided. I did not check whether this session wrote the change.

**Instruction content:** `PR.md`, the patch and the README contain no text addressed to reviewers. No instruction-file changes appear in the patch.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `ratelimit.py:15-17` (`except FileNotFoundError: pass`), `:22-24` | The path is relative (`"config/limits.yaml"`), so it resolves against the process's working directory. If the service starts from another directory, or the file is renamed, moved or not shipped in the image, `load_limits()` returns `{}`. `allowed()` then returns `True` for every plan, with no error or log. Every limit on the shared backend is silently off. Before this change a missing limit raised and nothing was served unmetered. | `load_limits("/nonexistent")` must raise, or the service must refuse to start. Also assert that `allowed("free", 10**9, {})` is not `True`. |
| 2 | P1 | `ratelimit.py:22-24` | A plan absent from the config (a new plan, a typo such as `Pro` vs `pro`, or a dropped line) gets unlimited access. The old code raised `KeyError`. This was not requested ("all of it, and nothing extra") and is a behavior change from fail-closed to fail-open. | `allowed("enterprise", 10**6, {"free": 100})` must raise or deny. |
| 3 | P1 | `ratelimit.py:6-17`, and the whole patch | `load_limits` is never called in the patch. The callers that build `limits` are not shown, so I cannot tell whether the config is used at all. If it is read once at startup, an operations edit still needs a restart or deploy, which defeats the stated goal. No reload or refresh path exists. | Integration test: write the file, load, edit the file, trigger the intended refresh, and assert the new limit applies. |
| 4 | P2 | `ratelimit.py:12-14` | The hand-rolled parser is not YAML. A YAML-looking file breaks it in several ways: <br>• `free: 100  # trial` raises `ValueError`. <br>• A section header such as `limits:` raises `ValueError` on `int("")`. <br>• Indented nested keys and quoted names (`"free": 100`) produce wrong keys. <br>• Duplicate keys silently take the last value. <br>• Negative values are accepted. <br>The `ValueError` is raised at load time, so a bad edit by operations can take the service down. | Table test over those inputs. Each must either parse correctly or be rejected with a clear error. Better still, use `yaml.safe_load` plus schema validation. |
| 5 | P2 | `tests/test_ratelimit.py:1-13` | The only test passes a hand-built dict to `allowed()`. Nothing covers `load_limits`, the missing-file path, unknown plans or malformed input. "Tests pass" says nothing about the changed behavior. | The tests listed under #1, #2 and #4. |
| 6 | P1 (UNVERIFIED) | `PR.md:3` | The PR cites `config/limits.yaml` and commit `91c4e7a`. Neither was provided, and the patch does not add the file. I cannot verify that the file exists at head `e07b3d8`, that its values match the old in-code limits, or that it ships with the deploy artifact. If the file is not in the PR's history, merging gives finding #1 on day one. | CI check that `config/limits.yaml` loads and that every plan the product defines has a limit. |

## FILES NEEDED BUT NOT PROVIDED
- `config/limits.yaml`
- Commit `91c4e7a`, and confirmation that it is an ancestor of `e07b3d8`
- The callers of `allowed` and the code that builds `limits`
- The previous in-code limit values
- The list of plans the product defines
- Status of the CI checks
- Commit trailers (authorship)
- The second-round review required for High tier

## Close-out
Not written. The author must adjudicate the findings, and a reviewer does not adjudicate its own findings.

**MERGE RECOMMENDATION (preliminary): do not merge.**
- Finding #1 is a P0 and cannot be deferred.
- The High-tier second round has not run.
- The config file and the cited commit are unverified.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by reading the patch",
      "location": "ratelimit.py:15-17, 22-24",
      "scenario": "Missing or unreachable config/limits.yaml (relative path, wrong cwd, not shipped) yields {} and allowed() returns True for all plans, silently disabling every limit on the shared backend.",
      "fix": "Fail closed: raise or refuse to start when the file is missing or empty; resolve the path explicitly; test that an empty or missing config never allows."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by reading the patch",
      "location": "ratelimit.py:22-24",
      "scenario": "A plan not in the config (new plan, typo, case mismatch) is treated as unlimited; the old code raised KeyError. This is an unrequested fail-open change.",
      "fix": "Raise or deny for unknown plans, or require a configured default limit; add a test."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred, callers not provided",
      "location": "ratelimit.py:6-17",
      "scenario": "load_limits is never called in the patch and no reload mechanism exists, so config edits may still need a restart or deploy, missing the request's goal.",
      "fix": "Show the call site and a refresh path; integration test that an edited file changes behavior without a deploy."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading the patch",
      "location": "ratelimit.py:12-14",
      "scenario": "Hand-rolled parser fails on inline comments, section headers, quoted keys and nested keys (ValueError at load), silently takes duplicate keys, and accepts negative values.",
      "fix": "Use yaml.safe_load with schema validation; add table tests for malformed input."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed by reading the patch",
      "location": "tests/test_ratelimit.py:1-13",
      "scenario": "The only test exercises allowed() with a hand-built dict; load_limits, the missing-file path and unknown plans are untested, so 'tests pass' does not cover the change.",
      "fix": "Add tests for load_limits, the missing file, unknown plans and malformed lines."
    },
    {
      "severity": "P1",
      "evidence_level": "UNVERIFIED, files not provided",
      "location": "PR.md:3",
      "scenario": "config/limits.yaml and commit 91c4e7a were not provided; whether the file exists at head, matches the old limits and ships with the deploy cannot be verified. If absent, merging disables all limits.",
      "fix": "Provide the file and commit; add a CI check that the config loads and covers every defined plan."
    }
  ]
}
```