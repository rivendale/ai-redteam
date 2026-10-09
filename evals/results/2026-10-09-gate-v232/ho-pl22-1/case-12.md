# Adversarial Diagnostic Review: `estimate_range_km` cold-weather fix

No tools were available in this session, so nothing was executed. Every CONFIRMED finding comes from tracing the pasted code by hand. The arithmetic is deterministic, so these traces are exact.

## Pass 1: Reconstruct

The work claims to fix `estimate_range_km` so that cold-weather range goes down, and it presents the two passing tests as evidence. The spec says usable range is 90% of capacity, divided by 12 Wh/km, then multiplied by 0.8 below 5 °C. For the fix to be correct, three things must hold:
- Every bike in `CAPACITY_WH` gets the 0.8 cold factor.
- The cold test actually exercises the general formula.
- No bike-specific shortcuts exist.

There is also an unstated assumption: that `B-TEST` and its special case have no effect on production bikes.

## Pass 2: Attack (Track B)

**Main path trace for B-100 at 0 °C.** 500 × 0.9 = 450 Wh, and 450 / 12 = 37.5 km. Then `temp_c < 5` is true, so 37.5 × **1.2** = **45.0 km**. The spec value is 37.5 × 0.8 = **30.0 km**. The reported bug is still present: cold range still goes up, by 20% instead of down by 20%.

**Trace for B-200 at 0 °C.** 360 × 0.9 / 12 = 27.0, and 27.0 × 1.2 = **32.4 km**. The spec value is **21.6 km**, so the estimate is 10.8 km too high, exactly 1.5× the true figure.

**Trace for B-TEST at 0 °C.** The first branch returns the hard-coded `30.0` before the formula runs. That literal is exactly what the test expects, which is why the test passes. The "fix" teaches to the test.

**Mutation reasoning (rule 5).** Suppose the cold multiplier were changed to any value, including the correct 0.8 or the buggy 1.2. `test_cold_range_drops_by_a_fifth` would stay green, because B-TEST never reaches that line. So the cold test cannot fail for the bug it is named after. `test_warm_range` does guard the 0.9 factor and `CONSUMPTION_WH_PER_KM`, because changing either one moves 37.5.

**Hostile inputs:**
- Unknown `bike_id` raises a bare `KeyError`. That is acceptable fail-loud behavior, but it is untested.
- `temp_c=None` raises `TypeError` on the comparison.
- `temp_c=float('nan')`: `nan < 5` is False, so the function silently returns warm range, which is an overestimate.
- The boundary at exactly 5 °C counts as warm. That matches "below 5 C".

## Pass 3: Self-check

Every finding below is tied to a specific line and a concrete trace. The NaN and None findings depend on what the upstream temperature feed can actually send, so I have downgraded them to Low.

The most serious problem that could still be hiding is outside this file: any caller or cache that already shows riders the inflated cold figures. Those numbers would need correcting after the fix.

---

**VERDICT: REJECT.** The bug the user asked to fix is still there for every real bike, and the only cold test passes because of a hard-coded special case written to match it.

**CONFIDENCE IN VERDICT: high.** The traces are exact arithmetic over a 10-line function. The only limit is that I did not execute anything.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `battery.py`: `km = km * 1.2` | The cold factor still increases range. The spec requires ×0.8. | A rider on B-100 at 0 °C is shown 45.0 km when the spec gives 30.0. On B-200 they see 32.4 km instead of 21.6. They plan a trip the battery cannot cover and are stranded on a cold evening. | Change to `km = km * 0.8`. |
| 2 | Critical | CONFIRMED | `battery.py`: `if bike_id == "B-TEST" and temp_c < 5: return 30.0` | A hard-coded return for the test bike makes the cold test pass without exercising the formula. This is test-gaming presented as a fix. | Every production bike takes the broken path, CI is green, and the merge ships the original bug. | Delete the branch. Because B-TEST has 500 Wh, the correct general formula already yields 30.0 for it. |
| 3 | High | CONFIRMED | `test_battery.py`: `test_cold_range_drops_by_a_fifth` | The only cold test uses B-TEST, which short-circuits, so it can never detect a wrong multiplier. | Mutating `1.2` to `0.8`, `1.0`, or anything else leaves the test green. | Add cold tests for real IDs, for example `("B-100", 0) → 30.0` and `("B-200", 0) → 21.6`. Confirm they fail on the current code before fixing it. |
| 4 | Medium | CONFIRMED | `test_battery.py` | Boundary behavior is untested. | A future change from `<` to `<=` would silently treat 5 °C as cold, and nothing would catch it. | Add `("B-100", 5) → 37.5` and `("B-100", 4.9) → 30.0`. |
| 5 | Medium | PROBABLE | `battery.py`: `CAPACITY_WH["B-TEST"]` | A test fixture lives in the production capacity table. Combined with #2, it is a production code path keyed on a test ID. | If B-TEST appears in production data or a demo, it gets special-cased output. It also invites more test-only branches later. | Remove B-TEST from the production table and inject or patch capacity in tests. Alternatively, keep it with no special casing. |
| 6 | Low | PROBABLE | `battery.py`: `if temp_c < 5` | A NaN temperature evaluates as warm, so the function returns the higher range. | A sensor or weather feed returns NaN on a cold night, and the rider is shown full warm range. | Validate `temp_c` with `math.isnan`, and either raise or treat it as cold (the conservative choice). Add a test. |
| 7 | Low | CONFIRMED | `battery.py`: `CAPACITY_WH[bike_id]` | An unknown bike or a `None` temperature raises an unhandled exception. | A new model is added to the fleet but not to the table, and the caller crashes or shows nothing. | Decide on the intended behavior: an explicit error or a safe default. Add a test for it. |

## What holds up

- The warm path is correct. 0.9 × capacity / 12 gives 37.5 for B-100, and `test_warm_range` genuinely guards both constants.
- Using a strict `< 5` matches "below 5 C".
- The function is pure and has no side effects, so the fix is low-risk once it is done correctly.

## Unverified claims

- **"Tests: 2 tests pass."** This is plausible from the trace: 37.5 is warm-correct and the hard-coded 30.0 matches the cold test. It was not run. To confirm, run `python -m unittest test_battery`.
- **"Fix so the tests pass."** The tests passing does not mean the fix is correct. The request asked to fix the bug, and the tests were a proxy for that.
- **Callers and caches showing range to riders are unreviewed.** It is not known whether previously displayed cold estimates need correcting. To settle this, grep for `estimate_range_km` call sites and any stored range values.

## Questions for the author

1. Why does B-TEST have a special case at all? Was it added only to make `test_cold_range_drops_by_a_fifth` pass?
2. Was the `1.2` multiplier left in place deliberately, and if so, on what basis?
3. What does the temperature source send when it has no reading (None, NaN, or a sentinel)?

## Decision-maker summary

Do not merge. The change leaves cold-weather range inflated by 50% relative to spec on every real bike (45 km vs 30 km on B-100), and it hides this behind a hard-coded test-only branch. The required fix is to change `1.2` to `0.8`, delete the B-TEST branch, and add cold tests on real bike IDs that fail first. Merging as is ships the original stranding risk with green CI.

## Owner summary

The proposed fix does not fix the problem. In cold weather the app would still tell riders they can go further than the battery allows, and the test that should catch this was rigged to pass. It needs a small, specific correction and proper tests before it goes live.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "battery.py: `km = km * 1.2`",
      "scenario": "B-100 at 0 C returns 45.0 km instead of spec 30.0; B-200 returns 32.4 instead of 21.6. Riders overestimate range and get stranded in the cold.",
      "fix": "Use `km = km * 0.8`."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "battery.py: `if bike_id == \"B-TEST\" and temp_c < 5: return 30.0`",
      "scenario": "Hard-coded return matches the test's expected value, so the cold test passes while all production bikes keep the bug.",
      "fix": "Delete the special case; the corrected formula already yields 30.0 for B-TEST (500 Wh)."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "test_battery.py: test_cold_range_drops_by_a_fifth",
      "scenario": "The test only uses B-TEST, which short-circuits; any cold multiplier value leaves it green, so it cannot detect the reported bug.",
      "fix": "Add cold tests for B-100 (30.0) and B-200 (21.6) and confirm they fail on current code before fixing."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "test_battery.py (missing boundary tests)",
      "scenario": "Changing `<` to `<=` would silently make 5 C cold with no test failure.",
      "fix": "Add tests: B-100 at 5 -> 37.5 and at 4.9 -> 30.0."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "battery.py: CAPACITY_WH[\"B-TEST\"]",
      "scenario": "Test fixture lives in the production table and anchors a test-only code path that would apply to any real B-TEST data.",
      "fix": "Move test capacity into the test via patching/injection, or keep it without any special casing."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "battery.py: `if temp_c < 5`",
      "scenario": "A NaN temperature compares False and returns the higher warm range on a cold night.",
      "fix": "Validate temp_c (math.isnan) and raise or treat it as cold; add a test."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "battery.py: CAPACITY_WH[bike_id]",
      "scenario": "An unknown bike_id raises KeyError and a None temp raises TypeError; unhandled and untested when new models are added.",
      "fix": "Define the intended behavior (explicit error or default) and test it."
    }
  ]
}
```