# PR #124 close-out: average score in the weekly report

**Recommendation: do not merge yet.** The F1 fix looks correct when read. But no check results for the new head `2fa9c10` were provided, and a missing check is not green.

## Review report (first round, relayed from `work/review_findings.md`)

**Reviewed:** PR #124, head `7e20d5b`, merge base `b8c31f9`.

**Tier:** Standard. This is an ordinary code change to an internal report. It touches no auth, secrets, network exposure, personal data or money. The context also states the stakes as standard. One round is required, and one ran.

**Reviewers:** the first-round reviewer's instance and model are not recorded in the inputs. No commit trailers were provided, so who wrote the change cannot be read from them and is unrecorded. This close-out was written by Claude (Opus 5.5) in a session that did not write the change.

**Findings:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | `report.py:6` | `average([])` raises `ZeroDivisionError`, so a week with no scores crashes the whole report. | Assert `average([])` does not raise. |

**Files needed but not provided:** none for the round as reported. For the close-out, I still need:
- the CI or check results for `2fa9c10`;
- the commit `2fa9c10` itself (only `work/fix.patch` was supplied).

## Close-out

**Adjudication:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Accepted** (verified by static read; tests not run) | Fix `2fa9c10` / `work/fix.patch`. See below. |

**Verified after fixes:**

The head moved from `7e20d5b` to `2fa9c10` after the review. `2fa9c10` was not fully reviewed. I did a targeted read of the correction diff, as Step 6 requires.

- **Patch applies.** After `change.patch`, `report.py` has the docstring at line 1, blank lines at 2–3, `def average` at 4–6, and `summary_line` at 9–10. The hunk `@@ -2,9 +2,12 @@` matches those lines exactly.
- **`report.py` `average` (now lines 4–8).** `if not values: return None` removes the division by zero for empty lists, which is the F1 scenario.
- **New-defect check on `average`.**
  - The return type is now `float | None`.
  - The only caller in the provided tree is `summary_line` (`base/` contains only `report.py`), and it handles `None`.
  - I found no new defect for list inputs.
  - Inputs that were already unsupported behave as before. A generator still fails at `len`, as it did in the base.
- **`report.py` `summary_line` (now lines 11–13).** It prints `"{name}: n/a"` when the average is `None`. Otherwise it gives the same `:.1f` output as before. No new defect found.
- **Regression tests, `tests/test_report.py`.**
  - `test_empty_average_is_none` and `test_empty_summary_line` would both error with `ZeroDivisionError` on `7e20d5b`, and both would pass on `2fa9c10`.
  - The existing tests still pass on `2fa9c10`: `average([2,4]) == 3.0 == 3`, and the summary is `"a: 3.0"`.
  - The author's claim that the tests "fail on the first commit and pass now" matches this reading. I could not run them in this session, so it rests on static reasoning only.
  - The suggested test ("`average([])` does not raise") is covered by `test_empty_average_is_none`.
- **Fit to the original request.** The change produces a per-team mean line and nothing extra. The PR description's "only place the report computes a mean" is consistent with the provided files. The rest of the repository was not provided.

**Minor note (not a finding):** `base/report.py:5` already calls `average`, which is undefined in the base. So the PR defines a missing function rather than "uses it in `summary_line`" for the first time. The description is slightly inaccurate, but this changes no merge decision.

**Merge recommendation: do not merge yet.** Merge once the expected checks are confirmed present and green on `2fa9c10`.

The blocking rule is Step 8: *"every expected check is present and green (a missing check is not green, and a red check is never overridden)."* No check results were supplied.

The other gates are met:
- the Standard tier's single round has run;
- F1 has a written decision;
- no P0 or P1 remains open;
- no owner or architecture decision is pending.

Also post this adjudication on the PR with the reviewed SHA `7e20d5b` and the fix SHA `2fa9c10`, as Step 7 requires. This session cannot post it.

```json
{
  "verdict": "do not merge yet: F1 accepted on static read, but checks for 2fa9c10 not provided (Step 8: a missing check is not green)",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "fix verified by static read of fix.patch against change.patch; regression tests reasoned through, not run (no tools)",
      "location": "report.py:6",
      "scenario": "average([]) raised ZeroDivisionError, so a week with no scores crashed the whole report",
      "fix": "Accepted in 2fa9c10: average returns None for empty input; summary_line (only caller in provided tree) prints 'n/a'; tests test_empty_average_is_none and test_empty_summary_line added"
    }
  ]
}
```