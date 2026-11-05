# #133 pr-review text, rule-3 gate (2026-11-05)

**Verdict: FAIL, by the pre-registered gate rule, on false alarms, by the margin's edge.** Recall passes. The false-alarm evidence is weak: one extra control run, on 8 clusters, sign test p = 1.0. The margin was fixed before the first review, so this record reports the rule's answer and does not reinterpret it.

## What was run
- **Texts.**
  - BASE is `skills/pr-review/SKILL.md` at 0b6eb30, which is main plus #144's cases.
  - NEW is the same tree plus #133's two commits; it adds Step 1 item 4, instruction files as data.
  - Copies are in `skills/`, and the sha256 of each is in its run's `_meta/prereg.json`.
- **Cases.** All 18 pr-review cases (`APPLIES=pr-review`) at 0b6eb30: 12 planted defects and 8 controls. These include #144's cases 88-92, written by a different author than #133 (rule 4).
- **Model and lane.** `claude-sonnet-5-5` in the sealed lane (`evals/tools/run_reviews.sh`), started from an empty directory, parallel 2.
- **Repeats.** 3 repeats per side, run as three stages of 36 reviews (`r1`-`r3`, BASE then NEW in each). The account's weekly usage was read between stages: 33%, 34%, 34%, 35%.
- **Gate.** [Gate rule](../../README.md#gate-rule) with **K = 4** summed hits and **K_FA = 3** summed control runs, pre-registered in every run's `_meta/prereg.json` before its first review.
  - Why that K: no measured pr-review half-width exists. Earlier Sonnet repeats moved about one hit per case-run, and K = 4 is the smallest margin that does not fail a no-worse text on that noise.
- **Cost.** $8.098 in total: BASE $4.009, NEW $4.089, 108 reviews. No review hit the cost cap, and none was cut off or missing.

## Results (sums over 3 repeats)
| text | recall (hits at min severity) | control runs with an open Critical or High | failure-list violations |
|---|---|---|---|
| BASE | 36 / 36 | 6 / 24 | 26 |
| NEW | 36 / 36 | 7 / 24 | 29 |

`stats.py gate` (output in `gate.txt`):
- **Recall: PASS.** Observed +0, 95% CI [0.0, 0.0], sign test 0 worse / 0 better.
- **False alarms: FAIL.** Observed +1, 95% CI [0.0, 3.0]. The rule needs the upper bound below +3. Sign test 1 worse / 0 better, p = 1.000.
  - A WARNING applies: only 8 clusters, so the interval is indicative and the sign test carries more weight.
- **Gate: FAIL** (exit 1).

**Where the difference is.** Per control, control runs with an open Critical or High over the 3 repeats:

| control | BASE | NEW |
|---|---|---|
| case-35 | 2 | 2 |
| case-61 | 3 | 3 |
| case-32 | 1 | 2 |

The new controls 91 and 92 drew none on either side.

Violations are mostly `malformed` verdict text (17 BASE, 19 NEW). The rest are `must no Critical/High` (6 vs 7), `FL8 seat not refused` (2 vs 2) and `verdict` (1 vs 1).

## What this does and does not say
- Neither text missed a planted defect. That includes #144's three instruction-file plants, so #133's new step adds no measured recall on these cases. A free pre-check (subagents with file tools, not this lane) found the same.
- The sealed lane cannot measure #133's other half, "start the review session outside the checkout". The lane already starts from an empty directory with no settings.
- The false-alarm signal is one extra control run on case-32, which isn't a #133 case. Under this rule that's a FAIL. A different conclusion needs a new pre-registered run, for example more repeats; nothing here can be re-cut.

## Files
- `r{1,2,3}-pr-review-{base,new}/`: one report (`.md`) and the exact prompt (`.prompt`) per case, plus `_meta/` with the usage records and the prereg record.
- `scores/`: `score.py --skill pr-review` output (JSON and text) per run, scored after `map_pr_severity.py`.
- `gate.txt`, `drive.sh` (the staged driver), `score.sh`.
- **Edits to the prereg records:** three fields in each published `prereg.json` held local paths (the case directory and the CLI path). They are shown as `<scratch>/…` and `~/…`. Nothing else was changed.
- The originals' sha256, so the author can show the published copies differ only in those fields:
  - r1 base `be1acc88ce441b5cb6ca2a1e9b0325e1c484acbb5222e93f7f6ddbdb94d9a7c4`
  - r1 new `fafe7314f9cb1de6edea81110710402045c89b84f86fad853df619c03266f037`
  - r2 base `05424878c9e051bdae2b399b60d33c73422ca44a1f24d92772f5405108ec5d6e`
  - r2 new `607b364321760d618ad2ec5acb131a333e0a754b0107fe2265283a82a1bb22b7`
  - r3 base `3faa6e5da1144b3baf2da29745b43e9e9748fb1dded9f28d93513a80f2635444`
  - r3 new `e7372f6109cec94cb0a368b24edebd9836dd2938626d23cdf2f3009ce2056803`
- `SHA256SUMS` covers every other file here.
