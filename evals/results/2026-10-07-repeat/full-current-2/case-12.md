# Redteam review: `retry.py` and `test_retry.py`

**VERDICT: SHIP WITH FIXES.** The helper meets every stated requirement and its logic traces correctly, but four Medium findings should be fixed before production jobs depend on it:
- a float overflow when `attempts` is large,
- a test suite that cannot detect removal of the jitter,
- an unsafe default for `retry_on`,
- configuration errors that only appear on the first failure.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so nothing was run. Every finding comes from reading and tracing the code by hand.
- No independent subagent seat was available. The work was not written in this conversation, so the anchoring risk is lower, but it is still a single-reviewer pass.
- Mutation testing was done on paper, not executed.

**INPUTS LEDGER:**

| Item | Status | Matters? |
|---|---|---|
| request.md (verbatim) | Seen | n/a |
| context.md | Seen | n/a |
| retry.py | Seen | n/a |
| test_retry.py | Seen | n/a |
| Test run output ("6 tests, all pass") | Not seen; asserted only | Low: I traced all 6 tests and each should pass |
| Callers in the shared library | Not seen | Medium: how callers set `attempts`, `base` and `retry_on` decides how much F1, F3 and F4 matter |

**SEATS AND GATE:**
- Sensitivity gate: passed. The work is generic code with no personal or confidential data.
- Cross-vendor seats: not used, because the user asked for standard seats only.
- Subagent seat: none available. This is a single reviewer with no tools.

## Pass 1: Reconstruct

The work claims to be a retry helper that:
- calls `fn()` with no arguments;
- retries only exceptions listed in `retry_on`;
- sleeps `rng() * min(cap, base * 2**k)` between tries, which is full jitter;
- does not sleep after the final attempt;
- re-raises the last error after `attempts` tries;
- lets callers inject the sleep function (the clock) and `rng`.

Load-bearing assumptions:
- `rng()` returns a value in [0, 1).
- `retry_on` is an exception class or a tuple of them.
- `base` and `cap` are non-negative finite numbers.
- `base * 2**k` stays representable as a float.
- The tests would detect a regression in each requirement.

Track: B.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (traced, not run) | B | `retry.py`, the line `sleep(rng() * min(cap, base * (2 ** k)))` | `base` is a float (default `0.1`), so `base * 2**k` converts the int `2**k` to a float. Once `k >= 1024` this raises `OverflowError: int too large to convert to float`. The cap is applied only after that multiplication, so it does not prevent the error. | A job configured to retry "nearly forever" (`attempts >= 1026`, float `base`) fails on retry 1025 with `OverflowError`. That error is raised inside the `except` block, so it replaces the real error and ends the retries. With `cap=5`, this happens after roughly 40 to 85 minutes of retrying. | Compute the delay without overflow, for example `min(cap, base * 2 ** min(k, 64))`, or stop doubling once `base * 2**k >= cap`. Add a test with `attempts=1100, sleep=lambda s: None` and a function that always fails, and assert that the raised error is `ConnectionError`. | n/a (Medium) |
| 2 | Medium | CONFIRMED (traced) | B (tests) | `test_retry.py`: every test that asserts sleep values uses `rng=lambda: 1.0` | Full jitter is a stated requirement but no test checks it. Multiplying by `1.0` changes nothing, so the tests cannot tell jitter from no jitter. Mutating `rng() * min(...)` to `min(...)` would leave all 6 tests green. | Someone later "simplifies" the jitter away, or replaces it with "equal jitter". CI stays green, and many production jobs then retry in lockstep against a recovering dependency, which is the thundering-herd problem jitter exists to prevent. | Add a test with `rng=lambda: 0.5`, `base=1`, `cap=100` that asserts `slept == [0.5, 1.0]`. Add a second test with `rng=lambda: 0.0` that asserts all sleeps are zero. | n/a |
| 3 | Medium | CONFIRMED (code) / PROBABLE (impact) | B | `retry.py`, signature: `retry_on=(Exception,)` | The request says to retry on *chosen* exceptions, but the default retries every `Exception`, including programming errors such as `TypeError`, `KeyError` and `AssertionError`. | A caller omits `retry_on`. Either a deterministic bug is retried 5 times, adding about 1.5 s of delay and hiding the stack trace's urgency, or a non-idempotent operation that failed after partly committing is repeated. | Make `retry_on` required (no default), or default it to a narrow transient set such as `(ConnectionError, TimeoutError)`. Document whichever you choose. | n/a |
| 4 | Medium | CONFIRMED (Python semantics, traced) | B | `retry.py`, the `except retry_on as e:` line and the parameter checks | Configuration is only partly validated: | | Validate at entry: convert with `retry_on = tuple(retry_on)` if it is not a class, check that each item is a `BaseException` subclass, require `base >= 0` and `cap >= 0` (finite), and require `attempts` to be an `int` (not `bool`). Add tests for a list `retry_on` and a negative `base`. | n/a |
| | | | | | (a) A list `retry_on=[ConnectionError]` is accepted silently. The `except` clause raises `TypeError` only when `fn` actually throws. | A misconfigured job works fine on the happy path, then reports a confusing `TypeError` during the outage it was meant to survive. | | |
| | | | | | (b) A negative `base` or `cap` causes `time.sleep` to raise `ValueError` inside the handler, which masks the original error. | Same as (a): the failure appears only during an outage, with the wrong error. | | |
| | | | | | (c) An `attempts` of `3.0` passes `attempts < 1`, then fails at `range()`. | The job fails immediately with an unclear error. | | |
| 5 | Low | CONFIRMED (code) | B | `retry.py`, the `rng` parameter | The contract that `rng()` returns a value in [0, 1) is not documented. An injected `random.uniform`-style function, or one returning values above 1, silently produces delays above `cap`. | A test or production caller injects a function with a different range, and the cap is no longer enforced. | Document the [0, 1) contract in the docstring. Optionally clamp: `min(cap, rng() * ...)`. | n/a |
| 6 | Low | PROBABLE | B (operations) | `retry.py`, whole function | There is no hook for logging or metrics, so production jobs cannot see that retries are happening. The request did not ask for this, so it is noted, not required. | A dependency degrades. Jobs absorb the failures silently, with slowly rising latency, and nobody is alerted until retries run out. | An optional `on_retry(exc, attempt, delay)` callback. Defer this unless the owners want it. | n/a |

### Confirm or refute
There are no Critical or High findings, so no candidates needed this round.

I considered and **refuted** two candidates:
- **`raise last` loses the traceback.** Refuted: a Python 3 exception object keeps its `__traceback__`, and re-raising it adds frames rather than replacing them.
- **`last` could be `None` at `raise last`.** Refuted: with `attempts >= 1`, the loop either returns, propagates a non-retryable error, or sets `last` before breaking.

Self-check: the most likely place for a missed problem is in how callers use the helper (finding 3), and those callers were not supplied.

## WHAT HOLDS UP
- **Backoff formula.** The code matches the docstring. Traced against the tests: `[1, 2]` for 2 failures, and `[1, 2, 3, 3, 3]` with `cap=3`.
- **No sleep after the final attempt.** This is correct, and `test_does_not_sleep_after_the_last_attempt` would catch removing the `break`.
- **Non-matching exceptions propagate at once.** This is correct and tested, with a call-count assertion.
- **Re-raising the last error.** This is correct and tested by checking for `"boom 3"`.
- **Interrupts are not retried.** `KeyboardInterrupt` and `SystemExit` derive from `BaseException`, not `Exception`, so the default never retries them.
- **`attempts < 1` is rejected.** This is tested.
- **The clock and random source are injectable**, as the request required.
- **The 6 tests all pass by trace.** Mutating the exponent, the cap, the `break`, or the `retry_on` filter would each turn at least one test red. The one exception is the jitter (finding 2).

## UNVERIFIED CLAIMS
- **"6 tests, all pass."** I did not run them. Run `python -m unittest test_retry` to settle it.
- **The `OverflowError` threshold in finding 1.** Settle it by running `0.1 * 2**1024` in a REPL.
- **The list-`retry_on` behavior in finding 4a.** Settle it by running `try: raise ValueError` / `except [ValueError]: pass` in a REPL.

## QUESTIONS FOR THE AUTHOR
1. Do any callers rely on the catch-all default for `retry_on`? Should it become required?
2. Does any job configure `attempts` in the hundreds or more, or use the helper as a "retry until it works" loop?

## DECISION-MAKER SUMMARY
The helper is correct for normal settings and can ship after four small fixes:
- guard the exponent against float overflow;
- add a test that actually exercises the jitter;
- narrow or require `retry_on`;
- validate arguments when the function is called.

If it ships as is, the main risks are untested jitter that could silently regress across many production jobs, and misconfigurations that only show up during real outages.

## OWNER SUMMARY
The retry code does what was asked and works correctly for normal settings. A few small gaps should be closed first: very long retry runs can crash, the tests would not notice if the random spreading of retries were removed, and by default it retries every kind of error, not just temporary ones. Each fix is a few lines and should be done before production jobs depend on it.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "retry.py", "status": "seen", "matters": true},
    {"item": "test_retry.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "library callers of retry()", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-single-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "generic library code, no personal or confidential data"},
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "retry.py: sleep(rng() * min(cap, base * (2 ** k)))",
     "scenario": "With float base and attempts >= 1026, base * 2**1024 raises OverflowError inside the except block; the job dies with OverflowError instead of retrying or re-raising the real error.",
     "fix": "Clamp the exponent (e.g. 2 ** min(k, 64)) or stop doubling once the delay reaches cap; test with attempts=1100 and assert ConnectionError is raised.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_retry.py: all sleep-asserting tests use rng=lambda: 1.0",
     "scenario": "Removing the rng() multiplication (dropping jitter) leaves all 6 tests green; jobs then retry in lockstep against a recovering dependency.",
     "fix": "Add tests with rng=lambda: 0.5 (expect [0.5, 1.0] for base=1) and rng=lambda: 0.0 (expect all zeros).", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "retry.py signature: retry_on=(Exception,)",
     "scenario": "A caller omits retry_on; deterministic bugs (TypeError, KeyError) or partially committed non-idempotent operations are retried 5 times.",
     "fix": "Make retry_on required or default to a narrow transient set; document it.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "retry.py: except retry_on as e; entry validation",
     "scenario": "retry_on passed as a list raises TypeError only when fn first fails; negative base/cap makes time.sleep raise ValueError in the handler, masking the original error; both surface only during an outage.",
     "fix": "Validate at entry: tuple-ize retry_on and check each item subclasses BaseException; require base, cap >= 0 and finite; require int attempts. Add tests.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "retry.py: rng parameter",
     "scenario": "An injected rng returning values above 1 produces delays above cap, silently breaking the cap guarantee.",
     "fix": "Document the [0, 1) contract; optionally clamp the final delay to cap.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "retry.py: whole function",
     "scenario": "Retries are invisible to production monitoring; a degrading dependency goes unnoticed until attempts run out.",
     "fix": "Optional on_retry(exc, attempt, delay) callback, if the owners want it.", "status": "n/a"}
  ]
}
```