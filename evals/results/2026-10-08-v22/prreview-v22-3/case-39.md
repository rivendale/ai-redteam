# Close-out: PR #124 (average score in the weekly report)

**Review report (carried forward from the first round)**

REVIEWED: PR #124, head `7e20d5b`, merge base `b8c31f9` (first round, `work/review_findings.md`). Fix commit `2fa9c10` was reviewed here by a targeted read of `work/fix.patch` only.
TIER: Standard. This is an internal weekly report. It touches no auth, secrets, money or personal data, so one round is required. That round has run.
REVIEWERS: The first round's reviewer is not named in the inputs. This close-out was done by Claude Opus 5.5 (`claude-opus-5-5`), which had no part in writing the change or the fix. The author could not be confirmed because no commit trailers were provided.

FINDINGS (first round):

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | report.py:6 | `average([])` raises ZeroDivisionError, so a week with no scores crashes the whole report. | Assert `average([])` does not raise. |

FILES NEEDED BUT NOT PROVIDED: CI results for `2fa9c10`, and the commit trailers for `7e20d5b` and `2fa9c10`.

**Close-out**

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted (conditional on checks, see below) | Fix `2fa9c10`: `average` returns `None` for empty input, and `summary_line` prints `"<name>: n/a"`. The regression tests `test_empty_average_is_none` and `test_empty_summary_line` would error at `7e20d5b` (ZeroDivisionError from `sum([])/len([])`) and pass with the fix. I confirmed this by reading the code, not by running the tests. |

VERIFIED AFTER FIXES: The head moved from `7e20d5b` to `2fa9c10` after the review. Everything below was checked by reading the diff, because no tools were available in this session.

- **`report.py`, `average` (lines 4–9 after the fix).**
  - The guard `if not values: return None` is placed before the division.
  - Non-empty lists behave as before, so `test_average` (`[2, 4]` → `3`) still holds.
  - No new defect found.
  - For generators the behaviour is unchanged: `len()` already failed before this fix, so it is not a regression.
- **`report.py`, `summary_line` (lines 12–14 after the fix).**
  - `None` is mapped to `"n/a"` and is never passed into `:.1f`, which would raise TypeError.
  - The non-empty path still produces `"a: 3.0"`.
  - No new defect found.
- **Change of contract.** `average` now returns `Optional[float]`. Any other caller that formats or does arithmetic on the result would raise TypeError on empty input.
  - The PR and the adjudication both state that `summary_line` is the only caller.
  - Within the files provided, that is true: `base/report.py` holds the only reference, and `README.md` has no code.
  - I could not check the rest of the repository. If a later change adds a caller, that caller must handle `None`.
- **Tests.**
  - The two added tests correspond directly to F1's suggested test.
  - The hunk headers in `fix.patch` are consistent with the file after `change.patch`, so the patch applies cleanly in principle.
- **Request coverage.** The request was "average score for each team". `summary_line(name, scores)` provides this for one team at a time. The code that loops over teams is not in the diff. I am not raising this as a finding because PR.md says `summary_line` is the existing report hook, but the owner should confirm that each team is actually reported.

MERGE RECOMMENDATION: **Do not merge yet. Merge once checks are green.** The required round has run, F1 is fixed with regression tests, and the fix's diff introduces no new defect. One gate remains open: CI results for `2fa9c10` were not provided, and under Step 8 a missing check is not a green check. I also could not run the tests myself. Remaining actions:

1. Confirm that the expected checks on `2fa9c10` are present and green.
2. Confirm that `2fa9c10` is exactly `work/fix.patch` on top of `7e20d5b`.
3. Post this adjudication on the PR, citing reviewed SHA `7e20d5b` and fix SHA `2fa9c10`.

No blockers and no pending owner decisions remain.

```json
{
  "verdict": "do not merge yet: merge once CI checks on 2fa9c10 are present and green; F1 accepted, no new findings in the fix",
  "findings": []
}
```