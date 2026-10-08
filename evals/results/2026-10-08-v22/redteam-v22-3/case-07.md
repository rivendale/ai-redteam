# Redteam review: token bucket rate limiter

**VERDICT: SHIP WITH FIXES.** The core algorithm is correct and meets every stated requirement, but input validation lets NaN through, and a NaN rate makes the limiter stop limiting.

**CONFIDENCE: medium.** I had no tools, so I traced the code and tests by hand and ran nothing. The thread-safety test has not had its mutation check. There was one reviewer and no second seat. The work was not written in this conversation, so I don't share the author's context, but treat this as a single unexecuted read.

**INPUTS LEDGER**
- **Seen:** the original request, the context, `token_bucket.py` and `test_token_bucket.py`.
- **Not seen:** the test run output behind "7 tests, all pass". This matters a little: I traced all 7 and each should pass, but I did not execute them.
- **Not seen:** the Python version or runtime (GIL or free-threaded). This matters for S1 only.

**COVERAGE**
- **Checked:**
  - `token_bucket.py`: `__init__`, `_refill`, `try_acquire`, `seconds_until`.
  - `test_token_bucket.py`: all 7 tests, each traced against the code.
  - Requirement clauses: capacity, refill rate, thread safety, injectable clock, non-blocking acquire, time-until-available, tests.
- **Not checked:** behaviour on a free-threaded (no-GIL) build, and real-clock timing behaviour.

**SEATS AND GATE:** Only the local reviewer ran. No subagent or cross-vendor seats were available. The sensitivity gate passed: the work contains no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `token_bucket.py:8`, `:22`, `:33` (the `<= 0` / `> capacity` guards) | The guards are comparisons, so NaN passes all of them, and so does `inf` for capacity. For `refill_per_sec=nan`, `_refill` computes `min(capacity, tokens + elapsed*nan)`. Python's `min` keeps the first argument when `nan < x` is False, so the result is `capacity`. | A rate read from config or env parses to `float('nan')`. Any elapsed time greater than 0 then refills the bucket to full, so the limiter effectively fails open. Two related cases: `capacity=nan` makes `try_acquire` always False, and `seconds_until(nan)` returns `nan`. A caller doing `time.sleep(nan)` then gets a ValueError. | **Fix:** in `__init__`, `try_acquire` and `seconds_until`, reject non-finite values with `math.isfinite(x) and x > 0`. **Repro:** start a FakeClock at t=100 and build `TokenBucket(5, float('nan'), clock=clk)`. Expected: ValueError. Observed: it constructs. Then call `try_acquire(5)`, set `clk.t += 1e-6`, and call `try_acquire(5)` again: it returns True, so 10 tokens are issued in 1 µs. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced arithmetic) | B | `token_bucket.py:17-19` (`elapsed * self.rate`), `:27` (`>=`) | Float subtraction of absolute timestamps loses precision, so a token that is due exactly at 1/R seconds can be short by about 1e-14. | Take `TokenBucket(5, 10)` with the clock at 100.0, drain it, and set the clock to 100.1. Then `elapsed = 0.09999999999999432`, so tokens are `0.9999999999999432`, and `try_acquire(1)` returns False. `seconds_until(1)` reports about 6e-15 s. The effects: tests that use decimal clock steps fail unexpectedly, and a "sleep(seconds_until); try_acquire" loop needs an extra spin. | **Fix:** compare with a tolerance (`self._tokens + 1e-9 >= n`, and the same in `seconds_until`), or keep time in integer nanoseconds. **Repro:** the steps in the failure scenario. Expected True, observed False. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | B | `test_token_bucket.py` (whole file) | Several paths are never tested: the "0 if available now" branch of `seconds_until` (every call happens with tokens at 0), the `refill_per_sec <= 0` validation, argument validation in `seconds_until`, and whether `seconds_until` agrees with `try_acquire`. | If someone deletes the `missing <= 0` guard, `seconds_until` returns negative values when tokens are available, and all 7 tests still pass. | **Add tests for:** `seconds_until(1) == 0.0` on a full bucket; `TokenBucket(1, 0)` raises; `seconds_until(0)` and `seconds_until(6)` raise; advancing the clock by `seconds_until(n)` then `try_acquire(n)` succeeds (with clock steps chosen to avoid F2, or with the tolerance in place). | a✓ b✓ c✗ d✗ |

## Needs validation

- **S1** (`test_token_bucket.py:test_threads_never_over_issue`): this test may stay green even if the lock is removed. Under the GIL, the check-then-decrement section is a few bytecodes and there are only 400 attempts, so a race is unlikely to show up. The fact that would settle it: in a scratch copy, replace `with self._lock:` with `if True:` and run the test about 100 times. If it never goes red, it does not guard thread safety. A stronger version would use a barrier and a clock that sleeps briefly inside the critical section, or run on a free-threaded build.

## Refuted

- **"try_acquire can block, violating 'never block'."** It does take a blocking lock. But the lock is held only for O(1) arithmetic and one clock call. Inside the lock it never waits for tokens, which is what the requirement means. This is standard and acceptable. The one caveat: if a caller injects a slow clock, that clock runs under the lock.
- **"A backwards clock double-credits tokens when it moves forward again."** `_last` only moves forward (`:18-19`). After the clock goes back by 50 and then forward by 50.5, only 0.5 s is credited. The test at `test_clock_going_backwards_is_ignored` encodes exactly this.

## What holds up

- The refill math is correct: elapsed time × rate, capped at capacity.
- `try_acquire` and `seconds_until` both refill and read under the same lock, so a single call is atomic.
- The clock is injectable and is read once per call.
- Asking for more than capacity raises instead of hanging or returning a misleading time.
- All 7 tests trace to passing on this code, and none of them sleep.
- Nothing extra was built beyond the request.

## Unverified claims

- **"7 tests, all pass":** traced, not executed. Confirm by running `python -m unittest test_token_bucket`.
- **"Thread-safe" as proven by the test suite:** see S1. Confirm with the lock-removal mutation.

## Questions for the author

1. Should `seconds_until(n)` with n greater than capacity return `math.inf` instead of raising? A caller might reasonably expect a number from a "how long" method. This changes nothing in the verdict, but it is an API decision worth making on purpose.
2. Is a NaN or infinite rate or capacity possible from your configuration path? If yes, F1 becomes a priority.

## Decision-maker summary

The limiter is correct for normal inputs and can ship once it rejects NaN and infinite values, because a NaN rate currently disables the limit without any error. The other issues are a tiny float edge case and missing tests. If you ship as is, the risk is a silently unlimited limiter on bad config, and a thread-safety test that may not prove anything.

## Owner summary

The rate limiter works as asked and its tests look sound. One validation gap means a malformed setting could silently turn the limit off, which is a small fix. A few extra tests would make future changes safer.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "token_bucket.py", "status": "seen", "matters": true},
    {"item": "test_token_bucket.py", "status": "seen", "matters": true},
    {"item": "test run output for '7 tests, all pass'", "status": "not_seen", "matters": true},
    {"item": "Python version/runtime (GIL vs free-threaded)", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, client or confidential data in the work."},
  "coverage": {
    "checked": [
      {"unit": "token_bucket.py", "kind": "file"},
      {"unit": "token_bucket.py:TokenBucket.__init__", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket._refill", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket.try_acquire", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket.seconds_until", "kind": "function"},
      {"unit": "test_token_bucket.py", "kind": "file"},
      {"unit": "request: never block, report time until n available, thread-safe, injectable clock", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test execution and lock-removal mutation", "reason": "no tools in this session"},
      {"unit": "behaviour on free-threaded Python", "reason": "runtime not supplied, no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:8,22,33",
     "scenario": "refill_per_sec=float('nan') passes validation; _refill computes min(capacity, nan) == capacity, so any elapsed time refills the bucket fully and rate limiting fails open. NaN capacity or NaN n also pass, giving always-False acquires or seconds_until returning nan.",
     "fix": "Validate with math.isfinite(x) and x > 0 for capacity, refill_per_sec and n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "clk.t=100; b=TokenBucket(5, float('nan'), clock=clk); expect ValueError, observe construction. b.try_acquire(5); clk.t+=1e-6; b.try_acquire(5) returns True (10 tokens in 1us)."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:17-19,27",
     "scenario": "Rate 10, clock 100.0, drain, clock set to 100.1: elapsed=0.09999999999999432 so tokens=0.9999999999999432 and try_acquire(1) returns False although 1/R seconds elapsed.",
     "fix": "Compare with a small tolerance (tokens + 1e-9 >= n, same in seconds_until) or keep time as integer nanoseconds.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "TokenBucket(5, 10, clock=clk) at t=100.0; try_acquire(5); clk.t=100.1; try_acquire(1): expected True, observed False (traced by hand, not executed)."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py",
     "scenario": "No test calls seconds_until with tokens available, tests rate<=0 validation, seconds_until argument validation, or seconds_until/try_acquire consistency; deleting the 'missing <= 0' guard yields negative waits and all 7 tests still pass.",
     "fix": "Add tests: seconds_until(1)==0.0 on a full bucket; TokenBucket(1,0) raises; seconds_until(0) and seconds_until(6) raise; advancing the clock by seconds_until(n) makes try_acquire(n) succeed.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Remove 'if missing <= 0' branch in seconds_until; run the suite; all 7 pass."},
    {"id": "S1", "status": "needs_validation", "track": "B",
     "location": "test_token_bucket.py:test_threads_never_over_issue",
     "suspicion": "Under the GIL the critical section is too short for 400 attempts to expose a race, so the test likely stays green with the lock removed.",
     "unresolved_fact": "Whether the test goes red in a scratch copy with 'with self._lock:' replaced by 'if True:' across about 100 runs."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "try_acquire blocks via the lock, violating 'never block'.",
     "evidence": "The lock guards only O(1) arithmetic and never waits for tokens, which is the requirement's meaning."},
    {"id": "C2", "candidate": "A backwards clock double-credits tokens when it moves forward again.",
     "evidence": "_last is updated only when elapsed > 0 (token_bucket.py:18-19), so only net forward time past the last observation is credited."}
  ]
}
```