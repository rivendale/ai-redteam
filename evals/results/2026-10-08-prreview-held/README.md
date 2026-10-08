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

## Limits of this result

- **Zero is not proof of no effect.** 0 / 0 / 0 is 6 control-runs per skill (2 controls, 3 runs). That cannot exclude a small
  difference in false alarms between the two texts.
- **The fixture claim rests on a before-and-after.** The support for "the earlier gap tracked the fixtures" is the same pair of
  texts on cases 35-39. On the old fixtures they raised 5 vs 1 false alarms (v2.2 vs current) over 9 control-runs each
  (3 controls, 3 runs; `../2026-10-08-v22`). On #29's fixtures they raised 0 vs 0.
- **"Neutral on detection" is not "helps".** It rests on the close-outs 37 and 38 and on code cases 06-13. Current pr-review is
  already at the ceiling there (every planted defect caught in every run). So this eval cannot show a benefit of the new rule;
  the rule is merged for its reasoning, not for a measured gain.

Each run folder holds the reports, `prompts/` and `_meta/` (usage). `SHA256SUMS` covers every file here.
