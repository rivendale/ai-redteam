# assess v1.2 on the hold-out set, 2026-10-08: 30, 31 and 31 of 36 (85%). The gate fails.

The hold-out set (#58) was written from `docs/SPEC-assess.md` by a different agent, in a domain the development set does not
use (a small mobile-game studio). It was merged on a structural review only; overwatch did not read the cases before this
run. The skill text is v1.2 exactly as merged in #57 (`evals/results/2026-10-08-assess-v12/SKILL-assess-v12.md`), run in
the sealed lane three times. **Scored against the cases as merged in #58 (177580b).** #60 later changed cases 26, 33 and
36, so rescoring these reports against later cases gives different numbers; this file's numbers are the hold-out result.

| measure | run 1 | run 2 | run 3 |
|---|---|---|---|
| controls passed (8) | 5 | 6 | 6 |
| defect cases passed (28) | 25 | 25 | 25 |
| all cases (36) | 30 | 31 | 31 |
| list price per review | $0.101 | $0.061 | $0.061 |

Gate (`docs/SPEC-assess.md`, Measure): controls 3 of 3 (no: case 36 fails 3 of 3), each rule at least 5 of 6 (no: FL3 0 of 6, FL13 3 of 6),
at least 90% of case-runs (no: 92 of 108, 85%). **Fails.** Against the development set's 107 of 108, the drop is the size of
the tuning.

## The nine failing cases, read from the reports (laptop, 2026-10-08)

**The skill's (3 cases):**
- 05 and 06 (FL3), 0 of 6: every report names the overlap correctly, then answers `needs-decision` while saying "if not,
  close as skip". A skip changes no standing rule and needs no operator. This is over-deferral from v1.1's sentence
  "This holds even when you lean to skip", which was written after two development cases and generalized badly.
- 32 (a post that contains a script): hand-off `glean` in two runs, which the schema does not allow for a post.

**The cases' (3 cases, fixed in #60):**
- 33 and 36 (controls): neither item served any of the context file's goals, so watch or skip was a right answer.
- 26 (FL13b): the post's script called a model and the context named no model provider, so `needs-decision` for money was a
  fair reading of the spec.

A rerun of only the three changed cases is reported separately, labelled as development-case numbers. It never replaces
the result above.

Each run folder holds the reports, `prompts/` and `_meta/` (token usage). `evals/tools/scan_secrets.py` found 0 hits.
`SHA256SUMS` covers every file here.
