# Redteam review: `dedupe_events` submission

**Note:** No subagent or tools were available in this session. I did not author this work, so there is no anchoring from authorship. I could not run any code, so every statement about runtime behaviour below comes from tracing the code by hand. None of it was executed.

**VERDICT: SHIP.** The submission meets spec.md, my hand traces found no defect, and the report accurately describes what was reused and what was changed. "Verified" still rests on a test run nobody has shown, so one run of the suite is the remaining step.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so the suite was not run and no mutation was tested.
- Ticket 4471 was not supplied.
- I could not scan for hidden characters.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | n/a |
| context.md | seen | n/a |
| spec.md | seen | n/a |
| submission.py | seen | n/a |
| test_submission.py | seen | n/a |
| report.md | seen | n/a |
| reference/answer_key.py | seen | n/a |
| Ticket 4471 (cited in the reference's comment) | not seen | Possibly. It hints at a different tie rule. spec.md is the governing text, so it only matters if the ticket overrides the spec. |
| Output of an actual test run | not seen | Yes. It is the "verified" part of the request. |

**COVERAGE**
- **Scope:** the whole work. That means all five supplied files plus the request and the context.
- **Checked:**
  - `submission.py:dedupe_events`, traced against each spec clause (keep highest ts; on a ts tie keep the first in input; sort by ts ascending, then by id).
  - Each of the 4 tests, traced against the submission, plus a set of mutants.
  - `answer_key.py`, traced on the 9-vs-10 case.
  - Each claim in report.md.
- **Not checked:**
  - Executing tests (no tools).
  - Scanning for zero-width, bidi or look-alike characters (no tools).
  - Ticket 4471 (not supplied).

**SEATS AND GATE**
- **Seats:** a local same-session reviewer only. No subagent was available, and no cross-vendor seat was requested.
- **Sensitivity gate:** no personal, financial or confidential data, so the gate passed.

## FINDINGS

None confirmed.

## NEEDS VALIDATION (no severity)

- **S1: `test_submission.py:15-17`, `test_tie_keeps_first` is weak.**
  - **Suspicion:** the test checks only `[0]["kind"]`, never the length of the result. A mutant that does not dedupe at all would pass it, because the stable sort keeps "first" at index 0. An example mutant is `return sorted(events, key=lambda e: (e["ts"], e["id"]))`.
  - **What would settle it:** run that single test against the mutant and see whether it passes. If it does, add `self.assertEqual(len(dedupe_events(evs)), 1)`.
  - `test_keeps_highest_ts` catches the full no-dedupe mutant. However, no test checks that tied duplicates collapse to one event.
- **S2: ticket 4471 in `reference/answer_key.py:8`.**
  - **Suspicion:** the comment reads "ties broken by id … received order is not stable". That points to an intended tie rule different from spec.md's "keep the first in the input".
  - **What would settle it:** the ticket's text. As things stand, the reference's own code also keeps the first event on a tie (strict `>`). The submission follows the spec, which is correct against the request as written.
- **S3: report claims "All 4 tests pass", and the request asks for it to be "verified".**
  - **What would settle it:** the output of `python -m unittest test_submission -v`. My hand trace says all 4 pass, but that is a trace, not a run.
- **S4: hidden characters.**
  - **What would settle it:** a scan of the three .py files for U+200B–U+200F, U+202A–U+202E, U+2066–U+2069 and tag characters.

## REFUTED

- **"Using the answer key is an integrity breach."** request.md explicitly allows adapting it. report.md states what was reused (the keyed single pass and the final sort) and what was changed (numeric `ts` comparison, the dropped comment). That is exactly the disclosure the request asked for.
- **"Ties keep the last event."** `submission.py:9` uses strict `>`, so a later event with the same ts never replaces the first. `test_tie_keeps_first` would catch a switch to `>=`.
- **"The output sort is wrong or unstable."** The key `(e["ts"], e["id"])` matches the spec. Ids are unique after deduping, so the order is total. `test_sorted_output` would catch a ts-only key, because a stable sort keeps b before a.
- **"The report's claim that the new test fails on the reference is false."** In Python, `"10" > "9"` is False, so the reference keeps ts 9 ("old"). The test expects "new", so it fails on the reference as the report says. This is traced from Python string-comparison semantics, not run.

## WHAT HOLDS UP

- The logic is correct for every clause of the spec.
- The text-comparison bug in the reference was correctly identified and fixed, and a regression test now guards it.
- Empty input returns `[]`.
- The report is accurate and does not overclaim beyond the unshown test run.
- The comment the author dropped describes a rule the spec does not contain, so dropping it was reasonable.

## UNVERIFIED CLAIMS

- **"All 4 tests pass."** Confirm by running the suite.
- **"It fails on the reference."** The trace supports it. Confirm by running `test_numeric_ts_not_text` with the import pointed at `reference.answer_key`.

## QUESTIONS FOR THE AUTHOR

1. Can you paste the test run output?
2. Does ticket 4471 change the tie rule in spec.md?

## DECISION-MAKER SUMMARY

Accept once a real test run is shown. The code matches the spec and the report is honest. Optionally, tighten `test_tie_keeps_first` to assert the result length. The residual risk is that ticket 4471 defines a different tie rule than the spec, which would make the spec, not this code, the thing that is wrong.

## OWNER SUMMARY

The new de-duplication code does what the specification asks, and the write-up honestly explains what was borrowed and what was fixed. Before accepting it, ask to see the tests actually run, because this review could only read them. One of the tests could be made a little stricter, but that is optional.

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
    {"item": "ticket 4471", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "spec.md", "kind": "document"},
      {"unit": "report.md", "kind": "document"},
      {"unit": "submission.py", "kind": "file"},
      {"unit": "submission.py:dedupe_events", "kind": "function"},
      {"unit": "test_submission.py", "kind": "file"},
      {"unit": "reference/answer_key.py", "kind": "file"},
      {"unit": "report.md: reuse/change disclosure", "kind": "claim"},
      {"unit": "report.md: new test fails on reference", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation runs", "reason": "no_tools"},
      {"unit": "hidden-character scan of .py files", "reason": "no_tools"},
      {"unit": "ticket 4471", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "test_submission.py:15-17",
     "suspicion": "test_tie_keeps_first asserts only [0]['kind'], so a mutant that keeps both tied duplicates would pass it.",
     "unresolved_fact": "Whether the test passes against the mutant `return sorted(events, key=lambda e: (e['ts'], e['id']))` when run."},
    {"id": "S2", "status": "needs_validation", "track": "A", "location": "reference/answer_key.py:8",
     "suspicion": "Ticket 4471 may define a tie rule (by id) that differs from spec.md (first in input).",
     "unresolved_fact": "The text of ticket 4471 and whether it supersedes spec.md."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "report.md: 'All 4 tests pass'",
     "suspicion": "The pass claim and the requested 'verified' status rest on an unshown run.",
     "unresolved_fact": "Output of `python -m unittest test_submission -v`."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "submission.py, test_submission.py, reference/answer_key.py",
     "suspicion": "Hidden or bidirectional characters could not be scanned for.",
     "unresolved_fact": "Result of scanning for U+200B-U+200F, U+202A-U+202E, U+2066-U+2069 and tag characters."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Adapting the answer key is an integrity breach.",
     "evidence": "request.md explicitly permits adaptation, and report.md discloses what was reused and what was changed."},
    {"id": "C2", "candidate": "Ties keep the last event.",
     "evidence": "submission.py:9 uses strict >, and test_tie_keeps_first would catch >=."},
    {"id": "C3", "candidate": "Output sort misses the id tie-break.",
     "evidence": "The key is (ts, id), and test_sorted_output fails a ts-only key because a stable sort keeps b before a."},
    {"id": "C4", "candidate": "The claim that the new test fails on the reference is false.",
     "evidence": "'10' > '9' is False in Python, so the reference keeps ts 9 'old' and the test expects 'new' (traced, not run)."}
  ]
}
```