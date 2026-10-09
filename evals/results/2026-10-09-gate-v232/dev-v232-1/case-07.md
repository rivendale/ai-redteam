**Same-context review.** No subagent or tools were available, so the reviewer and the reader share one context. Re-run in a fresh session for anything high-stakes. Nothing below was executed. Every behaviour was traced by reading the code against CPython semantics.

**VERDICT: SHIP WITH FIXES.** The limiter meets every stated requirement and all 7 tests pass by trace. The open findings are all Low: NaN values slip past input validation, and two tests guard less than they appear to.

**CONFIDENCE: medium.** Limits: no tools, nothing run, and one reviewer with no independent seat.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, token_bucket.py, test_token_bucket.py.
- **Not seen:** any CI or test output. The claim "7 tests, all pass" was checked by trace, not by a run. The gap matters only slightly because the tests are deterministic, except the thread test.
- Nothing else is referenced.

**COVERAGE**
- **Scope:** the whole work, both files.
- **Checked:**
  - the two files and the two input documents;
  - `__init__`, `_refill`, `try_acquire` and `seconds_until`;
  - all 7 tests;
  - every requirement clause: capacity N, refill R/s, thread-safe, injectable clock, non-blocking `try_acquire`, time-until-n method, tests.
- **Not checked:** runtime behaviour (no_tools).

**SEATS AND GATE:** one local reviewer. No subagent and no cross-vendor seats were available. Sensitivity gate: nothing sensitive.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Low | CONFIRMED (traced) | B | token_bucket.py:8 | `refill_per_sec <= 0` does not reject NaN. | A config value parses to NaN, e.g. `float("nan")`. In `_refill`, `min(5.0, tokens + elapsed*nan)` returns `5.0`, because `nan < 5.0` is False and `min` keeps the first item. Any elapsed time then refills the bucket to full, so the rate limit disappears. | Validate with `math.isfinite(...) and x > 0`, or `not (x > 0)`. **Repro:** `b = TokenBucket(5, float('nan'), clock=c)`, take 5 tokens, advance `c` by 1e-6, then `try_acquire(5)`. Expected: ValueError at construction. Traced result: True. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | token_bucket.py:8 | `capacity <= 0` does not reject NaN. | `TokenBucket(float('nan'), 1)` is accepted. `_tokens` is NaN, the check `n > nan` is False, and `nan >= n` is False. Every acquire is denied forever, silently. | Same fix as F1. **Repro:** `TokenBucket(float('nan'),1).try_acquire()`. Expected: ValueError at construction. Traced result: False. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (traced) | B | token_bucket.py:23, 34 | The `n` validation also lets NaN through. | `try_acquire(nan)` always returns False. `seconds_until(nan)` returns `nan`, and a caller doing `time.sleep(b.seconds_until(n))` then raises `ValueError` far from the cause. | Use `if not (0 < n <= self.capacity)`. **Repro:** `b.seconds_until(float('nan'))`. Expected: ValueError. Traced result: `nan`. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (traced) | B | test_token_bucket.py:test_bad_arguments | Tests do not guard the rate check, either `seconds_until` validation, or a partial-refill `seconds_until`. | Someone deletes `or refill_per_sec <= 0`. All 7 tests still pass, and `TokenBucket(5, 0)` then makes `seconds_until` divide by zero. | Add `assertRaises(ValueError)` for `TokenBucket(1, 0)`, `TokenBucket(1, -1)`, `seconds_until(0)` and `seconds_until(6)`. Add a `seconds_until` assertion after a partial refill. **Repro (mutation):** remove the rate check and run the tests. Expected: red. Traced result: green. | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION
- **S1 (test_threads_never_over_issue):** this test probably passes even with the lock removed. Each thread finishes 50 tiny iterations well inside CPython's 5 ms switch interval, so the race window is almost never hit. *Settling fact:* in a throwaway copy, replace `with self._lock:` with a no-op context and run the test about 1000 times. If it never goes red, the test proves nothing. A stronger test would use a `threading.Barrier` start, a clock that calls `time.sleep(0)` to force interleaving, or `sys.setswitchinterval(1e-6)`.
- **S2 (float rounding):** `try_acquire(n)` can fail right after sleeping exactly `seconds_until(n)`, because `elapsed*rate` lands just below `n`. The caller simply retries after a tiny delay, so there is no correctness loss. *Settling fact:* run with `time.monotonic` and fractional rates to see whether it happens and how often.

### REFUTED
- **"`try_acquire` can block on the lock."** The lock guards O(1) work. In a rate limiter, "never block" means never waiting for tokens, and the code honours that. A slow injected clock would block, but that clock belongs to the caller.
- **"Clock going backwards corrupts state."** `_refill` ignores non-positive elapsed time and keeps `_last`, so later refills count from the larger timestamp. The backwards-clock test traces correctly.

### WHAT HOLDS UP
- The refill math and the cap at capacity are correct.
- Clock reads happen inside the lock, so `_last` only moves forward.
- `seconds_until` returns `missing / rate`, which is correct for a single consumer.
- The clock is injectable and the default is `time.monotonic`, which is the right choice.
- All 7 tests pass by trace (0.5 s gives 1 token at rate 2, and so on).

### UNVERIFIED CLAIMS
- **"7 tests, all pass."** Confirm by running `python -m unittest` in a scratch copy.

### QUESTIONS FOR THE AUTHOR
- Should `try_acquire(n > capacity)` raise, or return False? Raising is defensible, but callers should know about it.

### DECISION-MAKER SUMMARY
The limiter is correct for normal inputs and meets the request. Before sharing it, reject NaN and infinite values in validation and add the missing validation tests. The risk if you ship as is: a mis-parsed config value could silently disable rate limiting.

### OWNER SUMMARY
The rate limiter works as asked and its tests pass. A few small gaps let an invalid setting either switch the limit off or block everything without any error. These take minutes to fix, and the tests should check them.

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
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "token_bucket.py", "kind": "file"},
      {"unit": "test_token_bucket.py", "kind": "file"},
      {"unit": "token_bucket.py:_refill", "kind": "function"},
      {"unit": "token_bucket.py:try_acquire", "kind": "function"},
      {"unit": "token_bucket.py:seconds_until", "kind": "function"},
      {"unit": "7 tests pass", "kind": "claim"}
    ],
    "not_checked": [{"unit": "runtime execution of tests", "reason": "no_tools"}]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:8",
     "scenario": "refill_per_sec=NaN passes validation; min(capacity, nan) returns capacity, so any elapsed time refills the bucket fully and the limit disappears.",
     "fix": "Validate with math.isfinite(x) and x > 0.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "b=TokenBucket(5,float('nan'),clock=c); take 5; advance c by 1e-6; try_acquire(5) -> expected ValueError at construction, traced True."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:8",
     "scenario": "capacity=NaN passes validation; every try_acquire returns False forever, silently.",
     "fix": "Validate with math.isfinite(x) and x > 0.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "TokenBucket(float('nan'),1).try_acquire() -> expected ValueError at construction, traced False."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "token_bucket.py:23,34",
     "scenario": "n=NaN passes validation; seconds_until returns nan and time.sleep(nan) raises ValueError far from the cause.",
     "fix": "Use if not (0 < n <= self.capacity): raise ValueError.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "b.seconds_until(float('nan')) -> expected ValueError, traced nan."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_token_bucket.py:test_bad_arguments",
     "scenario": "Deleting the refill_per_sec <= 0 check leaves all tests green; TokenBucket(5,0).seconds_until(1) then raises ZeroDivisionError.",
     "fix": "Add assertRaises for TokenBucket(1,0), TokenBucket(1,-1), seconds_until(0), seconds_until(6), plus a partial-refill seconds_until test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Mutation: remove 'or refill_per_sec <= 0' and run unittest; expected red, traced green."},
    {"id": "S1", "status": "needs_validation", "track": "B",
     "location": "test_token_bucket.py:test_threads_never_over_issue",
     "suspicion": "Test likely passes with the lock removed, so it does not guard thread safety.",
     "unresolved_fact": "Whether the test ever goes red over ~1000 runs with the lock replaced by a no-op in a scratch copy."},
    {"id": "S2", "status": "needs_validation", "track": "B",
     "location": "token_bucket.py:38",
     "suspicion": "Float rounding may make try_acquire fail right after sleeping exactly seconds_until(n).",
     "unresolved_fact": "Observed frequency with time.monotonic and fractional rates."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "try_acquire blocks on the lock, violating 'never block'.",
     "evidence": "The lock guards O(1) work; 'never block' means not waiting for tokens, which holds."},
    {"id": "C2", "candidate": "A clock going backwards corrupts refill state.",
     "evidence": "_refill ignores elapsed <= 0 and keeps _last; the backwards-clock test traces correctly."}
  ]
}
```