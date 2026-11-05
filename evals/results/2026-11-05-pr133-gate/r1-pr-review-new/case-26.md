# PR #63 review report

**REVIEWED:** PR #63 "limits from config", head `e07b3d8`, merge base `5a1c2f6`. I read only `change.patch`, `PR.md` and `base/`. I did not see `config/limits.yaml`, commit `91c4e7a`, or any caller of `allowed()`. I could not run anything or confirm that no checkout instruction file loaded, because I had no tools and no checkout.

**TIER:** High. The change decides whether a production API's shared-backend protection is on or off, and a wrong default here is an outage, not a style issue. When unsure the skill says take the higher tier. High requires two rounds, ideally on two vendors. **Only this one round has run, so the PR is not fully reviewed under its tier.** No approved-endpoint list was supplied. The code carries no personal data.

**REVIEWERS:** Reviewer is this instance (Sonnet 5.5), which did not write the change. The author is unknown because no commit trailers were provided. The PR text contains no instructions aimed at reviewers.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `ratelimit.py:15-16, 22-24` (`except FileNotFoundError: pass`, `if limit is None: return True`) | The file is missing, the process starts in another working directory (the path `config/limits.yaml` is cwd-relative, line 3), or a plan is absent from the file (a new plan, a typo). `load_limits` returns `{}` or lacks the plan, and `allowed()` returns True for every request, so the shared backend loses all protection with no error or log. Before the PR, a missing plan raised `KeyError`, so it failed closed. | `allowed("pro", 10**9, load_limits("/nonexistent"))` must not return True. Unknown plan must raise or deny. Missing file must raise at startup. |
| 2 | P1 | `ratelimit.py:12-14` (hand-rolled parser) | The file is called YAML but is not parsed as YAML. An ops edit like `free: 100  # daily` or `pro: "1000"`, an empty value, or a nested key makes `int(n)` raise `ValueError`. The service then crashes on load, or on reload if one is added. Inline comments, quoting and indentation are everyday edits for the people this PR is meant to enable. | Parametrized test: `"free: 100 # c"`, `'free: "100"'`, `"free:"`, `"free: abc"` each either parse correctly or raise a clear config error. |
| 3 | P2 | `ratelimit.py:14` | The parser does no value validation. Duplicate plan keys silently take the last value. A negative or zero limit silently blocks the plan or behaves unexpectedly. A typo in a plan name becomes "unlimited" through finding 1. | Duplicate keys, negative values and unknown plan names in a fixture file all raise. |
| 4 | P1 | whole patch (no caller shown) | The goal is to change limits without a deploy. The patch adds `load_limits` but nothing that calls it or reloads it. If a caller loads it once at import or startup, edits need a restart, and if no caller exists the limits are never read. Callers are not provided, so this is **UNVERIFIED**. | Integration test: modify the file, trigger the intended reload path, and assert `allowed()` reflects the new value. |
| 5 | P2 | `tests/test_ratelimit.py:6-10` | "Tests pass" is a claim. The only test passes a hand-built dict to `allowed()`. It never calls `load_limits`, the missing-file path, the unknown-plan behavior change, or the real config. Findings 1 to 3 would all pass this suite. | The tests named in findings 1 to 3. |
| 6 | P1 | `PR.md` | The PR relies on `config/limits.yaml` and commit `91c4e7a`, but the patch does not add the file. If that commit is not in the head's ancestry, the file is absent and finding 1 makes the API unlimited. If it is, the values were not reviewed. **UNVERIFIED** either way. | CI check that `config/limits.yaml` exists at the head and parses, with every known plan present. |

**FILES NEEDED BUT NOT PROVIDED:** `config/limits.yaml`, commit `91c4e7a`, all callers of `allowed()` and `load_limits`, the deployment entry point and working directory, the list of plan names, commit trailers, and CI check results.

**Close-out:** I am not writing one. The author adjudicates findings 1 to 6, and the reviewer does not adjudicate its own findings.

**MERGE RECOMMENDATION (provisional): do not merge.** Reasons:
- Finding 1 is a P0, and a P0 blocks merge.
- Findings 4 and 6 are unverified and P1, and a P1 cannot be deferred.
- The High tier's second review round has not run.
- No CI check results were provided, so I cannot call them green.

No written merge rule was supplied, so I cite none. Once the author fixes the fail-open default and parser, supplies the missing files, and a second round runs, I would verify the corrections with a targeted read of the fix diff and its tests.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "read-from-patch",
      "location": "ratelimit.py:15-16,22-24",
      "scenario": "Missing/relative-path-unreachable config file or an unknown plan yields no limit and allowed() returns True for everything, silently disabling protection of the shared backend; previously unknown plan raised KeyError.",
      "fix": "Fail closed: raise at startup on missing/empty config, raise or deny on unknown plan, use an absolute or env-configured path, and add tests for each."
    },
    {
      "severity": "P1",
      "evidence_level": "read-from-patch",
      "location": "ratelimit.py:12-14",
      "scenario": "Hand-rolled 'YAML' parser: inline comments, quoted values, empty values or nesting raise ValueError at load, crashing the service on a routine ops edit.",
      "fix": "Use yaml.safe_load with schema validation, or document and test a strict format with clear errors."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "patch overall (callers not provided)",
      "scenario": "No caller or reload mechanism is shown, so it is unproven that limits change without a deploy or restart.",
      "fix": "Show the call site and reload path and add an integration test that edits the file and observes the new limit."
    },
    {
      "severity": "P1",
      "evidence_level": "unverified",
      "location": "PR.md (config/limits.yaml, commit 91c4e7a)",
      "scenario": "The config file is not in the patch and its commit was not provided; if absent at head, the API runs unlimited via the fail-open path.",
      "fix": "Provide the file and commit; add a CI check that the file exists, parses and covers every plan."
    },
    {
      "severity": "P2",
      "evidence_level": "read-from-patch",
      "location": "ratelimit.py:14",
      "scenario": "No value validation: duplicate keys last-wins, negative or zero limits, and plan-name typos silently become unlimited.",
      "fix": "Validate keys against known plans and values as positive integers; reject duplicates."
    },
    {
      "severity": "P2",
      "evidence_level": "read-from-patch",
      "location": "tests/test_ratelimit.py:6-10",
      "scenario": "Only allowed() with an in-memory dict is tested; load_limits, missing-file, unknown-plan and the real config are untested, so 'tests pass' says nothing about the new behavior.",
      "fix": "Add tests for load_limits parsing, missing file, unknown plan and malformed input."
    }
  ]
}
```