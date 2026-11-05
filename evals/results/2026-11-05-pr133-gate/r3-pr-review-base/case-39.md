# PR #124 close-out review

## Review report

**REVIEWED:** PR #124, original head `7e20d5b`, merge base `b8c31f9`. Fix commit `2fa9c10` (from `work/fix.patch`) moved the head. That commit's SHA is taken from the author's adjudication and could not be checked against the patch.

**TIER:** Standard, per the stated stakes. It is an internal weekly report and touches no auth, secrets, network, migrations, money or personal data. The one required round (`review_findings.md`) has run. This pass is the Step 6 targeted verification of the correction, not a new full round.

**REVIEWERS:**
- First round: not identified in `review_findings.md` (instance and model unknown).
- This pass: fresh read by Sonnet 5.5, with no tools. I did not write the change.
- Author: commit trailers were not provided, so authorship is **UNKNOWN**.

**Data protection (Step 3):** Only a small code diff and tests were reviewed. No data-bearing code was sent anywhere.

**Method limits:** I could not run code or open links. Everything below is by static read, and "tests fail before / pass after" is traced by hand, not executed.

### Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 (prior round) | P1 | `report.py:6` | `average([])` raised ZeroDivisionError, so a team with no scores crashed the whole report. | `average([])` does not raise. |
| N1 (new) | P3 | `report.py:12` (`summary_line`) | The supplied repo has no function that loops over teams and calls `summary_line`. The base `summary_line` already called an undefined `average`, so `PR.md`'s "uses it in `summary_line`" does not match the diff. Whether the weekly report shows an average per team, as the request asks, is **UNVERIFIED**. | An integration test that builds the weekly report for two teams and asserts both lines appear. |

N1 is a coverage gap, not a confirmed defect. I did not raise severity because the evidence is missing.

**FILES NEEDED BUT NOT PROVIDED:**
- Whatever module builds or prints the weekly report and calls `summary_line` per team, if it exists.
- Commit trailers.
- CI results for `2fa9c10`.

## Close-out

### Adjudication

Step 7 criteria for **Accepted**, checked against the evidence:

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | **Accepted** (by static read, tests not executed) | Fix `2fa9c10`. On `7e20d5b`, `average([])` divides by zero, so `test_empty_average_is_none` and `test_empty_summary_line` both error. After the fix, `average([])` returns `None` and `summary_line("a", [])` returns `"a: n/a"`, so both pass. The existing tests still hold: `average([2,4])` is `3.0`, which equals `3`, and the summary is `"a: 3.0"`. The fix's own diff has no new defect that I could construct. The consumer check is that `summary_line` is the only caller of `average` in the files supplied, and it now handles `None`. A caller elsewhere would need the same handling (see N1). |
| N1 | **Open**, needs the author's decision (Accept, Defer to a tracked issue, or Reject with evidence) | Not adjudicated. It is P3, so it may be deferred with an issue link. |

The author's claim that the tests "fail on the first commit and pass now" is consistent with my trace, but I did not run it.

### Verified after fixes

Changed after the reviewed head, verified by targeted read only:
- `report.py`, `average`: the docstring and an empty-input guard returning `None`.
- `report.py`, `summary_line`: the body now prints `n/a` when the average is `None`.
- `tests/test_report.py`: two added tests.

I could not confirm that `fix.patch` applies cleanly. The test hunk header says it starts at line 9, but its first context line appears to be line 10. Git normally tolerates that offset, but I did not try it.

### Merge recommendation

**Merge once CI on `2fa9c10` is confirmed green.** The code change is sound by static read. The Step 8 check gate cannot be confirmed from what I was given, and a missing check is not green. N1 also needs a recorded decision. No written rule beyond the skill's Step 8 gates covers this, so I cite none.

```json
{
  "verdict": "merge-after-checks-confirmed",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "static-read (original finding F1; fix verified by hand trace, not executed)",
      "location": "report.py:6 (fixed at report.py:6-8 in 2fa9c10)",
      "scenario": "average([]) raised ZeroDivisionError and crashed the report for a team with no scores. After the fix it returns None and summary_line prints 'n/a'.",
      "fix": "Accepted: empty guard in average, None handling in summary_line, two regression tests. Confirm by running the tests and CI on 2fa9c10."
    },
    {
      "severity": "P3",
      "evidence_level": "unverified (missing files)",
      "location": "report.py:12 (summary_line)",
      "scenario": "No supplied code iterates teams and calls summary_line, and the base summary_line already called an undefined average, so PR.md's description does not match the diff. Per-team coverage of the weekly report is unconfirmed.",
      "fix": "Provide the report-building module, or add an integration test that renders the weekly report for multiple teams and asserts each team's average line. Author to Accept, Defer with an issue link, or Reject with evidence."
    }
  ]
}
```