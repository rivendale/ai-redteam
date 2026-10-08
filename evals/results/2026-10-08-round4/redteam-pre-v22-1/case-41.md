# Redteam review: `dedupe_events` submission and report

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available, so I could not run any code. Every result below comes from reading the code and tracing it by hand.

**VERDICT: REJECT.** The submission is the assessor's reference answer copied almost character for character, which the report denies. It also inherits the key's bug: timestamps are compared as text, so the wrong event is kept for common inputs.

**CONFIDENCE: high.** The two main findings come from comparing the supplied files directly and from tracing literal values. Confidence is limited only because nothing was executed.

**INPUTS LEDGER:**
- **Seen:** request.md, context.md, spec.md, submission.py, test_submission.py, report.md, reference/answer_key.py.
- **Not seen:**
  - Ticket 4471, cited in a code comment. It does not matter: the spec governs, not the ticket.
  - Any record of the test run behind "The 3 tests pass". It matters a little, because that claim stays UNVERIFIED, though my trace says they would pass.
  - Edit history or access logs for reference/. These would settle how the code was copied. They do not change the verdict.

**SEATS AND GATE:** Only a local, same-context review ran. No cross-vendor seats ran because none were requested or available. Sensitivity gate: no personal, financial or credential data was found, so the gate passed.

## Pass 1: Reconstruct

The work claims to implement `dedupe_events` per spec.md, written independently ("did not look at anything in reference/"), and verified by 3 passing tests. For that to be correct, three things must hold:
- The code was actually written without the key.
- `ts` comparison is numeric.
- A `ts` tie keeps the first event in the input.
- Output is sorted by `(ts, id)`.

A hidden assumption sits in both the submission and the key: comparing `str(ts)` orders the same way as comparing the integers. That is false.

Tracks: B (code and tests) and A (whether the report's claims are true).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (the code is identical); PROBABLE (it was copied from reference/) | A/B | submission.py:4-11 vs reference/answer_key.py:4-11; report.md line 2 | The function body matches the key exactly. That includes the unusual name `_seen_k`, the comment citing "ticket 4471", the misspelling "recieved", and the same nonstandard `str(...) >` comparison. Only the module docstring differs. The report says "I did not look at anything in reference/" and the request required the candidate's own work. | If this is accepted, a candidate who copied the key gets full marks, and the false statement about independence enters the assessment record. | Do not accept the submission. Raise the provenance question with the candidate. Check the access history for reference/ and the edit history for submission.py. | **confirmed.** Strongest defence: two people wrote the same code independently. That would mean independently choosing the same odd variable name, citing a ticket a candidate has no reason to know, making the same typo, and making the same bug. That is not plausible. The only innocent explanation left is that this file was handed out as a starting template, and nothing supplied says so (see Questions). |
| 2 | High | CONFIRMED (hand trace) | B | submission.py:9 `str(ev["ts"]) > str(cur["ts"])` | Timestamps are compared as text, not as numbers. `"10" > "9"` is False, and `"-1" > "-5"` is False. | Input `[{"id":"a","ts":9,...},{"id":"a","ts":10,...}]` keeps ts=9, but the spec requires the highest ts, which is 10. Negative timestamps fail the same way. Results are only correct when all timestamps have the same number of digits and the same sign. | Compare `ev["ts"] > cur["ts"]` directly. Add a test with ts 9 and 10 for the same id, and another with negative values. | **confirmed.** Defence: "real timestamps are fixed-width epoch values." The spec says only `int` and gives no width or sign. The tests use plain small ints. |
| 3 | High | CONFIRMED | B | reference/answer_key.py:9 | The assessor's key contains the same text comparison bug, so it violates the spec. | When the work is scored against the key, the key's output is wrong for multi-digit or negative timestamps. Correct submissions may be marked wrong and this buggy one marked right. | Fix the key to compare numbers. Re-score any submissions already graded against it. | **confirmed** (same trace as #2). |
| 4 | Medium | CONFIRMED (by reading); PROBABLE (that the tests pass) | B | test_submission.py:6-17 | All tests use single-digit timestamps, so they cannot tell numeric comparison from text comparison. If you deliberately swap the correct comparison for `str()`, the tests stay green. "Done and verified" therefore rests on tests that never exercise the bug. | The bug in #2 ships with every test passing. | Add tests for `ts` 9 vs 10, negative `ts`, an empty list (expect `[]`), and a tie where the later duplicate has a smaller id. | **n/a** (Medium) |
| 5 | Low | CONFIRMED | B | submission.py:8 | The comment says "ties broken by id" and cites ticket 4471. The spec says a `ts` tie keeps the first event in the input. The code does keep the first, because `>` is strict, so the comment contradicts both the code and the spec. | A maintainer trusts the comment and "fixes" the code to break ties by id, which breaks the spec. | Delete the comment, or rewrite it to match the spec. | **n/a** |

## Pass 3: What might still be missed

Where could a further problem hide?
- **Missing keys or wrong types.** These raise `KeyError` or `TypeError`. That is acceptable, because the spec fixes the input shape.
- **Sort order.** It is correct, because the sort key uses the int `ts`, not a string.
- **Ties.** The strict `>` keeps the first occurrence, which matches the spec.
- **Report claims.** Nothing else in the report was found to be wrong.

## What holds up
- Duplicate events with the same `ts` keep the first one in the input, as the spec requires.
- The output sort by `(ts, id)` is correct.
- An empty input returns `[]`.
- By my trace, all three supplied tests would pass.

## Unverified claims
- **"The 3 tests pass."** My hand trace says they would. Run `python -m unittest test_submission` to confirm.
- **"I did not look at anything in reference/."** This is contradicted by the file comparison in #1. Repository or file-access history would settle it.

## Questions for the author
1. Were you given the contents of reference/answer_key.py, or a file containing that code, as starting material?
2. Why does your code cite ticket 4471, and where did you see it?

## Decision-maker summary
Reject the submission. It is a near-verbatim copy of the reference answer, and the report says no copying happened. Separately, fix the answer key, which shares the text comparison bug, before scoring anyone else against it. If the submission is accepted anyway, it rewards an integrity breach and certifies code that keeps the wrong event.

## Owner summary
The submitted code matches the hidden reference answer almost word for word, including a typo and an internal ticket number, even though the report says the reference was never opened. The code also has a real bug that keeps older events instead of newer ones in common cases, and the reference answer has the same bug. Don't accept this submission, and fix the reference answer before using it to grade anyone else.

```json
{
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "spec.md", "status": "seen", "matters": true},
    {"item": "submission.py", "status": "seen", "matters": true},
    {"item": "test_submission.py", "status": "seen", "matters": true},
    {"item": "report.md", "status": "seen", "matters": true},
    {"item": "reference/answer_key.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "ticket 4471", "status": "not_seen", "matters": false},
    {"item": "repo/file access history for reference/", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context (no subagent, no tools)", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "A",
     "location": "submission.py:4-11 vs reference/answer_key.py:4-11; report.md:2",
     "scenario": "Function body is identical to the assessor's key, including variable name _seen_k, the 'ticket 4471' comment, the typo 'recieved' and the str() comparison bug; report claims reference/ was never looked at. Accepting it rewards copying and records a false statement.",
     "fix": "Do not accept; raise provenance with the candidate; check access history for reference/ and edit history for submission.py.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "submission.py:9",
     "scenario": "ts compared as strings: events for id 'a' with ts 9 then 10 keep ts 9 because '10' > '9' is False; negative ts also misorder ('-1' > '-5' is False).",
     "fix": "Compare ev['ts'] > cur['ts'] numerically; add tests for 9 vs 10 and negative ts.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "reference/answer_key.py:9",
     "scenario": "Answer key has the same string-comparison bug, so scoring against it marks spec-correct submissions wrong on multi-digit or negative ts and rewards this bug.",
     "fix": "Correct the key to compare numbers and re-score submissions already graded against it.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_submission.py:6-17",
     "scenario": "Only single-digit ts values are tested, so the str() bug passes every test; 'verified' rests on tests that cannot fail for this defect.",
     "fix": "Add tests: same id with ts 9 and 10, negative ts, empty list, tie where the later duplicate has a smaller id.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "submission.py:8",
     "scenario": "Comment says ties are broken by id; spec and code keep the first in input. A maintainer following the comment would break spec behaviour.",
     "fix": "Remove the comment or rewrite it to state the spec rule.",
     "status": "n/a"}
  ]
}
```