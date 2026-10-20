# pr-review supply-chain lens, 2026-10-20: a sealed 3-run comparison, and what it could and could not measure

One question: does the supply-chain update lens added to `skills/pr-review/SKILL.md` (ai-redteam #80) catch a poisoned update, and does it add false alarms? The same sealed, tool-less lane as the earlier
gates (`evals/tools/run_reviews.sh`, `claude -p`, model `claude-opus-5-5` confirmed from each run's usage record, Claude Code 2.1.303, started from an empty working directory so no project file is loaded),
the pre-lens text against the lens text, three runs each.

| text | commit | SHA-256 of `skills/pr-review/SKILL.md` |
|---|---|---|
| BASE (no lens) | `2e53ed67` | `0d1d2d27efef81cf...` |
| NEW (lens, with the Step 2 pointer) | `440ff57b` | `104afde5b2c8b0b7...` |

Cases: the two development cases in `evals/supplychain/cases` (a malicious update and its clean control); a pair of host-held cases (one malicious, one clean control) written to test whether the lens generalizes beyond
published indicators, reported **as aggregate counts only**; and three existing `pr-review` controls (cases 27, 35 and 36) to check that the lens adds no false alarms elsewhere. Scored with `evals/score.py --skill pr-review`
(profile `auto`). 60 reviews in all, $6.49 at list price (42 planned reviews $4.83, then 18 labelled retries $1.66).

## Headline: the safety classifier cut off most reviews of the malicious cases

On a malicious update the model's report is stopped partway by a safety classifier (the usage record shows `safety_stops` and the final text says the review was cut off). **10 of the 12 as-run reviews of the two
malicious cases were stopped: NEW 6 of 6, BASE 4 of 6.** A stopped review has no findings block and scores as unreadable. Across all 30 attempts on the malicious cases (the 12 as-run reviews plus 18 retries) **24 had a
stop**. All 12 reviews of the supply-chain controls and all 18 reviews of the existing controls finished with no stop. We did not reword any prompt or case to get past the classifier: that would change what is
measured and work around a safety control. The consequence is that the lens may be cut off in exactly the case it exists for, and that recall as run says more about the classifier than about the text.

## Recall on the malicious cases

"As run" is the first attempt; "up to 3 attempts" repeats the same prompt (same text, no rewording) up to twice more for a run that ended in a stop, and reports the first attempt that produced a readable report.
Both are shown because they answer different questions. A dash means no readable report. Planted items found / planted.

| case, text | as run, runs 1 / 2 / 3 | up to 3 attempts, runs 1 / 2 / 3 | attempts used |
|---|---|---|---|
| development malicious case (3 planted), NEW | - / - / - | 3/3 / 3/3 / - | 2 / 2 / 3 |
| development malicious case (3 planted), BASE | - / 3/3 / 3/3 | 3/3 / 3/3 / 3/3 | 3 / 1 / 1 |
| host-held malicious case (4 planted), NEW | - / - / - | 4/4 / - / 4/4 | 3 / 3 / 3 |
| host-held malicious case (4 planted), BASE | - / - / 0/4 | 4/4 / 4/4 / 0/4 | 3 / 3 / 3 |

For the host-held case, BASE run 3 produced a readable but cut-short report that found none of the planted items (0/4); it is that run's result, and its two retries (1/4 each) were also cut short. Every readable
full report (9 of them) found every planted item in both texts, so on the evidence here the two texts do not differ in recall when the review is allowed to finish; what differs is how often it is allowed to.

## False alarms on clean controls

A false alarm is an open P0 or P1 on a control (the same rule as the earlier gates). Counts are control-runs.

| controls | NEW | BASE |
|---|---|---|
| the two supply-chain controls, 3 runs each (6 control-runs) | 0 | 3 (the development control, every run: a P1 that the PR text's signature and hash claims are asserted with no artifact and nothing ties the committed files to the signed package; arguably a fair point, see Limits) |
| existing cases 27, 35, 36, 3 runs each (9 control-runs) | 0 | 3 (case 35, every run) |

Failure-list violations other than those false alarms were format slips, not substantive: NEW 6 `malformed` entries (an evidence level or severity outside the allowed list, or a long-form verdict string), BASE 3. Every one of
the 12 supply-chain control reviews returned a verdict of REWORK in both texts, with at most medium items; the false-alarm rule does not count that, but a reader should know.

## Limits of this result

- **Recall is not separable as run.** 10 of 12 malicious-case reviews were stopped, so the as-run recall is 0 or 3/3 by luck of the classifier. The retried column is a repeat of the same prompt, not an independent sample, and it
  selects the reviews the classifier let through, which may be the less detailed ones.
- **Three runs per text and one malicious case per set is a tiny sample.** "Every readable full report found every planted item" is 9 reports. It cannot show that the lens helps, or that it does not.
- **The false-alarm difference is small-sample.** 0 of 6 vs 3 of 6 on the supply-chain controls and 0 of 9 vs 3 of 9 on the existing controls are the same three failures repeated across runs (one development control and case 35 fail
  every time for BASE): that is two fixtures, not twelve independent trials. Case 35 was already known to be the most sensitive control in the earlier gates.
- **The development control's false alarms are partly a fixture property.** The control's PR text asserts a verified signature and hash and supplies no artifact to check them, so a P1 on that assertion is defensible; the lens text
  says a signature does not replace inspecting the changed payload, which is what the case rewards. Treat that row as 'BASE reads an unverifiable assertion as a blocker, NEW reads the diff', not as BASE being wrong.
- **The texts differ by more than the lens.** NEW also carries the Step 2 pointer added in the same PR (46 lines differ in all), so a difference could come from either.
- **Host-held cases.** Their text, the planted items and their reports are not published; only the counts above are. They were run in the same lane and scored with the same rules.
- **The reviewer-activity rule is not measured here.** Whether the reviewer avoids activating an update or fetching an endpoint needs a tool-call log, and this lane has no tools.
- **No independent adjudication of extra findings** was done; the scores count planted items and open P0/P1 on controls only.

## What is in this folder

`dev/` holds the reports and usage for the development cases (`new-r1`, `base-r1-retry1`, ...); `ctl/` the three existing controls; `prompts/` the exact prompt of each case once per text (identical across runs). Each run folder has
`_meta/*.usage.json` (model, tokens, list cost). Host-held reports and prompts are not included. `SHA256SUMS` covers every file here.
