**Reviewer note:** this is an independent review. I did not write this work. I had **no tools**, so I could not run any code or tests. Every finding below comes from reading the code and working through it by hand, including the floating-point arithmetic. Nothing was executed.

---

**VERDICT: SHIP WITH FIXES.** The limiter does what was asked and its locking is correct. Two things need fixing first: `seconds_until` can report a wait after which `try_acquire` still fails, and non-finite arguments (NaN, infinity) are accepted, which lets the limiter stop limiting.

**CONFIDENCE: medium.** No tools were available, so nothing was run. The context says "7 tests, all pass", which is unverified. The floating-point finding was worked out by hand at the bit level but not executed.

**INPUTS LEDGER:**
- **Seen:** the request, the context, `token_bucket.py` and `test_token_bucket.py`.
- **Not seen:**
  - The Python version and build (GIL or free-threaded). This matters for S1, the thread test.
  - Any test run output. This matters a little, because the "all pass" claim is unverified.
  - The callers and config source of this library. This matters a little for F2: realistic NaN or infinity inputs come from parsed config.

**COVERAGE:**
- **Checked:**
  - `TokenBucket.__init__`, `_refill`, `try_acquire` and `seconds_until`.
  - All 7 tests, each traced by hand against the code.
  - Every requirement clause in the request.
- **Not checked:**
  - Actual test execution.
  - Behaviour under free-threaded Python.
  - Mutation testing of the lock.

**SEATS AND GATE:** One local reviewer ran, with no subagent and no tools. The sensitivity gate passed, because the material contains no personal or confidential data. No cross-vendor seats were used, since none were requested and the stakes are standard.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (worked out by hand, not run) | B | `token_bucket.py` `seconds_until` (return line) vs `try_acquire` `if self._tokens >= n` | After waiting exactly the time `seconds_until(n)` reports, `try_acquire(n)` can still fail. This happens because adding a small wait to a large clock value loses precision. | The clock is at 100.0, the rate is 3 and the bucket is empty. `seconds_until(1)` returns 0.3333333333333333. Adding that to 100.0 and subtracting 100.0 gives 0.3333333333333286. Multiplying by 3 gives 0.9999999999999858, which is less than 1, so `try_acquire(1)` returns False. A caller that loops on "sleep, then acquire" then gets a near-zero wait of about 5e-15 s, so the loop spins. Any fake-clock test written as "advance the clock by `seconds_until`, then acquire" fails at random depending on the numbers. | **Fix:** apply one small tolerance in both methods, for example `EPS = 1e-9`, using `self._tokens + EPS >= n` and `missing <= EPS`. Alternatively, keep tokens as integer micro-tokens. **Reproduction:** `c=FakeClock(); b=TokenBucket(5,3,clock=c); b.try_acquire(5); c.t += b.seconds_until(1); assert b.try_acquire(1)`. Expected True; the hand calculation gives False. | a Y, b Y, c N, d N |
| F2 | Medium | CONFIRMED (traced by hand) | B | `token_bucket.py` `__init__` validation, `try_acquire` and `seconds_until` range checks | Because NaN compares False with everything, NaN passes every `<= 0` and `> capacity` check. | **Case 1:** `TokenBucket(5, float('nan'))`. When `_refill` runs, `elapsed*rate` is NaN, and `min(capacity, NaN)` returns `capacity`. The bucket refills completely on every call where the clock has moved, so it **stops limiting**. **Case 2:** a NaN capacity makes `min(NaN, …)` return NaN, so the bucket denies every request forever. **Case 3:** `try_acquire(nan)` always returns False, and `seconds_until(nan)` returns NaN. **Case 4:** a rate of `inf` also makes the limiter unlimited. These values realistically arrive from a config value parsed with `float()`. | **Fix:** in all three entry points, reject values where `not math.isfinite(x)`. **Reproduction:** `c=FakeClock(); b=TokenBucket(5, float('nan'), clock=c)`. Then loop: `b.try_acquire(5); c.t += 1e-6; assert not b.try_acquire(5)`. Expected False; observed True. | a Y, b Y, c N, d N |
| F3 | Low | CONFIRMED | B | `test_token_bucket.py` `test_bad_arguments` | The argument validation is mostly untested. There is no test for `n=0`, a negative `n`, `refill_per_sec<=0`, or any `seconds_until` argument checks. | If someone deletes the check in `seconds_until`, all tests still pass. `seconds_until(capacity+1)` would then report a wait time for a token count that can never be reached. | Add `assertRaises` cases for `try_acquire(0)`, `try_acquire(-1)`, `TokenBucket(1, 0)`, `seconds_until(0)` and `seconds_until(6)`. Add NaN cases once F2 is fixed. | a Y, b Y, c N, d N |

## NEEDS VALIDATION

- **S1: the thread test may never fail, even with no lock.** In `test_threads_never_over_issue`, the code it protects is a few bytecodes long. Under the GIL, removing `with self._lock` will probably still leave exactly 100 successful acquires. That means the "thread-safe" requirement may effectively be untested.
  - **What would settle it:** in a scratch copy, remove the lock and run the test about 50 times; see whether it ever goes red.
  - **Suggested hardening:** inject a clock that calls `time.sleep(0)` before returning, and set `sys.setswitchinterval(1e-6)`. This widens the gap between the check and the decrement, so the test turns red when the lock is removed.

## REFUTED

- **"`try_acquire` blocks because it takes a lock."** The lock only covers a short, bounded section of code with no waiting or I/O inside it. "Never blocks" in the request reasonably means "never waits for tokens". One caveat: the injected clock runs inside the lock, so a slow clock would stall callers. That is the caller's choice, not a defect.
- **"The backward-clock handling loses tokens."** When the clock goes backwards, `_last` is deliberately kept, so the bucket does not refill until the clock passes the old time again. `test_clock_going_backwards_is_ignored` checks this, and I traced it through: at 100, then 50, then 100.5, the bucket gains 1 token. The default clock is `time.monotonic`, which never goes backwards, so this only matters if a caller injects a wall clock.
- **"Tokens can exceed capacity."** `min(self.capacity, …)` caps the count, and `test_never_exceeds_capacity` checks that cap.

## WHAT HOLDS UP

- **Every requirement is met:** capacity, refill rate, a lock around both the refill and the check-then-take, an injectable clock, a non-waiting `try_acquire`, a wait-time method, and tests.
- **The refill logic is correct.** It only applies to positive elapsed time and is capped at capacity.
- **Validation rejects impossible requests.** It refuses `n > capacity`, so no wait time is reported that could never be satisfied.
- **The hand-traced tests are consistent with the code.** `test_starts_full`, `test_refills_at_rate`, `test_never_exceeds_capacity`, `test_clock_going_backwards_is_ignored` and `test_seconds_until` (expected 0.5) all match it.
- **No scope creep.** Nothing was built beyond what the request asked for.

## UNVERIFIED CLAIMS

- **"7 tests, all pass":** I counted 7 tests, but did not run them. To confirm, run `python -m unittest test_token_bucket -v`.
- **The thread-safety test proves anything:** see S1.

## QUESTIONS FOR THE AUTHOR

1. Should `seconds_until(n)` guarantee that `try_acquire(n)` succeeds once that time has passed? If yes, F1 must be fixed rather than just documented.
2. Can `capacity` or `refill_per_sec` come from parsed config? If yes, F2 is more urgent.

## DECISION-MAKER SUMMARY

The limiter is structurally sound and can ship once two medium-severity fixes are in: a tolerance in the token comparison, and rejecting NaN and infinity. Without the second fix, a bad config value silently turns rate limiting off. The thread-safety test should also be checked to confirm it can actually fail.

## OWNER SUMMARY

The rate limiter is built correctly and does what was asked. There are two small fixes to make before relying on it. Its "how long to wait" answer can come out a tiny bit too short, and an invalid setting such as "not a number" can quietly switch the limiting off.

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
    {"item": "test run output / Python version", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "token_bucket.py", "kind": "file"},
      {"unit": "token_bucket.py:TokenBucket.__init__", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket._refill", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket.try_acquire", "kind": "function"},
      {"unit": "token_bucket.py:TokenBucket.seconds_until", "kind": "function"},
      {"unit": "test_token_bucket.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no tools in session"},
      {"unit": "lock mutation test", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py: seconds_until return vs try_acquire `self._tokens >= n`",
     "scenario": "Clock at 100.0, rate 3, empty bucket: seconds_until(1)=0.3333333333333333; after advancing the clock by it, elapsed*rate = 0.9999999999999858 < 1 so try_acquire(1) returns False and seconds_until returns ~5e-15, causing a spin loop or flaky fake-clock tests.",
     "fix": "Use one tolerance in both methods (tokens + 1e-9 >= n; missing <= 1e-9 returns 0) or keep tokens in integer micro-units.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "c=FakeClock(); b=TokenBucket(5,3,clock=c); b.try_acquire(5); c.t += b.seconds_until(1); expect b.try_acquire(1) True, hand calculation gives False."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py: __init__ validation; try_acquire and seconds_until range checks",
     "scenario": "TokenBucket(5, float('nan')): min(capacity, NaN) returns capacity, so every call after the clock moves refills fully and the limiter stops limiting; rate=inf does the same; NaN capacity denies forever; seconds_until(nan) returns NaN.",
     "fix": "Reject non-finite capacity, refill_per_sec and n with math.isfinite.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "c=FakeClock(); b=TokenBucket(5,float('nan'),clock=c); loop: b.try_acquire(5); c.t+=1e-6; expect try_acquire(5) False, observe True."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py: test_bad_arguments",
     "scenario": "Deleting the n-range check in seconds_until or the rate<=0 check leaves all tests green.",
     "fix": "Add assertRaises for try_acquire(0), try_acquire(-1), TokenBucket(1,0), seconds_until(0), seconds_until(6).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Remove the ValueError check in seconds_until; run the suite; it stays green."},
    {"id": "S1", "status": "needs_validation", "track": "B",
     "location": "test_token_bucket.py: test_threads_never_over_issue",
     "suspicion": "Under the GIL the race window is so small the test likely passes with the lock removed, leaving thread safety effectively untested.",
     "unresolved_fact": "Whether the test goes red in a scratch copy with `with self._lock` removed, over ~50 runs."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "try_acquire blocks because it takes a lock.",
     "evidence": "The lock covers a short bounded section with no waiting or I/O; 'never blocks' means never waits for tokens."},
    {"id": "R2", "candidate": "Backward clock jumps lose or mint tokens.",
     "evidence": "_refill ignores elapsed <= 0 and keeps _last; traced 100 -> 50 -> 100.5 yields exactly 1 token, matching the test."},
    {"id": "R3", "candidate": "Tokens can exceed capacity.",
     "evidence": "min(self.capacity, ...) caps refill; test_never_exceeds_capacity covers it."}
  ]
}
```