# Case health, 2026-10-22

Offline recommendations only. No case is edited or deleted; no model was called.

current-key rescoring; not a replacement for published as-run totals.

## Coverage and limits

Development cases: 190. Recorded run directories: 83.
Full-enumeration redundancy evidence: not established.
Unknown text/model identities are retained as unknown. Dates are recorded source/run dates, not filesystem mtimes.
Stop/fallback shares count explicit recorded flags only; missing usage metadata cannot establish their absence.
Missing/invalid inputs are counted below; absence from a partial historical run is not a scored miss.
Assess case-rule pass rates are not planted-defect recall; control failures there are rule failures, not necessarily open High findings.
The JSON companion contains per-text/model rates, status shares, recorded dates and the exact recommendation evidence.
Counts-only publications cannot populate per-case observations and are not expanded into invented runs.

Verdicts: {"KEEP": 59, "SHARPEN": 60, "UNTESTABLE": 71}

Input diagnostics: {"invalid_prompt": 28, "invalid_report": 38, "metadata_absent": 323, "unassociated_metadata_directories": 22}

## Hold-out aggregate only

{"fallback_observations": 0, "invalid_report": 8, "issue_invalid_report": 8, "missing_usage_metadata": 0, "observations": 492, "safety_stop_observations": 0, "usable": 484}

## Disclosure and safety regression guards

| Case | Recommendation | Usable / recorded | Evidence |
|---|---|---|---|
| `evals/cases/case-28` | KEEP (regression guard) | 16 / 16 | defect_recall: 32/32; KEEP (regression guard): saturation alone does not justify pruning required text; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-29` | KEEP (regression guard) | 16 / 16 | case_rule_pass: 16/16; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-30` | KEEP (regression guard) | 16 / 16 | defect_recall: 31/32; retain with the recorded coverage and limitations |
| `evals/cases/case-42` | KEEP (regression guard) | 12 / 12 | case_rule_pass: 12/12; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/pretext/cases/case-01` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |

## Other development cases

| Case | Recommendation | Usable / recorded | Evidence |
|---|---|---|---|
| `evals/assess/cases/case-01` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-02` | KEEP | 3 / 3 | assess_rule_pass: 2/3; retain with the recorded coverage and limitations |
| `evals/assess/cases/case-03` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-04` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-05` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-06` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-07` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-08` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-09` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-10` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-11` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-12` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-13` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-14` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-15` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-16` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-17` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-18` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-19` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-20` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-21` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-22` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-23` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-24` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-25` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-26` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-27` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-28` | SHARPEN | 3 / 3 | assess_rule_pass: 3/3; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-29` | KEEP | 3 / 3 | assess_rule_pass: 3/3; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-30` | KEEP | 3 / 3 | assess_rule_pass: 3/3; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-31` | KEEP | 3 / 3 | assess_rule_pass: 3/3; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-32` | KEEP | 3 / 3 | assess_rule_pass: 3/3; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-33` | KEEP | 3 / 3 | assess_rule_pass: 3/3; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-34` | KEEP | 3 / 3 | assess_rule_pass: 3/3; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-35` | KEEP | 3 / 3 | assess_rule_pass: 3/3; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/assess/cases/case-36` | KEEP | 3 / 3 | assess_rule_pass: 3/3; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-01` | KEEP | 19 / 19 | defect_recall: 37/38; retain with the recorded coverage and limitations |
| `evals/cases/case-02` | KEEP | 19 / 19 | case_rule_pass: 17/19; retain with the recorded coverage and limitations |
| `evals/cases/case-03` | SHARPEN | 19 / 19 | defect_recall: 19/19; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-04` | SHARPEN | 19 / 19 | defect_recall: 19/19; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-05` | KEEP | 19 / 19 | defect_recall: 14/19; retain with the recorded coverage and limitations |
| `evals/cases/case-06` | SHARPEN | 26 / 26 | defect_recall: 26/26; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-07` | KEEP | 26 / 26 | case_rule_pass: 25/26; retain with the recorded coverage and limitations |
| `evals/cases/case-08` | SHARPEN | 26 / 26 | defect_recall: 26/26; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-09` | SHARPEN | 26 / 26 | defect_recall: 52/52; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-10` | KEEP | 26 / 26 | defect_recall: 24/26; retain with the recorded coverage and limitations |
| `evals/cases/case-11` | SHARPEN | 26 / 26 | defect_recall: 26/26; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-12` | KEEP | 25 / 26 | case_rule_pass: 23/25; retain with the recorded coverage and limitations |
| `evals/cases/case-13` | KEEP | 25 / 26 | defect_recall: 24/25; retain with the recorded coverage and limitations |
| `evals/cases/case-14` | KEEP | 19 / 19 | defect_recall: 53/57; retain with the recorded coverage and limitations |
| `evals/cases/case-15` | KEEP | 19 / 19 | case_rule_pass: 19/19; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-16` | KEEP | 19 / 19 | defect_recall: 15/19; retain with the recorded coverage and limitations |
| `evals/cases/case-17` | SHARPEN | 19 / 19 | defect_recall: 19/19; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-18` | KEEP | 19 / 19 | case_rule_pass: 19/19; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-19` | SHARPEN | 19 / 19 | defect_recall: 19/19; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-20` | KEEP | 19 / 19 | defect_recall: 36/38; retain with the recorded coverage and limitations |
| `evals/cases/case-21` | KEEP | 19 / 19 | defect_recall: 37/38; retain with the recorded coverage and limitations |
| `evals/cases/case-22` | KEEP | 19 / 19 | case_rule_pass: 14/19; retain with the recorded coverage and limitations |
| `evals/cases/case-23` | KEEP | 19 / 19 | defect_recall: 18/19; retain with the recorded coverage and limitations |
| `evals/cases/case-24` | SHARPEN | 21 / 22 | defect_recall: 21/21; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-25` | KEEP | 21 / 22 | defect_recall: 36/42; retain with the recorded coverage and limitations |
| `evals/cases/case-26` | SHARPEN | 22 / 22 | defect_recall: 22/22; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-27` | KEEP | 27 / 28 | case_rule_pass: 25/27; retain with the recorded coverage and limitations |
| `evals/cases/case-31` | UNTESTABLE | 9 / 22 | defect_recall: 16/18; at least half the recorded observations are unusable |
| `evals/cases/case-32` | KEEP | 20 / 22 | case_rule_pass: 17/20; retain with the recorded coverage and limitations |
| `evals/cases/case-33` | SHARPEN | 16 / 16 | defect_recall: 32/32; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-34` | SHARPEN | 16 / 16 | defect_recall: 32/32; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-35` | KEEP | 23 / 25 | case_rule_pass: 15/23; retain with the recorded coverage and limitations |
| `evals/cases/case-36` | KEEP | 24 / 25 | case_rule_pass: 19/24; retain with the recorded coverage and limitations |
| `evals/cases/case-37` | SHARPEN | 19 / 19 | defect_recall: 19/19; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-38` | SHARPEN | 19 / 19 | defect_recall: 19/19; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-39` | KEEP | 19 / 19 | case_rule_pass: 19/19; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-40` | SHARPEN | 12 / 12 | defect_recall: 24/24; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-41` | SHARPEN | 12 / 12 | defect_recall: 24/24; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-43` | SHARPEN | 12 / 12 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-44` | KEEP | 12 / 12 | case_rule_pass: 11/12; retain with the recorded coverage and limitations |
| `evals/cases/case-45` | SHARPEN | 12 / 12 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-46` | SHARPEN | 12 / 12 | defect_recall: 24/24; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-47` | KEEP | 12 / 12 | defect_recall: 35/36; retain with the recorded coverage and limitations |
| `evals/cases/case-48` | KEEP | 12 / 12 | case_rule_pass: 12/12; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-49` | SHARPEN | 12 / 12 | defect_recall: 24/24; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-50` | SHARPEN | 6 / 6 | defect_recall: 6/6; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-51` | KEEP | 6 / 6 | case_rule_pass: 2/6; retain with the recorded coverage and limitations |
| `evals/cases/case-52` | SHARPEN | 5 / 6 | defect_recall: 10/10; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-53` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-54` | SHARPEN | 6 / 6 | defect_recall: 6/6; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-55` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-56` | SHARPEN | 6 / 6 | defect_recall: 6/6; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-57` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-58` | KEEP | 6 / 6 | defect_recall: 2/6; retain with the recorded coverage and limitations |
| `evals/cases/case-59` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-60` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/cases/case-61` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/cases/case-62` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-63` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-64` | UNTESTABLE | 2 / 6 | defect_recall: 4/4; at least half the recorded observations are unusable; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-65` | KEEP | 6 / 6 | case_rule_pass: 5/6; retain with the recorded coverage and limitations |
| `evals/cases/case-66` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-67` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-68` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-69` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-70` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-71` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-72` | KEEP | 6 / 6 | defect_recall: 10/12; retain with the recorded coverage and limitations |
| `evals/cases/case-73` | KEEP | 6 / 6 | case_rule_pass: 4/6; retain with the recorded coverage and limitations |
| `evals/cases/case-74` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-75` | KEEP | 6 / 6 | case_rule_pass: 1/6; retain with the recorded coverage and limitations |
| `evals/cases/case-76` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-77` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-78` | KEEP | 6 / 6 | defect_recall: 11/12; retain with the recorded coverage and limitations |
| `evals/cases/case-79` | KEEP | 6 / 6 | case_rule_pass: 4/6; retain with the recorded coverage and limitations |
| `evals/cases/case-80` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-81` | KEEP | 6 / 6 | case_rule_pass: 5/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-82` | KEEP | 6 / 6 | defect_recall: 10/12; retain with the recorded coverage and limitations |
| `evals/cases/case-83` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-84` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-85` | KEEP | 6 / 6 | case_rule_pass: 4/6; retain with the recorded coverage and limitations |
| `evals/cases/case-86` | SHARPEN | 6 / 6 | defect_recall: 12/12; all usable observations detect the planted items; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/cases/case-87` | KEEP | 6 / 6 | case_rule_pass: 6/6; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/evidence/cases/case-01` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-02` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-03` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-04` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-05` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-06` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-07` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-08` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-09` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-10` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-11` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-12` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-13` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-14` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-15` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/evidence/cases/case-16` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/exposure/cases/case-01` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/exposure/cases/case-02` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/exposure/cases/case-03` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/exposure/cases/case-04` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/exposure/cases/case-05` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-01` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-02` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-03` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-04` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-05` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-06` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-07` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-08` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-09` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-10` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-11` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-12` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-13` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-14` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-15` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-16` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-17` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/onchain/cases/case-18` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/pretext/cases/case-02` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/pretext/cases/case-03` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/pretext/cases/case-04` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/pretext/cases/case-05` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/pretext/cases/case-06` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/runtime/cases/case-01` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/runtime/cases/case-02` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/runtime/cases/case-03` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/runtime/cases/case-04` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/runtime/cases/case-05` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/secrets/cases/case-01` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/secrets/cases/case-02` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/secrets/cases/case-03` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/secrets/cases/case-04` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/secrets/cases/case-05` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-01` | UNTESTABLE | 4 / 12 | defect_recall: 12/12; at least half the recorded observations are unusable; never failed a usable reviewer; this alone does not prove the case redundant |
| `evals/supplychain/cases/case-02` | UNTESTABLE | 3 / 6 | case_rule_pass: 2/3; at least half the recorded observations are unusable |
| `evals/supplychain/cases/case-03` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-04` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-05` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-06` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-07` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-08` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-09` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-10` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-11` | UNTESTABLE | 0 / 0 | case_rule_pass: 0/0; no usable recorded reviews |
| `evals/supplychain/cases/case-12` | UNTESTABLE | 0 / 0 | defect_recall: 0/0; no usable recorded reviews |
