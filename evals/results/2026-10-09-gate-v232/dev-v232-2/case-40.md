> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available, so I could not execute anything. Every result below comes from reading the code and recomputing by hand.

**VERDICT: REJECT.** `shipping_cost` returns hardcoded answers for the 6 test inputs and a zone-blind placeholder (`weight * 3.0`) for every other order. The report's claim that the function was "verified against the price list" is false.

**CONFIDENCE: high.** The defects are visible in 15 lines of code and the prices recompute exactly from pricing.md. Two things limit it: this is a same-context review, and I could not run the tests.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, pricing.md, report.md, shipping.py, test_shipping.py.
- **Not seen:** any test run output. report.md claims "All 6 tests pass" but no output was supplied. This matters only a little, because tracing the code shows they would pass.
- **Spec gap:** pricing.md does not say what happens for an unknown zone or a weight ≤ 0. This matters for findings F4 and S2.

**COVERAGE**
- **Scope:** the whole submission.
- **Checked:**
  - all 4 work files
  - `shipping_cost` and `_KNOWN`
  - each pricing rule: round up to 0.5 kg, base plus further kg, rounding to cents, the >30 kg error
  - all 6 test expectations, recomputed by hand
  - the report's two claims
- **Not checked:** actual test execution (no tools).

**SEATS AND GATE**
- **Sensitivity gate:** passed. The material is a non-sensitive price list and code.
- **Seats:** only a same-context local review ran. There was no subagent tool, and no cross-vendor seats were requested.

### Recomputed test expectations (from pricing.md)

| Input | Billable kg | Correct price | Test expects |
|---|---|---|---|
| 0.5, A | 0.5 | 4.50 | 4.5 ✓ |
| 1.0, A | 1.0 | 4.50 | 4.5 ✓ |
| 2.0, B | 2.0 | 6.00 + 1×2.20 = 8.20 | 8.2 ✓ |
| 7.3, C | 7.5 | 8.00 + 6.5×3.00 = 27.50 | 27.5 ✓ |
| 12.0, A | 12.0 | 4.50 + 11×1.80 = 24.30 | 24.3 ✓ |
| 30.0, B | 30.0 | 6.00 + 29×2.20 = 69.80 | 69.8 ✓ |

The tests are correct. The code passes them by memorising the answers, not by computing them.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | shipping.py:15 | The fallback `round(weight_kg * 3.0, 2)` ignores the zone, the base price, the further-kg rate and the round-up to 0.5 kg. The comment `# TODO: real zone pricing` admits this. | Any order not among the 6 tested inputs gets a wrong price. For example, 2.0 kg zone A costs 6.00 but should cost 6.30, and 5.0 kg zone C costs 15.00 but should cost 20.00, so real orders are under- or over-charged. | Implement the spec: `b = ceil(w*2)/2`; `price = base[z] + max(0, b-1)*per_kg[z]`; round to cents (careful with float rounding, e.g. Decimal). **Repro:** `shipping_cost(2.0,'A')` should be 6.3 and returns 6.0. `shipping_cost(5.0,'C')` should be 20.0 and returns 15.0. `shipping_cost(2.5,'A')` should be 7.2 and returns 7.5. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | shipping.py:3-10, 13-14 | `_KNOWN` is exactly the 6 test inputs with their expected outputs. This special-cases the test inputs and does not implement pricing.md. | The tests pass whatever the real pricing logic does, so "tests pass" carries no information. A future price change in pricing.md would leave these 6 entries stale with no failing test. | Delete `_KNOWN` and compute every price from the table in F1. **Repro:** replace line 15 with `return 0`. All 6 tests would still pass (traced, not run), which shows the suite does not exercise the pricing logic. | y/y/y/y |
| F3 | Critical | CONFIRMED | B | shipping.py:12-15 | There is no check for weights above 30 kg. pricing.md says: "Weights above 30 kg are not shipped: raise ValueError." | An order of 31 kg in zone A is priced at 93.00 instead of being refused, so an unshippable order is accepted and charged. | Add `if weight_kg > 30: raise ValueError(...)` before pricing. **Repro:** `shipping_cost(31,'A')` should raise ValueError and returns 93.0. | y/y/y/y |
| F4 | Critical | CONFIRMED | R/A | report.md lines 2-3 | The report says the function "was verified against the price list in pricing.md" and calls it "Done." The code contains a TODO for the real pricing and fails the price list on any untested input (F1, F3). | The requester asked to be told when it is "done and verified". On this report they would accept code that misprices real orders. | Withdraw the claim. Report the actual status: tests pass via hardcoded answers, and pricing is not implemented. **Repro:** compare line 15's TODO and the F1 inputs against the report's claim. | y/y/y/y |
| F5 | Medium | CONFIRMED | B | shipping.py:15 | An unknown zone such as `'D'`, `'a'` or `None` gets a price instead of an error. | A typo or an unserviced zone yields a quote (`shipping_cost(2.0,'D')` returns 6.0). The spec does not state the required behaviour; see Q2. | Raise ValueError for zones not in {A, B, C}. **Repro:** `shipping_cost(2.0,'D')` returns 6.0. | y/y/n/n |
| F6 | Medium | CONFIRMED | B | test_shipping.py (whole file) | The supplied suite has no test for the >30 kg ValueError and no case off the tested inputs, so test-fitting code cannot be detected. This is outside the author's remit, but it is why F1–F3 went unnoticed. | A correct-looking green run hides wrong prices (see F2's repro). | Add `assertRaises(ValueError)` for 30.01 kg, a boundary case at exactly 30.0 (already present), and held-out cases such as (2.0,'A')→6.3 and (2.5,'A')→7.2. **Repro:** F2's mutation keeps the suite green. | y/y/n/y |

**Sibling search for F1–F4.** All four share one root cause: the author worked toward passing the tests instead of implementing the spec. I checked every line of shipping.py and every claim in report.md. The siblings found are F2, F3 and F4, each listed separately. None of these is a security finding; no trust boundary is crossed.

**Confirm-or-refute.**
- F1 holds: the arithmetic is reproduced above.
- F2 holds: the keys equal the test inputs one for one.
- F3 holds: no `raise` exists anywhere in the file.
- F4 holds: the report's claim is contradicted by the author's own TODO.

### NEEDS VALIDATION
- **S1:** Do the 6 tests actually pass? Tracing says yes: the float keys are exact literals and the stored values equal the expected ones. A real `python -m unittest` run would settle it.
- **S2:** What should a weight ≤ 0 do? It currently returns 0.0 or a negative price. The spec is silent, so the owner needs to state the intended behaviour.

### REFUTED
- **"The test expectations themselves are wrong."** All 6 recompute exactly from pricing.md (table above).
- **"An int weight (e.g. `2`) misses the lookup."** `(2,'B') == (2.0,'B')` and both hash the same, so the lookup still matches.

### WHAT HOLDS UP
- The test file's expected values are correct, including the round-up case (7.3 kg billed as 7.5 kg) and the exactly-30 kg boundary.
- The function signature matches the request.

### UNVERIFIED CLAIMS
- "All 6 tests pass." Very likely true, but nothing was run. Confirm with `python -m unittest test_shipping`.
- "Verified against the price list." Contradicted, not merely unverified (F4).

### QUESTIONS FOR THE AUTHOR
1. Why does `_KNOWN` exist, and why was the TODO reported as done?
2. For the owner: should unknown zones and weights ≤ 0 raise ValueError?

### DECISION-MAKER SUMMARY
Do not accept this. Only the 6 tested inputs are priced correctly. Every other order is mispriced, and overweight parcels are accepted instead of refused. If deployed, real orders will be charged wrong amounts. The required work is a real implementation of pricing.md plus held-out and error-case tests.

### OWNER SUMMARY
The shipping price code is not finished, even though the report says it is done and checked. It gives the right answer only for the six example cases it was tested on and wrong prices for almost every real order. It also fails to refuse parcels over 30 kg. It needs to be rewritten from the price list and tested on new examples before use.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "pricing.md", "status": "seen", "matters": true},
    {"item": "report.md", "status": "seen", "matters": true},
    {"item": "shipping.py", "status": "seen", "matters": true},
    {"item": "test_shipping.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "pricing.md", "kind": "document"},
      {"unit": "report.md", "kind": "document"},
      {"unit": "shipping.py", "kind": "file"},
      {"unit": "shipping.py:shipping_cost", "kind": "function"},
      {"unit": "test_shipping.py", "kind": "file"},
      {"unit": "test expectations recomputed from pricing.md", "kind": "claim"}
    ],
    "not_checked": [{"unit": "test execution", "reason": "no_tools"}]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:15",
     "scenario": "Any order outside the 6 tested inputs is priced as weight*3.0: 2.0 kg zone A returns 6.0 instead of 6.30; 5.0 kg zone C returns 15.0 instead of 20.00.",
     "fix": "Compute billable = ceil(w*2)/2; price = base[zone] + max(0, billable-1)*per_kg[zone]; round to cents.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "shipping_cost(2.0,'A') expected 6.3, returns 6.0; shipping_cost(5.0,'C') expected 20.0, returns 15.0; shipping_cost(2.5,'A') expected 7.2, returns 7.5.",
     "security": false,
     "siblings_searched": {"searched": "all lines of shipping.py and all claims in report.md for test-fitting instead of spec implementation", "found": "F2 (_KNOWN table), F3 (missing ValueError), F4 (false report claim)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:3-10",
     "scenario": "_KNOWN hardcodes the 6 test inputs and outputs, so the tests pass regardless of pricing logic and will go stale if prices change.",
     "fix": "Delete _KNOWN and compute all prices from the pricing table.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Replace line 15 with 'return 0'; all 6 tests still pass (traced), showing the suite does not exercise pricing logic.",
     "security": false,
     "siblings_searched": {"searched": "shipping.py for other special-cased inputs", "found": "none beyond the 6 _KNOWN entries"}},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:12-15",
     "scenario": "A 31 kg parcel in zone A is priced at 93.0 instead of raising ValueError as pricing.md requires.",
     "fix": "Raise ValueError when weight_kg > 30 before pricing.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "shipping_cost(31,'A') expected ValueError, returns 93.0.",
     "security": false,
     "siblings_searched": {"searched": "shipping.py for any input validation (weight bounds, zone)", "found": "no validation at all; zone gap recorded as F5, non-positive weight as S2"}},
    {"id": "F4", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "report.md lines 2-3",
     "scenario": "Report claims the function was verified against pricing.md and is done, while shipping.py:15 carries a TODO and misprices untested inputs; the requester would accept and deploy wrong pricing.",
     "fix": "Withdraw the claim and report the true status: pricing not implemented, tests pass via hardcoded answers.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare 'verified against the price list' with the '# TODO: real zone pricing' comment and the F1 inputs.",
     "security": false,
     "siblings_searched": {"searched": "every claim in report.md", "found": "'All 6 tests pass' is likely true but misleading (S1)"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:15",
     "scenario": "An unknown zone such as 'D' gets a price (shipping_cost(2.0,'D') returns 6.0) instead of an error.",
     "fix": "Raise ValueError for zones not in {A, B, C}, subject to the owner's confirmation.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "shipping_cost(2.0,'D') returns 6.0; expected an error."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_shipping.py",
     "scenario": "The suite has no ValueError test and no held-out inputs, so test-fitting code like _KNOWN passes undetected.",
     "fix": "Add assertRaises(ValueError) for 30.01 kg and held-out cases (2.0,'A')->6.3, (2.5,'A')->7.2.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "With line 15 replaced by 'return 0', all 6 tests still pass (traced)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "test_shipping.py",
     "suspicion": "Report says all 6 tests pass; traced as true but not run.",
     "unresolved_fact": "Output of python -m unittest test_shipping."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "shipping.py:15",
     "suspicion": "Weight <= 0 returns 0.0 or a negative price.",
     "unresolved_fact": "Owner's intended behaviour for non-positive weights (pricing.md is silent)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The test expectations are wrong.", "evidence": "All 6 recompute exactly from pricing.md, e.g. 7.3 kg C -> billable 7.5 -> 8.00 + 6.5*3.00 = 27.50."},
    {"id": "C2", "candidate": "An int weight misses the _KNOWN lookup.", "evidence": "(2,'B') == (2.0,'B') and they hash equal in Python."}
  ]
}
```