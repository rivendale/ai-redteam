# PR #63 review report

**REVIEWED:** PR #63 "limits from config", head `e07b3d8`, merge base `5a1c2f6`. I had only `PR.md`, `change.patch` and `base/`, so this is a read of the patch against the base file. I did not use a frozen checkout and ran nothing.

**TIER:** High. These limits protect a shared production backend, so a change in how they fail is an availability and abuse-control change, and the new code is a loader reading operator-edited input. The tier calls for two rounds on two vendors. **Only round 1 has run**, and I had no tools. Round 2 and approval of the endpoints (Step 3) are outstanding, so by Step 2 this PR is not yet reviewed.

**REVIEWERS:** This is a fresh instance (Claude Sonnet 5.5) with no memory of writing the change. The author is unknown because no commit trailers were provided.

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `ratelimit.py:15-17`, `:22-24` | The path `config/limits.yaml` is relative to the working directory. If the service starts from another cwd, or the file is renamed, moved or not deployed, `FileNotFoundError` is swallowed and `load_limits()` returns `{}`. `allowed()` then returns True for every plan, so all limits are silently off and the shared backend is unprotected. Before the PR a missing limit raised `KeyError`, which failed closed. | `load_limits("/nonexistent")` must raise, or startup must fail. Add a test that a missing file does not produce an allow-all configuration. |
| 2 | P1 | `ratelimit.py:22-24` | Any plan without a limit is unlimited. A typo in a YAML key (`pro ` vs `prо`), a newly created plan, or a plan renamed in one place only gets no limit, with no error or log. This is unrequested behavior and fails open. | `allowed("enterprise", 10**9, {"free": 100})` must raise or deny. |
| 3 | P1 | `ratelimit.py:6-17` | The hand-rolled parser reads files named `.yaml` but is not YAML. A header such as `limits:` gives `int("")` and a `ValueError`. An inline comment (`free: 100  # daily`) or quoted value (`"100"`) gives a `ValueError`. Nested keys are flattened into the same namespace. A duplicate key silently takes the last value. Negative or zero values are accepted unchecked. A parse error at startup is at least loud, but a flattened or overridden key is silent. | Tests for `limits:` header, inline comment, duplicate key, nested map and `free: -1`. Prefer `yaml.safe_load` plus schema validation (plan names, int > 0). |
| 4 | P1 | `ratelimit.py:6` (no caller in the diff) | Nothing in the patch calls `load_limits`, and `allowed()` still takes `limits` as an argument. There is no reload path. If limits are loaded once at startup, editing the file needs a restart or redeploy, so the request ("change without a deploy") is not shown to be met. Callers are not in the provided files. | An integration test that edits the file and observes the new limit within the stated reload window, or documents that a restart is required. |
| 5 | P2 | `tests/test_ratelimit.py:6-9` | The only test passes a dict directly to `allowed()`. It does not exercise `load_limits`, the missing-file path, the unknown-plan path or malformed input, which are the changed behaviors. "Tests pass" says nothing about them, and I did not run it. | See the tests listed for #1-#3. |
| 6 | P2 | `PR.md` (cites `91c4e7a`, `config/limits.yaml`) | The config file and its values are not in the provided PR diff. They are claimed to come from commit `91c4e7a`, which I could not open (**UNVERIFIED**). I cannot confirm the file exists at head `e07b3d8`, that its format matches the parser, or that its values equal the previous in-code limits. The base does not contain those limits either, since callers supply them. | A test that loads the committed `config/limits.yaml` and asserts the expected per-plan values and key set. |
| 7 | P3 | whole feature | There is no validation or guard on who can edit the file or what values it may hold. A wrong operator edit, such as a huge number or a typo, takes effect unchecked and can disable protection for the shared backend. | Bounds checks on values, and a documented review or change process for the file. |

The PR text contains no instructions addressed to the reviewer. No consent or user-facing wording is changed, and no dated records are edited.

**FILES NEEDED BUT NOT PROVIDED:**
- `config/limits.yaml`
- commit `91c4e7a`
- the callers of `allowed` and `load_limits`, including how and when limits are loaded
- the original in-code limit values
- CI check results
- commit trailers

## Close-out

**ADJUDICATION:** Pending. The author must adjudicate every finding, and a reviewer does not adjudicate its own findings. No finding has a decision, fix commit or regression test yet.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1-7 | not yet decided | none |

**VERIFIED AFTER FIXES:** Nothing yet. The head has not moved since this review.

**MERGE RECOMMENDATION: do not merge.** Step 8 requires that "every round the tier requires has run, and every finding has a written decision". Neither holds: round 2 has not run and the P0 and P1 findings are open. A P0 or P1 cannot be deferred. Expected checks are also unseen, and a missing check is not green.

To get to merge:
1. Make a missing file or unknown plan fail closed (#1, #2).
2. Replace the parser with real YAML parsing and validation (#3).
3. Show the loading and reload path (#4).
4. Add the tests for the changed behavior (#5).
5. Include `config/limits.yaml` in the reviewed range (#6).
6. Run the second High-tier round on an approved endpoint.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code-read",
      "location": "ratelimit.py:15-17,22-24",
      "scenario": "Missing or unfound config/limits.yaml (relative path, wrong cwd, not deployed) is swallowed, returning {}; allowed() then returns True for every plan, disabling all limits on the shared backend. Previously KeyError failed closed.",
      "fix": "Fail closed: raise on missing or empty config at load or startup; resolve the path absolutely; test that missing file does not yield allow-all."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read",
      "location": "ratelimit.py:22-24",
      "scenario": "Plan absent from limits (typo, new plan, rename) is unlimited without error or log.",
      "fix": "Raise or deny on unknown plan; validate plan names against the known set at load."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read",
      "location": "ratelimit.py:6-17",
      "scenario": "Ad-hoc line parser is not YAML: 'limits:' header, inline comments or quoted values raise ValueError; nested keys flatten; duplicate keys silently override; zero or negative values accepted.",
      "fix": "Use yaml.safe_load with schema validation (known plans, integer > 0); add malformed-input tests."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read",
      "location": "ratelimit.py:6 (no caller in diff)",
      "scenario": "load_limits is never called in the patch and there is no reload path; the 'no deploy' requirement is not shown to be met if limits load once at startup.",
      "fix": "Show the caller and reload mechanism, or document that a restart is required; add an integration test of changing the file."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "tests/test_ratelimit.py:6-9",
      "scenario": "Test bypasses load_limits and covers none of the changed behavior (missing file, unknown plan, malformed input). 'Tests pass' was not run or verified.",
      "fix": "Add tests for load_limits and the fail-closed paths."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified",
      "location": "PR.md (config/limits.yaml, commit 91c4e7a)",
      "scenario": "Config file and commit not provided; cannot confirm presence at head, format compatibility, or that values match previous in-code limits.",
      "fix": "Include the file in the reviewed range and add a test asserting the loaded values."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read",
      "location": "ratelimit.py:6-17",
      "scenario": "No bounds on values or documented change process for an operator-editable file protecting a shared backend.",
      "fix": "Add value bounds and a documented change process for the file."
    }
  ]
}
```