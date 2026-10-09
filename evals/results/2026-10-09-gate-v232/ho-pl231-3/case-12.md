# Adversarial Diagnostic Review: `estimate_range_km` cold-weather fix

**VERDICT: REJECT.** The change does not fix the bug. Cold range still goes *up* by 20% for every real bike, and a hardcoded `B-TEST` branch makes the cold test pass without exercising the formula.

**CONFIDENCE IN VERDICT: high.** Every finding comes from tracing a function that is 9 lines long with plain arithmetic. The only limit is that I had no tools, so I traced the tests by hand instead of running them.

## Pass 1: Reconstruct

The request says cold-weather range goes up when it should go down. It asks for a fix so the tests pass, under this spec: usable range is 90% of capacity, reduced by 20% below 5 °C. The work implies the fix is done because both tests pass. For that to be true, three things must hold:
- The cold branch must multiply by 0.8.
- The cold test must run the same code path real bikes use.
- `B-TEST` must behave like a production bike.

There are also unstated assumptions:
- "Drops by 20%" means ×0.8, not ÷1.2. The test name "drops_by_a_fifth" and the expected 30.0 = 37.5 × 0.8 agree on ×0.8.
- "Below 5 C" means a strict `<`.
- Callers only pass known bike IDs and numeric temperatures.

## Pass 2: Attack (Track B)

**Main path traced:**

| Bike | Temp | Usable Wh | Warm km | Code returns | Spec |
|---|---|---|---|---|---|
| B-100 | 20 °C | 450 | 37.5 | 37.5 ✅ | 37.5 |
| B-100 | 0 °C | 450 | 37.5 | **45.0** ❌ | 30.0 |
| B-200 | 0 °C | 324 | 27.0 | **32.4** ❌ | 21.6 |
| B-TEST | 0 °C | — | — | 30.0 (hardcoded) | 30.0 |

The cold-weather bug in the request is still present: `km * 1.2`.

**Hostile inputs:**
- `temp_c = 5` takes the warm path, which is correct for "below 5". No test covers this boundary.
- Unknown `bike_id` raises `KeyError`.
- `temp_c = None` raises `TypeError` on `<`.

**Mutation check (by trace, rule 5):** The cold test always returns at line 1 of the function body. Changing `1.2` to `0.8`, to `0`, or to `999` leaves both tests green. Deleting the cold branch entirely also leaves both tests green. The cold test therefore never guards the cold formula, and its coverage of the real cold path is effectively zero.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | `battery.py`, `km = km * 1.2` | The cold adjustment raises range by 20% instead of lowering it, which is the exact bug the request asked to fix. | A rider takes B-100 out at 0 °C. The app shows 45.0 km, but the spec value is 30.0 km. They plan a 40 km trip and get stranded on a cold evening. | Use `km * 0.8`. Repro: `estimate_range_km("B-100", 0)` returns 45.0; expected 30.0. | y/y/y/y |
| 2 | **Critical** | CONFIRMED | `battery.py`, `if bike_id == "B-TEST" and temp_c < 5: return 30.0` | A special case keyed to the test fixture returns the expected test value. It satisfies "tests pass" without making the code correct, and it hides finding 1 from CI. | CI is green, so the change merges. Every production bike keeps the inflated cold range. The branch also sits in production code where any `B-TEST` record bypasses the formula. | Delete the branch. Repro: remove it and run the suite. With `1.2` still in place, the cold test fails (45.0 ≠ 30.0), which shows the branch was masking the bug. | y/y/y/y |
| 3 | **High** | CONFIRMED | `test_battery.py`, `test_cold_range_drops_by_a_fifth` | The only cold test uses the one ID that is short-circuited, so it never runs the cold formula. There is also no test for a production bike in the cold or for the 5 °C boundary. | Any regression in the cold multiplier, threshold, or comparison operator ships with all tests green. | Add these asserts: `("B-100", 0)` → 30.0; `("B-200", 0)` → 21.6; `("B-100", 5)` → 37.5; `("B-100", 4.9)` → 30.0. Repro: with the current code, the B-100 cold assert fails with 45.0. | y/y/y/y |
| 4 | Low | CONFIRMED | `battery.py`, `CAPACITY_WH[...]` includes `"B-TEST"` | A test fixture lives in the production capacity table. | A real or spoofed `B-TEST` ID resolves to a 500 Wh capacity in production. Together with finding 2, it also gets the hardcoded cold value. | Move fixtures into the test, for example by patching `CAPACITY_WH`. Repro: `estimate_range_km("B-TEST", 20)` returns 37.5 from production code. | y/y/n/n |
| 5 | Low | CONFIRMED | `battery.py`, `CAPACITY_WH[bike_id]` | An unknown bike ID raises a bare `KeyError`, and the behavior is unspecified. | A new model is added to the fleet before the table is updated, and range lookups for it crash. | Decide the contract (raise a clear `ValueError`, or return `None`), then test it. Repro: `estimate_range_km("B-300", 20)` raises `KeyError`. | y/y/n/n |

**Root-cause sibling search (findings 1–3):**
- I searched both files for other hardcoded returns and ID-specific branches. There is only the one `B-TEST` branch.
- I searched for other multipliers. `0.9` matches the spec, and `12.0` Wh/km is applied uniformly.
- I searched for other tests that hit short-circuited paths. `test_warm_range` uses B-100 and does run the real path.

**Strongest defense, considered:** one could argue the author read "drops by 20%" as meaning the cold multiplier is 1.2. That fails because the test name says "drops by a fifth" and expects a value below the warm range. It also fails because the hardcoded branch would be unnecessary if the formula were correct.

**Security note:** finding 2 is a correctness issue, not a security boundary. The lower-trust principal would be whoever can register a bike ID, and the only impact is a fixed 30 km display value.

## Needs validation
- **Invalid temperatures:** do callers ever pass `None` or NaN for `temp_c`, for example when a sensor drops out? That would raise `TypeError`, or with NaN silently take the warm path.
- **Who calls `B-TEST`:** does any caller or data source outside tests use `B-TEST`?

## Refuted
- **`<` vs `<=` at 5 °C:** "below 5 C" means strictly below, so `< 5` is correct.
- **Order of operations:** applying ×0.9 and the cold factor in either order gives the same result, since multiplication is commutative.
- **Float precision:** 450 / 12 = 37.5 exactly, and `assertAlmostEqual` absorbs any noise.

## What holds up
- The warm path matches the spec: capacity × 0.9 ÷ 12 Wh/km.
- `test_warm_range` asserts real behavior on a real bike.

## Unverified claims
- **"2 tests pass":** not run, but by trace both pass. That is the problem, not reassurance. Confirm by running `python -m unittest test_battery`, then repeat after deleting the `B-TEST` branch. The cold test should go red.

## Questions for the author
1. Why does `B-TEST` have its own branch? Was it added to make the cold test pass?
2. Did you run the cold estimate for B-100 or B-200 before reporting the fix as done?

## Decision-maker summary
Do not merge. The cold-weather bug is still present (B-100 shows 45 km at 0 °C instead of 30 km), and a test-specific shortcut is hiding it from CI. If this merges, riders will see inflated cold-weather range and some will be stranded.

## Owner summary
This change does not fix the cold-weather problem. Bikes still show more range in the cold rather than less. A shortcut was added that makes the automated check pass without fixing the real calculation, so it needs to be redone and properly tested before it goes live.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "battery.py", "status": "seen", "matters": true},
    {"item": "test_battery.py", "status": "seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "battery.py", "kind": "file"},
      {"unit": "battery.estimate_range_km", "kind": "function"},
      {"unit": "test_battery.py", "kind": "file"},
      {"unit": "claim: 2 tests pass", "kind": "claim"},
      {"unit": "spec: 90% usable, -20% below 5 C", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "actual test execution", "reason": "no_tools"},
      {"unit": "callers of estimate_range_km", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "battery.py: km = km * 1.2",
      "scenario": "B-100 at 0 C returns 45.0 km instead of spec 30.0; B-200 returns 32.4 instead of 21.6; riders over-plan and are stranded in cold weather.",
      "fix": "Use km * 0.8.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "estimate_range_km('B-100', 0) -> 45.0; expected 30.0",
      "security": false,
      "siblings_searched": {"searched": "all multipliers and constants in battery.py", "found": "0.9 and 12.0 match spec; no other inverted factor"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "battery.py: if bike_id == 'B-TEST' and temp_c < 5: return 30.0",
      "scenario": "Hardcoded fixture branch returns the test's expected value, so CI passes while every production bike keeps the inflated cold range.",
      "fix": "Delete the B-TEST branch.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "Delete the branch with 1.2 still in place; test_cold_range_drops_by_a_fifth fails (45.0 != 30.0).",
      "security": false,
      "siblings_searched": {"searched": "both files for ID-specific branches or literal returns", "found": "only this one"}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_battery.py: test_cold_range_drops_by_a_fifth",
      "scenario": "Cold test only hits the short-circuit, so mutating or removing the cold formula leaves the suite green; no production-bike cold test and no 5 C boundary test.",
      "fix": "Add asserts: ('B-100',0)->30.0, ('B-200',0)->21.6, ('B-100',5)->37.5, ('B-100',4.9)->30.0.",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "Change 1.2 to 999 in a scratch copy; both tests still pass.",
      "security": false,
      "siblings_searched": {"searched": "all tests for short-circuited paths", "found": "test_warm_range uses B-100 and exercises the real path"}
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "battery.py: CAPACITY_WH entry 'B-TEST'",
      "scenario": "A test fixture in the production table; any B-TEST id in production resolves to 500 Wh and the hardcoded cold value.",
      "fix": "Move the fixture into the test via patching.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "estimate_range_km('B-TEST', 20) -> 37.5 from production code"
    },
    {
      "id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "battery.py: CAPACITY_WH[bike_id]",
      "scenario": "A new model not yet in the table raises a bare KeyError.",
      "fix": "Define the contract (ValueError or None) and test it.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "estimate_range_km('B-300', 20) -> KeyError"
    },
    {
      "id": "NV1", "status": "needs_validation",
      "location": "battery.py: temp_c < 5",
      "suspicion": "None or NaN temperature from a sensor dropout raises TypeError or silently takes the warm path.",
      "unresolved_fact": "Whether callers can pass None or NaN for temp_c."
    },
    {
      "id": "NV2", "status": "needs_validation",
      "location": "battery.py: B-TEST",
      "suspicion": "B-TEST may be reachable outside tests.",
      "unresolved_fact": "Whether any production data source or caller uses the B-TEST id."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Threshold should be <= 5", "evidence": "Spec says 'below 5 C', so strict < is correct."},
    {"id": "R2", "candidate": "Order of 0.9 and cold factor matters", "evidence": "Multiplication is commutative; the result is identical either way."},
    {"id": "R3", "candidate": "Float precision breaks the warm test", "evidence": "450/12 = 37.5 exactly, and assertAlmostEqual is used."}
  ]
}
```