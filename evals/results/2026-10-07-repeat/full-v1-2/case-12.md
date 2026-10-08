**Review setup:** The work was not produced in this conversation, so the review is independent. There were no tools in this session, so nothing was executed. Behavior was established by tracing the code against Python semantics.

## Pass 1: Reconstruct

`retry(fn, ...)` calls a zero-argument `fn` up to `attempts` times. It retries only exceptions matching `retry_on`. Before try k+1 it sleeps `rng() * min(cap, base * 2**k)`. It never sleeps after the final attempt, and it re-raises the last caught exception. `sleep` and `rng` are injectable.

For this to be correct, a few things must hold:
- Injecting `sleep` must satisfy "the clock must be injectable." No elapsed-time logic exists, so `sleep` is the only clock touchpoint.
- Callers pass a meaningful `retry_on`.
- `base` and `cap` are sane.
- `fn` is a synchronous callable.
- `attempts` is small enough that `2**k` stays representable as a float.

## Pass 2 and 3: Results

**VERDICT: SHIP WITH FIXES.** The core loop is correct and matches the request. However, the default `retry_on=(Exception,)` contradicts "retry on chosen exceptions" and is risky in a shared production library, and the jitter behavior is not tested at all.

**CONFIDENCE IN VERDICT: medium-high.** It is limited by not being able to execute the code or tests; everything below comes from tracing.

### Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (trace) | `retry.py` signature: `retry_on=(Exception,)` | The request says retry on *chosen* exceptions. The default retries everything derived from `Exception`, including programming errors. | A production job calls `retry(lambda: charge(order))` without `retry_on`. A `TypeError` bug gets retried 5 times with up to ~1.5s of sleep before surfacing. If `fn` failed after a partial side effect (e.g. a non-idempotent write that then raised `ValueError` on response parsing), the side effect is duplicated up to 5×. | Make `retry_on` a required keyword with no default, or default to `()` and reject empty. Add a test that a call without `retry_on` raises `TypeError`. |
| 2 | Medium | CONFIRMED (trace) | `test_retry.py`: every test that inspects `slept` uses `rng=lambda: 1.0` | Jitter is never exercised. A mutation that deletes `rng() *` (making the delay deterministic) passes all 6 tests, because `1.0 * x == x`. "6 tests, all pass" does not cover the "full jitter" requirement. | A regression removes jitter, and every worker retries in lockstep (thundering herd). CI stays green. | Add `rng=lambda: 0.5, base=1, cap=100` with two failures and assert `slept == [0.5, 1.0]`. Add `rng=lambda: 0.0` and assert all zeros. Optionally use a seeded `random.Random(…).random` and assert each value lies in `[0, ceiling]`. |
| 3 | Medium | CONFIRMED (Python semantics, not executed) | `retry.py`: `except retry_on as e:` and `sleep(rng() * …)`; only `attempts` is validated | Bad configuration is only detected when `fn` first fails, inside the exception handler, so the real error gets buried. | (a) `retry_on=[ConnectionError]` (a list): on the first exception Python raises `TypeError: catching classes that do not inherit from BaseException is not allowed`. The original error appears only as `__context__`, and this happens only in production when the dependency first flakes. (b) `base=-1` or `cap=-1`: `time.sleep(negative)` raises `ValueError` after the first failure. | Validate up front: coerce `retry_on` to a tuple, check every element is a `BaseException` subclass, and require `base >= 0` and `cap >= 0`. Add tests for each. |
| 4 | Low | CONFIRMED (Python semantics, not executed) | `retry.py`: `base * (2 ** k)` | With a float `base` and k ≥ 1024, the int `2**k` cannot convert to float and raises `OverflowError`, which masks the real error. With an int `base` it instead builds a huge int every iteration. | `retry(fn, attempts=2000, base=0.1, cap=5, retry_on=(IOError,))` used as a "retry for a long time" loop raises `OverflowError` on the 1025th failure. | Clamp the exponent, e.g. `min(cap, base * 2 ** min(k, 60))`. Add a test with `attempts=1100` and a no-op sleep. |
| 5 | Low | PROBABLE | `retry.py`: `return fn()` | An `async def` function (or a generator function) returns a coroutine or generator without raising, so nothing is retried and nothing warns the caller. | Someone in a shared codebase writes `await retry(fetch_async, ...)`. Failures inside the coroutine are never retried. | Reject coroutine functions (`inspect.iscoroutinefunction(fn)`), or document the limitation clearly. Add a test. |
| 6 | Low | PROBABLE | `retry.py`: whole function | There is no hook or logging for intermediate failures. Only the last error survives, and earlier errors are silently discarded. | A production job succeeds on attempt 4 every run. The degradation is invisible until it starts failing outright. | Add an optional `on_retry(attempt, exc, delay)` callback. Test that it is called `attempts-1` times with the delays. |

### What holds up

- **Loop and termination logic:**
  - `last` is always set before `raise last`, because the final iteration either returns, propagates, or breaks with `last` assigned.
  - There is no sleep after the final attempt.
  - `attempts < 1` is rejected.
  - `attempts=1` correctly makes one call and then raises.
- **Exception scope:** Exceptions outside `retry_on` propagate immediately with their original traceback. `BaseException`s such as `KeyboardInterrupt` are never swallowed.
- **Backoff formula:** The delay matches AWS-style full jitter: `random(0, min(cap, base·2^k))`. The cap is applied before jitter.
- **Tests:** Tracing all 6 tests gives a pass:
  - `[1, 2]`
  - 3 calls with "boom 3"
  - 2 sleeps
  - 1 call on `KeyError`
  - `[1, 2, 3, 3, 3]`
  - `ValueError` for zero attempts

  The non-jitter assertions are meaningful.
- **Injectability:** Injecting `sleep` and `rng` is a reasonable reading of "clock and random source injectable." The function never reads the time, so `sleep` is the clock.

### Unverified claims

- **"6 tests, all pass":** Consistent with tracing, but not executed here. Confirm with `python -m unittest test_retry -v`.
- **Mutation survival (finding 2):** Confirm by deleting `rng() *` and rerunning; all 6 tests should still pass.
- **Exception text (findings 3 and 4):** The `TypeError` and `OverflowError` messages come from known CPython behavior. Confirm with the one-liners in the Fix column.

### Questions for the author

1. Was the `retry_on=(Exception,)` default deliberate? If callers are expected to always pass it, why not make it required?
2. Is "clock injectable" meant to include an overall deadline or elapsed-time budget? If yes, the current design is missing a feature, not just a test.
3. Will any callers pass `async` functions? If yes, finding 5 rises to High.

### Decision-maker summary

The retry loop is correct. Fix the risky catch-everything default and up-front argument validation before this goes into the shared library, and add jitter tests, since the current suite cannot detect jitter being removed. If you ship as is, the main risk is silent retries of non-idempotent operations on programming errors, plus misconfigurations that only surface during a real outage.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "retry.py signature: retry_on=(Exception,)",
      "scenario": "Caller omits retry_on; programming errors (TypeError, ValueError) are retried up to 5 times with sleeps, duplicating side effects of non-idempotent fn and delaying failure; contradicts 'retry on chosen exceptions'.",
      "fix": "Make retry_on a required keyword (no default) or reject empty; test that omitting it raises TypeError."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "test_retry.py: all sleep-asserting tests use rng=lambda: 1.0",
      "scenario": "Removing 'rng() *' from retry.py (no jitter) still passes all 6 tests; lockstep retries (thundering herd) ship undetected.",
      "fix": "Add tests with rng=lambda: 0.5 asserting [0.5, 1.0] and rng=lambda: 0.0 asserting zeros; optionally seeded Random range check."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "retry.py: 'except retry_on as e' and 'sleep(rng() * ...)'; only attempts validated",
      "scenario": "retry_on=[ConnectionError] raises TypeError on first failure inside the handler; negative base/cap make time.sleep raise ValueError; both mask the real error and appear only when the dependency first fails in production.",
      "fix": "Validate up front: tuple of BaseException subclasses, base >= 0, cap >= 0; add a test per case."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "retry.py: base * (2 ** k)",
      "scenario": "Float base with attempts > 1024 raises OverflowError (int too large to convert to float) on the 1025th failure, masking the real error.",
      "fix": "Clamp exponent: min(cap, base * 2 ** min(k, 60)); test attempts=1100 with no-op sleep."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "retry.py: return fn()",
      "scenario": "Async (or generator) fn returns a coroutine without raising; failures inside it are never retried, silently.",
      "fix": "Reject inspect.iscoroutinefunction(fn) or document the limitation; add a test."
    },
    {
      "severity": "Low",
      "evidence_level": "PROBABLE",
      "location": "retry.py: whole function",
      "scenario": "Intermediate failures are discarded with no hook or log; a job that routinely needs 4 attempts degrades invisibly until it fails.",
      "fix": "Add optional on_retry(attempt, exc, delay) callback; test it is called attempts-1 times with the delays."
    }
  ]
}
```