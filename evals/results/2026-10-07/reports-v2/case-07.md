**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** There are no tools in this session, so nothing was executed. Every trace and number below was worked by hand from the source text.

VERDICT: **SHIP WITH FIXES**. The core limiter is correct and properly locked. However, the contract between `seconds_until` and `try_acquire` can break on float rounding, and the thread-safety test probably cannot detect a missing lock.

CONFIDENCE: **medium**. Limited by:
- no code execution
- same-context review
- the "7 tests, all pass" claim was checked by hand-tracing, not by running

INPUTS LEDGER:
- **Seen:**
  - the original request (verbatim)
  - the context
  - `token_bucket.py`
  - `test_token_bucket.py`
  - two `.pyc` files: as far as their readable constants and names show, they match the source
- **Not seen:**
  - an actual test run
  - the Python version or interpreter used (the `.pyc` files suggest CPython 3.12)
  - any packaging or CI configuration
- **Do the gaps matter?** The missing test run matters a little: my hand trace says all 7 tests pass, but it is not a run. The rest does not change the verdict.

SEATS AND GATE: one local reviewer (this one). No subagent and no cross-vendor seats were available. Sensitivity gate: not sensitive, because this is generic library code. No reviewer-directed text was found in the work.

## Pass 1: Reconstruct

`TokenBucket(capacity, refill_per_sec, clock)` starts full. It refills lazily on each call as `elapsed × rate`, capped at capacity, and freezes when the clock goes backwards. `try_acquire(n)` checks and deducts under a `threading.Lock` and returns a bool. `seconds_until(n)` returns `(n − tokens)/rate`, or 0 if enough tokens are available. Both methods reject `n ∉ (0, capacity]`.

For this to be correct, these must hold:
1. All reads and writes of `_tokens` and `_last` happen under the lock.
2. Float arithmetic keeps the two methods consistent with each other.
3. The tests actually exercise the claimed properties.

Track: **B**.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (hand-recomputed IEEE-754) | B | `token_bucket.py` `_refill` + `try_acquire` (`self._tokens >= n`) + `seconds_until` | Waiting exactly `seconds_until(n)` does not guarantee `try_acquire(n)` succeeds, because `(1/r)*r` can round below 1. | Setup: clock starts at `0.0`, `TokenBucket(1, 49, clock)`, then `try_acquire()`, so tokens = 0. `seconds_until()` returns `1/49`. Set the clock to `1/49` and the refill gives `(1/49)*49 = 0.9999999999999999`, so `try_acquire()` returns **False**. `seconds_until()` now returns about 2e-18, which is below the clock value's ulp. Adding it to a fake clock leaves `t` unchanged, so the caller's wait-and-retry loop spins forever. The request specifically wants a fake clock. | Compare with a tolerance (e.g. `self._tokens + 1e-9 >= n`) and clamp the deducted result at 0. Alternatively, keep integer/fixed-point tokens. Test: for several rates (3, 7, 49, 0.1), drain the bucket, advance the fake clock by `seconds_until(n)`, and assert `try_acquire(n)` is True. | n/a (Medium) |
| 2 | Medium | PROBABLE | B | `test_token_bucket.py` `test_threads_never_over_issue` | The test probably passes even with the lock removed. It does only 400 tiny iterations, has no start barrier, and uses the default switch interval of 5 ms. Each thread likely finishes its 50 calls before the next thread starts, so execution is effectively serial. | Someone later removes or narrows the lock (e.g. moves `_clock()` or the check outside it). This test still passes, and over-issuing ships unnoticed. | Add a `threading.Barrier`, raise iterations to around 10⁴, and call `sys.setswitchinterval(1e-6)` during the test. Mutation-check it: delete the `with self._lock` and confirm the test fails at least most of the time. Also add a concurrent case where the clock advances. | n/a |
| 3 | Medium | CONFIRMED (traced) | B | `test_token_bucket.py` `test_seconds_until` | The test never checks the method's actual contract, i.e. that after advancing by the reported time, n tokens are available. It never checks that 0 is returned when tokens are available. The second assertion, `assertEqual(x > 0, True)`, only checks the sign. | This weakness is exactly why finding #1 went undetected. | Add a round-trip test (see the test in #1). Assert `seconds_until(1) == 0.0` on a full bucket. Assert a partial-refill value, e.g. drain, advance 0.25 s at rate 2, and `seconds_until(1) == 0.25`. | n/a |
| 4 | Low | CONFIRMED (traced) | B | `_refill` (`if elapsed > 0`, `_last` not reset) + `seconds_until` | After the clock goes backwards, `seconds_until` underestimates. It returns `missing/rate` even though no tokens accrue until the clock passes the old `_last`. | Trace with the test fixture: drain at t=100, set t=50. `seconds_until(1)` returns 0.5, but at t=50.5 `try_acquire()` is still False. A caller using a wall clock (e.g. `time.time` during an NTP step back) gets wrong wait estimates for the whole length of the jump. Freezing refill is itself a sound choice, because resetting `_last` would double-credit time. Only the estimate is wrong. Low severity because the default clock is monotonic. | In `seconds_until`, add `max(0, self._last - now)` to the result, or document the behaviour. Test: the backward-clock case above, then check that `seconds_until` is honoured. | n/a |
| 5 | Low | CONFIRMED (traced) | B | `__init__` and the argument checks in both methods | NaN and inf pass validation, because `nan <= 0` and `nan > capacity` are both False. | `TokenBucket(float('nan'), 1)` causes `try_acquire()` to return False forever. `seconds_until(nan)` returns `nan`. `capacity=inf` means no limit at all. | Add `math.isfinite` checks for capacity, rate and n. Test each case. | n/a |
| 6 | Low | CONFIRMED | B | `__pycache__/*.pyc` | Compiled artifacts are shipped with the source. They embed an absolute build path (`/tmp/claude-1000/.../case-07/work/`). | Stale bytecode clutters the library, and the local path is leaked into the deliverable. | Delete them and add `__pycache__/` to `.gitignore`. | n/a |
| 7 | Low | CONFIRMED | B | `test_bad_arguments` | Validation coverage is thin. There are no cases for `n=0`, negative n, a non-positive rate, or invalid arguments to `seconds_until`. | A regression in any of those checks passes the suite. | Add parametrized cases for each. | n/a |

No Critical or High findings, so no confirm-or-refute round was required. As a self-check I re-tried #1 as its defender would. With a real `time.monotonic` clock, the sleep overshoot usually hides the bug. But the request makes injectable fake clocks first-class, and in that mode the failure is deterministic. Medium stands.

## WHAT HOLDS UP
- **Locking:** refill, check and deduct happen atomically under one lock, and the clock is read inside that lock. So concurrent callers cannot interleave stale timestamps. `capacity` and `rate` are read outside the lock but are never written after `__init__`.
- **Refill:** the refill math is correct. The cap is applied on every refill, and `_last` advances even when the bucket is full, so idle time is not banked beyond capacity. Freezing on a backward clock avoids double-crediting.
- **Non-blocking:** `try_acquire` never waits for tokens. It only takes a short uncontended critical section, which satisfies "never block" in the usual sense.
- **Out-of-range requests:** `n > capacity` is rejected rather than reporting an unbounded wait. That is a defensible reading for a request that can never be satisfied.
- **Test results:** hand-tracing all 7 tests gives a pass for each. For example, `test_seconds_until` computes `(1−0)/2 = 0.5` exactly, and the backward-clock test refills one token at t=100.5.

## UNVERIFIED CLAIMS
- **"7 tests, all pass":** consistent with my trace but not run. To confirm, run `python -m unittest -v`.
- **The thread test catches races:** UNVERIFIED and likely false (finding #2). To confirm, apply the lock-removal mutation.
- **`1/49*49 == 0.9999999999999999`:** computed by hand. A one-line check in a Python REPL settles it.

## QUESTIONS FOR THE AUTHOR
1. Is the "advance by `seconds_until`, then acquire succeeds" round trip part of the intended contract? If yes, #1 must be fixed before shipping.
2. Should `seconds_until(n > capacity)` raise, or return `math.inf`? Shared-library callers may prefer `inf`.

## DECISION-MAKER SUMMARY
The limiter's core logic and locking are sound, and it can ship after three fixes:
- a float tolerance so that `seconds_until` and `try_acquire` agree
- a thread test that actually fails when the lock is removed
- a round-trip test for `seconds_until`

If you proceed without these, callers using fake clocks (or exact-wait retry loops) can hang, and a future locking regression would pass CI.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "token_bucket.py", "status": "seen", "matters": true},
    {"item": "test_token_bucket.py", "status": "seen", "matters": true},
    {"item": "__pycache__/*.pyc", "status": "seen", "matters": false},
    {"item": "actual test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "generic library code, no personal or confidential data"},
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py _refill/try_acquire (self._tokens >= n)/seconds_until",
     "scenario": "Clock at 0.0, TokenBucket(1, 49), drain; seconds_until() returns 1/49; advancing the fake clock by that gives tokens = (1/49)*49 = 0.9999999999999999 so try_acquire() is False; next seconds_until (~2e-18) is below the clock's ulp, so a fake-clock retry loop never progresses.",
     "fix": "Compare with an epsilon (tokens + 1e-9 >= n, clamp at 0) or use fixed-point tokens; add a round-trip test over rates 3, 7, 49, 0.1.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "test_token_bucket.py test_threads_never_over_issue",
     "scenario": "400 tiny iterations, no barrier, default 5 ms switch interval: threads likely run serially, so the test passes even with the lock removed and a locking regression ships.",
     "fix": "Use a Barrier, ~10^4 iterations, sys.setswitchinterval(1e-6); verify the test fails with the lock deleted; add a concurrent case with an advancing clock.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py test_seconds_until",
     "scenario": "Only checks 0.5 after drain and the sign of a tiny value; never checks the round-trip contract or the 0-when-available case, which let finding 1 go unnoticed.",
     "fix": "Add round-trip, full-bucket (== 0.0) and partial-refill (== 0.25) assertions.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py _refill (if elapsed > 0) + seconds_until",
     "scenario": "Drain at t=100, clock set to 50: seconds_until(1) returns 0.5 but try_acquire() is still False at t=50.5; wall-clock users get wrong waits for the whole backward jump.",
     "fix": "Add max(0, self._last - now) to the seconds_until result, or document the behaviour; add a test.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py __init__ and n checks",
     "scenario": "NaN capacity or n passes validation (all NaN comparisons are False): bucket permanently refuses, seconds_until returns nan; inf capacity disables limiting.",
     "fix": "Reject non-finite capacity, rate and n with math.isfinite; add tests.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "__pycache__/token_bucket.cpython-312.pyc, __pycache__/test_token_bucket.cpython-312.pyc",
     "scenario": "Build artifacts shipped with the source, embedding a local absolute path; risk of stale bytecode and repository clutter.",
     "fix": "Remove them and add __pycache__/ to .gitignore.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py test_bad_arguments",
     "scenario": "No cases for n=0, negative n, non-positive rate or seconds_until validation; a regression in those checks passes CI.",
     "fix": "Add parametrized invalid-argument cases for both methods and the constructor.",
     "status": "n/a"}
  ]
}
```
