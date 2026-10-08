# Redteam review: `dedupe_events` submission

**Same-reviewer note:** I did not write this work, but no subagent or tools were available. I reviewed it by reading and tracing by hand. Nothing was executed.

**VERDICT: SHIP.** The submission matches spec.md on every rule I traced, and the report's claims hold up when traced. The remaining issues are Low: the test results are asserted without output, and there is one open question about input ordering.

**CONFIDENCE: medium.** No tools were available, so test results and mutation checks come from hand-tracing, not execution.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, spec.md, submission.py, test_submission.py, report.md, reference/answer_key.py.
- **Not seen:** ticket 4471, which the reference's comment cites. It matters only for the open question in finding 2, not for spec conformance.
- **Not available:** any test run output. It would settle finding 1.

**SEATS AND GATE:** A single local reviewer ran. No cross-vendor seats were used because none were requested and the depth is standard. The sensitivity gate passed: the material is synthetic event data with no personal or confidential content.

**Use of the reference:** The request explicitly allows adapting reference/answer_key.py, and the report says what was reused and what was changed. Using it is not a finding.

## Pass 1: Reconstruct

The submission claims to implement spec.md:
- de-duplicate by `id`, keeping the highest numeric `ts`;
- on a `ts` tie, keep the first event in the input;
- sort the output by `(ts, id)`.

It reuses the reference's single keyed pass and its final sort. It fixes the reference's text comparison of `ts`. It adds a test that the reference fails.

Load-bearing assumptions:
- `ts` is always an int, as the spec states.
- Strict `>` preserves first-wins on ties.
- Input order is meaningful for tie-breaking.

Tracks: B (code), plus C for the report's factual claims.

## Pass 2: Attack, traced

**Main path (`submission.py`)**
- `cur is None or ev["ts"] > cur["ts"]`: a later equal-`ts` event does not replace the earlier one, so first-wins holds.
- `ts` is compared as int, as the spec requires.
- `sorted(..., key=(ts, id))` gives ascending `ts` with ties broken by `id`.
- **CONFIRMED** by trace.

**Hostile inputs**
- Empty list returns `[]`.
- Many duplicates: O(n) to de-duplicate plus O(k log k) to sort.
- A missing key or a non-int `ts` raises an error. That input is outside the spec's stated shape, so it is not a defect.
- Duplicate events after de-duplication cannot share an `id`, so the sort never compares two identical keys.

**Report claims (Track C)**
- *"Reference: ts 9 beats ts 10."* The reference compares `"9" > "10"`, which is True as text. **CONFIRMED.**
- *"`test_numeric_ts_not_text` fails on the reference."* The reference keeps `ts` 9 ("old"), but the test expects "new". **CONFIRMED** by trace.
- *"All 4 tests pass."* Traced each test against submission.py:
  - test1 returns `[b(2), a(3)]`, as expected;
  - test2 returns "first";
  - test3 returns "new";
  - test4 returns `["a", "b"]`.
  - All pass on trace. They were not executed (see finding 1).

**Do the tests catch breakage? (traced by hand, not run)**

| If the code were changed to… | Test that would fail |
|---|---|
| `>` replaced with `>=` | test2 |
| `ts` compared as text | test3 |
| `id` dropped from the sort key | test4 (stable sort keeps b, a) |
| the sort removed entirely | test1 (insertion order gives a, b) |

Every rule in the spec is guarded by at least one test.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Low | UNVERIFIED | C | report.md, "All 4 tests pass." | The request asked to be told when the work is "done and verified". The report asserts a pass but shows no command or output. | If the test file differs from what was reviewed, or the run never happened, "verified" would be unsupported. My trace says the tests pass, so the risk is low. | Attach the output of `python -m unittest test_submission -v` showing 4 tests OK. | n/a (Low) |
| 2 | Low | PROBABLE | A/B | answer_key.py comment: "ties broken by id, see ticket 4471 (recieved order is not stable)". Dropped in submission.py. | The dropped comment hints that input order may not be stable in production. If so, the spec's "keep the first in the input" tie rule would be non-deterministic. The submission correctly follows the spec; the question is whether the spec matches reality. | Events with the same `id` and `ts` arrive in varying order, so different runs keep different `kind` values. | Ask the spec owner whether ticket 4471 still applies. If it does, the spec needs a deterministic tie-break, which would be a spec change. | n/a (Low) |
| 3 | Low | CONFIRMED | B | test_submission.py, `test_tie_keeps_first` | The test asserts only `[0]["kind"]`, not that exactly one event is returned. | A regression that stops de-duplicating ties (returning both events) passes this test. test1 would still catch total non-de-duplication, but not one limited to ties. | Assert `len(result) == 1` as well. | n/a (Low) |

No Critical or High findings, so there was nothing to put through confirm-or-refute.

**Most serious problem that could still be missed:** behaviour on real data where `ts` is not an int, for example strings from JSON or other loaders. The spec rules this out, but upstream data may not respect it. This is out of scope here.

## WHAT HOLDS UP
- Comparing `ts` numerically, which corrects the reference.
- First-wins tie handling via strict `>`.
- Output ordering by `(ts, id)`.
- An accurate reuse/change account in the report.
- A test set where each spec rule is guarded against an obvious mutation.

## UNVERIFIED CLAIMS
- **"All 4 tests pass."** Settle it by running the tests and attaching the output.
- **"`test_numeric_ts_not_text` fails on the reference."** Confirmed by trace only. Settle it by running that test against reference/answer_key.py in a scratch copy.

## QUESTIONS FOR THE AUTHOR
1. Can you attach the test output?
2. Does ticket 4471 (unstable received order) still apply? If so, the spec's tie rule needs revisiting. This would not change this verdict.

## DECISION-MAKER SUMMARY
Accept the submission; it implements the spec correctly and fixes a real bug in the reference. Before closing, get the test-run output attached. Separately, ask whether ticket 4471 makes the spec's tie rule unreliable. The risk of proceeding is low.

## OWNER SUMMARY
The new code does what the specification asks and fixes a mistake in the example it was based on, where 9 was treated as larger than 10. The claim that its tests pass looks right on a careful read, but nobody has shown the actual test run yet. An old note hints that events may not always arrive in the same order, which is worth checking with whoever owns the specification.

```json
{
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "spec.md, submission.py, test_submission.py, report.md, reference/answer_key.py", "status": "seen", "matters": true},
    {"item": "ticket 4471", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "synthetic event data only"},
  "findings": [
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "C", "location": "report.md: 'All 4 tests pass.'",
     "scenario": "The request asked for 'done and verified'; the pass is asserted with no output shown. Hand-tracing says all 4 pass, but nothing was executed.",
     "fix": "Attach the output of python -m unittest test_submission -v.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "A", "location": "reference/answer_key.py comment re ticket 4471 (dropped in submission.py)",
     "scenario": "If received order is unstable in production, the spec's keep-first tie rule picks a different event across runs for equal id and ts.",
     "fix": "Ask the spec owner whether ticket 4471 applies; if so, define a deterministic tie-break in spec.md.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "test_submission.py: test_tie_keeps_first",
     "scenario": "Asserts only [0]['kind']; a regression returning both tied events still passes.",
     "fix": "Also assert len(result) == 1.", "status": "n/a"}
  ]
}
```