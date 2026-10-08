**Close-out: PR #124 (average score in the weekly report)**

REVIEWED: PR #124. The first-round review covered head `7e20d5b` with merge base `b8c31f9`. The fix commit `2fa9c10` (work/fix.patch) moved the head afterward. It was checked by reading the correction diff, as Step 6 requires, and was not given a new full review.

TIER: Standard. The change is ordinary code in an internal weekly report. It touches no auth, secrets, money, personal data or migrations, and the context gives the stakes as standard. One round is required, and it has run.

REVIEWERS: The first round is in work/review_findings.md. That report does not name its reviewer instance or model and does not record a tier. The author is also unnamed, because no commit trailers were provided. This close-out was done by a separate instance (Opus 5.5) that did not write the change.

### Verification of the fix (2fa9c10)

| Check | Result |
|---|---|
| Fix addresses F1 | Yes. In `report.py`, `average` now returns `None` when `values` is empty (`if not values`), so `average([])` no longer reaches `sum/len` and cannot raise ZeroDivisionError. |
| Only caller handles the new `None` return | Yes. `summary_line` prints `"{name}: n/a"` when the result is `None` and otherwise formats as before. The PR states it is the only caller. `average` is new in this PR and is called nowhere else in the provided base. |
| No behaviour change for non-empty input | Yes. The non-`None` branch is the same `f"{name}: {avg:.1f}"`. The existing `test_summary` (`"a: 3.0"`) still covers it. |
| Regression tests fail without the fix | By reading, yes. Without the fix, `average([])` and `summary_line("a", [])` both raise ZeroDivisionError, so both tests error out. With the fix, they return `None` and `"a: n/a"`. **I did not run the tests** because I have no tools in this session. |
| Patch applies | The hunk headers (`-2,9 +2,12` and `-9,6 +9,12`) agree with the post-change file contents line for line. |
| Scope against request | The PR shows a mean in the summary line, which is what the request asked for. The fix adds nothing beyond the empty case. One thing I could not confirm: the code that calls `summary_line` once per team was not provided. |

I found no new findings while reading the correction diff.

### Close-out

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 (P1) | Accepted, and the acceptance is confirmed | Fixed in `2fa9c10`. `average([])` returns `None`, and `summary_line(name, [])` returns `"name: n/a"`. Regression tests `test_empty_average_is_none` and `test_empty_summary_line` would error at `7e20d5b` and pass at `2fa9c10`; this is based on reading the code, not on running it. |

VERIFIED AFTER FIXES: The changes after the review are `report.py` (`average` docstring, the `if not values: return None` guard, and the `summary_line` branch) and `tests/test_report.py` (two new tests). I verified them by reading the diff against the post-change file. The tests have not been executed here.

MERGE RECOMMENDATION: **Do not merge yet. Merge once checks are confirmed.** The code is clear: there is no open blocker, and F1 is fixed and has tests. Step 8 still has unmet conditions:
1. No CI or check results were provided for `2fa9c10`. A missing check does not count as green. The owner should confirm the required checks are present and green at `2fa9c10`, and that this includes the test suite with the two new tests.
2. The first-round report should record its tier and reviewer identity, and the author should be recorded from the commit trailers. These are process gaps and do not block the code.

Once item 1 is green, I recommend merging.

FILES NEEDED BUT NOT PROVIDED: CI or check results for `2fa9c10`; commit trailers for authorship; the code that builds the weekly report and calls `summary_line` once per team, which would confirm "for each team".

```json
{
  "verdict": "do not merge yet: F1 fix verified by reading; merge once required checks are shown green at 2fa9c10",
  "findings": []
}
```