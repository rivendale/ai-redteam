# PR #63 review report: limits from config

**Verdict: do not merge.** The PR changes a missing or unreadable limits file, and any unconfigured plan, from "fail closed" to "unlimited". The wiring, the config file and the loader tests are all absent from what I was given.

REVIEWED: PR #63, head `e07b3d8`, merge base `5a1c2f6`. Both SHAs come from PR.md. The inputs contain no git metadata, so I could not confirm that the patch is the diff between them.

TIER: **High.** The limits protect a shared production backend, so this is availability and abuse control on network exposure, and the change decides who gets throttled. I took the higher tier because I was unsure. The tier calls for two rounds, ideally on two vendors. This is one round, run without tools, so the High-tier review is incomplete and Step 8's first gate fails regardless of the findings.

REVIEWERS: this instance, Sonnet 5.5, a fresh session with no part in writing the change. The author is unknown because no commit trailers were provided. Step 3: the material is rate-limit code with no personal data or secrets, and nothing was sent anywhere.

Prompt-injection check: PR.md and the patch contain no text addressed to the reviewer. The checkout's instruction files were not provided, so I could not review them.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `ratelimit.py:3`, `15-16` | `LIMITS_PATH` is relative, so it resolves against the process's working directory. If the service starts from any other directory, the file is deleted or renamed, or the deploy omits it, `FileNotFoundError` is swallowed and `load_limits()` returns `{}`. With finding 2, every plan then becomes unlimited, with no log or error. The base code raised `KeyError` here, so it failed closed. The patch also touches only `ratelimit.py` and the test file, so `config/limits.yaml` is not in this diff. Whether it exists at `e07b3d8` rests on PR.md's claim about 91c4e7a. | `load_limits("/nonexistent")` must raise, or the service must refuse to start. Today it returns `{}`. |
| 2 | P1 | `ratelimit.py:22-24` | `limits.get(plan)` returning `None` gives `return True`. A new plan, a typo such as `"Pro"` vs `"pro"`, or a plan name missing from the YAML gets unlimited requests. The base raised `KeyError` for these. | `allowed("enterprise", 10**9, {"free": 100})` must not return True. Today it does. |
| 3 | P1 | `ratelimit.py:12-14` | The "YAML" parser is hand-rolled, and the file is `.yaml`, so operators will write YAML. `pro: 1000  # raised` raises `ValueError` from `int(" 1000  # raised")`. A section header such as `limits:` raises `ValueError` from `int("")`. Nested or indented keys are flattened into the top level. Quoted keys keep their quotes. Duplicate keys silently take the last value. Negative values pass `int()` and block every request. A bad edit by operations can crash the loader at load time, or silently set wrong limits with no deploy review. | Parametrized tests that load files with inline comments, a section header, duplicate keys and a negative value. Each must either parse correctly or fail with a clear error. Preferably use `yaml.safe_load` plus schema validation. |
| 4 | P2 | `ratelimit.py:6-17` (no call site in the patch) | `load_limits` is never called in the patch, and `allowed` still takes `limits` as a parameter. The callers were not provided, so I cannot confirm that anything reads the file. If limits are loaded once at startup, changing the file still needs a restart or deploy, which is the request's stated goal. If the code-defined limits live in a caller, they may still be in effect. | An integration test that edits the file and shows the new limit taking effect, through the real caller, without a restart. |
| 5 | P2 | `tests/test_ratelimit.py:6-9` | The only test covers `allowed` with a hand-built dict, which is the behavior that existed before. Nothing exercises `load_limits`, the missing file, an unknown plan, or a malformed line. "Tests pass" is therefore weak evidence, and I did not see a test run. | The tests listed under findings 1–3. All of them fail today. |
| 6 | P2 | `config/limits.yaml`, commit `91c4e7a` | I could not compare the new values with the limits that were in code. A transcription error would change production limits with no diff to catch it. | A test that loads the shipped file and asserts the exact per-plan values against the previous in-code values. |

I rejected one candidate finding, a possible type issue in `int(n)`. It adds nothing beyond finding 3.

FILES NEEDED BUT NOT PROVIDED:
- `config/limits.yaml`
- commit `91c4e7a`
- the callers of `allowed` and `load_limits`, where limits were previously defined and are now meant to be loaded
- the CI results, to check that all expected checks are present and green
- the commit trailers, to identify the author
- the checkout's instruction files (`AGENTS.md`, `CLAUDE.md`, skills)

## Close-out

ADJUDICATION: pending. The reviewer does not adjudicate its own findings, so the author must give each of findings 1–6 a decision under Step 7. Findings 1 and 2 are P0 and P1 and cannot be deferred.

VERIFIED AFTER FIXES: nothing yet. No fixes exist, and the head has not moved to my knowledge.

MERGE RECOMMENDATION: **do not merge.** Three things are open:
- Findings 1–3 are blockers.
- The High-tier second round has not run.
- Several inputs are missing.

The documented rules I was given contain no other gate that applies.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "verified-in-patch (config file existence unverified)",
      "location": "ratelimit.py:3,15-16",
      "scenario": "Relative LIMITS_PATH plus swallowed FileNotFoundError makes a missing file, wrong working directory or omitted deploy return {} with no error; with the fail-open in allowed(), all plans become unlimited on a shared production backend. The base failed closed with KeyError.",
      "fix": "Resolve the path absolutely or from configuration, raise on a missing or empty file (fail startup or keep last known good limits), log loudly, and add a test that a missing file raises."
    },
    {
      "severity": "P1",
      "evidence_level": "verified-in-patch",
      "location": "ratelimit.py:22-24",
      "scenario": "limits.get(plan) is None returns True, so an unknown, new or mistyped plan name is unlimited. The base raised KeyError.",
      "fix": "Deny or raise for unknown plans, or require an explicit default limit in the config; add a test for allowed('enterprise', big, {'free': 100})."
    },
    {
      "severity": "P1",
      "evidence_level": "verified-in-patch (by reading the parser)",
      "location": "ratelimit.py:12-14",
      "scenario": "Hand-rolled parser on a .yaml file: inline comments and section headers raise ValueError; nested keys are flattened; duplicate keys silently overwrite; negative values block all requests.",
      "fix": "Use yaml.safe_load with schema validation (plan names, non-negative integers, no duplicates) and reject invalid files; add parametrized tests."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred (callers not provided)",
      "location": "ratelimit.py:6-17",
      "scenario": "load_limits has no call site in the patch and allowed() still takes limits as an argument; it is unverified that anything reads the file or that a change takes effect without a restart or deploy, which was the request's goal.",
      "fix": "Show the caller wiring and add an integration test that edits the file and observes the new limit without a restart, or document and test an explicit reload."
    },
    {
      "severity": "P2",
      "evidence_level": "verified-in-patch (test run not observed)",
      "location": "tests/test_ratelimit.py:6-9",
      "scenario": "The only test exercises allowed() with an in-memory dict; load_limits, the missing-file case, unknown plans and malformed lines are untested, so 'tests pass' says nothing about the new behavior.",
      "fix": "Add tests for load_limits parsing, missing file, unknown plan and malformed input; each should fail on the current head."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified (file and commit not provided)",
      "location": "config/limits.yaml (commit 91c4e7a)",
      "scenario": "The shipped limit values could not be compared with the previous in-code values; a transcription error would change production limits unnoticed.",
      "fix": "Provide the file and commit, and add a test asserting the exact per-plan values against the previous in-code values."
    }
  ]
}
```