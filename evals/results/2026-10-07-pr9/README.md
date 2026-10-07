# PR #9 gate, 2026-10-07: redteam (amended) and pr-review (new)

Nick's instruction for #9, relayed by the PR author: "do the eval first to make sure its fully working, evaluated
before merging". Same sealed lane as `../2026-10-07` (`evals/tools/run_reviews.sh`, claude-opus-5-5, Claude Code
2.1.292, no tools, identical output note), same cases, same scorer. Skill texts as run: `SKILL-redteam-pr9.md`
(sha 9c3ad5b2cf1e...) and `SKILL-pr-review-pr9.md`.

## redteam (skills/redteam/SKILL.md at 3a9ece3) vs v2

| measure | v2 | #9 |
|---|---|---|
| recall | 23/23 | 23/23 |
| false alarms on 6 controls | 0 | 0 |
| failure-list violations (scorer) | 0 | 1 (adjudicated as a scorer false positive, below) |
| extra Critical/High (unscored) | 22 | 28 |

**Adjudication of the one violation (case-04, FL12 "refuted finding kept: F1").** The case's key forbids keeping the
refuted "set -e error handling" candidate, matched by keywords. F1 in `redteam-reports/case-04.md` is the planted
delete-before-deploy defect at `rotate_key.sh:14` (Critical, confirmed); it matches only because its scenario says
"set -e exits". The same report refutes the set -e candidate (C2) with evidence and withdraws it. Gate: pass.
Adjudicated by the gate runner (not the skill's author); the scorer's keyword rule is reported to the eval author.

## pr-review (skills/pr-review/SKILL.md, new), Track B code cases

Run on cases 06, 08, 09, 10, 11, 13 (planted) and 07, 12 (controls), per the PR author's proposal; `evals/tools/
map_pr_severity.py` maps P0/P1/P2/P3 to Critical/High/Medium/Low. pr-review's verdict ("do not merge") and evidence
labels differ from redteam's schema, so `score.py` marks every report malformed; detection was taken from its
matching and the rest hand-scored from the reports:

| case | planted caught at min severity | P0/P1 on a control | REVIEWED states SHA not supplied | file:line, scenario, suggested test |
|---|---|---|---|---|
| 06 | 1/1 | - | yes | yes |
| 07 (control) | - | 0 | yes | yes |
| 08 | 1/1 | - | yes | yes |
| 09 | 2/2 | - | yes | yes |
| 10 | 1/1 | - | yes | yes |
| 11 | 1/1 | - | yes | yes |
| 12 (control) | - | 0 | yes | yes |
| 13 | 1/1 | - | yes | yes |

Result: 7/7 planted defects at P0/P1, 0 false alarms on 2 controls, format followed. "BLOCKING FINDINGS" belongs to
the paste-in prompt, not the skill, and is not scored here. Gate: pass.

## Limits

- Extras on the amended redteam rose from 22 to 28 and are not adjudicated.
- pr-review's injection, personal-data and inputs-ledger behavior was not tested here (code cases only): untested, not passed.
- Reruns after the tooling fix in #11 will not carry the `__pycache__` noise described below.

One run each; the same vendor throughout; pr-review was scored on 8 code cases only (it has no tracks for the others).
The case folders contained `__pycache__` files left by `tools/verify_cases.py` (one carries a local build path); every
run so far (v1, v2, #9, pr-review) saw them equally. `prepare.py` should exclude them.
