> **Review conditions:** This is a same-context review with no tools, so I could not run any code. Everything below comes from reading and hand-tracing the source. The work was not produced in this conversation, so there is no authorship anchoring. For a shared library, the float-precision finding (#1) is worth confirming by running the test sketched in its fix.

**VERDICT: SHIP WITH FIXES.** The core algorithm, locking and validation are correct. However, `seconds_until` can promise a wait that is too short, and the concurrency test would probably pass even with the lock removed.

**CONFIDENCE IN VERDICT: medium.** Nothing was executed. The float finding (#1) is reasoned, not reproduced. The test-strength finding (#2) depends on CPython GIL scheduling.

## Pass 1: Reconstruct

The work is a `TokenBucket` with these properties:
- It holds float tokens, starts full, and is capped at `capacity`.
- It refills lazily from an injectable clock (default `time.monotonic`).
- One `threading.Lock` guards refill, check and decrement.
- `try_acquire(n)` returns True or False and raises `ValueError` for n outside (0, capacity].
- `seconds_until(n)` returns `max(0, n - tokens) / rate`.
- If the clock goes backwards, the bucket freezes until the clock catches up again.

Load-bearing assumptions:
1. Float arithmetic on `now - last` is exact enough that "wait `seconds_until(n)`, then `try_acquire(n)`" succeeds.
2. The clock only moves forward. `seconds_until` silently depends on this.
3. The threaded test actually interleaves the threads.
4. Holding a short lock counts as "never blocks".

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | PROBABLE | `token_bucket.py` `_refill` (`elapsed = now - self._last`) and `seconds_until` (`missing / self.rate`) | The refill is computed from the difference of two large floats. Rounding at the clock's magnitude can make the refill slightly smaller than `seconds_until` predicted. | Bucket is empty, rate=3, `_last`=100.0 (or a `time.monotonic()` value around 1e6, where the rounding step is about 1e-10). `seconds_until(1)` returns 0.333…; the caller advances or sleeps exactly that long. `elapsed*3` can come out as 0.99999999999998 < 1, so `try_acquire(1)` returns False. The method's own contract is broken. | Test: loop over several rates and clock origins (100.0, 1e6, 1e9). Drain the bucket, set `clock.t += b.seconds_until(1)`, assert `try_acquire(1)`. Fix: compare with a small epsilon (`tokens >= n - 1e-9`), or round `seconds_until` up (e.g. `math.nextafter` or a small additive margin), or track integer nanoseconds. |
| 2 | Medium | PROBABLE | `test_threads_never_over_issue` | The test does not prove the class is thread-safe. Each worker makes 50 tiny calls, which likely finishes inside one GIL switch interval (5 ms), so the threads probably run one after another. The test would very likely still pass with `with self._lock:` deleted. | A future refactor drops or narrows the lock. CI stays green. Production over-issues tokens under real contention, or under free-threaded CPython 3.13t. | Widen the race window: use a clock that calls `time.sleep(0)`, or start the threads behind a `threading.Barrier`, and use more iterations. Then do a mutation check: confirm the test fails with the lock removed. |
| 3 | Low | CONFIRMED (trace) | `seconds_until` combined with the backward-clock branch of `_refill` | After the clock moves backwards, `_last` stays at the old, later time. `seconds_until` ignores the gap between now and `_last`, so it under-reports the wait. This is exactly the case `test_clock_going_backwards_is_ignored` claims is handled. | In the fixture, acquire 5 at t=100, then set t=50. `seconds_until(1)` returns 0.5. `try_acquire()` at t=50.5 returns False; the token only becomes available at t=100.5. It only bites with an injected non-monotonic clock such as `time.time`. | Return `max(0, self._last - now) + missing/rate`, or reset `_last = now` on a backward jump. Add a `seconds_until` assertion to the backward-clock test. |
| 4 | Low | CONFIRMED | `test_seconds_until` line 2: `assertEqual(self.b.seconds_until(0.0001 + 0) > 0, True)` | The assertion only checks that the result is greater than 0. The value should be exactly 0.00005. No test covers the "0 if available now" branch. | A bug returning a wrong positive value, such as `n / rate`, still passes. A bug that never returns 0 is not caught. | `assertAlmostEqual(b.seconds_until(0.0001), 0.00005)`, and on a full bucket `assertEqual(b.seconds_until(5), 0.0)`. |
| 5 | Low | CONFIRMED (trace) | `__init__` and the guards `n <= 0 or n > self.capacity` | NaN passes every `<=`/`>` guard. `rate=inf` is also accepted. | `try_acquire(float('nan'))` always returns False, and `seconds_until(nan)` returns `nan`. `TokenBucket(nan, 1)` makes a bucket that never grants. With `rate=inf`, `seconds_until` returns 0.0 even when no time has elapsed and the tokens are not there. | Add `math.isfinite` checks on capacity, rate and n. |
| 6 | Low | CONFIRMED | `test_bad_arguments` | It covers only `capacity=0` and `n > capacity`. | A regression in the `rate <= 0`, `n <= 0` or `seconds_until` validation goes unnoticed. | Add cases for `TokenBucket(1, 0)`, `try_acquire(0)`, `try_acquire(-1)` and `seconds_until(6)`. |
| 7 | Low | CONFIRMED | `__pycache__/*.pyc` in the deliverable | Build artifacts are shipped alongside the source. The paths embedded in them are machine-specific. | A stale `.pyc` could shadow edited source for the wrong interpreter, and it adds repo noise. | Delete the files and add `__pycache__/` to `.gitignore`. |

## WHAT HOLDS UP

- **Atomicity.** Refill, check and decrement all happen under one lock. The clock is read inside the lock, so there is no stale-time race. The capacity cap is applied correctly.
- **Never blocks.** `try_acquire` never sleeps or waits on tokens. The lock is held only for a few arithmetic operations, which reasonably satisfies "never blocks".
- **Fractional refill is not lost.** `_last` advances on every positive elapsed time, and float tokens keep the partial amounts.
- **Clock injection works.** The clock is honoured at construction and on every call, and the tests never sleep.
- **Argument checks are consistent.** Both public methods share the same range check. Raising for n > capacity is a defensible way to signal "never available".
- **The test outcomes trace correctly.** I traced all 7 tests by hand; each passes against this code. That matches "7 tests, all pass", the 7 test methods in the source, and the bytecode in the `.pyc` files.

## UNVERIFIED CLAIMS

- **"7 tests, all pass".** Confirmed only by hand trace. To confirm, run `python -m unittest -v`.
- **The threaded test detects races.** To check, remove the lock and run the test about 100 times (finding #2).
- **The `seconds_until` → `try_acquire` round-trip holds for the default monotonic clock.** To check, run the property test described in finding #1.

## QUESTIONS FOR THE AUTHOR

1. Must "wait `seconds_until(n)`, then `try_acquire(n)`" be guaranteed to succeed when nothing else is contending? If yes, finding #1 rises to High.
2. Are non-monotonic clocks such as `time.time` a supported injection? If yes, finding #3 rises to Medium.
3. Do you target free-threaded CPython? If yes, finding #2 matters more.

## DECISION-MAKER SUMMARY

The limiter's core logic is sound and safe to build on. Before publishing it as a shared library:
- Fix the float round-trip so callers who wait the reported time don't get refused.
- Strengthen the concurrency test so it would actually catch a missing lock.

If shipped as is, the main risk is occasional spurious `False` results right at the predicted refill moment, plus a test suite that would not catch a future thread-safety regression.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "token_bucket.py _refill (now - self._last) / seconds_until (missing / self.rate)", "scenario": "Empty bucket, rate=3, clock origin 100.0 or ~1e6 monotonic; advancing exactly seconds_until(1) yields tokens like 0.99999999999998 so try_acquire(1) returns False, breaking the reported-wait contract", "fix": "Epsilon tolerance in the comparison or round seconds_until up (nextafter/margin) or integer-ns arithmetic; add a round-trip test across rates and clock origins"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "test_token_bucket.py test_threads_never_over_issue", "scenario": "Workers likely run serially under the GIL, so the test passes even with the lock removed; a lock regression ships green", "fix": "Use a Barrier and a yielding clock (time.sleep(0)) to force interleaving; verify the test fails with the lock removed"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "token_bucket.py seconds_until with backward-clock handling in _refill", "scenario": "Acquire 5 at t=100, set t=50: seconds_until(1) returns 0.5 but try_acquire at t=50.5 is False; real availability is t=100.5", "fix": "Include max(0, _last - now) in seconds_until or reset _last on backward jump; assert seconds_until in the backward-clock test"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "test_token_bucket.py test_seconds_until second assertion", "scenario": "Only checks > 0; a wrong positive value or never returning 0.0 passes", "fix": "assertAlmostEqual(seconds_until(0.0001), 0.00005) and assertEqual(seconds_until(5), 0.0) on a full bucket"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "token_bucket.py __init__ and n guards", "scenario": "NaN passes all guards: try_acquire(nan) always False, seconds_until(nan) returns nan, TokenBucket(nan,1) never grants; rate=inf makes seconds_until report 0.0 with no tokens", "fix": "Validate with math.isfinite for capacity, rate and n"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "test_token_bucket.py test_bad_arguments", "scenario": "rate<=0, n<=0 and seconds_until validation are untested; regressions go unnoticed", "fix": "Add cases for TokenBucket(1,0), try_acquire(0), try_acquire(-1), seconds_until(6)"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "__pycache__/*.pyc", "scenario": "Build artifacts with machine-specific paths shipped with the source; possible stale bytecode confusion", "fix": "Remove them and add __pycache__/ to .gitignore"}
  ]
}
```
