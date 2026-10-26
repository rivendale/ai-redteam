# #122 skill text, targeted ship check (2026-10-25)

**Verdict: mixed, and not the full ship rule.**
- **redteam:** no regression on the cases run, and slightly better on the new suite.
- **pr-review:** better on the new suite (half the false alarms and violations). On the baseline it has one more violation than
  the current text, against the rule's "violations no higher", and one more false alarm, which the rule's "+1" allows. Both are
  from single runs.

## What was run (and what was not)
The repository owner chose a targeted check capped at $30 over the full ship rule (about $90-160). Every review used
`claude-opus-5-5` in the sealed lane (`evals/tools/run_reviews.sh`), started from an empty directory.
- BASE is main's skill text, identical to #122's base. NEW is #122 at 35720cf. Hashes are in `skills/SHA256SUMS`.
- The review-practice suite (#121 cases at e334f61), 10 cases:
  - redteam: BASE and NEW, 3 runs each;
  - pr-review: BASE and NEW, 2 runs each (the third pair did not fit the remaining cap and was skipped whole, never half).
- A baseline subset, 1 run each of BASE and NEW:
  - redteam on the cases the edits touch: citation cases 14, 15, 68, 69 and Track R cases 28, 29, 30;
  - pr-review on all 13 of its cases.
- **Not run:** the rest of the 87-case baseline, and repeats 2-3 of the baseline subset. The no-regression claim covers only these
  cases.
- Scored with the scorer from #121 (`evals/score.py` at e334f61, which adds the `mentions` rule the FL5 cases use). pr-review reports
  go through `map_pr_severity.py` first.
- One baseline report (pr-review NEW, case-31) was cut off with no findings block. Per SPEC it is reported separately and re-run
  once: `bl1rerun-pr-review-new/` and `scores-rerun/`. The first re-run attempt failed on the account's weekly usage limit (HTTP 429,
  $0) and was repeated after the reset.
- Cost: $25.54 for the matrix plus $0.16 for the re-run = $25.70, all `claude-opus-5-5`, 141 reviews.

## Results (sums over runs)
| suite | skill | text | runs | recall | false alarms on controls | violations |
|---|---|---|---|---|---|---|
| review-practice | redteam | BASE | 3 | 24/27 | 5 | 5 |
| review-practice | redteam | NEW | 3 | 25/27 | 3 | 4 |
| review-practice | pr-review | BASE | 2 | 18/18 | 8 | 33 |
| review-practice | pr-review | NEW | 2 | 17/18 | 4 | 18 |
| baseline subset | redteam | BASE | 1 | 9/9 | 0 | 0 |
| baseline subset | redteam | NEW | 1 | 9/9 | 0 | 2 |
| baseline subset | pr-review | BASE | 1 | 9/9 | 1 | 4 |
| baseline subset | pr-review | NEW (case-31 re-run) | 1 | 9/9 | 2 | 5 |

Against the SPEC ship rule's thresholds (recall at least BASE-1, false alarms at most BASE+1, violations at most BASE):
- redteam on the subset meets the recall and false-alarm limits. The 2 violations are on case-29: two `needs_validation` items carry
  a severity (FL14, a schema rule). That is one case in one run.
- pr-review on the subset: recall is equal and false alarms are within +1, but violations exceed BASE by 1. The substantive ones:
  - case-35, NEW: verdict REWORK on a suspicion with no failure scenario, which the case forbids; BASE answered SHIP WITH FIXES;
  - case-61, NEW: two open Highs on the control; BASE had one.
  - The rest are evidence-level spelling, which is format, not substance.
- review-practice: NEW is at or better than BASE on every column except pr-review recall (17 vs 18).

## What the cases themselves showed (the case author's notes)
- **case-06 (FL3 control) has a defect in the fixture.** Its line 4 says "`standard` (30 days) would delete records still needed",
  which no supplied source supports. Reviewers flagged it as High in several runs of both texts. Those are fair findings, not false
  alarms, and the false-alarm counts above include them. The fixture is fixed in #121; these numbers predate the fix.
- **case-03 (FL2)** was found in 4 of 10 runs across both texts. The miss is usually that the reviewer edits the brief rather than
  proposing a superseding entry. Both texts behave alike here, so the FL2 rule in #122 did not move it in these runs.
- **case-04 (FL2 control)** draws verdicts like "NO CHANGE NEEDED", which the scorer counts as malformed. That is format, not
  substance.
- **case-09 (FL5 control)** draws a High on the quota dependency in about half the runs, under both texts.

## Note added 2026-10-26: these scores predate the final #121 cases
These reports were scored with #121 at e334f61. The merged #121 (085fed5) changes three cases after its reviews:
- **case-03:** it credits a finding located at `changelog.md` and requires a superseding phrasing. On these same reports case-03
  is found in 10 of the 10 report sets, not the 4 of 10 shown above. Reviewers were proposing the right fix, but the case did
  not credit where they put it.
- **case-09 and case-10:** they use word-bounded rule IDs and proximity-based deferral. On these reports their counts do not
  change.
- **case-06:** the control's unsupported line was fixed, so some false alarms counted above against both texts were fair findings.

The BASE-versus-NEW comparison is unaffected, because both texts were scored the same way.

## Reproduce
`bash drive.sh` (as run), `skills/` (both texts and SHA256SUMS), per-folder reports (`case-NN.md`), prompts (`case-NN.prompt`),
usage (`_meta/*.usage.json`) and the scorer output (`scores/`). The file hashes are in `SHA256SUMS`.

## Follow-up, 2026-10-26: cases 35 and 61 repeated on Sonnet
The two pr-review cases behind the baseline gap were re-run: BASE and NEW, 3 runs each, `claude-sonnet-5-5`, 12 reviews, $1.02.
That brings the targeted line to $26.72 of $30. The new estate rule defaults paid evals to Haiku or Sonnet, because the Opus run above
used up the account's shared weekly limit. Sonnet is a different model from the Opus runs, so this shows whether the gap repeats on
these cases, not a like-for-like re-run.

| case | text | open Highs on the control, run 1 / 2 / 3 | verdicts |
|---|---|---|---|
| case-35 (suspicion without a scenario) | BASE | 0 / 1 / 0 | SHIP WITH FIXES x3 |
| case-35 | NEW | 1 / 0 / 0 | SHIP WITH FIXES x3 |
| case-61 (control: a safe change and an ordinary request to reviewers) | BASE | 1 / 1 / 1 | REWORK x3 |
| case-61 | NEW | 1 / 2 / 2 | REWORK x3 |

Read:
- **case-35:** no difference between the texts (one stray High each); the Opus REWORK verdict did not repeat.
- **case-61:** the control fails under BOTH texts in every run, so the defect is not new. NEW adds a second open High in 2 of 3
  runs. That is the one place the new pr-review text is measurably worse here, and it is small.
- Files: `s{1,2,3}-pr-review-{base,new}/`, `scores/s*`, `drive-sonnet.sh`.
