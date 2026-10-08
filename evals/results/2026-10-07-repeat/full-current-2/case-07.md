**Review mode: same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools, so I could not delegate to a subagent or run anything. I did not write the work. Every behavioural claim below comes from tracing the code by hand, not from running it.

---

**VERDICT: SHIP WITH FIXES.** The limiter is correct on every path I traced, but two tests would stay green if the bugs they are named after were introduced.

**CONFIDENCE: medium.** Three things limit it: I did not execute anything, this is a same-context review, and the thread-safety assessment depends on CPython scheduling that I could not observe.

**INPUTS LEDGER**
- **Seen:** request.md (the original request), context.md, `token_bucket.py`, `test_token_bucket.py`.
- **Not seen:** any test run output. The context says "7 tests, all pass". I traced all 7 by hand and each one passes, so the claim holds by trace but is not observed. This gap does not change the verdict.
- **Not seen:** the Python version and whether the build is free-threaded. This matters only for finding 2.

**SEATS AND GATE**
- No sensitive data, so the gate passed.
- One seat ran: a local same-context review.
- No subagent or cross-vendor seats were available because this session has no tools.

---

## Pass 1: Reconstruct

The work claims to deliver a token bucket that:
- holds at most `capacity` tokens and refills continuously at `rate` per second,
- has a non-waiting `try_acquire(n)`,
- has `seconds_until(n)` reporting the wait until n tokens are available,
- uses a lock for thread safety and an injectable clock.

For it to be correct, three things must hold:
- the read, refill, check and decrement must happen under one lock,
- the refill must clamp at capacity and must not credit time that never elapsed,
- the tests must actually fail when those properties break.

Load-bearing assumptions:
- The clock is monotonic, or the backwards-clock policy is sound.
- Argument validation rejects every input that could cause a permanent wait.
- Track B applies.

---

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (traced) | B | `test_token_bucket.py:36-41` | `test_clock_going_backwards_is_ignored` cannot detect the bug it is named for. It asserts only that at least one token is available. | **Mutation:** in `_refill`, replace the guard with `elapsed = max(elapsed, 0)` and always set `_last = now`. **Trace:** the clock drops from 100 to 50, so `_last` becomes 50. The clock then moves to 100.5, so elapsed is 50.5 and tokens become `min(5, 101) = 5`. **Result:** a backwards-then-forward clock jump grants a full phantom burst, and the test still passes. Removing the guard entirely (letting tokens go negative) also passes. | After line 41, add `self.assertFalse(self.b.try_acquire())`. Alternatively assert `seconds_until(1) == 0` and `seconds_until(2) == 0.5`. Also add a variant that starts with a full bucket, which separates "ignore" from "debit". | n/a (Medium) |
| 2 | Medium | PROBABLE | B | `test_token_bucket.py:54-66` | The thread test is unlikely to go red if the lock is removed. That leaves "thread-safe" effectively unguarded. | 8 threads × 50 iterations is about 400 cheap calls. Under the GIL with the default 5 ms switch interval, each worker likely finishes inside one timeslice. A preemption landing between `if self._tokens >= n` (line 29) and `-=` (line 30) is rare. **Result:** a lock-free regression ships green. Rule 5: I could not run this mutation, so the test's coverage is UNVERIFIED. | Force the race deterministically. One way: a test subclass that makes `_tokens` a property whose getter calls `time.sleep(0)`. Another way: `sys.setswitchinterval(1e-6)` with far more iterations, using a `threading.Barrier` start. Then confirm the test fails with the `with self._lock:` lines removed. | n/a |
| 3 | Low | CONFIRMED (traced) | B | `test_token_bucket.py:43-46`; `token_bucket.py:41` | The "0 if available now" branch of `seconds_until` is never exercised. Line 46 only checks `> 0` on an empty bucket; its `+ 0` is noise, and it uses `assertEqual(x, True)`. | **Mutation:** change line 41 to `return missing / self.rate`, which returns negative seconds when tokens are available. All 7 tests still pass. A caller doing `time.sleep(b.seconds_until())` would then get `ValueError` on a full bucket. | Add a test that asserts `seconds_until(1) == 0.0` on a full bucket. Add a round-trip test: drain the bucket, read `w = seconds_until(k)`, advance the clock by `w`, then assert `try_acquire(k)`. | n/a |
| 4 | Low | CONFIRMED (traced) | B | `token_bucket.py:8, 25, 36` | NaN passes every validation check, because both `nan <= 0` and `nan > cap` are False. | `try_acquire(float('nan'))` returns False forever. `seconds_until(nan)` returns `nan`, and a caller passing that to `time.sleep` raises. `TokenBucket(float('nan'), 1)` constructs a bucket that never grants anything. `float('inf')` capacity or rate is also accepted. | Write the checks positively, for example `if not (0 < n <= self.capacity)`. Add `math.isfinite` checks for capacity and rate in the constructor. Add one test for each case. | n/a |
| 5 | Low | CONFIRMED (traced) | B | `test_token_bucket.py:48-52` | Most validation branches are untested: `refill_per_sec <= 0`, `n <= 0`, and all of `seconds_until`'s argument checks. | Deleting `or refill_per_sec <= 0` (line 8) or `n <= 0` (lines 25 and 36) leaves every test green. A rate of 0 would then make `seconds_until` divide by zero. | Add `assertRaises` cases for `TokenBucket(1, 0)`, `try_acquire(0)`, `seconds_until(0)` and `seconds_until(6)`. | n/a |
| 6 | Low | PROBABLE | B | `token_bucket.py:17-21, 40-41` | If the injected clock goes backwards, the bucket stops refilling until the clock passes `_last` again. `seconds_until` does not account for this gap. | A user injects `time.time` and NTP steps the clock back 1 hour. No refill happens for an hour, while `seconds_until` keeps reporting short waits. The default `time.monotonic` is safe, so this needs a non-default clock. | Document that the clock must be monotonic. Alternatively, on a negative `elapsed`, reset `_last = now` without crediting tokens. This also makes finding 1's test meaningful. | n/a |
| 7 | Low | PROBABLE | B | `token_bucket.py:40-41` | Float rounding can make the documented wait fall slightly short. | Example: tokens are 0.3, rate is 3, and the caller sleeps exactly `seconds_until(1)` (0.2333...). The recomputed `(t + w) - t` times 3 plus 0.3 can land 1 ulp below 1.0. `try_acquire` then returns False, and the caller has to retry. | Add a tiny epsilon in the comparison, or document "may need one retry". Cover it with the round-trip test from finding 3, using non-dyadic values. | n/a |
| 8 | Low | CONFIRMED (traced) | B | `token_bucket.py:28, 39` | The injected clock is called while the lock is held. | A slow or blocking clock (for example, one that does I/O) makes `try_acquire` block and serializes every caller. That bends the "must never block" requirement. With `time.monotonic` the hold time is negligible. | Document that the clock must be cheap and non-blocking. Alternatively, read the clock before taking the lock and pass `max(now, self._last)` into it. | n/a |

---

## WHAT HOLDS UP

- **Atomicity.** Refill, check and decrement all happen under a single lock (lines 27-32). The same is true for `seconds_until`. I found no unlocked read-modify-write.
- **Capacity clamp.** `min(capacity, ...)` holds. `test_never_exceeds_capacity` would go red if `min` were removed: tokens would reach 2005 and the second acquire would succeed.
- **Idle refill does not accumulate.** `_last` advances even when the bucket is full, so idle time does not bank extra tokens beyond capacity.
- **Never waits for tokens.** `try_acquire` returns immediately whether or not tokens are available.
- **No infinite wait for oversized requests.** Rejecting `n > capacity` means `seconds_until` never promises a wait that can never be satisfied.
- **Refill rate is guarded.** `test_refills_at_rate` would catch a wrong rate, and its trailing `assertFalse` pins the exact count.
- **All 7 tests pass by trace.**
- **The rest of the request is met:** injectable clock, rate and capacity parameters, and a wait-time method.

## UNVERIFIED CLAIMS

- **"7 tests, all pass."** True by trace, but not observed. To settle it, run `python -m unittest -v`.
- **"Thread-safe" is covered by tests.** To settle it, delete the `with self._lock:` lines in a scratch copy and run `test_threads_never_over_issue` about 50 times. If it never fails, finding 2 is confirmed.

## QUESTIONS FOR THE AUTHOR

1. Is the clock required to be monotonic? If yes, findings 1 and 6 reduce to documentation plus a sharper test. If no, the backwards-clock policy needs a decision.
2. Which Python versions are targeted, and is free-threaded 3.13t among them? The answer affects how severe a missing lock would be, and how likely the existing thread test is to catch it.

## DECISION-MAKER SUMMARY

The limiter's logic is sound and can ship once the tests are tightened. The main fixes are the backwards-clock assertion, a deterministic race test, and coverage of the `seconds_until` zero path, plus NaN validation. If it ships as is, the code works today, but a future edit could break thread safety or the clock handling without any test noticing.

## OWNER SUMMARY

The rate limiter itself appears to work correctly and safely. Some of its tests are too weak to catch the mistakes they are meant to catch, so a future change could break it silently. Strengthening a few tests and rejecting a couple of invalid inputs would make it ready to rely on.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "token_bucket.py", "status": "seen", "matters": true},
    {"item": "test_token_bucket.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "target Python version / free-threading", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_token_bucket.py:36-41",
     "scenario": "Mutating _refill to clamp elapsed at 0 while always setting _last=now grants 5 phantom tokens after a back-50/forward-50.5 clock jump; the test only asserts >=1 token and stays green.",
     "fix": "Assert exactly one token is available after line 41 (try_acquire False afterwards, or seconds_until(2)==0.5); add a full-bucket variant.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "test_token_bucket.py:54-66",
     "scenario": "With the lock removed, ~400 cheap calls under the GIL rarely preempt between the check (line 29) and the decrement (line 30), so over-issue goes undetected.",
     "fix": "Force the race with a test subclass whose _tokens getter sleeps(0), or a tiny switch interval plus a Barrier; confirm the test goes red without the lock.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "test_token_bucket.py:43-46; token_bucket.py:41",
     "scenario": "Removing the 0.0 clamp makes seconds_until return negative seconds when tokens are available; all tests stay green, and time.sleep(negative) raises.",
     "fix": "Test seconds_until(1)==0 on a full bucket, plus a round trip: advance the clock by seconds_until(k), then assert try_acquire(k).", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "token_bucket.py:8,25,36",
     "scenario": "NaN passes validation: try_acquire(nan) is False forever, seconds_until(nan) returns nan, and TokenBucket(nan, 1) constructs; inf is also accepted.",
     "fix": "Use `if not (0 < n <= self.capacity)` and math.isfinite checks in __init__; add tests.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "test_token_bucket.py:48-52",
     "scenario": "Deleting the rate<=0 or n<=0 checks leaves all tests green; rate 0 then divides by zero in seconds_until.",
     "fix": "Add assertRaises for TokenBucket(1,0), try_acquire(0), seconds_until(0), seconds_until(6).", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "token_bucket.py:17-21,40-41",
     "scenario": "With an injected wall clock stepped back 1h, refill stalls for an hour while seconds_until reports short waits.",
     "fix": "Document that the clock must be monotonic, or reset _last on negative elapsed without crediting tokens.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "token_bucket.py:40-41",
     "scenario": "Float rounding: sleeping exactly seconds_until(n) can leave tokens 1 ulp short, so try_acquire(n) returns False once.",
     "fix": "Add an epsilon or document a retry; cover with a non-dyadic round-trip test.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "token_bucket.py:28,39",
     "scenario": "The injected clock runs under the lock; a slow or blocking clock makes try_acquire block and serializes all callers.",
     "fix": "Document that the clock must be cheap and non-blocking, or read it before taking the lock.", "status": "n/a"}
  ]
}
```