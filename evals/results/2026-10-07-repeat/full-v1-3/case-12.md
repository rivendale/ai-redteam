# Redteam review: `retry.py` and `test_retry.py`

**Review mode:** This work was not written in this conversation, so I reviewed it directly with no inherited anchoring. I had no tools, so I could not run anything. Every claim about behaviour comes from tracing the code by hand and from Python semantics, not from execution.

**VERDICT: SHIP WITH FIXES.** The core logic is correct and matches the request, but one input-range crash, one untested core feature (jitter) and a risky default should be fixed before production jobs rely on it.

**CONFIDENCE IN VERDICT:** medium-high. It is limited by having no execution, so "6 tests, all pass" is checked by trace only.

## Pass 1: Reconstruct

`retry(fn, ...)` calls `fn()` up to `attempts` times. It catches only the exception types in `retry_on`. Between attempts it sleeps `rng() * min(cap, base * 2**k)`, which is AWS-style full jitter. It never sleeps after the final attempt, and it re-raises the last caught error. Sleep and rng are injectable.

For this to be correct, these must be true:
- `rng()` returns a value in [0, 1).
- `base` and `cap` are non-negative finite numbers.
- `retry_on` is an exception class or a tuple of them.
- `base * 2**k` stays representable for every reachable `k`.
- "Injectable clock" means an injectable sleep. This one is unstated.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (Python semantics) | `retry.py`: `base * (2 ** k)` | A float times an int above about 1.8e308 raises `OverflowError: int too large to convert to float`. The `min(cap, …)` runs too late to prevent it. | The default `base=0.1` (a float) with `attempts=1100` and `cap=5`, used for a long-running "retry nearly forever" job. When k reaches 1024, the helper raises `OverflowError` inside the `except` block. The real error is hidden behind "During handling of the above exception…". | Clamp the exponent, e.g. `min(cap, base * 2 ** min(k, 64))`, or stop doubling once the cap is reached. Add a test with `attempts=1100`, `base=0.1`, `cap=1` and a no-op sleep. |
| 2 | Medium | CONFIRMED (traced) | `test_retry.py`: every test that asserts delays uses `rng=lambda: 1.0` | Jitter is never tested. Multiplying by 1.0 is the identity, so the tests cannot tell full jitter apart from no jitter. | A refactor to `sleep(min(cap, base*2**k))` drops the jitter, and all 6 tests still pass. Production jobs then retry in lockstep and stampede the dependency, which is exactly what full jitter is meant to prevent. | Add a test with `rng=lambda: 0.5`, `base=1`, `cap=100` that expects `[0.5, 1.0]`. Add one with `rng=lambda: 0.0` that expects all zeros. Optionally assert that rng is called once per sleep. |
| 3 | Medium | PROBABLE | `retry.py` signature: `retry_on=(Exception,)` | The request says "retry on *chosen* exceptions", but the default retries everything, including programming errors. | A caller forgets `retry_on`. A `TypeError` or `KeyError` bug in `fn` is retried 5 times with backoff, which delays failure, multiplies non-idempotent side effects (for example, duplicate writes before the crash point) and hides the bug in logs. | Make `retry_on` required (no default), or default it to a narrow transient set and document that. Add a test for the chosen behaviour. |
| 4 | Low | CONFIRMED (Python semantics) | `retry.py`: `except retry_on as e` | `retry_on` is not validated. A list such as `[ConnectionError]` is only rejected when the first exception happens. | `retry(fn, retry_on=[ConnectionError])` runs fine until `fn` fails. Then `TypeError: catching classes that do not inherit from BaseException is not allowed` is raised and the real error is hidden. Easy to miss in review and in happy-path tests. | Normalise and validate up front: accept a class or an iterable, convert to a tuple, and check `issubclass(c, BaseException)`. Add a test. |
| 5 | Low | CONFIRMED (Python semantics) | `retry.py`: there is a check for `attempts`, but none for `base` or `cap` | A negative or NaN `base` or `cap` produces an invalid delay. The default `time.sleep` raises `ValueError` inside the `except` block. | `cap=-1` from a config typo makes `time.sleep` raise "sleep length must be non-negative" on the first retry, which hides the real error. | Validate `base >= 0` and `cap >= 0` (and finite) next to the `attempts` check, and add tests. |
| 6 | Low | PROBABLE | Signature: `sleep=`, `rng=` | The request asks for an injectable clock. The code injects `sleep`, and there is no time-reading clock. | If "clock" was meant to support deadlines or elapsed-time checks, that is a silent scope cut. If it only meant the sleep function, this is fine. | Confirm the intent with the requester. If sleep injection was the intent, note it in the docstring. |
| 7 | Low | CONFIRMED (traced) | `test_retry.py` | Several boundaries are not tested: `attempts=1` (one call, no sleep), success on the first try (no sleep), a single exception class passed as `retry_on`, and `attempts=-1`. | A regression in the `k == attempts - 1` guard when `attempts=1`, or in handling a bare class, would go unnoticed. | Add the four small tests. |

## What holds up

- The delay schedule `rng() * min(cap, base*2**k)` matches the standard full-jitter formula. Tracing the cap test with base 1 and cap 3 gives `1, 2, 3, 3, 3`, which is correct.
- There is no off-by-one: `fn` is called exactly `attempts` times, there are `attempts - 1` sleeps, and there is no sleep after the last failure.
- The error raised at the end is the last one ("boom 3"). It keeps its own traceback, and older attempts are not implicitly chained onto it, because the raise happens outside the `except` block.
- Exceptions not in `retry_on` propagate immediately after one call.
- `KeyboardInterrupt`, `SystemExit` and `CancelledError` (all `BaseException` but not `Exception`) are not caught by the default.
- Rejecting `attempts < 1` covers both 0 and negative values.
- `last` can never be `None` at `raise last`. The only path to the raise is the `break`, which follows `last = e`.

## Unverified claims

- **"6 tests, all pass":** My hand trace says all 6 pass under the given code. Confirm by running `python -m unittest test_retry`.
- **Fitness for production use:** I could not see how callers use this, for example whether any pass async functions or very large `attempts`. A grep of the call sites would settle it.

## Questions for the author

1. Does "injectable clock" mean only the sleep function, or is a deadline or elapsed-time cap expected?
2. Is the `Exception` default for `retry_on` deliberate for this shared library, given that production callers may wrap non-idempotent operations?
3. Do any callers use `attempts` in the hundreds or thousands, which would hit finding 1?

## Decision-maker summary

The helper is logically correct and matches the request. Before production use, fix the overflow at very high attempt counts and add a test that actually exercises the jitter. Also decide whether retrying every `Exception` by default is acceptable. If you ship as is, the main risks are a hidden crash in very long retry loops and a future change that silently removes jitter with no test catching it.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "retry.py: base * (2 ** k)", "scenario": "Float base (default 0.1) with attempts > 1024: float*int raises OverflowError inside the except block, hiding the real error.", "fix": "Clamp the exponent (2 ** min(k, 64)) or stop growing once the cap is reached; test attempts=1100, base=0.1, cap=1."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "test_retry.py: every delay-asserting test uses rng=lambda: 1.0", "scenario": "Removing jitter (sleep(min(cap, base*2**k))) still passes all 6 tests; production clients then retry in lockstep.", "fix": "Add tests with rng=0.5 (expect halved delays) and rng=0.0 (expect zeros)."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "retry.py signature: retry_on=(Exception,)", "scenario": "A caller omits retry_on; programming errors (TypeError, KeyError) are retried with backoff, delaying failure and repeating non-idempotent side effects.", "fix": "Make retry_on required or narrow the default; document and test it."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "retry.py: except retry_on as e", "scenario": "retry_on=[ConnectionError] (a list) raises TypeError on the first failure, hiding the original error.", "fix": "Normalise to a tuple and validate issubclass(c, BaseException) up front; add a test."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "retry.py: no validation of base or cap", "scenario": "cap=-1 makes time.sleep raise ValueError on the first retry, hiding the real error.", "fix": "Validate base >= 0 and cap >= 0 (and finite) next to the attempts check; add tests."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "retry.py signature: sleep=, rng=", "scenario": "The request asks for an injectable clock; only sleep is injectable. If deadlines were intended, this is a silent scope cut.", "fix": "Confirm the intent; document that sleep is the injected clock, or add a monotonic clock plus deadline."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "test_retry.py", "scenario": "No tests for attempts=1, success on the first try (no sleep), a single class as retry_on, or negative attempts; regressions there go unnoticed.", "fix": "Add those four tests."}
  ]
}
```