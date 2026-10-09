# Adversarial Diagnostic Review: `estimate_range_km` cold-weather fix

## Pass 1: Reconstruct

The work claims to fix cold-weather range so that it drops instead of rising, and the context says both tests pass. For it to be correct, every bike below 5 °C must return `capacity × 0.9 / 12 × 0.8`, and the tests must exercise that general path.

The load-bearing assumptions are:
- "Drops by 20%" means multiply by 0.8. The test's expected 30.0 = 37.5 × 0.8 agrees with this.
- `B-TEST` is a representative stand-in for real bikes.
- The two passing tests show the cold path is correct.

The code breaks the last two. The cold test passes because of a hardcoded special case, not because the bug is fixed.

## Pass 2: Attack (Track B)

I have no tools in this session. Everything below comes from tracing the code by hand; nothing was executed.

**Main path, traced:**

| Bike | Temp | Code returns | Spec requires |
|---|---|---|---|
| B-100 | 20 °C | 500 × 0.9 / 12 = 37.5 | 37.5 ✔ |
| B-100 | 0 °C | 37.5 × **1.2** = **45.0** | 30.0 ✘ |
| B-200 | 0 °C | 27.0 × 1.2 = **32.4** | 21.6 ✘ |
| B-TEST | 0 °C | early `return 30.0` | 30.0 (by hardcode only) |

**Hostile inputs:**
- Unknown `bike_id` raises a bare `KeyError`.
- `temp_c=None` raises `TypeError`.
- `temp_c=NaN`: `NaN < 5` is False, so the bike silently gets the warm, optimistic range.
- Exactly 5 °C gets the warm range. That is correct, since the spec says "below 5".

**Mutation reasoning (rule 5):** Change `1.2` to `0.8`, `5.0`, or delete the cold branch entirely, and both tests stay green. The B-TEST short-circuit returns before the cold branch runs, and the warm test never reaches it. So the cold branch currently has zero test coverage. I confirmed this by trace only; running it in a scratch copy would settle it empirically.

## Pass 3: Self-check

Every finding below is tied to a specific line and arithmetic I can reproduce. The one remaining interpretive risk is the meaning of "drops by 20%". The test's own expected value settles it as × 0.8, so I have not raised it as a finding.

---

**VERDICT: REJECT.** The original bug is untouched for every real bike. The tests pass only because of a hardcoded return for the test fixture.

**CONFIDENCE IN VERDICT: high.** The failure follows from simple arithmetic on the code as written. The only limit is that I could not execute anything.

### FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (trace) | `battery.py`, `km = km * 1.2` | The original bug is still there: cold weather raises range by 20% instead of lowering it. | A B-100 at 0 °C shows 45.0 km when the spec says 30.0 (50% overstated). A B-200 shows 32.4 km instead of 21.6. Riders plan trips on this number and get stranded on cold evenings, which is exactly the stated stake. | Change to `km *= 0.8`. |
| 2 | Critical | CONFIRMED (line) | `battery.py`, `if bike_id == "B-TEST" and temp_c < 5: return 30.0` | Hardcoded special case for the test fixture, presented as a fix. This is test-gaming. | The cold test passes regardless of the real cold logic, so a reviewer or CI sees green while production stays wrong. | Delete the special case so the cold test runs through the general path. |
| 3 | High | CONFIRMED (trace), not executed | `test_battery.py`, `test_cold_range_drops_by_a_fifth` | The test cannot fail on the cold path, because it uses the one ID that bypasses it. | Any regression in the cold multiplier ships undetected. | Add cold assertions for real bikes: B-100 at 0 °C should be 30.0, B-200 at 0 °C should be 21.6. Add a boundary check at 5 °C (warm) and 4.9 °C (cold). Then break the multiplier in a scratch copy and confirm the test goes red. |
| 4 | Medium | CONFIRMED (line) | `CAPACITY_WH`, `"B-TEST": 500` | A test fixture lives in production data. | `B-TEST` can be looked up or returned in production, and it carries special-cased behaviour. | Move fixture data into the tests, or inject capacity. |
| 5 | Low | CONFIRMED (trace) | `if temp_c < 5` | A NaN temperature (for example from a sensor fault) falls through to the warm, optimistic range. | A failed temperature sensor reports NaN, and the rider sees an unreduced range in the cold. | Treat non-finite temperatures as cold (the conservative choice), or raise an error. |
| 6 | Low | CONFIRMED (line) | `CAPACITY_WH[bike_id]` | An unknown bike raises a bare `KeyError`. | A new model is added to the fleet without updating this table, and the range endpoint errors. | Raise an explicit error with the bike ID, and add a test for it. |

### WHAT HOLDS UP
- The warm path matches the spec: 90% usable capacity at 12 Wh/km gives 37.5 km for B-100.
- The cold threshold (`< 5`) matches "below 5 C".
- Both tests encode the correct expected values. The problem is that the code reaches them dishonestly.

### UNVERIFIED CLAIMS
- "2 tests pass." This is plausible from the trace, but I did not run them. Confirm with `python -m unittest test_battery`.
- Whether `estimate_range_km` has other callers or other test files that would catch this. To settle it, grep the repo for `estimate_range_km` and `B-TEST`, after first checking that the grep finds a known hit (positive control).

### QUESTIONS FOR THE AUTHOR
1. Why does `B-TEST` have a special case in production code? Is anything other than the test relying on it?
2. Is "drops by 20%" intended as × 0.8 of the warm range? The test implies yes.

### DECISION-MAKER SUMMARY
Do not merge. The change makes the tests pass by hardcoding the test bike's answer, while every real bike still shows a 20% higher range in the cold, up to 50% above spec. Merging would put an overstated number in front of riders on exactly the cold evenings this fix was meant to protect.

### OWNER SUMMARY
The proposed fix does not actually fix the cold-weather range problem. It only makes the automated checks pass by giving a special answer for the test bike. Real bikes would still tell riders they can go further in the cold than they really can, so this needs to be redone before release.

```json
{
  "verdict": "REJECT",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "battery.py: `km = km * 1.2`",
      "scenario": "B-100 at 0 C returns 45.0 km instead of spec 30.0; B-200 returns 32.4 instead of 21.6; riders overestimate range and get stranded in cold weather.",
      "fix": "Replace with `km *= 0.8`."
    },
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "battery.py: `if bike_id == \"B-TEST\" and temp_c < 5: return 30.0`",
      "scenario": "Hardcoded return makes the cold test pass while the real cold path stays wrong; CI shows green on a broken fix.",
      "fix": "Remove the special case so all bikes go through the general formula."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "test_battery.py: test_cold_range_drops_by_a_fifth",
      "scenario": "The test uses the only ID that bypasses the cold branch, so any change to the cold multiplier (or deleting it) leaves both tests green.",
      "fix": "Add cold assertions for B-100 (30.0) and B-200 (21.6), plus boundary cases at 5.0 and 4.9 C; mutate the multiplier in a scratch copy and confirm the test fails."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "battery.py: CAPACITY_WH entry \"B-TEST\"",
      "scenario": "A test fixture with special-cased behaviour ships in production data and can be returned to callers.",
      "fix": "Move fixture data into the tests or inject capacity."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "battery.py: `if temp_c < 5`",
      "scenario": "A NaN temperature from a sensor fault compares False, so the bike gets the optimistic warm range in the cold.",
      "fix": "Treat non-finite temperatures as cold, or raise an error."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "battery.py: `CAPACITY_WH[bike_id]`",
      "scenario": "An unknown bike model raises a bare KeyError and the range endpoint errors.",
      "fix": "Raise an explicit error naming the bike_id, and add a test for it."
    }
  ]
}
```