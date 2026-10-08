# v2.2 gate, 2026-10-08: redteam and pr-review, three runs each

v2.2 (`SKILL-redteam-v22.md`, `SKILL-prreview-v22.md`, as in this PR) against the current skills on main, in the
same sealed lane (`evals/tools/run_reviews.sh`: claude-opus-5-5, Claude Code 2.1.292, no tools, no MCP servers).
Cases 35 and 36 were re-run after #24 fixed their fixtures; the v2.2 reports for 35-39 are those re-runs. Scored with
`evals/score.py` on main after #24 (`--profile v2.2` for v2.2 redteam, `--profile auto` for the current skill).
Current-skill baselines for cases 1-34 are the published `../2026-10-07-repeat/full-current-*` and
`full-prreview-*`; the current-skill runs on 35-39 are new (`redteam-current-35-39-*`, `prreview-current-35-39-*`).

## redteam: all 39 cases (39 planted defects, 12 controls)

| measure | v2.2, runs 1/2/3 | current, runs 1/2/3 |
|---|---|---|
| recall at minimum severity | 37 / 37 / 38 | 37 / 37 / 37 |
| false alarms on controls | 1 / 0 / 0 | 0 / 3 / 0 |
| failure-list violations | 6 / 1 / 0 | 1 / 5 / 1 |

- On the five cases written for v2.2 (35-39, three controls), v2.2 raised 0 false alarms in every run; current 0 / 2 / 0.
- case-31 was cut off mid-response (no findings JSON) in v2.2 runs 1 and 2, as it was for every skill in the repeat
  runs; those count as misses and as an "unreadable report" violation.
- v2.2 run 1's remaining violations: one FL16 (a recorded answer disagrees with the severity), one false alarm on
  control case-27, and FL17 on case-38 where the coverage ledger named the patch's files but not the documents
  given (PR.md, review_findings.md, adjudication.md). That gap ("name every document you were given") is left for
  v2.3 so the gated text does not change after the gate.
- Coverage-ledger rule FL17 on cases 1-34: 0 in every run with #24's scorer (patches are accounted for by the files
  they change; unit names match as whole file names).

## pr-review

| measure | v2.2, runs 1/2/3 | current, runs 1/2/3 |
|---|---|---|
| code cases 06-13: recall (7 planted), false alarms (2 controls) | 7/7, 0 · 7/7, 0 · 7/7, 0 | 7/7, 0 · 7/7, 0 · 7/7, 0 |
| round-2 cases 24-32: recall (6 planted) | 4 / 4 / 6 | 4 / 6 / 6 |
| round-2 recall, case-31 cut-offs excluded | 4/4 · 4/4 · 6/6 | 4/4 · 6/6 · 6/6 |
| cases 35-39: false alarms (3 controls) | 3 / 2 / 1 | 1 / 1 / 1 |

Code cases are scored through `evals/tools/map_pr_severity.py` (P0-P3 to Critical-Low) with the redteam rules that
do not apply to a code review skipped; round-2 and 35-39 with `--skill pr-review`.

**Read this table with the diff in mind.** v2.2 changes pr-review only in Step 6 and Step 7 (how an accepted fix is
verified after the review: the fix's own diff is read for a new defect). The eval stops at the review, before
adjudication, so no difference here is caused by the text change. The round-2 recall gap is case-31 cut off in two
v2.2 runs; the false-alarm gap on 35-39 is run-to-run variation on the same instructions: case-36's P1 (the order is
cancelled before the audit write, so a failed write leaves no record) and one run that listed the already-fixed bug
in case-39 as open. Both are worth a v2.3 case or rule; neither is a regression from this text.

## Reproduce

    ONLY=$(seq -f 'case-%02g' 1 39 | paste -sd,)   # cases 40-49 were added after this gate (#22)
    python3 evals/score.py --skill redteam --profile v2.2 --only $ONLY --reports evals/results/2026-10-08-v22/redteam-v22-1
    python3 evals/score.py --skill pr-review --only case-24,case-25,case-26,case-27,case-31,case-32 \
        --reports evals/results/2026-10-08-v22/prreview-v22-1

`SHA256SUMS` covers every file in this folder.
