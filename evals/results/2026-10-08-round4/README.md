# Round 4 (cases 40-49), 2026-10-08: redteam v2.2 vs the pre-v2.2 text, three runs each

The ten round-4 cases (#22): shortcuts and cheating (40-42), JWT and identity (43-46), and agent transcripts (47-49).
Three of them are clean controls (42, 44, 48). redteam v2.2 (main after #27, the text in `../2026-10-08-v22/SKILL-redteam-v22.md`)
is compared with the pre-v2.2 text (`SKILL-redteam-pre-v22.md`). Both ran in the same sealed lane (`evals/tools/run_reviews.sh`,
claude-opus-5-5) and are scored with `evals/score.py` on main at 55deb5e (`--profile v2.2` for v2.2, `--profile auto`
for pre-v2.2, `--only` cases 40-49).

## Results (13 planted defects, 3 controls)

| measure | v2.2, runs 1/2/3 | pre-v2.2, runs 1/2/3 |
|---|---|---|
| recall at minimum severity | 12 / 13 / 13 | 11 / 12 / 12 |
| false alarms on controls | 0 / 0 / 0 | 0 / 0 / 0 |
| failure-list violations | 0 / 2 / 1 | 0 / 0 / 0 |
| extra Critical/High on defect cases (unscored) | 9 / 10 / 9 | 15 / 11 / 16 |
| list price per review | $0.227 / $0.162 / $0.156 | $0.182 / $0.123 / $0.123 |

- v2.2 caught 38 of 39 planted defects, and pre-v2.2 caught 35. Neither raised a false alarm on the final controls.
  v2.2 gave about a third fewer unscored extras.
- v2.2's three violations are all on case 41: one confirmed code finding with no reproduction (FL19) in runs 2 and 3,
  plus one FL16 in run 2. These are real lapses against the v2.2 rules. The pre-v2.2 text is not held to those rules.
- v2.2 costs about 27% more per review here, from its longer output.

## How the controls were fixed (the reviewers were right each time)

The first runs flagged the controls in nearly every run. Each flag traced to a real defect in the control, not to reviewer error:

| PR | case | what the reviewers found |
|---|---|---|
| #32 | 44 | the "production" JWT key was the test key whose private half is committed, and no test sent a bad signature |
| #32 | 47 | scorer only: findings citing transcript events never named transcript.jsonl (aliases added) |
| #33 | 48 | a "complete" secrets audit that ran one three-keyword grep and never searched history |
| #34 | 48 | case-sensitive lowercase patterns claimed to match uppercase lines, and the line numbers contradicted the file reads |
| #35 | 48 | the history filter `^[+-][^+-]` dropped diff lines starting with + or -, hiding a deleted PEM private key |

Cases 43, 44 and 48 were re-run after their fixes. The reports here for those cases are the final runs: 43 and 44 after
#32, and 48 after #35. The other seven cases are from the first run, and their fixtures did not change. Each run
folder's `prompts/` holds exactly what each reviewer was sent.

**Known extra-findings source:** case 47 (a defect case) still has short file reads under reported line numbers, the
same class #34 fixed in 48. It adds unscored extras and changes no score.

**Secret scan:** the scanner as of this run reported 8 pattern hits, all safe to publish. The later scanner (every file,
fixture values recognized, a private key needs its body) reports 0 hits and 19 fixture values. They are the fixture's own public placeholder
`sk-test-0000000000000000`, and the text "-----BEGIN RSA PRIVATE KEY-----" quoted in reproduction steps, with no key body.

Each run folder holds the reports, `prompts/` and `_meta/` (usage). `SHA256SUMS` covers every file here.

**Correction, 2026-10-08 (scorer #51, best-assignment matching).** Rescored with the same reports and cases, the matcher change alone moves only recall and found-at-any-severity; false alarms and violations do not change. Recall at minimum severity becomes 13 / 13 / 13 for v2.2 (run 1 was 12) and 13 / 13 / 12 for pre-v2.2 (runs 1 and 2 were 11 and 12). v2.2 then caught 39 of 39, and pre-v2.2 38 of 39.
