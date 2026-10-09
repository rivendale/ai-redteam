**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so I ran nothing. Every result below comes from reading and tracing the code by hand. The work was not written in this conversation, so there is no author-context anchoring, but I had no subagent to delegate to.

VERDICT: **SHIP WITH FIXES**. The limiter is correct on its main paths and meets every stated requirement, but two things should be fixed: `seconds_until` can report a wait after which the tokens are still not available (float boundary), and the tests leave guards and the `seconds_until` contract unchecked.

CONFIDENCE: **medium**. Limited by having no tools (I ran neither the tests nor any reproduction; the float arithmetic was traced by hand), by the same-context review, and by having no subagent.

INPUTS LEDGER:
- Seen: `request.md` (verbatim request), `context.md`, `token_bucket.py`, `test_token_bucket.py`.
- Not seen: any test run output behind "7 tests, all pass". This matters a little; I traced all 7 as passing but did not run them.
- Not seen: target Python version or build (GIL or free-threaded). This matters for how much the thread-safety test proves (see NV1).

COVERAGE:
- Scope: the whole work (two files).
- Checked:
  - `token_bucket.py`: `__init__`, `_refill`, `try_acquire`, `seconds_until`.
  - `test_token_bucket.py`: all 7 tests, each traced against the code.
  - `request.md`: each requirement (capacity, rate, thread-safe, injectable clock, non-blocking `try_acquire`, wait-time method, tests).
  - `context.md`.
- Not checked: behaviour on free-threaded CPython and actual execution (no tools).

SEATS AND GATE:
- Sensitivity gate: no personal data, credentials or confidential material.
- Seats: a single local reviewer. No subagent or cross-vendor tool was available, and the user did not request cross-vendor seats.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (hand-traced float arithmetic, not run) | B | `token_bucket.py:41`, `:29` (also `:18`) | `seconds_until` returns the exact `missing/rate`. Advancing the clock by that amount can give `elapsed*rate` slightly below `missing`, so the strict `>= n` at line 29 still fails. | Fake clock at 100.0, `TokenBucket(5, 3)`. Drain with `try_acquire(5)`. `seconds_until(1)` returns 0.3333333333333333. Set the clock to 100 + that value, which rounds to 100.33333333333333. Then elapsed = 0.3333333333333286, tokens = 0.9999999999999858, and `try_acquire(1)` returns **False**. A caller doing `sleep(b.seconds_until(n)); b.try_acquire(n)` with the injected clock fails. With `time.monotonic` it fails only when sleep overshoot is below about 1e-14 s, which is rare. Repeated small refills can drift the same way, since summing 0.1 ten times gives 0.9999999999999999. | **Fix:** compare with a tolerance (`self._tokens + 1e-9 >= n`) and/or round the returned wait up (e.g. `math.nextafter`, or add a small epsilon). Alternatively, keep time in integer nanoseconds and tokens as integers or `Fraction`. **Repro:** `c=FakeClock(); b=TokenBucket(5,3,clock=c); b.try_acquire(5); c.t += b.seconds_until(1); assert b.try_acquire(1)` is expected to pass but is traced to fail. | a Y, b Y, c N (the contract is off by about 1e-14 s), d N |
| F2 | Low | CONFIRMED (traced) | B | `test_token_bucket.py` `test_seconds_until`, `test_bad_arguments` | Guards and contract branches have no test. All 7 tests still pass under these mutations: (1) delete `n <= 0 or` at `token_bucket.py:25`, which lets `try_acquire(-5)` mint 5 tokens; (2) delete the `0.0 if missing <= 0 else` branch at `:41`, which makes `seconds_until` return a negative value when tokens are available; (3) drop the `refill_per_sec <= 0` check at `:8`. Also missing: any test that advancing the clock by `seconds_until(n)` makes `try_acquire(n)` succeed. That test would have caught F1. | A future edit removes or breaks one of these lines and CI stays green. The negative-`n` case quietly lets callers exceed the rate limit. | **Fix:** add tests for `try_acquire(0)`, `try_acquire(-1)`, `seconds_until(0)`, `seconds_until(6)`, `TokenBucket(5, 0)`, `seconds_until` returning 0.0 when tokens are available, and an "advance by `seconds_until`, then acquire" property over several rates (e.g. 3, 7, 0.1). **Repro:** apply mutation (1), run `python -m unittest`, observe 7 passes. Traced, not run. | a Y, b Y, c N, d N |
| F3 | Low | CONFIRMED (traced) | B | `token_bucket.py:8`, `:25`, `:36` | NaN passes every range check, because comparisons with NaN are all False. | `TokenBucket(float('nan'), 1)` constructs. Every `try_acquire` then returns False silently, a permanent deny with no error. `seconds_until(float('nan'))` returns `nan`, and `time.sleep(nan)` then raises. | **Fix:** `if not (math.isfinite(capacity) and capacity > 0 ...)`, with the same check on `n`. **Repro:** `b=TokenBucket(float('nan'),1); assert b.try_acquire() is False`. | a Y, b Y, c N, d N |
| F4 | Low | CONFIRMED (traced) | B | `token_bucket.py:18-21`, `:40-41` | When an injected clock reads earlier than `_last`, `seconds_until` reports `missing/rate` and ignores the gap the clock must recover first. | Run `test_clock_going_backwards_is_ignored` up to `clock.t -= 50`. At that point `seconds_until(1)` returns 0.5, but 50.5 clock-seconds are actually needed. This only happens with a non-monotonic injected clock, such as `time.time` after an NTP step. | **Fix:** return `max(0, self._last - now) + missing/self.rate`, or document that the clock must be monotonic. **Repro:** in that test, after `-= 50`, assert `seconds_until(1) == 50.5`; it returns 0.5. | a Y, b Y, c N, d N |

### NEEDS VALIDATION
- **NV1:** `test_threads_never_over_issue` may never go red with the lock removed on GIL CPython. The check-then-decrement window is tiny and the GIL switch interval is 5 ms. *Settled by:* remove `with self._lock` (in a scratch copy) and run the test about 100 times on standard CPython and on free-threaded 3.13t. Until then, the claim that this test proves thread safety is UNVERIFIED. The code itself is correctly locked.
- **NV2:** "7 tests, all pass." I count 7 tests and traced each one as passing, but I did not run them. *Settled by:* running `python -m unittest -v`.

### REFUTED
- **"`try_acquire` blocks because it takes a `threading.Lock`."** Withdrawn. The request's "never block" means it does not wait for tokens. The critical section is O(1) arithmetic plus one clock call, and a non-blocking lock attempt would return spurious False results, which is worse. Residual note: a slow injected clock is called under the lock and would serialize callers. Documenting that is enough.
- **"A clock going backwards credits extra tokens."** Withdrawn. The `elapsed > 0` guard at `:19` leaves `_last` untouched, so no tokens are credited until the clock passes the old high-water mark.
- **"A long idle period over-issues tokens."** Withdrawn. `min(self.capacity, ...)` at `:20` caps the count, and `test_never_exceeds_capacity` covers it. An `inf` elapsed time also clamps to capacity.

### WHAT HOLDS UP
- Locking covers the whole read-refill-decide-write sequence in both public methods.
- The injected clock works and the tests never sleep.
- Capacity is enforced, and validation rejects `n > capacity` on both methods.
- Backwards-clock handling is sound for issuance.
- The requirement fit is complete with nothing extra.

### UNVERIFIED CLAIMS
- "All 7 tests pass": run them.
- "Thread-safe as proven by the test": the code is safe by reading, but the test's power is unverified (NV1).

### QUESTIONS FOR THE AUTHOR
1. Is exact-boundary behaviour (acquiring after advancing by `seconds_until`) part of the contract callers will rely on? If so, F1 rises in priority.
2. Which Python builds must this support? Free-threaded builds make NV1 matter.

### DECISION-MAKER SUMMARY
The limiter is correct and complete in substance. Before sharing it, fix the float boundary in F1 and add the missing guard and contract tests (F2). If it ships as is, the main risk is flaky "wait, then acquire" behaviour in callers' fake-clock tests, plus untested guards that can regress silently.

### OWNER SUMMARY
The rate limiter works as asked and safely handles many callers at once. A tiny rounding issue can make it say "wait this long" when slightly longer is actually needed, and a few safety checks have no test protecting them. Both are small fixes and should be made before others depend on the library.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "token_bucket.py", "status": "seen", "matters": true},
    {"item": "test_token_bucket.py", "status": "seen", "matters": true},
    {"item": "test run output for '7 tests, all pass'", "status": "not_seen", "matters": false},
    {"item": "target Python version/build", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "token_bucket.py", "kind": "file"},
      {"unit": "token_bucket.py:__init__", "kind": "function"},
      {"unit": "token_bucket.py:_refill", "kind": "function"},
      {"unit": "token_bucket.py:try_acquire", "kind": "function"},
      {"unit": "token_bucket.py:seconds_until", "kind": "function"},
      {"unit": "test_token_bucket.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "claim: 7 tests, all pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "execution of tests and reproductions", "reason": "no_tools"},
      {"unit": "free-threaded CPython behaviour", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:41, token_bucket.py:29",
     "scenario": "With TokenBucket(5, 3) drained and a fake clock at 100.0, advancing the clock by seconds_until(1)=0.3333333333333333 yields tokens=0.9999999999999858, so try_acquire(1) returns False at the reported time.",
     "fix": "Compare with a tolerance (tokens + 1e-9 >= n) and/or round the returned wait up; or use integer nanoseconds/Fraction.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "c=FakeClock(); b=TokenBucket(5,3,clock=c); b.try_acquire(5); c.t += b.seconds_until(1); assert b.try_acquire(1)  # expected pass, traced to fail (not run)"},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py:test_seconds_until, test_bad_arguments",
     "scenario": "Deleting 'n <= 0 or' at token_bucket.py:25 (letting try_acquire(-5) mint tokens), the zero branch at :41, or the rate check at :8 leaves all 7 tests green.",
     "fix": "Add tests for n<=0, seconds_until validation and zero case, refill_per_sec<=0, and an advance-by-seconds_until-then-acquire property over several rates.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy remove 'n <= 0 or' from token_bucket.py:25; run python -m unittest; traced: 7 pass (not run)."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:8, :25, :36",
     "scenario": "TokenBucket(float('nan'), 1) constructs and then denies every request silently; seconds_until(nan) returns nan.",
     "fix": "Validate with math.isfinite(...) and > 0 for capacity, rate and n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "b=TokenBucket(float('nan'),1); b.try_acquire() returns False; expected ValueError at construction."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:18-21, :40-41",
     "scenario": "After an injected clock steps back 50s, seconds_until(1) reports 0.5 though 50.5 clock-seconds are needed.",
     "fix": "Add max(0, self._last - now) to the returned wait, or document that the clock must be monotonic.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In test_clock_going_backwards_is_ignored after clock.t -= 50, assert b.seconds_until(1) == 50.5; traced value 0.5."},
    {"id": "NV1", "status": "needs_validation", "track": "B", "location": "test_token_bucket.py:test_threads_never_over_issue",
     "suspicion": "The thread test may pass with the lock removed on GIL CPython, so it may not prove thread safety.",
     "unresolved_fact": "Whether removing 'with self._lock' in a scratch copy makes the test fail across ~100 runs on CPython and 3.13t."},
    {"id": "NV2", "status": "needs_validation", "track": "B", "location": "context.md: 'Tests: 7 tests, all pass'",
     "suspicion": "Pass claim not observed.",
     "unresolved_fact": "Output of python -m unittest -v."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "try_acquire blocks because it takes a threading.Lock.",
     "evidence": "The request's 'never block' means not waiting for tokens; the critical section is O(1) plus a clock call (token_bucket.py:27-32)."},
    {"id": "C2", "candidate": "A clock going backwards credits extra tokens.",
     "evidence": "The elapsed > 0 guard at token_bucket.py:19 leaves _last unchanged; no credit until the clock passes it."},
    {"id": "C3", "candidate": "A long idle period over-issues beyond capacity.",
     "evidence": "min(self.capacity, ...) at token_bucket.py:20; covered by test_never_exceeds_capacity."}
  ]
}
```