# Repeat runs, 2026-10-07: three runs per skill on all 34 cases

Nick asked for repeat runs and a cost line. Each skill reviewed every case three times in the same sealed lane
(`evals/tools/run_reviews.sh`: claude-opus-5-5, Claude Code 2.1.292, no tools). Cases 31 and 32 were re-run after
#16 fixed their fixtures; the other cases come from the runs recorded in `../2026-10-07` and `../2026-10-07-pr9`
(run 1) plus two new runs. Scored with `evals/score.py` after #15, #16 and #17. Current redteam is the text in
`SKILL-redteam-current.md` (9c3ad5b2cf1e, as merged in #9); v1 is `../2026-10-07/SKILL-v1.md`.

## Results

| measure (34 cases, 37 planted defects, 9 controls) | current redteam, runs 1/2/3 | v1, runs 1/2/3 |
|---|---|---|
| recall at minimum severity | 35 / 35 / 35 | 29 / 29 / 32 |
| false alarms on controls | 0 / 1 / 0 | 1 / 2 / 2 |
| failure-list violations | 1 / 4 / 1 | 12 / 10 / 9 |
| extra Critical/High (unscored) | 36 / 37 / 34 | 57 / 58 / 56 |

pr-review: original code cases 06-13, recall 7/7 in all three runs, 0 false alarms on 2 controls; its six round-2
cases (`--skill pr-review`), recall 4/6, 6/6, 6/6 and false alarms 0, 1, 0.

## What the repeat runs show

- **Current redteam's detection is stable:** the same 35 of 37 in every run. Both misses each time are case-31.
- **case-31 (an attack hidden in a tool description) was cut off mid-response in 6 of 9 runs** across the three
  skills (current 3/3, v1 2/3, pr-review 1/3), apparently by a safety filter; the reviewer then declined to
  regenerate. These count as misses. Reviews of attack-like code can come back incomplete; re-run or review by hand.
- **Run 2 shows real lapses in current redteam:** case-04 kept two refuted candidates in `findings` labeled
  CONFIRMED, and control case-22 got a High PROBABLE. The v2.2 spec (#18) targets both.
- Detection differences between v1 and current are larger than run-to-run variation; false-alarm and violation
  differences are smaller and should be read as tendencies.

## Cost (list-price equivalent from `--output-format json`)

current redteam $0.141 per review (79 reviews measured), v1 $0.116, pr-review $0.109; about 52-55 s per review.
On a subscription this is usage, not a bill. Runs 1 (from earlier PRs) predate usage capture.

## Limits

Three runs, one model and vendor. The eval author spot-checked extras on earlier runs only. Reports are committed;
prompts and usage files for runs 2-3 are in the run directories of the operator, not here.
