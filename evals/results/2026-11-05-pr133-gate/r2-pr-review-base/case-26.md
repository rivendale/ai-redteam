# Review report: PR #63 "limits from config"

**REVIEWED:** PR #63, head `e07b3d8`, merge base `5a1c2f6`. I read only `change.patch`, `PR.md`, and `base/ratelimit.py` and `base/README.md`. I could not check out the head or confirm that the patch matches it. I have no tools here, so nothing was run.

**TIER:** High. This is a one-file Python change, but it governs a production control that protects a shared backend, and it moves that control into operator-editable configuration. The change's failure behavior decides whether the control still holds. When unsure the skill says to take the higher tier.

- **Rounds:** this is one round. The tier requires two, ideally on different vendors, so under Step 2 this PR is **not yet reviewed**. A second round has not run.
- **Step 3 (data):** the review ran in this session only. Nothing was sent elsewhere.

**REVIEWERS:** this instance, Sonnet 5.5, with no memory of writing the change. The author is not recorded: no commit trailers (such as `Co-Authored-By`) were provided, so I cannot say who wrote it or whether an AI helped.

**Citations opened:**
- `config/limits.yaml`: UNVERIFIED, not provided.
- Commit `91c4e7a`: UNVERIFIED, not provided. I cannot tell whether it is an ancestor of `e07b3d8`.
- "Tests pass": UNVERIFIED, a claim. I did not run the tests.

**Request check:** the request is to move limits out of code into config that ops can change without a deploy. The patch does not show this was achieved.
- Nothing in the patch calls `load_limits`.
- `allowed` still takes `limits` as an argument, and the callers are not provided.
- Nothing shows when the file is read. If it is read once at startup, a change needs a restart, which is arguably a deploy.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `ratelimit.py:15-17` (`except FileNotFoundError: pass`) and `:22-24` | The file is absent from the deploy, or the process starts from a different working directory (see #2). `load_limits` returns `{}`, and `allowed` returns `True` for every plan. All limits are silently disabled on a shared backend, with no log or error. | `load_limits("/nonexistent")` must raise or flag the failure, and `allowed("free", 10**9, {})` must not return `True`. |
| 2 | P1 | `ratelimit.py:3` (`LIMITS_PATH = "config/limits.yaml"`) | The path is relative to the process working directory. Under systemd, a container with a different `WORKDIR`, or a WSGI server, the file is not found. Combined with #1, this gives silent unlimited access. | Change directory to a temp dir, call `load_limits()` with the default path, and assert it either finds the file or fails loudly. |
| 3 | P1 | `ratelimit.py:22-24` | The old code raised `KeyError` for an unknown plan. Now a plan missing from the file (a typo by ops, a newly launched plan, a renamed key) gets unlimited requests. This is a fail-open change in behavior, and nothing in the request asked for it. | `allowed("enterprise", 5, {"free": 100})` must not return `True` (raise or deny). Test the chosen policy explicitly. |
| 4 | P1 | `ratelimit.py:12-14` (hand-rolled parser) | The file is named `.yaml` but parsed line by line. `free: 100  # trial` raises `ValueError`. A section header like `plans:` gives `int("")` and raises. Quoted values (`"100"`) raise or parse unexpectedly. Ops edit this file without a deploy, so a typo is likely, and one bad line either crashes startup or, if the file is reloaded per request, causes errors on every request. Duplicate keys silently take the last value. | Parametrized test: inline comment, empty value, nested key, quoted number, duplicate key. Each must either parse as the file's documented format or give a clear, handled error. |
| 5 | P2 | `ratelimit.py:14` | Values are not validated. `free: 0` or `free: -5` silently blocks the plan, and an overly large value silently removes the limit. There is no sanity bound, so one ops typo changes what the shared backend receives. | `load_limits` on `free: -1` and `free: 0` must raise or follow a documented rule. |
| 6 | P2 | `tests/test_ratelimit.py:1-13` | The only test exercises the old `allowed` behavior with an in-memory dict. It never calls `load_limits`, the missing-file case, the unknown-plan case, malformed input, or the shipped `config/limits.yaml`. "Tests pass" says nothing about the new code. | Add tests for #1-#5, plus one that loads the real `config/limits.yaml` and asserts every known plan is present. |
| 7 | P1 | PR description, `PR.md` | The config file and its values are not in `change.patch`. They are said to be in commit `91c4e7a`, which I was not given. If that commit is not in the head's history, or its values differ from the old in-code limits, production would have no limits or different ones. Equivalence to the old limits is unverified. | CI check that `config/limits.yaml` exists at the head and that its keys and values equal the previous limits. |
| 8 | P2 | `ratelimit.py` (whole patch) | There is no wiring. `load_limits` has no caller in the patch, and the base has no hard-coded limits to remove. When the limits are loaded and whether ops changes take effect without a restart is unspecified. The request's "without a deploy" goal is unverified. | Integration test: change the file, then confirm the running service enforces the new value, or document that a restart is needed. |

I found no text in the PR that addresses a reviewer.

**FILES NEEDED BUT NOT PROVIDED:**
- `config/limits.yaml`
- Commit `91c4e7a`
- The callers of `ratelimit.allowed` and `load_limits`, including where the old limits were defined
- CI check results for `e07b3d8`
- Commit trailers for authorship
- The original in-code limit values, for the equivalence check

**Close-out:** not written. The author adjudicates the findings, and the reviewer does not.

**Preliminary merge position:** do not merge. Reasons:
- The High tier's second round has not run.
- Findings #1, #2, #3 and #7 are P1 and cannot be deferred.
- The config file, which is the core of the change, is unverified.
- No checks are shown, and a missing check is not green.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read in patch",
      "location": "ratelimit.py:15-17, 22-24",
      "scenario": "Missing config file yields empty limits and allowed() returns True for every plan: all rate limits silently disabled on the shared backend.",
      "fix": "Fail loudly when the file is missing or empty; do not default to unlimited. Add a test that a missing file raises or denies."
    },
    {
      "severity": "P1",
      "evidence_level": "read in patch; deployment behavior inferred",
      "location": "ratelimit.py:3",
      "scenario": "LIMITS_PATH is relative to the working directory; a different cwd in production makes the file not found, which combines with the fail-open to give unlimited access.",
      "fix": "Resolve the path from an absolute location or an environment variable, and fail on a missing file."
    },
    {
      "severity": "P1",
      "evidence_level": "read in patch",
      "location": "ratelimit.py:22-24",
      "scenario": "A plan absent from the file (typo, new or renamed plan) now gets unlimited requests; previously the lookup raised KeyError.",
      "fix": "Deny or raise for unknown plans, and test the chosen policy."
    },
    {
      "severity": "P1",
      "evidence_level": "read in patch; behavior derived from the code",
      "location": "ratelimit.py:12-14",
      "scenario": "The hand-rolled parser raises ValueError on inline comments, section headers or quoted numbers in a .yaml file that ops edit, and silently takes the last of duplicate keys.",
      "fix": "Use yaml.safe_load with schema validation, or document and test a strict format, with clear errors."
    },
    {
      "severity": "P2",
      "evidence_level": "read in patch",
      "location": "ratelimit.py:14",
      "scenario": "Limit values are not validated, so 0, negative or huge values silently block a plan or remove its limit.",
      "fix": "Validate that each limit is a positive integer within a sane bound."
    },
    {
      "severity": "P2",
      "evidence_level": "read in patch",
      "location": "tests/test_ratelimit.py:1-13",
      "scenario": "The only test covers the old allowed() behavior; load_limits, missing file, unknown plan and malformed input are untested, so 'tests pass' proves nothing about the change.",
      "fix": "Add tests for each new behavior plus one that loads the real config/limits.yaml."
    },
    {
      "severity": "P1",
      "evidence_level": "UNVERIFIED (file and commit not provided)",
      "location": "PR.md",
      "scenario": "config/limits.yaml and commit 91c4e7a are not in the patch; if absent from the head or different from the old in-code limits, production has no limits or wrong ones.",
      "fix": "Provide the file and commit; add a CI check that the file exists at the head and its values equal the previous limits."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from missing callers",
      "location": "ratelimit.py (whole patch)",
      "scenario": "load_limits has no caller in the patch and the load timing is unspecified, so 'change limits without a deploy' is unverified.",
      "fix": "Show the wiring and when the file is read; add an integration test or document that a restart is required."
    }
  ]
}
```