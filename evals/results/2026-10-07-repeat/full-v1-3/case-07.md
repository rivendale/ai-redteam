**Review setup:** The work was not produced in this conversation, so there is no author-context anchoring. This session has no tools, so nothing was executed. Every behavioural claim below comes from tracing the code by hand.

## Pass 1: Reconstruct

The work delivers `TokenBucket(capacity, refill_per_sec, clock)` with three methods:
- `try_acquire(n)` is non-blocking and returns a bool.
- `seconds_until(n)` reports the wait until `n` tokens exist.
- `_refill` is lazy and runs under a `threading.Lock`.

Seven unittest tests come with it. For the work to be correct, these must be true:
1. Every read-modify-write of `_tokens` and `_last` happens under the lock.
2. Float arithmetic on `tokens + elapsed*rate` is accurate enough that `seconds_until`'s answer is honoured by a later `try_acquire`.
3. The tests would actually fail if the lock were removed or the maths were wrong.

There are also unstated assumptions:
- The bucket starts full.
- `n > capacity` is an error rather than "never".
- A backwards clock should freeze refills rather than resync.
- `seconds_until` is advisory, not a reservation.

## Pass 2 and 3: Findings

**VERDICT: SHIP WITH FIXES.** The implementation is correct on the main path and properly locked. However, the concurrency test cannot detect a missing lock, and `seconds_until` can return a wait that `try_acquire` then refuses because of float rounding.

**CONFIDENCE IN VERDICT: medium.** Nothing was run. The two main findings come from code reading and knowledge of CPython/IEEE-754 behaviour, not from execution.

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | PROBABLE | `test_threads_never_over_issue` | The test cannot detect a race. Each worker does only 50 cheap iterations. Under the GIL with the default 5 ms switch interval, each thread very likely runs its loop to completion without being preempted between the `>=` check and the `-=`. | Delete `with self._lock:` from `try_acquire`. The test very likely still passes 100/100, so "thread-safe" is asserted but not demonstrated. | Call `sys.setswitchinterval(1e-6)` in the test and restore it after. Inject a clock that calls `time.sleep(0)` to force switches inside the critical section. Start threads behind a `threading.Barrier` and use thousands of iterations. Then confirm the test fails with the lock removed. |
| 2 | Medium | PROBABLE | `seconds_until`: `missing / self.rate`; `_refill`: `self._tokens + elapsed * self.rate` | The wait is computed as `missing/rate`. Refill later computes `(now - last) * rate` with a different rounding path, and the result can land 1 ulp below `n`. | Take `rate=3`, empty the bucket, then advance the fake clock by `seconds_until(1)` (about 0.333…). `elapsed*3` can come out as `0.9999999999999998`, so `try_acquire(1)` returns False. A caller looping "sleep(seconds_until); try_acquire" with a fake clock, or with a precise scheduler, spins on ~1e-16 waits. | Add a test: for several rates (3, 7, 0.3), drain, advance by exactly `seconds_until(n)`, assert `try_acquire(n)`. Fix by comparing with a tolerance (`self._tokens + 1e-9 >= n`), or by tracking time in integer ns and rounding the wait up. |
| 3 | Low | CONFIRMED | `__init__` and the `n` validation (`capacity <= 0`, `n <= 0 or n > self.capacity`) | NaN passes every check, because all comparisons with NaN are False. | `TokenBucket(float('nan'), 1)` constructs, and `try_acquire()` is then False forever. Separately, `seconds_until(float('nan'))` returns `nan`. | Reject non-finite capacity and `n` (for example with `math.isfinite`), and decide explicitly whether `rate=inf` is allowed. Add tests for both. |
| 4 | Low | CONFIRMED | `_refill`: `if elapsed > 0:` (no `_last` update otherwise) | A backward clock jump freezes refills until the clock passes the old `_last` again. `test_clock_going_backwards_is_ignored` encodes exactly this. | Inject `time.time` and let NTP step it back 1 hour. The bucket then refills nothing for an hour. This cannot happen with the default `time.monotonic`. | This is a conservative choice and defensible (it cannot over-issue). Document it, or state in the docstring that the clock must be monotonic. |
| 5 | Low | CONFIRMED | `test_bad_arguments`, `test_seconds_until` | Coverage is thin. | Untested paths: `try_acquire(0)`, `try_acquire(-1)`, `refill_per_sec <= 0`, all `seconds_until` validation, the `seconds_until` "available now" `0.0` branch, and fractional refill accumulating across several calls. The assertion `seconds_until(0.0001 + 0) > 0` is oddly written and only checks the sign. | Add one assertion for each listed path, and replace the sign check with `assertAlmostEqual(seconds_until(0.0001), 0.00005)`. |

**Self-check:**
- I considered calling lock contention a violation of "never block" and dropped it. The critical section is O(1) and the request clearly means "never wait for tokens".
- I dropped the mutable public attributes `capacity` and `rate`. There is no realistic failure scenario for them.
- The most likely remaining miss is CPython-version-specific GIL behaviour, which affects how weak finding 1 really is.

## WHAT HOLDS UP
- The lock covers the full refill → check → decrement sequence in both methods. The clock is read inside the lock, so reads are ordered.
- Capacity clamping is correct, and `test_never_exceeds_capacity` exercises it.
- Validation happens before the lock is taken, and an exception from the clock still releases the lock because of `with`.
- `n > capacity` raising, instead of returning False forever or an infinite wait, is a reasonable and documented contract.
- Tracing the 7 tests by hand, all of them should pass against this implementation.

## UNVERIFIED CLAIMS
- **"7 tests, all pass":** traced, not executed. Confirm by running `python -m unittest -v`.
- **"Thread-safe":** the code looks correct, but the test does not prove it. Confirm by running the hardened test from finding 1 with the lock removed and checking that it fails.
- **Float mismatch (finding 2):** confirm by running the suggested rate=3 test.

## QUESTIONS FOR THE AUTHOR
1. Should `seconds_until` guarantee that `try_acquire` succeeds after exactly that wait? If yes, finding 2 becomes High.
2. Is a non-monotonic clock (for example `time.time`) a supported injection? If yes, finding 4 needs a decision rather than a doc note.

## DECISION-MAKER SUMMARY
The limiter is logically sound and safe to use as written. Before relying on it as a shared library:
- Harden the concurrency test so it would actually catch a missing lock.
- Add an epsilon or round-up so that `seconds_until` and `try_acquire` agree.

If you ship as-is, the risk is mostly spurious retries for callers that sleep exactly `seconds_until()`, not over-issuing tokens.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "test_threads_never_over_issue", "scenario": "Removing the lock from try_acquire likely still passes: 50 cheap iterations per thread rarely preempt between check and decrement under the GIL's 5 ms switch interval, so thread safety is untested.", "fix": "sys.setswitchinterval(1e-6), a clock that calls time.sleep(0), a Barrier start, more iterations; verify the test fails without the lock."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "seconds_until (missing / self.rate) vs _refill (tokens + elapsed * rate)", "scenario": "rate=3, empty bucket, advance clock by exactly seconds_until(1): refill can yield 0.9999999999999998 tokens, so try_acquire(1) returns False and sleep/retry loops spin on ~1e-16 waits.", "fix": "Compare with a tolerance or use integer-ns time and round waits up; add a test advancing by exactly seconds_until(n) across several rates."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "__init__ and n validation comparisons", "scenario": "NaN capacity or n passes validation; TokenBucket(nan, 1).try_acquire() is always False; seconds_until(nan) returns nan.", "fix": "Reject non-finite values with math.isfinite and add tests."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "_refill: if elapsed > 0 (no _last resync)", "scenario": "Injected wall clock stepped back 1 h freezes refills for 1 h; the test encodes this behaviour.", "fix": "Document that the clock must be monotonic, or choose and document a resync policy."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "test_bad_arguments, test_seconds_until", "scenario": "No tests for n<=0, rate<=0, seconds_until validation, the 0.0 available-now branch, or fractional refill; the 'seconds_until(0.0001 + 0) > 0' assertion only checks sign.", "fix": "Add an assertion per path; replace the sign check with assertAlmostEqual(seconds_until(0.0001), 0.00005)."}
  ]
}
```