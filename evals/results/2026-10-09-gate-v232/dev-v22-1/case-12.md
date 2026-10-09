**Reviewer note:** single reviewer with no tools and no subagent. I did not write this work, so there is no shared-author context, but nothing was executed. Every CONFIRMED label below means traced by hand against Python semantics, not run.

VERDICT: **REWORK.** One confirmed Critical: for `attempts ≥ 1026` with a float `base`, the helper crashes with `OverflowError` instead of capping the delay and retrying. The fix is one line plus one test; everything else holds.

CONFIDENCE: **medium.** Nothing was run, there was no independent second seat, and the callers that set `attempts` and `retry_on` were not supplied.

INPUTS LEDGER:
- **Seen:** `request.md` (verbatim), `context.md`, `retry.py`, `test_retry.py`.
- **Not seen:**
  - Test-run output behind "6 tests, all pass". It matters a little: I traced all six as passing but did not run them.
  - The production callers of this library. This matters for how likely F1 and F3 are, not for whether they are real.
  - Packaging and other modules. These do not matter.

COVERAGE:
- **Checked:**
  - `retry.py:retry`: every branch, plus hostile inputs (huge `attempts`, list `retry_on`, negative `cap`, non-matching exception, success on the first try).
  - All six tests in `test_retry.py` and the `Flaky` helper.
  - Each requirement clause in the request.
- **Not checked:** runtime behaviour (no interpreter), callers, concurrency of the shared `random` state (not relevant to correctness).

SEATS AND GATE:
- Local Claude reviewer ran.
- Cross-vendor seats were not run, because the context says "standard seats only".
- Sensitivity gate passed: generic library code, no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `retry.py:22` | `base * (2 ** k)` is computed before `min(cap, …)`. When `k = 1024`, `2**1024` cannot convert to float, so `float * int` raises `OverflowError`. The cap never gets a chance to apply. | A job calls `retry(fn, attempts=5000, base=0.1, cap=1)` to "keep trying for about an hour". After the 1025th failure it raises `OverflowError: int too large to convert to float` from inside the `except` block. It neither continues retrying nor re-raises the last real error, which breaks the request's "cap the delay … stop after N attempts and re-raise the last error". | Stop growing the exponent once the delay reaches the cap, e.g. `delay = cap if k >= 64 else min(cap, base * 2 ** k)`, or track `delay = min(cap, delay * 2)`. **Test:** `slept = []`, then run `retry(Flaky(2000), attempts=1100, base=0.1, cap=1, sleep=slept.append, rng=lambda: 1.0)`. Expected: `ConnectionError("boom 1100")` and `len(slept) == 1099`. Today's code raises `OverflowError`. | a✔ b✔ c✔ d✘ |
| F2 | Medium | CONFIRMED (traced) | B | `test_retry.py:19,32,44` | Every test that checks sleep values uses `rng=lambda: 1.0`. Full jitter, an explicit requirement, is never exercised. | Someone refactors line 22 to `sleep(min(cap, base * 2 ** k))`, dropping `rng()`. All 6 tests still pass, and production jobs fall back to synchronized backoff (thundering herd). | Add a test with `rng=lambda: 0.5`, `base=1`, `cap=100`, `Flaky(2)` that expects `slept == [0.5, 1.0]`. It fails against the mutant above. | a✔ b✔ c✘ d✘ |
| F3 | Low | CONFIRMED (traced) | B | `retry.py:6` (`retry_on=(Exception,)`) | The request says "retry on chosen exceptions", but the default chooses everything, including programming errors (`TypeError`, `AttributeError`). | A caller omits `retry_on`. Their non-idempotent `fn` posts a payment and then raises `KeyError` while parsing the response. It is posted 5 times. | Make `retry_on` a required keyword argument, or default to a narrow transient set. Test: `retry(lambda: 1)` without `retry_on` should raise `TypeError`, if the parameter becomes required. | a✔ b✔ c✘ d✘ |
| F4 | Low | CONFIRMED (traced) | B | `retry.py:12-13` | Only `attempts` is validated. A `list` for `retry_on` or a negative `base`/`cap` stays latent until the first real failure. | `retry(fn, retry_on=[ConnectionError])` works while `fn` succeeds. The first production `ConnectionError` then hits `except [ConnectionError]` and raises `TypeError: catching classes that do not inherit from BaseException is not allowed`. With `cap=-1`, `time.sleep` raises `ValueError` instead of retrying. | Validate up front: coerce `retry_on` to a tuple and check every item is an `issubclass` of `BaseException`; require `base >= 0` and `cap >= 0`. Test: `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)` should return `"ok"` or raise `TypeError` immediately. Today it raises `TypeError` only once a failure occurs. | a✔ b✔ c✘ d✘ |

**Confirm-or-refute (F1).**
- Defender's case: nobody passes more than 1000 attempts.
- Response: likelihood is question (d), which is answered no. Severity is set by a, b and c. The input is valid under the signature, and the observed outcome is a different exception from the one the request promises. The finding holds.
- On the evidence label: CONFIRMED is by trace of CPython's int-to-float conversion, not by execution. Run the reproduction above to close it.

## Needs validation
- **S1:** whether the six tests actually pass as claimed. The unresolved fact is the output of `python -m unittest test_retry`. I traced all six as passing.
- **S2:** whether any production caller sets `attempts > 1025` or omits `retry_on`. A grep of the callers settles it. This affects urgency, not validity.

## Refuted
- **`raise last` could raise `None`.** The loop only exits without returning via `break`, which follows `last = e`, and `attempts >= 1` is enforced.
- **Off-by-one in the backoff exponent.** `k=0` gives `base`, which matches the docstring. `test_succeeds_after_failures` expects `[1, 2]`, and the trace gives `[1, 2]`.
- **Sleeps after the final attempt.** The `break` at line 20-21 precedes the sleep, and `test_does_not_sleep_after_the_last_attempt` covers it.
- **`raise last` loses the original traceback.** The exception keeps its `__traceback__`. It is raised outside the `except` block, so no misleading `__context__` is added.
- **The docstring says `[0, x]` but `random.random()` returns `[0, 1)`.** The upper bound is never reached. This is harmless and is standard full jitter.

## What holds up
- Retry only on `retry_on`, with immediate propagation of anything else: correct and tested.
- Re-raising the last error after N attempts: correct and tested, including the `"boom 3"` message.
- Cap: correct for `k < 1024` and tested (`[1, 2, 3, 3, 3]`).
- `sleep` and `rng` injection: works and is used by the tests.
- `BaseException` subclasses such as `KeyboardInterrupt` are not swallowed under the default.

## Unverified claims
- "6 tests, all pass": run the suite.
- "The clock … must be injectable": satisfied by injecting `sleep`, provided the requester did not also want a time source for deadline-based stopping. See question 2.

## Questions for the author
1. Is `attempts` ever set very high to mean "retry for a long time"? If yes, F1 is urgent rather than latent.
2. Did "clock injectable" mean only `sleep`, or also a `monotonic()` source for a max-elapsed-time stop?

## Decision-maker summary
Fix F1 by bounding the exponent and add its regression test. Add the jitter test (F2). With those two changes this can ship. If it ships as-is, any job configured with more than 1025 attempts crashes with an unrelated `OverflowError` instead of retrying.

## Owner summary
The retry helper is mostly correct and well tested. It has one bug: when it is told to retry a very large number of times, it crashes partway through instead of continuing. That is a small fix. The tests also never check that the random spreading of retry times actually happens, so one more test is needed before relying on it.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "retry.py", "status": "seen", "matters": true},
    {"item": "test_retry.py", "status": "seen", "matters": true},
    {"item": "test run output for '6 tests, all pass'", "status": "not_seen", "matters": true},
    {"item": "production callers of retry()", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-local", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": false, "reason": "Generic library code; no personal or confidential data. Cross-vendor seats not run because context requested standard seats only."},
  "coverage": {
    "checked": [
      {"unit": "retry.py", "kind": "file"},
      {"unit": "retry.py:retry", "kind": "function"},
      {"unit": "test_retry.py", "kind": "file"},
      {"unit": "test_retry.py:Flaky", "kind": "function"},
      {"unit": "test_retry.py:RetryTests", "kind": "function"},
      {"unit": "request.md requirement clauses", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "runtime execution of tests", "reason": "no tools in this session"},
      {"unit": "production callers", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:22",
     "scenario": "retry(fn, attempts=5000, base=0.1, cap=1): after the 1025th failure, base * 2**1024 raises OverflowError inside the except block, so the helper neither caps the delay nor re-raises the last real error.",
     "fix": "Bound the exponent before multiplying, e.g. delay = cap if k >= 64 else min(cap, base * 2 ** k), or grow delay = min(cap, delay * 2).",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "slept = []; retry(Flaky(2000), attempts=1100, base=0.1, cap=1, sleep=slept.append, rng=lambda: 1.0): expect ConnectionError('boom 1100') and len(slept) == 1099; current code raises OverflowError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_retry.py:19,32,44",
     "scenario": "All sleep-asserting tests use rng=lambda: 1.0, so a refactor that drops rng() from retry.py:22 removes full jitter and all 6 tests still pass.",
     "fix": "Add a test with rng=lambda: 0.5, base=1, cap=100, Flaky(2) expecting slept == [0.5, 1.0].",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Mutate retry.py:22 to sleep(min(cap, base * (2 ** k))); run the suite; all 6 tests pass (should fail)."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:6",
     "scenario": "A caller omits retry_on; a non-idempotent fn that raises KeyError after a side effect is executed 5 times because the default retries every Exception.",
     "fix": "Make retry_on a required keyword argument or default to a narrow transient set.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "f = Flaky(10, exc=KeyError); retry(f, sleep=lambda s: None) raises KeyError with f.calls == 5; expected a single call for a non-transient error."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:12-13",
     "scenario": "retry_on=[ConnectionError] (a list) works until the first real ConnectionError, then raises TypeError from the except clause; a negative cap makes time.sleep raise ValueError instead of retrying.",
     "fix": "Validate at entry: coerce retry_on to a tuple of BaseException subclasses; require base >= 0 and cap >= 0.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None): expect 'ok' or an immediate TypeError at call time; observe TypeError only after fn fails."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "context.md",
     "suspicion": "The claim '6 tests, all pass' was not observed.",
     "unresolved_fact": "Output of python -m unittest test_retry."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "production callers (not supplied)",
     "suspicion": "Callers may set attempts > 1025 or omit retry_on, making F1 or F3 live.",
     "unresolved_fact": "A grep of callers for retry( arguments."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "raise last could raise None.", "evidence": "The loop exits without returning only via break at retry.py:20-21, which follows last = e; attempts >= 1 is enforced at retry.py:12."},
    {"id": "C2", "candidate": "Off-by-one in backoff exponent.", "evidence": "k=0 gives base; test_succeeds_after_failures expects [1, 2], matching the trace."},
    {"id": "C3", "candidate": "Sleeps after the final attempt.", "evidence": "break precedes sleep at retry.py:20-22; covered by test_does_not_sleep_after_the_last_attempt."},
    {"id": "C4", "candidate": "raise last loses the original traceback.", "evidence": "The exception object retains __traceback__; raised outside the except block, so no spurious __context__."},
    {"id": "C5", "candidate": "Docstring interval [0, x] mismatches random.random() range [0, 1).", "evidence": "The upper bound is never reached; harmless and standard full jitter."}
  ]
}
```