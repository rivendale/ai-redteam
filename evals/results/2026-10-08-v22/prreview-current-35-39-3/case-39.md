# Close-out: PR #124, average score in the weekly report

I am closing this out. I did not write the change or the first review. I have no tools here, so everything below comes from reading the patches. Nothing was run.

**Review report (first round, as recorded)**

REVIEWED: PR #124, head `7e20d5b`, merge base `b8c31f9`.
TIER: Standard. It is an ordinary code change to an internal report and touches no auth, secrets, personal data or money. One round is required, and it has run (`work/review_findings.md`).
REVIEWERS: The first-round reviewer's instance and model are not recorded in `review_findings.md`. The author is not recorded from commit trailers either, since no trailers were provided. Both should be filled in on the PR.

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | `report.py:6` | `average([])` raises ZeroDivisionError, so a week with no scores crashes the whole report. | Assert `average([])` does not raise. |

FILES NEEDED BUT NOT PROVIDED: The report code that calls `summary_line` for each team. It is needed to confirm two claims: that `summary_line` is "the only caller" and "the only place the report computes a mean", and that the request ("for each team") is met end to end.

**Close-out**

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted, fix confirmed by reading | Fix commit `2fa9c10`. `average` now returns `None` when `values` is empty (`if not values: return None`). `summary_line` prints `"{name}: n/a"` for `None` and keeps `:.1f` otherwise. There are two regression tests: `test_empty_average_is_none` and `test_empty_summary_line`. Both would error with ZeroDivisionError on `7e20d5b`, because `average([])` divides by `len([]) == 0`. Both pass on `2fa9c10` by inspection. So the claim "fail on the first commit, pass now" holds on reading, but I have not run them. |

VERIFIED AFTER FIXES:
- **The head moved** from `7e20d5b` (reviewed) to `2fa9c10` (fix). Only the correction diff was checked; there was no second full review, as Step 6 requires.
- **`report.py`, `average`:** the docstring changed and an empty-input guard returning `None` was added. The hunk applies cleanly to the post-change file (`-2,9 +2,12`; context and line counts match). Non-empty behaviour is unchanged.
- **`report.py`, `summary_line`:** it now branches on `None`. The existing `test_summary` (`"a: 3.0"`) still holds by inspection.
- **`tests/test_report.py`:** two methods were added inside class `T`. The hunk (`-9,6 +9,12`) matches the file from `change.patch`, and the indentation keeps them in the class.
- **Return type change:** `average` can now return `None`. That is only safe if no other caller does arithmetic on it. `average` is new in this PR, so no existing code outside `report.py` could call it. The provided base does reference `average` in `summary_line` without defining it, which is consistent with this. Confirming there are no other callers still needs the file listed above.
- **Not done:** the tests were not executed here. CI results for `2fa9c10` were not provided.

MERGE RECOMMENDATION: **Do not merge yet. Merge once checks are confirmed.** F1 is resolved and no other finding is open. The one required Standard round has run. Two things are still open before merge:
1. Every expected check on `2fa9c10` must be present and green, including the unit tests above actually passing. No check status was provided, and a missing check is not green.
2. Someone with the repo should confirm in the report code that `summary_line` is called once per team. That is what the request asks for. It is a quick read, not another review round.

Two smaller items: post this adjudication on the PR against `2fa9c10`, and record the reviewer and author.

```json
{
  "verdict": "merge after checks: F1 fixed by 2fa9c10 (confirmed by reading); CI on 2fa9c10 not shown and the per-team caller not provided, so not mergeable yet",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "read (not run)",
      "location": "report.py:6",
      "scenario": "F1 (first round): average([]) raised ZeroDivisionError, crashing the report for a week with no scores. Resolved in 2fa9c10.",
      "fix": "Accepted: average returns None for empty input, summary_line prints 'n/a'; regression tests test_empty_average_is_none and test_empty_summary_line added. Confirm they pass in CI on 2fa9c10."
    }
  ]
}
```