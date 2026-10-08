# v2.2 gate, 2026-10-08: redteam (merged) and pr-review (held), three runs each

> **Update:** the held pr-review half was tested on #29's fixtures and merged in #30. See
> [`../2026-10-08-prreview-held`](../2026-10-08-prreview-held/README.md). This page is the gate as it was run; "held" below
> describes the state before #30.

v2.2 (`SKILL-redteam-v22.md`; `SKILL-prreview-v22.md` is kept as the text that was run, but its changes are NOT in this PR) against the current skills on main, in the
same sealed lane (`evals/tools/run_reviews.sh`: claude-opus-5-5, Claude Code 2.1.292, no tools, no MCP servers).
Cases 35 and 36 were re-run after #24 fixed their fixtures; the v2.2 reports for 35-39 are those re-runs. Scored with
`evals/score.py` on main after #28 (`--profile v2.2` for v2.2 redteam, `--profile auto` for the current skill).
Current-skill baselines for cases 1-34 are the published `../2026-10-07-repeat/full-current-*` and
`full-prreview-*`; the current-skill runs on 35-39 are new (`redteam-current-35-39-*`, `prreview-current-35-39-*`).

## redteam: all 39 cases (39 planted defects, 12 controls)

| measure | v2.2, runs 1/2/3 | current, runs 1/2/3 |
|---|---|---|
| recall at minimum severity | 37 / 37 / 38 | 37 / 37 / 37 |
| false alarms on controls | 1 / 0 / 0 | 0 / 3 / 0 |
| failure-list violations | 6 / 1 / 0 | 1 / 5 / 1 |
| extra Critical/High on defect cases (unscored) | 25 / 22 / 24 | 38 / 39 / 36 |

- On the five cases written for v2.2 (35-39, three controls), v2.2 raised 0 false alarms in every run; current 0 / 2 / 0.
- case-31 was cut off mid-response (no findings JSON) in v2.2 runs 1 and 2, as it was for every skill in the repeat
  runs; those count as misses and as an "unreadable report" violation.
- v2.2 run 1's remaining violations: one FL16 (a recorded answer disagrees with the severity), one false alarm on
  control case-27, and FL17 on case-37 where the coverage ledger named the patch's files but not the documents
  given (PR.md, review_findings.md, adjudication.md). That gap ("name every document you were given") is left for
  v2.3 so the gated text does not change after the gate.
- Coverage-ledger rule FL17 on cases 1-34: 0 in every run with #24's scorer (patches are accounted for by the files
  they change; unit names match as whole file names).

## pr-review (the v2.2 pr-review change is held, not merged)

Held at this gate; tested and merged later in #30 ([`../2026-10-08-prreview-held`](../2026-10-08-prreview-held/README.md)).

| measure | v2.2, runs 1/2/3 | current, runs 1/2/3 |
|---|---|---|
| code cases 06-13: recall (7 planted), false alarms (2 controls) | 7/7, 0 · 7/7, 0 · 7/7, 0 | 7/7, 0 · 7/7, 0 · 7/7, 0 |
| round-2 cases 24-32: recall (6 planted) | 4 / 4 / 6 | 4 / 6 / 6 |
| round-2 recall, case-31 cut-offs excluded | 4/4 · 4/4 · 6/6 | 4/4 · 6/6 · 6/6 |
| cases 37-38 (fix-regression close-outs): recall | 2/2 · 2/2 · 2/2 | 2/2 · 2/2 · 2/2 |
| cases 35-39: false alarms (3 controls), scorer after #28 | 2 / 2 / 1 | 0 / 1 / 0 |

Code cases are scored through `evals/tools/map_pr_severity.py` (P0-P3 to Critical-Low) with the redteam rules that
do not apply to a code review skipped; round-2 and 35-39 with `--skill pr-review`.

**Why the pr-review change is held.** v2.2 changed pr-review only in Step 6 and Step 7 (an accepted fix also needs
its own diff read for a new defect). Cases 37-39 are close-outs, which is exactly where Step 7 applies; there the
current text already catches both planted fix regressions in every run, so the change shows no benefit. On the
controls, v2.2 raised more false alarms (2/2/1 vs 0/1/0 after #28 removed a scoring artifact on case 39), four of
five on cases 35 and 36, where #29 later found three real weak spots in the fixture. Three runs cannot separate a
fixture effect from a text effect (one candidate mechanism: the new Step 7 sentence on AI-written fixes adding
flaws may prime stricter ratings). So the redteam change merges on its own evidence and the eight pr-review lines
wait for a re-run of 35 and 36 on #29's fixtures. The round-2 recall gap is case-31 cut off in two v2.2 runs.

`prompts/adversarial-review.md` (the plain prompt) is unchanged in this PR and still uses the v2.1 output format;
bringing it to schema 2.2 is a follow-up with its own eval.

## Cost (list price, from `_meta/*.usage.json`)

Like for like, cases 35-39, runs 1/2/3, per review (measured by the second reader on the committed usage files):

| skill | v2.2 | current |
|---|---|---|
| redteam | $0.200 / $0.140 / $0.131 | $0.156 / $0.095 / $0.110 |
| pr-review | $0.116 / $0.072 / $0.073 | $0.115 / $0.082 / $0.078 |

redteam v2.2 costs about 30% more per review on these cases (longer output: coverage, answers, reproduction);
pr-review is level. Over all 39 cases, redteam v2.2 run 3 averaged $0.145 and 74 s per review.

Each run folder holds the reports, `prompts/` (exactly what each reviewer was sent) and `_meta/` (usage).
Re-run summary: `python3 evals/tools/summarize_usage.py <run folder>`.

## Reproduce

    ONLY=$(seq -f 'case-%02g' 1 39 | paste -sd,)   # cases 40-49 were added after this gate (#22)
    python3 evals/score.py --skill redteam --profile v2.2 --only $ONLY --reports evals/results/2026-10-08-v22/redteam-v22-1
    python3 evals/score.py --skill pr-review --only case-24,case-25,case-26,case-27,case-31,case-32 \
        --reports evals/results/2026-10-08-v22/prreview-v22-1

`SHA256SUMS` covers every file in this folder.
