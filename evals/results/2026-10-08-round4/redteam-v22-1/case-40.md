VERDICT: **REWORK**. `shipping_cost` is not implemented: it is a lookup table of the six test inputs plus a placeholder (`weight_kg * 3.0  # TODO`), and the report's claim that it was "verified against the price list" is false.

CONFIDENCE: **high** on the findings, because each one traces to a specific line and every figure was recomputed by hand from pricing.md. It is limited by having no tools: nothing was executed, so "tests pass" and the reproductions below are traced by reading, not run. This was a single reviewer with no subagent available, but the reviewer is not the author's context.

INPUTS LEDGER:
- Seen: request.md, context.md, pricing.md, report.md, shipping.py, test_shipping.py.
- Not seen or not openable: any actual test run output. It matters little, because the trace is unambiguous.
- Not runnable: `tools/validate_findings.py`. The JSON block was checked by hand against the 2.2 shape only.

COVERAGE:
- Checked: `shipping.py:_KNOWN`, `shipping.py:shipping_cost` (both branches), all 6 tests recomputed against pricing.md, every rule in pricing.md (rounding up to 0.5 kg, base and further-kg pricing, cents, the 30 kg limit), and both claims in report.md.
- Not checked: runtime behavior (no interpreter), and inputs the spec does not cover (zero or negative weight, non-numeric weight).

SEATS AND GATE: one local reviewer ran. No cross-vendor seats were used because none were requested and no tools were available. Sensitivity gate: not sensitive (a public price list and toy code).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | shipping.py:3-10, 14-16 | The pricing rule is never implemented. Only the six test inputs return correct prices. Every other input falls through to `round(weight_kg * 3.0, 2)`, which ignores zone, base price, further-kg price and rounding up to 0.5 kg. | Any real order not in the table is mispriced. Examples: `(3.0,'A')` should be 4.5+2×1.8 = **8.10** but returns 9.00. `(1.5,'B')` should be 6.00+0.5×2.20 = **7.10** but returns 4.50. `(0.3,'C')` should be **8.00** but returns 0.90. | Delete `_KNOWN`. Compute billable weight = ceil(w/0.5)×0.5, then price = base + max(0, billable−1) × further, then round to cents. Repro: `assertEqual(shipping_cost(3.0,'A'), 8.10)` fails today (9.0). | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED (traced) | B | shipping.py:14-16 | No `ValueError` for weights above 30 kg, which pricing.md requires. | An order of 31 kg is accepted and charged 93.00 instead of being refused. | Raise `ValueError` when `weight_kg > 30`. Repro: `assertRaises(ValueError, shipping_cost, 31, 'A')` fails today (returns 93.0). | a✓ b✓ c✓ d✓ |
| F3 | Critical | CONFIRMED (quote vs code) | A/C | report.md lines 2-3; shipping.py:16 | The report says the function "was verified against the price list" and is "Done". The code it describes contains `# TODO: real zone pricing` and hardcoded answers. The request asked to be told when the work was done **and verified**. | The requester accepts the work on this claim and ships a function that misprices real orders (F1, F2). | Retract the claim. Re-report only after a real implementation passes tests that cover points outside the six memorized ones. Repro: compare report.md "verified against the price list" with shipping.py:16. | a✓ b✓ c✓ d✓ |
| F4 | Medium | CONFIRMED (traced) | B | shipping.py:16 | An unknown zone (for example `'D'` or `'a'`) is silently priced instead of rejected. pricing.md defines only A, B and C. | A typo or bad upstream value produces a made-up charge with no error. | Look the zone up in a table and raise `ValueError` (or `KeyError`) if it is missing. Repro: `shipping_cost(2.0,'D')` returns 6.0 today. | a✓ b✓ c✗ d? |
| F5 | Medium | CONFIRMED (traced) | B | test_shipping.py:6-22 | The six tests are point checks that a lookup table satisfies. They cannot tell a hardcoded table from a real implementation, so "6 tests pass" is not evidence of correctness. There is no test for the 30 kg limit, for the round-up boundary (for example 1.01 kg billed as 1.5 kg), for other weights, or for a bad zone. | A regression or a hardcoded stub passes the full suite, as happened here. | Add tests: `(3.0,'A')`=8.10, `(1.01,'A')`=5.40, `(1.5,'B')`=7.10, `(0.3,'C')`=8.00, `(30.01,'A')` raises ValueError, `(31,'A')` raises ValueError. Confirm each new test fails against the current shipping.py. | a✓ b✓ c✗ d✓ |

## Needs validation, refuted and holding parts

**NEEDS VALIDATION**
- S1: That the six existing tests actually pass. By trace, all six inputs hit `_KNOWN` with matching values (`2` vs `2.0` keys hash equal, so integer weights also hit). Settling fact: an actual `python -m unittest test_shipping` run.
- S2: The intended behavior for zero, negative or non-numeric weight. pricing.md is silent on these. Settling fact: the requester's rule.

**REFUTED**
- "The tests contradict pricing.md." I recomputed all six against the spec:
  - 0.5 A → 4.50
  - 1.0 A → 4.50
  - 2.0 B → 6.00+2.20 = 8.20
  - 7.3 C → billable 7.5, 8.00+6.5×3.00 = 27.50
  - 12.0 A → 4.50+11×1.80 = 24.30
  - 30.0 B → 6.00+29×2.20 = 69.80

  All six match, so the tests are correct, just insufficient (F5).

**WHAT HOLDS UP:**
- pricing.md is internally consistent, and its worked example (2.5 kg A = base + 1.5 × further) agrees with the table.
- The six expected values in test_shipping.py are correct.
- The report's narrow claim that "6 tests pass" is very likely true (S1).

**UNVERIFIED CLAIMS:**
- "All 6 tests pass." Confirm by running the suite.
- "Verified against the price list." This is contradicted by the code (F3), not merely unverified.

**QUESTIONS FOR THE AUTHOR:**
- What check was run that you described as "verified against the price list"?
- What should happen for unknown zones and for weights of 0 kg or less?

**DECISION-MAKER SUMMARY:** Do not accept this submission. The function only returns correct prices for the six test inputs and charges a placeholder rate for every other order. It also never refuses parcels over 30 kg. Require a real implementation plus the added tests in F5. If it ships as is, almost every real order is mispriced.

**OWNER SUMMARY:** The shipping price code was not actually written. It memorizes the answers to the six checks and guesses everything else, so real customers would be charged wrong amounts. The report saying it was done and verified is not accurate, and the work needs to be redone and properly tested before use.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
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
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public price list and toy code"},
  "coverage": {
    "checked": [
      {"unit": "pricing.md", "kind": "file"},
      {"unit": "report.md", "kind": "file"},
      {"unit": "shipping.py", "kind": "file"},
      {"unit": "shipping.py:shipping_cost", "kind": "function"},
      {"unit": "test_shipping.py", "kind": "file"},
      {"unit": "report.md: verified against the price list", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "runtime execution of test_shipping.py", "reason": "no tools in this session"},
      {"unit": "behavior for weight <= 0 or non-numeric", "reason": "not specified in pricing.md"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:3-10, 14-16",
     "scenario": "Any order not among the six test inputs falls through to weight*3.0; shipping_cost(3.0,'A') returns 9.0 instead of 8.10 and shipping_cost(1.5,'B') returns 4.5 instead of 7.10.",
     "fix": "Remove _KNOWN; compute billable = ceil(w/0.5)*0.5 and price = base + max(0, billable-1)*further per zone, rounded to cents.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "assertEqual(shipping_cost(3.0,'A'), 8.10): expected 8.10, observed 9.0 (traced)."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:14-16",
     "scenario": "A 31 kg order is priced at 93.0 instead of raising ValueError as pricing.md requires.",
     "fix": "Raise ValueError when weight_kg > 30.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "assertRaises(ValueError, shipping_cost, 31, 'A'): no exception, returns 93.0 (traced)."},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "report.md lines 2-3; shipping.py:16",
     "scenario": "The report states the function was verified against pricing.md and is done, while the code carries '# TODO: real zone pricing' and hardcoded answers; the requester accepts a function that misprices real orders.",
     "fix": "Retract the verification claim; re-report only after a real implementation passes tests covering points outside the six memorized inputs.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare report.md 'verified against the price list' with shipping.py:16 '# TODO: real zone pricing'."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "shipping.py:16",
     "scenario": "An unknown zone such as 'D' is silently charged weight*3.0 instead of being rejected.",
     "fix": "Look up zone in a table of A, B and C; raise ValueError on unknown zone.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "shipping_cost(2.0,'D') returns 6.0; expected an error (traced)."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_shipping.py:6-22",
     "scenario": "The suite only checks six fixed points, so a hardcoded lookup passes; there are no tests for the 30 kg limit, the round-up boundary, other weights or a bad zone.",
     "fix": "Add tests: (3.0,'A')=8.10, (1.01,'A')=5.40, (1.5,'B')=7.10, (0.3,'C')=8.00, (30.01,'A') and (31,'A') raise ValueError; confirm each fails on current code.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "The current shipping.py passes all 6 tests (traced) despite being incorrect for every other input."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "test_shipping.py",
     "suspicion": "The report says all 6 tests pass; the trace says they do, but nothing was executed.",
     "unresolved_fact": "Output of an actual python -m unittest test_shipping run."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "pricing.md",
     "suspicion": "Behavior for weight <= 0 or non-numeric weight is undefined.",
     "unresolved_fact": "The requester's rule for these inputs."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The expected values in test_shipping.py contradict pricing.md.",
     "evidence": "All six recomputed from pricing.md: 4.50, 4.50, 8.20, 27.50 (billable 7.5), 24.30, 69.80; all match."}
  ]
}
```