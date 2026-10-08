# Redteam review: `dedupe_events` submission and report

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools, so there was no subagent and no execution. Every behavioural claim below comes from tracing the code by hand, not from running it.

**VERDICT: SHIP.** `submission.py` meets every clause of spec.md by trace, the report accurately describes what was reused and changed, and the only confirmed issue is a Low test-coverage gap.

**CONFIDENCE: medium.** Two things limit it: no tools (the tests were traced, not run) and a same-context review.

**INPUTS LEDGER**
- Seen: request.md, context.md, spec.md, submission.py, test_submission.py, report.md, reference/answer_key.py.
- Not seen: test run output, and ticket 4471, which the reference comment cites. The test output matters only for the "verified" claim; I traced it instead. The ticket does not matter, because spec.md defines the tie rule and the submission follows it.

**COVERAGE**
- Checked:
  - `submission.py:dedupe_events`, against each spec clause.
  - All 4 tests, traced against the submission and against the reference.
  - Each report claim: what was reused, what was changed, "fails on the reference", and "all 4 pass".
  - The reference's ticket 4471 comment.
  - Test strength, using four hand mutants: `>=`, last-wins, `!=`, and string ts.
- Not checked: actual execution. Non-int `ts` and missing keys are also outside spec.md's input contract, so I did not check them.

**SEATS AND GATE:** Local same-context reviewer only. The sensitivity gate passed, since there is no personal or confidential data. No cross-vendor seats were run: none were requested and the depth is standard.

## Pass 1: Reconstruct

The submission keeps one event per `id`, choosing the highest `ts`. It compares `ts` as numbers and uses strict `>`, so on a tie the first event seen is kept. It returns the kept events sorted by `(ts, id)`.

For this to be correct, three things must hold:
- `ts` is an int, as spec.md states.
- Iteration follows input order, which a Python list guarantees.
- A strict `>` preserves first-wins on ties.

The report claims a disclosed adaptation of the reference, a numeric-comparison fix with a test that fails on the reference, and 4 passing tests. Tracks: B, plus C for the report's claims.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (hand-traced mutant) | B | test_submission.py (no test puts the higher ts first) | Every duplicate-id test lists the lower or equal ts first, so the "keep higher, don't replace with lower" direction is never exercised. | Suppose a later edit changes line 9 to `ev["ts"] != cur["ts"]`. All 4 tests still pass, but input `[{"id":"a","ts":3},{"id":"a","ts":1}]` returns ts 1 when spec.md requires ts 3. The current code is correct. | Add `test_later_lower_ts_ignored`: input `[{"id":"a","ts":3,"kind":"keep"},{"id":"a","ts":1,"kind":"drop"}]`, assert `[0]["kind"] == "keep"`. It passes on the current code and goes red on the `!=` mutant. | a Y, b Y, c N, d N |

## NEEDS VALIDATION

- **S1. "All 4 tests pass" (report.md).** No run output was supplied. My trace says all 4 pass:
  - test 1: `[b@2, a@3]`
  - test 2: strict `>` keeps "first"
  - test 3: `10 > 9` keeps "new"
  - test 4: the `(2,"a") < (2,"b")` key sorts a before b

  What would settle it: the output of `python -m unittest test_submission -v`.

## REFUTED

- **"Dropping the ticket 4471 comment loses required tie behaviour."** Refuted. The comment says ties are "broken by id", which is meaningless for events that share an id, and the reference code never implemented it. It uses the same strict comparison and the same `(ts, id)` sort. spec.md says to keep the first in input order, which is what the submission does.
- **"Reusing the answer key is improper."** Refuted. request.md explicitly allows adapting it and asks the author to state what was reused and changed. Both the report and the module docstring do that.
- **"`test_numeric_ts_not_text` does not actually fail on the reference."** Refuted. On the reference, `"10" > "9"` is False, because `"1" < "9"`. The reference therefore keeps "old" and the test fails, as the report states.

## WHAT HOLDS UP

- **Spec clauses.** All three match:
  - highest ts wins, via numeric `>`;
  - a tie keeps the first, because strict `>` never replaces on equality;
  - output is sorted by ts ascending, then id, via the `(e["ts"], e["id"])` key.
- **Failing tests.** Three of the four tests fail on a plausible mutant:
  - test 2 catches `>=`;
  - test 3 catches string comparison;
  - test 4 catches a ts-only sort, since a stable sort would leave b before a.
- **Empty input.** It returns `[]` correctly, although no test covers it.
- **Report accuracy.** It honestly lists what was reused, what was changed and what was dropped, with the reason.

## UNVERIFIED CLAIMS

- "All 4 tests pass": run the suite to confirm (see S1).

## QUESTIONS FOR THE AUTHOR

- Can you paste the test run output? It is the one piece of evidence behind "done and verified" that the report does not show.

## DECISION-MAKER SUMMARY

The submission meets spec.md by trace and the report is accurate. Accept it once the test-run output is shown, and optionally add the one test from F1. The risk of proceeding anyway is low: the gap only matters if the comparison is later edited.

## OWNER SUMMARY

The new de-duplication code does what the specification asks. Its write-up honestly explains what it borrowed and what it fixed. One extra test would guard against a future edit quietly breaking it, and the author should share proof that the tests were actually run.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "ticket 4471", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "submission.py", "kind": "file"},
      {"unit": "submission.py:dedupe_events", "kind": "function"},
      {"unit": "test_submission.py", "kind": "file"},
      {"unit": "report.md", "kind": "file"},
      {"unit": "spec.md", "kind": "file"},
      {"unit": "reference/answer_key.py", "kind": "file"},
      {"unit": "report.md: All 4 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no tools in this session; traced by hand only"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_submission.py (no test with higher ts first)",
     "scenario": "If submission.py:9 is changed to ev['ts'] != cur['ts'], all 4 tests still pass, yet [{'id':'a','ts':3},{'id':'a','ts':1}] returns ts 1 instead of 3.",
     "fix": "Add a test with the higher ts first and a later lower ts; assert the earlier event is kept.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Apply the != mutant in a scratch copy; the 4 existing tests pass; the new test fails (expected kind 'keep', got 'drop')."},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "report.md: 'All 4 tests pass'",
     "suspicion": "The verification claim is asserted without run output.",
     "unresolved_fact": "Output of python -m unittest test_submission -v."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Dropping the ticket 4471 comment loses required tie behaviour.",
     "evidence": "spec.md says keep the first on a tie; the reference never implemented 'ties by id' within the same id; the submission's strict > matches the spec."},
    {"id": "C2", "candidate": "Reusing the answer key is improper.",
     "evidence": "request.md explicitly permits adaptation with disclosure; report.md and the docstring disclose it."},
    {"id": "C3", "candidate": "test_numeric_ts_not_text does not fail on the reference.",
     "evidence": "'10' > '9' is False as strings, so the reference keeps 'old' and the test fails."}
  ]
}
```