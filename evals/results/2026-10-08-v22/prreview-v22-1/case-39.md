# Close-out of PR #124: average score in the weekly report

This is a close-out, not a new review round. The Standard tier needs one round, and that round has run (`work/review_findings.md`). What remains is a targeted read of the fix, checking each adjudication against the code, and the merge gates.

I had no tools in this session. Everything below comes from reading the patches. No test was run.

**Review report (from the first round, restated for the record)**

REVIEWED: PR #124, head `7e20d5b`, merge base `b8c31f9`.

TIER: Standard. This is an ordinary code change to an internal weekly report. It does not touch auth, secrets, network exposure, personal data, money or migrations.

REVIEWERS: the first-round reviewer is not identified in `review_findings.md`. I did this close-out and did not write the change. The author is not recorded either: no commit trailers were provided, so authorship is unconfirmed.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | `report.py:6` | `average([])` raises `ZeroDivisionError`, so a week with no scores crashes the whole report. | Assert `average([])` does not raise. |

FILES NEEDED BUT NOT PROVIDED: the code that calls `summary_line` once per team, which builds the report itself. `base/report.py` contains only `summary_line`. Without the caller I cannot confirm the request ("for each team") end to end, or that `summary_line` is the only caller. That second point is asserted in `PR.md` and is consistent with every file shown.

**Close-out**

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted | Fix commit `2fa9c10` (`work/fix.patch`). See the verification below. |

**Verification of F1's acceptance (targeted read of the fix diff):**

- **Fix is correct.** `average` now returns `None` when `not values`. Otherwise it computes `sum/len` exactly as before, so non-empty behaviour is unchanged and `test_average` and `test_summary` are unaffected.
  - The guard does not misfire on zero scores: `not [0, 0]` is `False`.
  - Iterators are not newly broken: `len()` already required a sized sequence before the fix.
- **The only caller handles `None`.** `summary_line` checks `avg is None` and prints `"{name}: n/a"`. It no longer formats `None` with `:.1f`, which would have raised `TypeError` and moved the crash from one line to another.
  - In the base, `average` did not exist (`base/report.py` called an undefined name). So no other caller in the shown code can receive the new `None` return.
- **Regression tests would fail before the fix and pass after it.**
  - On `7e20d5b`, `test_empty_average_is_none` and `test_empty_summary_line` both error with `ZeroDivisionError`. On `2fa9c10` they pass.
  - `test_empty_summary_line` exercises the actual crash path in the report, which is stronger than the first review's suggested "does not raise".
  - This was verified by reading. I did not run the tests.
- **The fix introduces no new defect.** I found none in the changed lines. Both hunks are consistent with the files they patch (line counts check out).

VERIFIED AFTER FIXES: the head moved from `7e20d5b` (reviewed) to `2fa9c10` (fix). The lines changed after the review are:

- `report.py`: the `average` docstring, the empty-input guard in `average`, and the two lines of `summary_line`.
- `tests/test_report.py`: the two new tests.

Each change was verified by the targeted read above, not by running anything. Only `2fa9c10` is covered. Any later commit is unreviewed.

MERGE RECOMMENDATION: **merge once checks are confirmed green on `2fa9c10`. It is not yet clear to merge.** The single round has run, F1 has a written decision, and no blocker or owner decision is pending. Two things are still open:

1. **No CI result for `2fa9c10` was provided.** A missing check is not green. The expected checks, including the unit tests, must be present and passing on that SHA.
2. **The adjudication must be posted on PR #124** with the reviewed SHA (`7e20d5b`) and the fix SHA (`2fa9c10`).

Optional, not a gate: have the owner confirm that "n/a" is the wanted display for a team with no scores that week.

```json
{
  "verdict": "merge after checks: F1 accepted (fix 2fa9c10 verified by targeted read); CI on 2fa9c10 not shown and adjudication not yet posted on the PR",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read (fix diff and regression tests read against change.patch; tests not run, no tools)",
      "location": "report.py:6",
      "scenario": "average([]) raised ZeroDivisionError, crashing the report for a team with no scores that week.",
      "fix": "Accepted in 2fa9c10: average returns None for empty input; summary_line, the only caller in the shown code, prints 'n/a'; test_empty_average_is_none and test_empty_summary_line fail on 7e20d5b and pass on 2fa9c10."
    }
  ]
}
```