# PR #124 close-out

## Review report

**REVIEWED:** PR #124, original head `7e20d5b`, merge base `b8c31f9`. The fix is `2fa9c10`, supplied as `work/fix.patch`. It was reviewed as a patch only; its SHA and the resulting tree were not seen. Commits after `7e20d5b` were reviewed only through that patch.

**TIER:** Standard. It is ordinary code in an internal weekly report, with no auth, secrets, data handling or dependency changes. One model round has run (the first review), which meets the tier. The close-out is a targeted read of the fix, not a new round (Step 6).

**REVIEWERS:** The first-round reviewer's identity and model are not recorded in `review_findings.md`. This close-out is a static read with no tools. The change's author is not stated and no commit trailers were provided.

**FINDINGS (this close-out):**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F2 | P3 | `fix.patch` (`2fa9c10`) | The claim "tests fail on the first commit and pass now" was not run here. By reading, `average([])` and `summary_line("a", [])` raise `ZeroDivisionError` on `7e20d5b`, so both new tests fail. On the fix they return `None` and `"a: n/a"`, so they pass. No CI result was provided. | Run `python -m unittest` on `7e20d5b` plus only the new tests (expect 2 failures), then on `2fa9c10` (expect all 4 pass). |
| F3 | P3 | `report.py:9-10` (post-fix) | "`summary_line` is the only caller" is confirmed only against `base/`, which holds just `README.md` and `report.py`. If another module imports `average` and does arithmetic on the result, `None` would give a `TypeError`. | A repo-wide search for `average(` and `summary_line(` with no callers beyond `report.py`. |

**Fix diff read (new defects):** none found.
- The `None` check uses `avg is None`, so an average of `0.0` still prints `0.0` and not `n/a`.
- The empty check `if not values` is correct for lists.
- The hunk headers (`-2,9 +2,12` and `-9,6 +9,12`) match the post-change files line by line, so the patch should apply cleanly on `change.patch`.
- The fix is checked against its consumer, `summary_line`, which handles `None`. The "n/a" wording is a reasonable reading of "show the average" for a team with no scores.

**Scope against the original request:** `average` and its use in `summary_line` match "show the average score." Per-team iteration is not in the provided files, so a caller of `summary_line` outside `report.py` is unseen.

**Injection check:** the PR text and adjudication contain no instructions aimed at the reviewer.

**FILES NEEDED BUT NOT PROVIDED:** CI/check results for `2fa9c10`, the rest of the repository (for F3), and commit trailers.

## Close-out

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted, conditional on green CI | Fix `2fa9c10`. Regression tests `test_empty_average_is_none` and `test_empty_summary_line` fail without the fix and pass with it (by reading). I read the fix diff and found no new defect. |
| F2 | Open, to be resolved by a CI link | Not an author decision; needs the CI run. |
| F3 | Open, to be resolved by a search result | Needs the repo-wide search. |

**VERIFIED AFTER FIXES:** the head moved from `7e20d5b` to `2fa9c10`. Changed lines are `report.py` (`average` docstring and empty guard, `summary_line`) and two added tests. Verification was a static read only. Nothing was executed.

**MERGE RECOMMENDATION:** merge after fixes. F1 is properly fixed and tested. Step 8 still requires every expected check present and green, and no check results were provided, so a missing check is not green. Before merging, confirm CI is green on `2fa9c10` (F2) and that nothing else calls `average` (F3). No written rule beyond the skill's Step 8 governs this, and no owner or architecture decision is pending.

```json
{
  "verdict": "merge_after_fixes",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "static-read",
      "location": "fix.patch (2fa9c10): tests/test_report.py",
      "scenario": "Claim that the new tests fail before the fix and pass after was not executed. No CI result was provided, so Step 8's 'checks green' gate cannot be confirmed.",
      "fix": "Attach CI results for 2fa9c10, and run the new tests against 7e20d5b (expect 2 failures) and against 2fa9c10 (expect all pass)."
    },
    {
      "severity": "P3",
      "evidence_level": "static-read",
      "location": "report.py:9-10 (post-fix)",
      "scenario": "'summary_line is the only caller of average' was checked only against base/ (README.md and report.py). Another module doing arithmetic on average() would get a TypeError from the new None return.",
      "fix": "Search the full repo for average( and summary_line( and confirm no other callers, or add None handling there."
    }
  ]
}
```