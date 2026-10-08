# pr-review v2.2 (held half), 2026-10-08: cases 35 and 36 on #29's fixtures, three runs each

The v2.2 gate (`../2026-10-08-v22`) held the pr-review change back. On the 35-39 controls it raised more false
alarms than the current text (2/2/1 vs 0/1/0), four of five on cases 35 and 36, and #29 then found three real weak
spots in those two fixtures. This page tests the held text after #29: the same sealed lane
(`evals/tools/run_reviews.sh`, claude-opus-5-5), the held text (`../2026-10-08-v22/SKILL-prreview-v22.md`, which is
this PR's `skills/pr-review/SKILL.md`) against main's pr-review, cases 35 and 36 only, scored with `evals/score.py`
after #28 (`--skill pr-review --only case-35,case-36`).

| measure (2 controls) | v2.2, runs 1/2/3 | current, runs 1/2/3 |
|---|---|---|
| false alarms (open P0/P1 on a control) | 0 / 0 / 0 | 0 / 0 / 0 |
| failure-list violations | 0 / 0 / 0 | 0 / 0 / 0 |
| list price per review, run 3 | $0.106 | $0.095 |

All twelve reports contain a findings block, and every verdict is merge or merge after fixes. The earlier gap
tracked the fixtures, not the text. On the fix-regression close-outs (37, 38), both texts caught the planted
regression in every gate run. So the change is neutral on detection, and it adds the explicit rule that an accepted
fix has its own diff read for a new defect.

Each run folder holds the reports, `prompts/` and `_meta/` (usage). `SHA256SUMS` covers every file here.
