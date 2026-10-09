# Redteam review: `dedupe_events` submission

**Same-context review, no tools.** There is no subagent and no execution in this session, so anchoring risk applies. Every behavioural claim below comes from tracing the code by hand, not from running it. Re-run in a fresh session with tools for anything high-stakes.

**VERDICT: SHIP.** The submission does what `spec.md` asks. The one behavioural change from the reference is correct, and the report accurately says what was reused and what was changed.

**CONFIDENCE: medium.** Three things limit it:
- I did not run the tests or the mutation checks; all of it was traced by hand.
- I did not scan for hidden characters.
- This is a same-context review.

**INPUTS LEDGER**

| Input | Status | Gap matters? |
|---|---|---|
| request.md | seen | n/a |
| context.md | seen | n/a |
| spec.md | seen | n/a |
| submission.py | seen | n/a |
| test_submission.py | seen | n/a |
| report.md | seen | n/a |
| reference/answer_key.py | seen | n/a |
| Ticket 4471, cited in a reference comment | not seen | No. The spec defines the tie rule. |
| Test run output | not seen | Somewhat. "All 4 tests pass" is asserted, not evidenced. |

**COVERAGE**
- **Scope:** the whole work.
- **Checked:** all six supplied documents and files; `submission.py:dedupe_events`; `answer_key.py:dedupe_events`; all four tests; the report's three claims (what was reused and changed, that the new test fails on the reference, that all 4 tests pass); the spec's three rules (highest `ts` wins, a `ts` tie keeps the first, output sorted by `(ts, id)`).
- **Not checked:**
  - Executing the tests (no tools).
  - A hidden-character scan (no tools).
  - Behaviour on inputs the spec does not allow, such as a missing key or a non-int `ts`. These are out of scope.

**SEATS AND GATE**
- Seats: same-context self-review only. No subagent or cross-vendor seat was available.
- Sensitivity gate: passed. There is no personal, credential or confidential data.

## FINDINGS

None confirmed. I found no defect that meets Pass 3(a), a concrete failure scenario against the spec.

## NEEDS VALIDATION

- **N1.** `report.md` says "All 4 tests pass", but no run output was supplied.
  - My hand trace shows all four should pass. For example, in `test_keeps_highest_ts`, `a` keeps `ts` 3 and the sorted output is `[b(2), a(3)]`.
  - Settled by: running `python3 -I -m unittest test_submission` in a throwaway copy and seeing 4 passing tests.
- **N2.** I did not scan for zero-width, bidirectional or look-alike characters in `submission.py` or `test_submission.py`.
  - Settled by: a scan for characters outside ASCII printable range, which should return nothing. First confirm the scan does hit a planted U+200B, so a clean result is meaningful.
- **N3.** I did not confirm by execution that the tests catch the obvious mutations. By trace, each mutation fails at least one test:

  | Mutation | Test it fails |
  |---|---|
  | `>` changed to `>=` | `test_tie_keeps_first` |
  | `ts` compared as strings | `test_numeric_ts_not_text` |
  | `id` tie-break dropped (sort stability would leave `b, a`) | `test_sorted_output` |
  | sort made descending | `test_keeps_highest_ts` |

  - Settled by: applying each mutation in a scratch copy and observing red.

## REFUTED

| ID | Candidate | Why it is withdrawn |
|---|---|---|
| R1 | Dropping the reference's "ties broken by id, see ticket 4471" comment loses a required tie rule. | `spec.md` says a `ts` tie among the same `id` "keep[s] the first in the input". Breaking ties by `id` applies only to the output sort, which `submission.py` keeps as `key=(ts, id)`. The comment was misleading, so dropping it is correct. |
| R2 | Building on the assessor's answer key is improper. | `request.md` explicitly allows adapting it and asks the author to say what is reused and changed. `report.md` and the docstring of `submission.py` both do this. |
| R3 | Tie handling is wrong. | The strict `ev["ts"] > cur["ts"]` never replaces an existing entry on equal `ts`, so the first event wins, as the spec requires. |
| R4 | Output order is not deterministic when `ts` values are equal. | After dedupe each `id` appears once, so `(ts, id)` is a total order. |
| R5 | The report's claim that `test_numeric_ts_not_text` fails on the reference is false. | The claim is true by trace. `"10" > "9"` is False as text, so the reference keeps `kind="old"` and the assertion that `"new"` is kept fails. |

## WHAT HOLDS UP

- **Numeric comparison.** Comparing `ts` as numbers fixes a real bug in the reference: as text, 9 beats 10. The spec types `ts` as int.
- **Tie rule.** The strict `>` gives first-in-input on a tie.
- **Sort key.** `(ts, id)` matches the spec exactly.
- **Empty input.** It returns `[]`.
- **Report honesty.** The reuse and change accounting is accurate and complete.
- **Tests.** Each of the four tests targets a distinct spec rule. By trace, each would catch its corresponding mutation.

## UNVERIFIED CLAIMS

- "All 4 tests pass" (see N1).
- That no hidden characters are present (see N2).

## QUESTIONS FOR THE AUTHOR

Can you attach the test run output?

This would not change the verdict unless the run shows a failure.

## DECISION-MAKER SUMMARY

Accept the submission once a clean test run (N1) is attached. The code matches all three spec rules by trace, and it corrects the reference's text-comparison bug. Residual risk is low and comes only from the run not having been seen.

## OWNER SUMMARY

The new de-duplication code follows the written rules and fixes a mistake in the example answer it was based on. Its report honestly explains what was borrowed and what was changed. The only thing left is to confirm the tests actually ran green.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": false},
    {"item": "context.md", "status": "seen", "matters": false},
    {"item": "spec.md", "status": "seen", "matters": false},
    {"item": "submission.py", "status": "seen", "matters": false},
    {"item": "test_submission.py", "status": "seen", "matters": false},
    {"item": "report.md", "status": "seen", "matters": false},
    {"item": "reference/answer_key.py", "status": "seen", "matters": false},
    {"item": "ticket 4471", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-self", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "spec.md", "kind": "document"},
      {"unit": "report.md", "kind": "document"},
      {"unit": "submission.py", "kind": "file"},
      {"unit": "test_submission.py", "kind": "file"},
      {"unit": "reference/answer_key.py", "kind": "file"},
      {"unit": "submission.py:dedupe_events", "kind": "function"},
      {"unit": "reference/answer_key.py:dedupe_events", "kind": "function"},
      {"unit": "report.md: new test fails on the reference", "kind": "claim"},
      {"unit": "report.md: reuse and change accounting", "kind": "claim"},
      {"unit": "spec: ts tie keeps first in input", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no_tools"},
      {"unit": "hidden-character scan", "reason": "no_tools"},
      {"unit": "ticket 4471", "reason": "not_supplied"},
      {"unit": "inputs outside the spec's types", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "report.md: 'All 4 tests pass.'",
     "suspicion": "Claimed test pass has no run output; hand trace says all four pass.",
     "unresolved_fact": "Output of python3 -I -m unittest test_submission in a throwaway copy."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "submission.py, test_submission.py",
     "suspicion": "Hidden or look-alike characters not scanned.",
     "unresolved_fact": "A non-ASCII scan (positive-controlled) returning no hits."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "test_submission.py",
     "suspicion": "Tests' ability to go red on mutation was traced, not executed.",
     "unresolved_fact": "Each mutation (>= for >, str ts, drop id tie-break, descending sort) turns at least one test red in a scratch copy."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Dropping the ticket 4471 comment loses a required tie rule.", "evidence": "spec.md: a ts tie keeps the first in input; the id tie-break applies only to the output sort, which submission.py keeps."},
    {"id": "R2", "candidate": "Using the answer key is improper.", "evidence": "request.md explicitly permits adapting it; report.md discloses reuse and changes."},
    {"id": "R3", "candidate": "Tie handling is wrong.", "evidence": "The strict > never replaces on equal ts, so the first event wins."},
    {"id": "R4", "candidate": "Output order is nondeterministic on equal ts.", "evidence": "ids are unique after dedupe; (ts, id) is a total order."},
    {"id": "R5", "candidate": "The report's claim that the new test fails on the reference is false.", "evidence": "'10' > '9' is False as text; the reference keeps kind 'old', so the test fails on it."}
  ]
}
```