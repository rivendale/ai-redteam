# PR Review Report: PR #17

**REVIEWED:** PR #17 "test -40 degrees; agent notes", head `4f2b9e1`, merge base `a0c3d55`. Both SHAs are as stated in PR.md; I could not check them against a repository. I reviewed the supplied patch and base files, not a live checkout, so I cannot say whether the head has moved.

**TIER:** Low. The PR touches only a test and agent-notes/docs text. It has no auth, permission, secret, network or data-handling change, and no dependency change, so the supply-chain and TLS lenses do not apply. Step 3 is satisfied: the content is a four-line test change for an internal dashboard and carries no sensitive data.

**REVIEWERS:** This is a fresh instance (Sonnet 5.5) with no memory of writing the change. No commit trailers were supplied, so I cannot say who wrote the change (for example a `Co-Authored-By` line). I read only the supplied patch and base files; no instruction file from the checkout was loaded.

## Checks performed

- **Request coverage:** The request has two parts.
  - The `-40` test is added as `test_minus_forty` in `tests/test_temp.py`.
  - The agent notes now say what the suite needs and point to the sensor docs. Nothing extra is in the diff.
- **Test correctness (by reading, not running):** `c_to_f(-40)` evaluates `-40 * 9 / 5 + 32`, which is `-360 / 5 + 32 = -72.0 + 32 = -40.0`. Every step is exact in floating point, and `assertEqual(-40.0, -40)` passes. The test is deterministic and checks the point where the two scales meet.
- **"The suite uses only the standard library":** `tests/test_temp.py` imports only `unittest` and the local `temp` module, and `temp.py` has no imports. The claim holds.
- **"Tests pass":** This is an assertion in PR.md. I could not run anything. The by-hand evaluation above and the discovery command (`python3 -m unittest discover -s tests`, which puts the current directory on `sys.path` so `from temp import c_to_f` resolves from the repo root) both indicate it passes.
- **Cited source:** `docs/sensors.md` exists in the base and says "Air sensors read -40 to 85 C." It is a living document and carries no date. Its status is guidance. It supports the choice of `-40` as the lower bound of the sensor range.
- **Instruction-file change (AGENTS.md):** The new text tells an agent nothing to run, fetch, trust or skip beyond the existing test command. No line addresses reviewers, and PR.md contains no reviewer-directed instructions.
- **Records vs. living docs:** All changed files are living documents or code, so editing in place is correct.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| none | | | | |

**FILES NEEDED BUT NOT PROVIDED:** None for the content under review. Not supplied: CI check results, commit trailers and a live checkout at the head SHA.

## Close-out

There are no findings to adjudicate, and the reviewer does not adjudicate its own findings.

**ADJUDICATION:** none (no findings).

**VERIFIED AFTER FIXES:** Nothing changed after the review.

**MERGE RECOMMENDATION:** Merge, once the expected CI checks are confirmed present and green. They were not provided, and Step 8 does not accept a missing check as green. No owner or architecture decision is pending. No written rule beyond the skill's Step 8 gates covers this PR, so I cite none.

```json
{
  "verdict": "merge",
  "findings": []
}
```