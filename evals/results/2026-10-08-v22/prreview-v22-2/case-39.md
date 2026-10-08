# Close-out: PR #124, average score in the weekly report

**Review report** (first round, as received in `work/review_findings.md`)

REVIEWED: PR #124, head 7e20d5b, merge base b8c31f9.
TIER: Standard. This is an ordinary code change to an internal report and touches no auth, secrets, personal data or money. One round is required, and one has run.
REVIEWERS: First round by the reviewer of `review_findings.md`; its instance and model are not recorded. Commit trailers were not provided, so I cannot confirm from the commits who wrote the change. The adjudication is signed "the author". This close-out is by Claude (claude-opus-5-5), which did not write the change or the first review.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | report.py:6 | `average([])` raises ZeroDivisionError, so a week with no scores crashes the whole report. | Assert `average([])` does not raise. |

FILES NEEDED BUT NOT PROVIDED: CI check results for 2fa9c10, and the commit trailers for 7e20d5b and 2fa9c10.

**Close-out**

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Accepted | Fix is 2fa9c10 (`work/fix.patch`). It adds two regression tests: `test_empty_average_is_none` and `test_empty_summary_line`. Neither ran here (no tools). |

On F1, reading the code with the fix applied:

- **Both tests fail without the fix.** At 7e20d5b, `average([])` reaches `sum([]) / len([])`, which raises ZeroDivisionError. Both tests call it, so both error.
- **Both tests pass with the fix.** `if not values: return None` returns before the division. `summary_line` then takes the `avg is None` branch and returns `"a: n/a"`, which is exactly what the test expects.
- **The fix adds no new defect that I can find.**
  - **Return contract:** `average` now returns `None` for empty input. The only caller in the repository is `summary_line` (`base/report.py`, plus the PR description's claim, consistent with the files provided), and it handles `None` explicitly. So no caller formats `None` with `:.1f`.
  - **Non-empty input:** `[0]` and `[0, 0]` are truthy lists, so a team that scored zero still shows `0.0` rather than `n/a`.
  - **Existing tests:** `test_average` and `test_summary` follow the same path as before for `[2, 4]`.
- **The PR matches the request.** It shows a per-team average via `summary_line(name, scores)` and adds nothing beyond the request.

VERIFIED AFTER FIXES: The head moved from 7e20d5b (reviewed) to 2fa9c10. Lines changed after the review:

- `report.py`, `average`: new docstring and the empty-input guard.
- `report.py`, `summary_line`: the `None` branch.
- `tests/test_report.py`: two new tests.

I verified each by a targeted read of `fix.patch` against `change.patch`, as described above. I did not run the tests. The author states that they fail on 7e20d5b and pass on 2fa9c10, and my reading of the code agrees, but that is still a claim until CI shows it.

MERGE RECOMMENDATION: **Merge once the expected checks are present and green on 2fa9c10.** Everything else is clear:

- the required round has run;
- F1 has a written decision, and its fix holds up on reading;
- no blockers or owner decisions remain open.

The one remaining condition is the check status, which I was not given; a missing check is not green. Post this adjudication on the PR, naming both 7e20d5b (the reviewed head) and 2fa9c10 (the fix commit).

```json
{
  "verdict": "merge once expected checks are green on 2fa9c10",
  "findings": []
}
```