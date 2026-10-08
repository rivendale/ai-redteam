# Review of PR #124 (first round)

REVIEWED: PR #124, head 7e20d5b, merge base b8c31f9.

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | report.py:6 | `average([])` raises ZeroDivisionError, so a week with no scores crashes the whole report. | Assert average([]) does not raise. |

FILES NEEDED BUT NOT PROVIDED: none.
