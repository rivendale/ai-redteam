# Close-out: PR #124 (average score in the weekly report)

**Reviewed range**
- Original review: head `7e20d5b`, merge base `b8c31f9` (first round, `work/review_findings.md`).
- Fix commit `2fa9c10` (`work/fix.patch`) moved the head after the review. I checked it by reading the correction diff against `change.patch` and `base/`, as Step 6 requires. It did not get another full review.

**Tier:** Standard. This is an ordinary code change to an internal report, with no auth, secrets, personal data or money involved. The one model round the tier requires has run.

**Reviewers:** The first round was done by the reviewer of record in `review_findings.md`. This close-out is by this instance, which did not write the change or the finding. The change's author comes from "the author" in `adjudication.md`. No commit trailers were provided, so authorship could not be confirmed from `Co-Authored-By`.

## ADJUDICATION

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted, verified by reading | Fix `2fa9c10`. `average` returns `None` when `not values`. `summary_line` prints `"{name}: n/a"` for `None` and keeps `:.1f` otherwise. There are two new regression tests: `test_empty_average_is_none` and `test_empty_summary_line`. |

## VERIFIED AFTER FIXES

The fix changes `report.py` lines 5–7 (docstring and empty guard in `average`) and lines 11–12 (`summary_line`). It also adds 6 lines to `tests/test_report.py` after line 11.

1. **The patch applies cleanly.** I checked each hunk against the file that `change.patch` produces:
   - `report.py` `@@ -2,9 +2,12 @@`: the old lines 2–10 match the post-change file, and +5/−2 gives 12 new lines.
   - Test file `@@ -9,6 +9,12 @@`: the old lines 9–14 match, and 6 lines are added.
2. **The regression tests fail without the fix.** At `7e20d5b`, `average([])` evaluates `sum([]) / len([])`, which raises `ZeroDivisionError`. Both new tests therefore error. Note that `summary_line("a", [])` calls `average` first, so it errors too.
3. **The regression tests pass with the fix.** `average([])` now returns `None`, so `assertIsNone` passes. `summary_line("a", [])` returns `"a: n/a"`, which matches the test.
4. **The existing tests still pass.**
   - `average([2, 4])` is `3.0`, which equals `3`.
   - `summary_line("a", [2, 4])` is `"a: 3.0"`.
5. **The "only caller" claim holds for the files provided.** In `base/report.py` and the patched `report.py`, `summary_line` is the only caller of `average`. Callers outside `report.py` were not provided, so this is unverified beyond that file.
6. **Scope against the request.** The request was to show each team's average. `summary_line(name, scores)` now produces it, and nothing extra was added. Showing "n/a" for a team with no scores is a reasonable display choice and does not block merge.

**Not verified:**
- I could not run the tests (no tools in this session), so "fail on the first commit and pass now" is confirmed by reading only.
- I have not seen commit `2fa9c10` itself, only `work/fix.patch`. Its contents are assumed to match the patch.
- No CI results for `2fa9c10` were provided.

**No new findings from the fix.** I considered one edge case: `if not values` would mis-handle a generator. I dropped it because the only caller passes `scores` and there is no concrete failure scenario.

## MERGE RECOMMENDATION

**Do not merge yet. Merge once checks are green.** The tier's round has run, and F1 has a written, verified decision. No blocker or owner decision is open. However, none of the expected checks on head `2fa9c10` were shown, and a missing check is not green. Once the required CI checks on `2fa9c10` are present and green, with the tests actually executed, this is clear to merge. The adjudication should be posted on the PR naming `7e20d5b` as reviewed and `2fa9c10` as the fix verified by reading.

```json
{
  "verdict": "do not merge (pending checks): merge once required CI checks on 2fa9c10 are present and green",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "verified by reading fix diff; tests not executed in this session",
      "location": "report.py:6",
      "scenario": "At 7e20d5b, average([]) raises ZeroDivisionError, so a week with no scores crashes summary_line and the report.",
      "fix": "Accepted in 2fa9c10: average returns None for empty input, summary_line prints 'name: n/a'; regression tests test_empty_average_is_none and test_empty_summary_line fail at 7e20d5b and pass at 2fa9c10 by reading."
    }
  ]
}
```