# Week-1021 lens texts against the baseline, 2026-10-22: aggregate counts only

One question: do the candidate lens texts (`pr-review` at main `77c4b98` minus its OSV paragraph, and the `redteam` lens text) catch more planted defects than the baseline texts they extend (`4165a3f`, `4b8fe51`)? This is a counts-only public record. It holds no case text, no report text and no hold-out content; the 18 hold-out cases and every review stay on the host that ran them. It was registered before the run (texts, matrix, reporting rules, input digests), and the scorer was not changed.

## Method

- 192 reviews: 48 cases, two texts (BASE, NEW), two repeats, model `claude-opus-5-5` through the sealed, tool-less lane (`evals/tools/run_reviews.sh`, `claude -p`, empty working directory). The 48 cases are the 26 development cases in this repository's `week-1021-dev-cases` sets (PR #92) plus 18 host-only hold-out cases and the 4 earlier host-only cases of the same sets.
- Cost: $41.62 in total (about $0.12 to $0.15 per `pr-review` review, $0.30 to $0.33 per `redteam` review). No prompt was reworded or retried.
- Scoring: `evals/score.py --profile auto`, unchanged. Recall counts planted defects found at any severity; a control is "flagged" when the report has any open Critical or High finding.

## What happened to the 192 reviews

| status | BASE | NEW |
|---|---|---|
| usable `claude-opus-5-5` report | 81 | 82 |
| safety-stopped, no usable report | 7 | 5 |
| completed by a fallback model | 8 | 9 |

- **12 reviews were stopped** by the safety classifier and have no usable report (supply chain: 5 development and 5 hold-out; pretext: 2). One host-only container-image case was stopped in all 4 of its reviews, so it has no result.
- **The pretext set (lens e) cannot be assessed in this lane.** After a stop, the CLI finished 17 of its 24 reviews with `claude-opus-4-8` instead (the behaviour PR #96 now detects and flags); only 5 clean `claude-opus-5-5` reviews exist for it. No claim is made about lens (e).

## Paired clean reviews

Only pairs where both texts produced a usable `claude-opus-5-5` report for the same case and repeat. n is reviews; recall is planted defects found; control columns are control reviews flagged (open Critical/High).

| set | n | recall BASE | recall NEW | controls flagged BASE | controls flagged NEW |
|---|---|---|---|---|---|
| supply chain, dev | 18 | 14/14 | 13/14 | 6/12 | 4/12 |
| supply chain, hold-out | 9 | 4/5 | 2/5 | 0/6 | 0/6 |
| runtime/trust, dev | 10 | 10/10 | 10/10 | 2/4 | 2/4 |
| runtime/trust, hold-out | 8 | 8/8 | 8/8 | 0/2 | 0/2 |
| secrets, dev | 8 | 10/10 | 10/10 | 4/4 | 4/4 |
| secrets, hold-out | 8 | 8/8 | 8/8 | 2/4 | 2/4 |
| exposure, dev | 8 | 8/8 | 8/8 | 2/4 | 2/4 |
| exposure, hold-out | 8 | 7/8 | 8/8 | 2/2 | 2/2 |
| pretext, dev | 2 | not assessable | not assessable | | |
| **all development** | 46 | 42/42 | 41/42 | 14/26 | 14/26 |
| **all hold-out** | 33 | 27/29 | 26/29 | 4/14 | 4/14 |

## Reading

1. **No measurable benefit from the new texts on these sets.** BASE already recalls 97% of planted defects outside the pretext set (69/71; NEW 67/71), so the sets cannot show an improvement. The one visible gap, supply-chain hold-out (4/5 against 2/5), rests on five defects; it is not a result.
2. **The control column overstates false alarms.** Several controls were flagged because the control itself carried a reviewer-directed instruction (a correct report rates it High and reports it) or because a reviewer found a real gap in the control's design. Those controls were corrected after the run (PR #92); the counts above are as run. The same reviews are not re-scored against the corrected controls.
3. **Not claimed:** no improvement of any lens, no regression of any lens, no result for lens (e), no result for the stopped container case. The sets need harder, subtler planted defects and distractors to separate a lens from the baseline, and the sealed lane's safety stops and silent fallback limit what it can measure for attack-shaped content.

Reviews, prompts and usage records stay on the host (`~/work/icf/_tools/w21-run/out/`); skill text hashes are in the registration record kept with them.
