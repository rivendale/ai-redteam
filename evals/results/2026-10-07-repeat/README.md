# Repeat runs, 2026-10-07: three runs per skill on all 34 cases

Nick asked for repeat runs and a cost line. Each skill reviewed every case three times in the same sealed lane
(`evals/tools/run_reviews.sh`: claude-opus-5-5, Claude Code 2.1.292, no tools). Cases 31 and 32 were re-run after
#16 fixed their fixtures. Sources per run: redteam run 1 cases 01-23 are the reports in `../2026-10-07-pr9`
(current) and `../2026-10-07/reports-v1` (v1); cases 24-34 for every run, and all pr-review runs, are new runs made
for this page (`current-n*`, `v1-n*`, `prreview-p*`, then `*-q*` for cases 31-32 after #16). Scored with `evals/score.py` after #15, #16 and #17. Current redteam is the text in
`SKILL-redteam-current.md` (9c3ad5b2cf1e, as merged in #9); v1 is `../2026-10-07/SKILL-v1.md`.

## Results

**case-31 was blocked, not reviewed, in 6 of 9 runs** (current 3/3, v1 runs 1 and 3, pr-review run 1): the response
stopped mid-way, apparently by a safety filter, leaving no usable findings JSON (277-1160 bytes). Those runs count as misses in
the scorer's totals below; the second table separates them.

| measure (34 cases, 37 planted defects, 9 controls) | current redteam, runs 1/2/3 | v1, runs 1/2/3 |
|---|---|---|
| recall at minimum severity | 35 / 35 / 35 | 29 / 29 / 32 |
| false alarms on controls | 0 / 1 / 0 | 1 / 2 / 2 |
| failure-list violations | 1 / 4 / 1 | 12 / 10 / 9 |
| extra Critical/High (unscored) | 36 / 37 / 34 | 57 / 58 / 56 |

| unblocked cases only (35 planted defects) | current redteam | v1 |
|---|---|---|
| recall at minimum severity | 35 / 35 / 35 | 29 / 27 / 32 |

pr-review: original code cases 06-13, recall 7/7 in all three runs, 0 false alarms on 2 controls; its six round-2
cases (`--skill pr-review`), recall 4/6, 6/6, 6/6 and false alarms 0, 1, 0; run 1's 4/6 is the blocked case-31.

## What the repeat runs show

- **Current redteam's detection is stable:** the same 35 of 37 in every run. Both misses each time are case-31.
- **case-31 (an attack hidden in a tool description) was cut off mid-response in 6 of 9 runs** across the three
  skills (current 3/3, v1 2/3, pr-review 1/3), apparently by a safety filter; the reviewer then declined to
  regenerate. These count as misses. Reviews of attack-like code can come back incomplete; re-run or review by hand.
- **Run 2 shows real lapses in current redteam:** case-04 kept two refuted candidates in `findings` labeled
  CONFIRMED, and control case-22 got a High PROBABLE. The v2.2 spec (#18) targets both.
- On unblocked cases current redteam caught 35/35 in every run; v1 caught 29, 27 and 32. Violations do not overlap
  (current 1/4/1, v1 12/10/9). False alarms (0/1/0 vs 1/2/2) are too few to separate.

## Cost (list-price equivalent from `--output-format json`)

current redteam $0.141 per review (79 reviews measured), v1 $0.116, pr-review $0.109; about 52-55 s per review.
On a subscription this is usage, not a bill. Runs 1 (from earlier PRs) predate usage capture. The per-review usage
files are in `usage/<run>/`; they hold 85/85/48 reviews per skill, of which six per skill are the superseded pre-#16
case-31/32 runs, excluded from the cost above (79/79/42); re-derive with `python3` over them (total_cost_usd and duration_ms per file).

## Limits

Three runs, one model and vendor. The eval author spot-checked extras on earlier runs only. Reports are committed;
prompts and usage files for runs 2-3 are in the run directories of the operator, not here.

**Correction, 2026-10-08 (scorer #51, best-assignment matching).** Rescored with the same reports and cases, the matcher change alone moves only recall and found-at-any-severity; false alarms and violations do not change. v1 recall rises by 1 in runs 1 and 2 (run 3 unchanged), so v1 is 30 / 30 / 32 on the table's terms. The moved cases are 14 (run 1) and 34 (run 2), neither of them the blocked case-31, so the unblocked-cases row for v1 rises to 30 / 28 / 32. The current redteam runs and pr-review do not move.
