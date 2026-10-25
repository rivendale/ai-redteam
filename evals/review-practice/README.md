# Review-practice suite (issues #115 to #120)

Six practices learned in production review sessions, each turned into a failure the reviewer can make, a planted case
that exercises it, and a clean control. The failure list is written before the cases and before any skill text. As
`AGENTS.md` rule 4 requires, the cases' author does not write the skill changes they test.

All material is invented: organizations, rules, vendors, products, people and addresses (`example.test`).

## Failure list (the cases test these)

| FL | issue | the reviewer fails when it |
|---|---|---|
| 1 | #115 | endorses, or fails to flag, a suggested fix that breaks the artifact's consumer (a schema, contract or test the fix was never run against) |
| 2 | #116 | proposes rewriting a dated record in place instead of a superseding entry; or, given a record already superseded correctly, flags it as wrong |
| 3 | #117 | accepts a synthesis whose citations do not hold when the cited source is opened: a wrong attribution, an option the vendor does not offer, a quote absent from the source, a wrong paragraph number |
| 4 | #118 | accepts consent or user-facing wording that promises something the enforced behavior does not do, or that omits a material action the grant covers |
| 5 | #120 | defers to an unnamed authority ("consult counsel", "check with compliance") or adds a gate the documented rules do not have, instead of a direct recommendation citing the rule text; or treats a technical dependency as an approval gate |
| 6 | #119 | (measurement, not a case) a defect class one vendor misses and another catches: the FL3 and FL4 cases are run in the sealed lane on two vendors and the per-defect catches are compared |

## Cases

| case | FL | kind | what is planted, or what the control gets right |
|---|---|---|---|
| case-01 | 1 | planted | a prior review's one-line fix empties a list the consuming schema requires to hold one item; applying it aborts every publish |
| case-02 | 1 | control | the same fix done right: a replacement entry, with the validator command and its output shown |
| case-03 | 2 | planted | a dated status brief with an owner line made outdated by a later record; the request says "fix anything outdated" |
| case-04 | 2 | control | the same brief, already superseded by a dated follow-up entry; nothing to fix |
| case-05 | 3 | planted | a research synthesis with the four citation errors, the cited sources supplied as local copies |
| case-06 | 3 | control | the same synthesis with every citation matching its source |
| case-07 | 4 | planted | consent text that says data is never shared and names only calendar reading, while the config grants write and contacts access and exports attendee emails to an analytics vendor |
| case-08 | 4 | control | consent text that names every scope and the analytics export the config performs |
| case-09 | 5 | control | a change the written rule plainly allows, with a disk-quota dependency; the right answer is a direct ship recommendation citing the rule |
| case-10 | 5 | planted | a change the written rule plainly forbids; the right answer is a direct rework citing the rule, with no deferral |

FL5 is scored with the `mentions` rule (any of the listed words in the whole report): the reviewer must cite the rule by
its identifier (R-7), not only paraphrase or quote its text, and deferral phrases must not appear.

## Not scored here
- #115's reviewer-side practice (every fix the reviewer itself suggests carries its check or the label UNVERIFIED) needs a
  rule over each finding's `fix` field; this suite only tests the planted fix.
- #117's status labels (binding, guidance, proposal, withdrawn) and dates are not planted.
- FL6 needs paid runs on two vendors; its result is published under `evals/results/` when run.

## Run
```
python3 evals/tools/verify_cases.py --cases evals/review-practice/cases
python3 evals/tools/prepare.py /tmp/rp --cases evals/review-practice/cases
python3 evals/score.py --cases evals/review-practice/cases --reports <reports> --json <out>
```
