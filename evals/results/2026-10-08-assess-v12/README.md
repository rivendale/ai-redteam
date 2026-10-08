# assess v1.2, 2026-10-08: three runs over the 36 assess cases

The `assess` skill text in `SKILL-assess-v12.md` (identical to `skills/assess/SKILL.md` on this branch) ran in the sealed
lane (`evals/tools/run_reviews.sh` with `CASES=evals/assess/cases NOTE=assess`, claude-opus-5-5), three runs per case.
Cases as merged through #55; scored with `evals/score_assess.py` as merged in #56.

## Results

| measure | run 1 | run 2 | run 3 |
|---|---|---|---|
| controls passed (8) | 8 | 8 | 8 |
| defect cases passed (28) | 28 | 28 | 27 |
| all cases (36) | 36 | 36 | 35 |
| list price per review | $0.096 | $0.060 | $0.058 |

Gate (`docs/SPEC-assess.md`, Measure): every control passes in 3 of 3 runs (yes); each failure-list rule's defect cases
pass in at least 5 of 6 runs (yes; the only miss is FL1, case 02 run 3, 5 of 6); at least 90% of case-runs pass
(107 of 108). **Passes.**

The one failure: case 02 run 3 marked "41 s to 19 s is a 2x speedup" CONFIRMED. The arithmetic holds; the defect is that
the speedup was measured on a toy workload, which that run's report did not carry into the claim status.

## How we got here (earlier runs, not published)

- v1 (first text): 22, 25 and 24 of 36. Most control failures were flaws in the controls or blunt scorer words, fixed in
  #50 and #53 (the reviewers were right each time). Defect-case failures were skill wording, fixed in v1.1.
- v1.1: 32 to 35 of 36 after #53. Case 07 exposed a schema gap: a claim the item disproves had no status, so #55 added
  REFUTED, and v1.2 tells the reviewer to use it.
- v1.2 first scoring: FL9 failed 6 of 6 because the scorer read a true star count as popularity offered as evidence;
  #56 fixed the scorer, and the same reports were rescored (no rerun).

## Vendors

Only Claude ran here. The skill's use in Codex, ChatGPT, Gemini and Grok is untested until a run per vendor exists.

Each run folder holds the reports, `prompts/` (exactly what each reviewer was sent) and `_meta/` (token usage).
`evals/tools/scan_secrets.py` found 0 hits. `SHA256SUMS` covers every file here.
