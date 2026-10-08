# pr-review: TokenBucket

## Review report

**REVIEWED:** No PR number, head SHA or merge base was supplied. The inputs are two files pasted inline, so I couldn't freeze the target (Step 1). This review covers the text of `token_bucket.py` and `test_token_bucket.py` exactly as given. If those files differ from the PR head, it does not apply to that head. Whoever posts this should attach the head SHA it matches.

**TIER:** Standard. This is ordinary code in a small shared library, with no auth, secrets, network exposure, personal data or money. One round was run and that completes the budget.

**DATA (Step 3):** The code carries no personal or secret data. The review ran in this session and nothing was sent to another endpoint.

**REVIEWERS:**
- Reviewer: this session, Claude Opus 5.5 (`claude-opus-5-5`). It did not write or help write the change.
- Author: unknown. No commits or `Co-Authored-By` trailers were provided.

**Verification limits:** I have no tools in this session, so nothing was run. The claim "7 tests, all pass" is unverified. I counted 7 tests and traced each by hand, and all 7 should pass against this code. Each finding below is backed by reasoning or hand arithmetic, not an executed test.

**Requirement coverage:**

| Requirement | Status |
|---|---|
| Capacity N, refill R per second | Met |
| Thread-safe | Met: one lock around every read and write of `_tokens` and `_last` |
| Injectable clock | Met |
| `try_acquire` never blocks | Met: the only wait is a short uncontended critical section |
| Time-until-available method | `seconds_until` exists, but see #1 |
| Tests included | Met |
| Nothing extra | Met |

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `token_bucket.py:40-41` (`seconds_until`), interacting with `:18-20` and `:29` | **The promised wait can be too short.** The wait is computed as `missing / rate`. The tokens actually gained after that wait are `(now - last) * rate`, and the subtraction loses precision when clock values are large. Worked example: capacity 5, rate 3, clock starts at 100.0. Drain the bucket, so `seconds_until(1)` returns 0.3333333333333333. Advance the clock by exactly that amount, giving 100.33333333333333. Then `elapsed` is 0.33333333333332860, `elapsed * 3` is 0.99999999999998579, which is less than 1, and `try_acquire(1)` returns **False** at the moment the API said it would succeed. A caller that does `sleep(b.seconds_until(n)); b.try_acquire(n)` can spuriously fail, then retry, spin or drop work. The error grows with clock magnitude, for example `time.monotonic()` on a long-running host. Tests that use the fake clock hit it deterministically. | `FakeClock` at t=100.0, `TokenBucket(5, 3, clock)`, `try_acquire(5)`, then `w = seconds_until(1)`, `clock.t += w`, then `assertTrue(try_acquire(1))`. This fails today. Fix it by rounding the returned wait up by a few ulps (`math.nextafter`) or a small epsilon, or by comparing `_tokens >= n - eps` in `try_acquire`. |
| 2 | P3 | `token_bucket.py:8`, `:25`, `:36` | **NaN passes validation.** All the guards are written as `x <= 0` or `n > capacity`, and every comparison with NaN is False. So `try_acquire(float('nan'))` silently returns False forever, and `seconds_until(float('nan'))` returns `nan`, which makes `time.sleep(nan)` raise. `TokenBucket(float('nan'), 1)` and `TokenBucket(5, float('nan'))` are also accepted, and the second makes `seconds_until` return `nan`. | `assertRaises(ValueError)` for `try_acquire(nan)`, `seconds_until(nan)`, `TokenBucket(nan, 1)` and `TokenBucket(1, nan)`. Fix by validating with `math.isfinite` plus a positive check, or with the positive form `not (0 < n <= capacity)`. |
| 3 | P3 | `token_bucket.py:18-21`; behaviour pinned by `test_token_bucket.py:36-41` | **A backward clock step stalls refills.** When the clock steps back, `_last` is left at the old, later time. If a non-monotonic clock is injected (for example `time.time` across an NTP or DST step back of D seconds), the bucket refills nothing for D seconds. During that time `seconds_until` under-reports the real wait by D, so callers sleep, fail and re-sleep for the whole gap. This is a design choice, and the test currently specifies it. | Step the clock back 3600 s, then forward 1 s from the new time, and assert at least one refilled token is available. Fix by setting `_last = now` when `elapsed < 0`, and update `test_clock_going_backwards` to match. |
| 4 | P3 | `test_token_bucket.py:54-66` (`test_threads_never_over_issue`) | **The thread-safety test would not catch a missing lock.** The clock is constant, so no refill path runs. The critical section is a handful of bytecodes, while the default GIL switch interval is 5 ms. Delete the `with self._lock:` lines and this test will almost certainly still pass. Thread-safety, a stated requirement, therefore has no test that guards it. | Widen the race window deterministically: inject a clock that calls `time.sleep(0)` or waits on a `threading.Barrier` inside `__call__` so threads interleave between refill and decrement. Run it with `sys.setswitchinterval(1e-6)`, advance time concurrently, and assert total taken ≤ capacity + rate × elapsed. Confirm the test fails with the lock removed. |

**FILES NEEDED BUT NOT PROVIDED:**
- The PR itself: head SHA, merge base, commit trailers and CI check results.
- The callers of `TokenBucket` in the shared library, which would show whether anyone injects a non-monotonic clock (affects the severity of #3) or uses the sleep-then-acquire pattern (affects #1).

## Close-out

**Not written.** Adjudication belongs to the author, and the close-out to whoever closes the PR. A reviewer does not adjudicate its own findings. The open items for the close-out are:
- a decision on each of #1–#4;
- the reviewed SHA;
- the CI check status, which is unknown here. A missing check is not green.

**Reviewer's input to the merge decision:** merge after fixes. There is no P0 or P1. #1 is a real defect in a stated requirement and has a cheap fix. #2–#4 can be fixed or deferred with linked issues.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "reasoned (hand-computed float arithmetic; not executed)",
      "location": "token_bucket.py:40-41 (with :18-20, :29)",
      "scenario": "capacity 5, rate 3, fake clock at 100.0, bucket drained: seconds_until(1)=0.3333333333333333; advancing clock by exactly that gives elapsed=0.3333333333333286, refill 0.9999999999999858 < 1, so try_acquire(1) returns False at the promised time. Sleep-then-acquire callers spuriously fail.",
      "fix": "Round the returned wait up (math.nextafter / small epsilon) or compare tokens >= n - eps; add the regression test described."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned (Python NaN comparison semantics)",
      "location": "token_bucket.py:8, :25, :36",
      "scenario": "NaN n or NaN capacity/rate passes the <=0 / >capacity guards; try_acquire(nan) silently returns False forever, seconds_until(nan) returns nan, and time.sleep(nan) raises.",
      "fix": "Validate with math.isfinite and the positive form not (0 < n <= capacity); add assertRaises tests."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned (code trace)",
      "location": "token_bucket.py:18-21; test_token_bucket.py:36-41",
      "scenario": "An injected non-monotonic clock that steps back D seconds leaves _last in the future: no refill for D seconds, and seconds_until under-reports the wait by D.",
      "fix": "Set _last = now when elapsed < 0; update the test to assert refill resumes from the new time."
    },
    {
      "severity": "P3",
      "evidence_level": "reasoned (GIL switch interval vs. critical-section length)",
      "location": "test_token_bucket.py:54-66",
      "scenario": "With a constant clock and a tiny critical section, removing the lock would very likely still pass this test, so the thread-safety requirement is unguarded.",
      "fix": "Force interleaving (clock that yields or hits a Barrier, sys.setswitchinterval(1e-6), concurrent time advance); verify the test fails without the lock."
    }
  ]
}
```