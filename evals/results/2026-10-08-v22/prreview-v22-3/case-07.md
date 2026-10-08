# Review report

**REVIEWED:** No PR number, head SHA or merge base was supplied. The work under review is the two files pasted inline, `token_bucket.py` and `test_token_bucket.py`. I could not freeze a commit, so this review applies only to the text quoted above. Anyone closing the PR must confirm that the PR head matches it byte for byte, and record both SHAs.

**TIER:** Standard. This is an ordinary code change to a small shared library. It touches no authentication, permissions, secrets, network exposure, data handling or money. One model round is required, and this report is that round.

**DATA:** The code is a pure rate-limit algorithm and carries no personal or regulated data. It was reviewed in-session and sent nowhere else.

**REVIEWERS:**
- Reviewer: Claude Opus 5.5 (`claude-opus-5-5`), a fresh session with no part in writing the change.
- Author: unknown. No commit or `Co-Authored-By` trailers were provided, so record them at close-out.

**Verification limits:** I had no tools in this session, so nothing was run. The claim "7 tests, all pass" is unverified. Tracing each test by hand, all 7 should pass against this code. Every finding below comes from reading the code and tracing values, not from execution.

**Request coverage:**
- Capacity and refill rate: present.
- Thread safety: a lock is present.
- Injectable clock: present.
- Non-blocking `try_acquire`: present.
- `seconds_until`: present.
- Tests: present.
- Nothing extra was added.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `token_bucket.py:19-21` (`_refill`), affects `token_bucket.py:41` | **A backward clock step is charged against future refill instead of being ignored.** When `elapsed <= 0`, `_last` keeps the old high-water time, so no tokens accrue until the clock climbs back past it. Traced with the existing test: drain at t=100, step back to t=50, then advance 50.5 s to t=100.5. Only 0.5 s of refill is credited, and 50 s of real time is lost. This matters because the clock is injectable. A caller passing `time.time` sees an NTP step back of 1 h, and the limiter then grants nothing for an hour. During that window `seconds_until` (line 41) still reports `missing / rate`, for example 0.5 s, when the true wait is 50.5 s, so callers that sleep on it spin. The test `test_clock_going_backwards_is_ignored` (`test_token_bucket.py:36-41`) asserts this behaviour rather than catching it. | Drain the bucket at t=100, set t=50, and assert that `seconds_until(1)` either equals the real wait or that refill resumes from the new time. Under the latter, setting t=50.5 should make `try_acquire()` return True. Fails today. |
| 2 | P3 | `token_bucket.py:8`, `token_bucket.py:25`, `token_bucket.py:36` | **Validation accepts NaN and infinity.** Comparisons with `nan` are always False, so `TokenBucket(float('nan'), 1)` and `TokenBucket(5, float('nan'))` construct successfully. With `rate=nan`, `min(5.0, nan)` returns `5.0`, so every refill fills the bucket to capacity and the limit is gone. `capacity=inf` likewise gives an unlimited bucket. `try_acquire(float('nan'))` passes validation and returns False forever. `seconds_until(float('nan'))` returns `nan`, and passing that to `time.sleep` raises `ValueError`. | Assert that `ValueError` is raised for `TokenBucket(nan, 1)`, `TokenBucket(5, nan)`, `TokenBucket(inf, 1)`, `b.try_acquire(nan)` and `b.seconds_until(nan)`. All of these fail today. |
| 3 | P3 | `token_bucket.py:41` with `token_bucket.py:20` | **Floating-point rounding in the wait time.** `(n - tokens) / rate` followed by `tokens + elapsed * rate` does not always round-trip to `>= n`. A caller that sleeps exactly `seconds_until(n)` and then calls `try_acquire(n)` can get False when the fractional token count came from earlier float arithmetic, for example `rate=0.3` with a fractional `n`. Real `time.sleep` usually overshoots, so this is mostly theoretical with the default clock. It is reachable with a fake clock that advances exactly the reported amount. | Property test with a fake clock: for random rate, n and prior draws, set `t += b.seconds_until(n)` and assert `b.try_acquire(n)` is True. This may fail on some inputs today. |
| 4 | P3 | `test_token_bucket.py:55-67` | **The thread test does not demonstrate thread safety.** The work per call is tiny and the GIL switch interval is 5 ms, so the check-then-decrement race at `token_bucket.py:29-30` would almost never interleave. The test would very likely still pass with the lock removed. The "thread-safe" claim is therefore untested. | Delete `with self._lock` and confirm the test fails. To make it fail reliably, inject a clock that calls `time.sleep(0)`, or set `sys.setswitchinterval(1e-6)` inside the test. |
| 5 | P3 | `test_token_bucket.py:43-53` | **Test coverage gaps.** There is no test that `seconds_until` returns `0.0` when tokens are available, and none that it raises on a bad `n`. Nothing covers `n=0`, negative `n`, negative or zero `refill_per_sec`, or a fractional partial refill. The assertion at line 46, `seconds_until(0.0001) > 0`, is weak, and `assertEqual(x, True)` should be `assertTrue`. | Add tests for `seconds_until(1) == 0.0` on a full bucket, `ValueError` for `try_acquire(0)`, `try_acquire(-1)`, `seconds_until(6)` and `TokenBucket(5, 0)`, and refill after `t += 0.25` giving exactly 0.5 tokens. |

**No P0 or P1 found.** The core logic is correct for the default monotonic clock:
- the refill is capped at capacity;
- the check and the decrement in `try_acquire` are atomic under the lock;
- `try_acquire` never blocks beyond lock acquisition.

**FILES NEEDED BUT NOT PROVIDED:** the PR description, the commit list with trailers, and the CI configuration and check results.

# Close-out

Not written by me: the reviewer does not adjudicate its own findings. The author must record a decision for each finding:
- **Accepted:** name the fix commit and the regression test.
- **Deferred:** allowed only for P2 or P3, with a linked issue.
- **Rejected:** give the evidence.

**ADJUDICATION:** pending for findings #1 to #5.

**VERIFIED AFTER FIXES:** none yet. Each fix should get a targeted read of its own diff plus its new test, not another full round.

**MERGE RECOMMENDATION (provisional): merge after fixes.** This recommendation becomes final only once all of these hold:
- the reviewed text is tied to a head SHA;
- all five findings have written decisions;
- all expected CI checks are present and green.

Finding #1 is P2 and may be deferred with a linked issue. I recommend fixing it, because the injectable clock is an explicit requirement and the backward-step behaviour silently stalls the limiter.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "traced by reading (not executed)",
      "location": "token_bucket.py:19-21, token_bucket.py:41",
      "scenario": "Clock steps back by D (e.g. injected time.time after an NTP correction): _last keeps the old value, so no refill accrues for D seconds of real time, and seconds_until reports missing/rate (e.g. 0.5s) while the true wait is D+0.5s. The existing backwards-clock test asserts this behaviour.",
      "fix": "When now < self._last, set self._last = now without adding tokens (resume refill from the new time); update test_clock_going_backwards_is_ignored to expect a refill 0.5s after the step back."
    },
    {
      "severity": "P3",
      "evidence_level": "traced by reading (not executed)",
      "location": "token_bucket.py:8, token_bucket.py:25, token_bucket.py:36",
      "scenario": "NaN or infinite capacity/refill_per_sec/n pass validation because comparisons with NaN are False; rate=nan makes min(capacity, nan) return capacity on every refill (unlimited), try_acquire(nan) always returns False, and seconds_until(nan) returns nan.",
      "fix": "Validate with math.isfinite(x) and x > 0 for capacity, refill_per_sec and n; add tests for each."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned from floating-point semantics (not executed)",
      "location": "token_bucket.py:41, token_bucket.py:20",
      "scenario": "Advancing a fake clock by exactly seconds_until(n) can leave tokens a few ULP below n, so try_acquire(n) returns False right after the reported wait.",
      "fix": "Round the wait up (e.g. math.nextafter(result, inf)) or compare with a small epsilon in try_acquire; add a property test."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned (not executed)",
      "location": "test_token_bucket.py:55-67",
      "scenario": "With the lock removed, the check-then-decrement race at token_bucket.py:29-30 would almost never interleave under the GIL, so the test would very likely still pass; thread safety is effectively untested.",
      "fix": "Force interleaving (sys.setswitchinterval(1e-6) or a clock that calls time.sleep(0)) and confirm the test fails without the lock."
    },
    {
      "severity": "P3",
      "evidence_level": "read from tests",
      "location": "test_token_bucket.py:43-53",
      "scenario": "No test covers seconds_until returning 0.0 when tokens are available, seconds_until raising on bad n, n<=0, a zero or negative rate, or fractional refill; the line 46 assertion is near-trivial.",
      "fix": "Add these cases; use assertTrue instead of assertEqual(..., True)."
    }
  ]
}
```