# Close-out review: PR #124

**Scope.** This is a targeted read of the fix diff and the adjudication, as Step 6 and Step 7 require, not a new full round. I have no tools in this session, so I did not run any code. The commit trailers and CI status were not supplied.

## Review report

**REVIEWED:** PR #124, original head `7e20d5b`, merge base `b8c31f9`. The adjudication names a fix commit `2fa9c10`, so the head has moved. I read `work/fix.patch` on top of `work/change.patch`. I could not see commit `2fa9c10` itself, so I have not confirmed that it contains exactly this patch.

**TIER:** Standard. It is an ordinary code change with no auth, secrets, data handling or dependency changes, in an internal report. The one required model round has already run (`review_findings.md`).

**REVIEWERS:** The first-round reviewer is as recorded in `review_findings.md`, which does not name the instance or model. The author's identity is unknown because no commit trailers were supplied. I did not write the change and had no part in it, but I cannot confirm independence from the author without the trailers.

**FINDINGS (this close-out pass):** none new.

**FILES NEEDED BUT NOT PROVIDED:**
- Commit `2fa9c10`, to confirm it matches `fix.patch`.
- CI results for `2fa9c10`.
- Commit trailers.

## Close-out

**F1 (P1, `average([])` raises ZeroDivisionError): the Accepted decision is supported by reading.**
- **Fix correctness.** `average` now returns `None` for empty input, using `if not values`. `summary_line` tests `avg is None`, not truthiness, so a genuine mean of `0.0` still prints `0.0`.
- **Consumer check.** The only consumer in the repo is `summary_line` (base has only `report.py` and `README.md`). It handles `None`, and `test_empty_summary_line` asserts `"a: n/a"`.
- **Regression tests.** Both new tests (`test_empty_average_is_none`, `test_empty_summary_line`) would fail on `7e20d5b`, which raises ZeroDivisionError. This is established by reading only, because I did not run them.
- **Hunk headers.** I counted the lines in both hunks of `fix.patch` and the headers are consistent.
- **New defects in the fix.** None found. The only side effect is that `average` is now `Optional`. No other caller exists today, so I do not raise it as a finding.

**Observation, not a finding.** The repo contains no code that loops over teams. The request is "average score for each team", and `summary_line` formats one team. I cannot confirm from these files that the weekly report calls it per team. If a caller exists elsewhere, it was not provided.

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted (supported by reading) | `2fa9c10` per the author. Fix diff read, no new defect, two regression tests that fail on `7e20d5b` by inspection. Not run by me. |

**VERIFIED AFTER FIXES:**
- **Changed since review:** `report.py` (`average` and `summary_line`) and `tests/test_report.py` (two added tests).
- **How verified:** by a targeted read of `fix.patch` only.
- **Not verified:** the contents of `2fa9c10`, and whether the tests actually pass.

**MERGE RECOMMENDATION:** merge after fixes. Merge once CI is green on `2fa9c10` and the commit is confirmed to match `fix.patch`. Step 8 requires every expected check to be present and green, and I have no CI evidence. A missing check is not green. No written rule settles anything beyond that, and no owner or architecture decision is pending.

```json
{
  "verdict": "merge after fixes",
  "findings": []
}
```