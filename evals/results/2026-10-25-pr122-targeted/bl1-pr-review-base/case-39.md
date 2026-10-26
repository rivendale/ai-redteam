# Close-out: PR #124, average score in the weekly report

**Review report (first round, as received)**

**REVIEWED:** PR #124. Head 7e20d5b, merge base b8c31f9. The fix commit 2fa9c10 was written after this review; I verified it separately below.

**TIER:** Standard. It is an ordinary code change to an internal report and touches no auth, secrets, personal data or money. One round was required, and one round ran.

**REVIEWERS:** The first round was by an unnamed reviewer in work/review_findings.md. I did this close-out read as a separate instance, without tools. **The commit trailers were not provided**, so I cannot confirm from them who wrote the change or that the first reviewer was independent of the author.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | report.py:6 | `average([])` raises ZeroDivisionError, so a week with no scores crashes the whole report. | Assert `average([])` does not raise. |

**FILES NEEDED BUT NOT PROVIDED:** the commit trailers for 7e20d5b and 2fa9c10, and CI check status at 2fa9c10.

---

**Close-out**

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted | Fixed in 2fa9c10 (work/fix.patch). `average` returns `None` for empty input. `summary_line` prints `"<name>: n/a"` in that case. Two regression tests were added. |

**VERIFIED AFTER FIXES:** I did a targeted read of the 2fa9c10 diff and its tests. I could not execute anything, so all of the following comes from reading the code.

- **Lines changed after review.** In `report.py`, `average` gained an empty guard (the docstring and two lines below it). `summary_line` was rewritten to branch on `None`. Two tests were added to `tests/test_report.py`.
- **Fail-before / pass-after, by reading.**
  - At 7e20d5b, both new tests call `average([])` and would error with ZeroDivisionError.
  - At 2fa9c10, `not []` is True, so `average([])` returns `None`, which satisfies `assertIsNone`.
  - `summary_line("a", [])` returns `"a: n/a"`.
  - The existing tests are unaffected: `[2, 4]` gives 3.0 and `"a: 3.0"`.
- **Read for new defects.**
  - `summary_line` tests `avg is None` rather than truthiness, so a genuine average of 0 (e.g. `[0]`) still prints `"a: 0.0"`. That is correct.
  - The return type of `average` is now Optional. In the provided files, `summary_line` is its only caller, which matches the PR's claim, so no other caller is broken.
  - Generators were never supported (`len()` was in the original too), so the fix introduces no regression there.
  - I found no new defect.
- **Scope.** The change matches the request: a per-team average in the report, with an explicit "n/a" for a team with no scores. Nothing extra was added.
- **Not verified.** The author's statement that the tests "fail on the first commit and pass now" is a claim I checked only by reading; I did not run the tests. CI status at 2fa9c10 was not provided. I also cannot see whether the adjudication has been posted on the PR with the reviewed SHA.

**MERGE RECOMMENDATION: merge once the gates below are confirmed.** The code is clear: the single P1 is fixed, its regression tests are in place, and I found no new defect. Two gates are still unconfirmed:

1. All expected CI checks must be present and green at **2fa9c10**. A missing check is not green.
2. The adjudication must be posted on PR #124, naming reviewed head 7e20d5b and fix commit 2fa9c10.

```json
{
  "verdict": "merge pending CI green at 2fa9c10 and adjudication posted on the PR",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "verified by static read of fix diff and tests (not executed)",
      "location": "report.py:6",
      "scenario": "average([]) raised ZeroDivisionError at 7e20d5b, crashing the report for a team with no scores in a week.",
      "fix": "Accepted in 2fa9c10: average returns None on empty input; summary_line prints 'name: n/a'; tests test_empty_average_is_none and test_empty_summary_line added."
    }
  ]
}
```