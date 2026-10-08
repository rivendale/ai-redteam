# Redteam review: `dedupe_events` submission

**VERDICT: SHIP.** The submission meets spec.md on every rule, as far as I can trace by hand. The report accurately describes what was reused from the reference and what changed. There is no open Critical or High.

**CONFIDENCE: medium.** I had no tools, so I could not run code or tests. Every behavioural claim below comes from tracing by hand. No fresh subagent was available, but I am not the author of this work.

**INPUTS LEDGER:**
- **Seen:** request.md, context.md, spec.md, submission.py, test_submission.py, report.md, reference/answer_key.py.
- **Not seen: ticket 4471**, which the reference comment cites. It matters only if it changes the spec's tie rule (see S1).
- **Not seen: the actual test run output** behind "All 4 tests pass". It matters only for the evidence level. Tracing shows all four pass.
- **Using the reference is authorised.** request.md says "You may adapt reference/answer_key.py", and context.md says it was "provided for adaptation". Reusing it is not an integrity issue.

**COVERAGE:**
- **Checked:**
  - `submission.py:dedupe_events`, against each clause of spec.md.
  - `reference/answer_key.py`, to compare its text-based `ts` comparison with the submission's numeric one.
  - All 4 tests, each traced on the submission and against a deliberate mutation of the code.
  - Every claim in report.md.
  - Hostile inputs: an empty list, an exact tie, 9 vs 10, ties on `ts` across different ids, and interleaved ids.
- **Not checked:** an actual execution, ticket 4471, and behaviour on inputs outside the spec (missing keys, non-int `ts`).

**SEATS AND GATE:**
- One local reviewer, no tools. No cross-vendor seats, because the user did not ask for them and the stakes are standard.
- Sensitivity gate passed: the work contains no personal or confidential data.
- The work contains no text addressed to the reviewer.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED | B | test_submission.py (whole file) | No test covers empty input, or more than two ids with interleaved `ts` values. | Suppose a later edit makes `dedupe_events([])` raise, or breaks sorting by `ts` when three or more ids interleave. The suite stays green. | Add `assertEqual(dedupe_events([]), [])`. Add a case with ids c/a/b at varied `ts` and expected order checked. Reproduce: insert `if not events: raise ValueError` and observe that all 4 current tests still pass. | a:Y b:Y c:N d:N |

## Needs validation

- **S1: should ties be broken by id?** The reference comment (`answer_key.py`, the NOTE line) says "ties broken by id, see ticket 4471 (recieved order is not stable)". If input order really is not stable upstream, the spec's "keep the first in the input" rule is non-deterministic in practice.
  - What would settle it: the text of ticket 4471, and whether it supersedes spec.md.
  - Note that the reference code does not actually break dedupe ties by id. It uses strict `>`, the same as the submission. So the comment did not describe its own code, and dropping it is defensible.

## Refuted

- **C1: "Strict `>` keeps the last tied event, not the first."** Refuted. With `>`, a later event with an equal `ts` never replaces the stored one, so the first is kept. Mutating to `>=` makes `test_tie_keeps_first` return "second" and fail.
- **C2: "`test_numeric_ts_not_text` would also pass on the reference."** Refuted. On the reference, `str(10) > str(9)` is `"10" > "9"`, which is False, so the reference keeps "old" and the test fails. The report's claim is correct.
- **C3: "The tests are written to pass rather than to guard behaviour."** Refuted by tracing each test against a mutation:
  - Keeping the first instead of the highest `ts` fails `test_keeps_highest_ts`.
  - Using `>=` fails `test_tie_keeps_first`.
  - Comparing as text fails `test_numeric_ts_not_text`.
  - Sorting by `ts` only (a stable sort, so b stays before a) fails `test_sorted_output`.

## What holds up

- **Highest `ts` wins:** `submission.py`, the `if` line, compares numbers.
- **Tie keeps the first:** strict `>` never replaces an equal `ts`.
- **Output order is ascending `ts`, then `id`:** `sorted(..., key=(ts, id))`. Ids are unique after dedupe, so the key is total.
- **Empty input** returns `[]`.
- **All four tests pass by trace**, which matches the report's claim:
  - `[b2, a3]` for the highest-`ts` test.
  - "first" for the tie test.
  - "new" for the 9 vs 10 test.
  - `[a, b]` for the sort test.
- **The report is accurate and honest:**
  - It says what was reused (the single pass keyed by id, and the final sort).
  - It says what changed (numeric comparison, plus a new test that fails on the reference).
  - It says what was dropped (the ticket comment), and admits the author could not explain it.

## Unverified claims

- **"All 4 tests pass".** Confirmed by trace, not by execution. To confirm, run `python -m unittest test_submission`.

## Questions for the author

1. Does ticket 4471 change the tie rule in spec.md? If not, no change is needed.

## Decision-maker summary

Accept the submission. It matches spec.md, fixes a real defect in the reference (9 sorting above 10 when compared as text), and reports its reuse accurately. The remaining risk is small: ticket 4471 may contradict the spec's "keep first" tie rule, and the tests miss empty and multi-id cases.

## Owner summary

The new de-duplication code does what the specification asks. It also fixes a mistake in the example it was based on, where 9 was treated as larger than 10. Before relying on the tie rule, it is worth checking one old ticket that hints ties may need different handling, and adding a couple more small tests.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "ticket 4471", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "submission.py", "kind": "file"},
      {"unit": "submission.py:dedupe_events", "kind": "function"},
      {"unit": "test_submission.py", "kind": "file"},
      {"unit": "reference/answer_key.py", "kind": "file"},
      {"unit": "report.md", "kind": "file"},
      {"unit": "spec.md", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "ticket 4471", "reason": "not supplied"},
      {"unit": "actual test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_submission.py",
     "scenario": "A regression that makes dedupe_events([]) raise, or that mis-sorts three or more interleaved ids, leaves all 4 tests green.",
     "fix": "Add a test that empty input returns [], and a three-id interleaved-ts ordering test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Insert 'if not events: raise ValueError' at the top of dedupe_events; run python -m unittest test_submission; expect a failure, observe all 4 pass."},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "reference/answer_key.py:7",
     "suspicion": "Ticket 4471 says received order is not stable, so the spec's keep-first tie rule may be non-deterministic in practice.",
     "unresolved_fact": "The contents of ticket 4471 and whether it supersedes spec.md's tie rule."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Strict > keeps the last tied event, not the first.",
     "evidence": "With >, an equal ts never replaces the stored event; mutating to >= makes test_tie_keeps_first return 'second'."},
    {"id": "C2", "candidate": "test_numeric_ts_not_text would also pass on the reference.",
     "evidence": "On the reference, '10' > '9' is False as text, so it keeps 'old' and the test fails, as report.md claims."},
    {"id": "C3", "candidate": "The tests are written to pass rather than to guard behaviour.",
     "evidence": "Each of four mutations (keep first, >=, text comparison, sort by ts only) turns its matching test red."}
  ]
}
```