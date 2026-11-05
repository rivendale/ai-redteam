# PR #124 close-out

## Review report (first round, restated)

**REVIEWED:** PR #124, head 7e20d5b, merge base b8c31f9. The fix is commit 2fa9c10, which moves the head. Its full SHA and the post-fix head were not provided.
**TIER:** Standard. The change is ordinary code in an internal weekly report, with no auth, secrets, personal data or money.
**REVIEWERS:** The first round is `work/review_findings.md`; the reviewer's identity and model are not recorded there. The author is not identifiable because no commit trailers were supplied. This close-out is a targeted read of the fix diff and does not repeat the full review.

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | report.py:6 | `average([])` raises ZeroDivisionError, so a team with no scores crashes the whole report. | Assert `average([])` does not raise. |

**FILES NEEDED BUT NOT PROVIDED:** CI or check status, commit trailers, and the full SHA of 2fa9c10.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Accepted** (pending the check status below) | Fix 2fa9c10 (`work/fix.patch`). The author's reading is confirmed by my read of the diff. |

My targeted read of the fix diff found:
- **Empty input:** `average([])` now returns None via `if not values`, so the division is never reached. `summary_line` checks `avg is None` and prints `"a: n/a"`. A real average of 0 still prints `0.0`, because the check is `is None` and not falsiness.
- **Regression tests:** `test_empty_average_is_none` and `test_empty_summary_line` fail on 7e20d5b, where `average([])` raises ZeroDivisionError. They should pass on the fix, since the patched code returns None and `"a: n/a"`. I read the tests and code but could not run them in this session.
- **Patch validity:** The hunk line counts in both files are consistent with `change.patch` applied to `base/`.
- **Other callers:** The "only caller" claim holds for the files provided. `average` is new in this PR and the base `report.py` contained only `summary_line`. The new None return would break any later caller that does arithmetic on the result, but no such caller exists in the inputs, so this is not a finding.
- **Original request:** The change delivers an average per team and nothing extra. The base repository has no function that loops over teams, so the per-team loop is outside this PR.

**VERIFIED AFTER FIXES:**
- The correction diff and its tests were read, not run.
- The claim that the new tests fail on the first commit and pass now was checked by reading only. It has not been confirmed by execution.
- No new defect was found in the fix.

**MERGE RECOMMENDATION:** Merge, conditional on the expected checks being present and green on the post-fix head. Step 8 requires that, and no check status was provided, so the gate is not yet evidenced. Every finding has a decision, no blocker is open, and no owner decision is pending. Showing "n/a" for an empty team is a reasonable product choice and not a gate. No written rule was supplied on this point, so none is cited.

```json
{
  "verdict": "merge_after_checks_confirmed",
  "findings": []
}
```