VERDICT: **SHIP WITH FIXES**. The helper does what the request asks for every realistic configuration, but the test suite never checks the jitter and the delay maths overflows above about 1,024 attempts.

CONFIDENCE: **medium**. I traced the code and tests by hand, but this session has no tools, so nothing was executed. One reviewer only: no subagent was available. I am not the author's context, so authorship anchoring does not apply.

INPUTS LEDGER:
- Seen: request.md (verbatim), context.md, `retry.py`, `test_retry.py`.
- Not seen: any test run output; the production callers of this library.
- Does it matter? The "6 tests, all pass" claim is unverified, but I traced all six and expect them to pass. The callers matter only for S1 (async functions).

COVERAGE:
- Checked: `retry.py` (the file and `retry()`); `test_retry.py` (all 6 tests, plus a mutation analysis of what they would and would not catch); each requirement in the request; the claim that the tests pass.
- Not checked: production call sites; behavior under a real interpreter.

SEATS AND GATE: one local reviewer ran. Cross-vendor seats were not used because the context says "standard seats only". The sensitivity gate passed: the work contains no personal or confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `test_retry.py:19,32,44`; `retry.py:22` | Full jitter, an explicit requirement, is untested. Every test that inspects delays uses `rng=lambda: 1.0`. Every other test discards the sleep value. | Someone edits line 22 to `sleep(min(cap, base * (2 ** k)))`, removing jitter. All 6 tests stay green, and production jobs retry in lockstep (thundering herd). | Mutate line 22 as described: 6/6 still pass. Add a test with `rng=lambda: 0.5`, `base=1, cap=100`, `Flaky(2)` that expects `slept == [0.5, 1.0]`. Also add one with `rng=lambda: 0.0` that expects all zeros. | a✓ b✓ c✗ d✗ |
| F2 | Medium | PROBABLE (Python semantics; not executed) | B | `retry.py:22` | `base * (2 ** k)` multiplies a float by an unbounded int. Once k ≥ 1024, CPython raises `OverflowError: int too large to convert to float` before `min(cap, …)` can cap it. | `attempts=1100`, and `fn` keeps failing. On the 1,025th failure the helper raises `OverflowError` instead of sleeping `cap`. The caller then gets the wrong exception type rather than "the last error". | Use `min(cap, base * 2.0 ** min(k, 1000))`. Float overflow to `inf` is then capped by `min`. Repro: `retry(Flaky(10**4), attempts=1100, sleep=lambda s: None)` should raise `ConnectionError`; expect it to raise `OverflowError` instead. | a✓ b✗ c✓ d✗ |
| F3 | Low | PROBABLE (Python semantics; not executed) | B | `retry.py:6,12-13,18` | Only `attempts` is validated. If `retry_on` is a list, the `except` clause raises `TypeError` at the moment an exception occurs, which masks the real error. A negative `base` or `cap` produces a negative sleep. | `retry(f, retry_on=[ConnectionError])`: the first failure surfaces as `TypeError: catching classes that do not inherit from BaseException is not allowed`. `base=-1` makes `time.sleep` raise `ValueError`. | Validate up front: `retry_on = tuple(retry_on)` with an issubclass check, and require `base >= 0, cap >= 0`. Repro: the call above with `Flaky(1)` and `sleep=lambda s: None` should return `"ok"`; expect `TypeError`. | a✓ b✗ c✗ d✗ |
| F4 | Low | CONFIRMED | B | `retry.py:6` (`retry_on=(Exception,)`) | The request says "retry on chosen exceptions", but the default retries everything, including programming errors such as `TypeError`, `AttributeError` and `KeyError`. | A caller forgets `retry_on`. A bug then fails 5 times with up to about 1.5 s of sleeps before surfacing. With larger `attempts`, a deterministic bug burns the full retry budget in a production job. | Make `retry_on` required (no default), or document the choice loudly. Test: `retry(f)` without `retry_on` raises `TypeError` (required keyword). | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1** (`retry.py:17`): if a caller passes an `async def` function, `fn()` returns a coroutine object at once. The helper then "succeeds" without awaiting it, and nothing is retried. **What settles it:** whether any production job passes coroutine functions to this helper.

## REFUTED
- **"Clock is not injectable."** The only time interaction is `sleep`, and it is injected (`retry.py:6,22`). There is no deadline or elapsed-time logic that would need a `now()` clock. (See the author question below.)
- **"`raise last` could raise `None`."** With `attempts >= 1` (enforced at line 12), the loop either returns or assigns `last` before breaking.
- **"Sleeps after the final attempt."** Lines 20-21 break before sleeping, and `test_retry.py:33` asserts exactly 2 sleeps for 3 attempts.
- **"Exponent off by one."** The first delay is `base * 2**0 = base`. Test line 20 expects `[1, 2]` for `base=1`, which matches the AWS full-jitter definition.

## WHAT HOLDS UP
- The core algorithm is correct full jitter: `rng() * min(cap, base * 2**k)`.
- The cap is applied, and `test_cap_applies` expects `[1, 2, 3, 3, 3]`, which matches.
- The last error, not the first, is re-raised, and the test checks `"boom 3"`.
- Non-matching exceptions propagate after one call.
- `attempts < 1` is rejected.
- `sleep` and `rng` are injectable.
- `KeyboardInterrupt` and `CancelledError` (BaseException) are not retried under the default.
- One minor docstring nit: it says `[0, x]`, but `random.random` gives `[0, x)`.

## UNVERIFIED CLAIMS
- **"6 tests, all pass."** My hand trace says each assertion holds. Confirm with `python -m unittest test_retry -v`.
- **F2 and F3 behavior.** Confirm with the reproductions in the table.

## QUESTIONS FOR THE AUTHOR
1. Did "the clock must be injectable" mean only `sleep`, or was an overall deadline (`max_elapsed`) intended? If a deadline was intended, the request is not fully met.
2. Do any production jobs pass async functions (S1)?

## DECISION-MAKER SUMMARY
Fix F1 (add a jitter test) and F2 (bound the exponent) before release. Both are a few lines. Shipping as-is risks a silent future loss of jitter that CI will not catch, plus a wrong exception type for very large attempt counts.

## OWNER SUMMARY
The retry helper works correctly for normal settings and does what was asked. However, its tests would not notice if someone accidentally removed the randomness that stops many jobs from retrying at the same moment. It also breaks if told to retry more than about a thousand times. Both are small fixes worth making before other teams rely on it.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "retry.py", "status": "seen", "matters": true},
    {"item": "test_retry.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "production call sites", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "retry.py", "kind": "file"},
      {"unit": "retry.py:retry", "kind": "function"},
      {"unit": "test_retry.py", "kind": "file"},
      {"unit": "6 tests, all pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "production call sites", "reason": "not supplied"},
      {"unit": "runtime execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_retry.py:19,32,44; retry.py:22",
     "scenario": "Removing rng() from retry.py:22 leaves all 6 tests green, so a regression that disables full jitter ships unnoticed and jobs retry in lockstep.",
     "fix": "Add tests with rng=lambda: 0.5 (expect [0.5, 1.0] for base=1, Flaky(2)) and rng=lambda: 0.0 (expect zeros).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace line 22 with sleep(min(cap, base * (2 ** k))); run python -m unittest test_retry; observe 6/6 pass, expected a failure."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "retry.py:22",
     "scenario": "With attempts > 1024 and persistent failure, base * (2 ** k) raises OverflowError at k=1024 instead of sleeping cap, so the caller gets OverflowError, not the last error.",
     "fix": "Use min(cap, base * 2.0 ** min(k, 1000)).",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "retry(Flaky(10**4), attempts=1100, sleep=lambda s: None); expected ConnectionError, observe OverflowError."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "retry.py:6,12-13,18",
     "scenario": "retry_on passed as a list makes the except clause raise TypeError on the first failure, masking the real error; negative base or cap makes time.sleep raise ValueError.",
     "fix": "Normalize retry_on to a tuple of BaseException subclasses and validate base >= 0 and cap >= 0 up front.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None); expected 'ok', observe TypeError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:6",
     "scenario": "A caller omits retry_on; a deterministic programming error (TypeError, AttributeError) is retried the full budget with backoff before surfacing.",
     "fix": "Make retry_on a required keyword argument, or default to () and document it.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "f = Flaky(10, exc=TypeError); retry(f, sleep=lambda s: None); observe f.calls == 5, expected 1 if only chosen exceptions are retried."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "retry.py:17",
     "suspicion": "An async fn returns an un-awaited coroutine immediately, so retry 'succeeds' without retrying anything.",
     "unresolved_fact": "Whether any production job passes coroutine functions to retry()."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The clock is not injectable.", "evidence": "The only time interaction is sleep, injected via the sleep parameter (retry.py:6,22); there is no deadline logic needing a now() clock."},
    {"id": "C2", "candidate": "raise last could raise None.", "evidence": "attempts >= 1 is enforced at retry.py:12; the loop returns or assigns last before breaking."},
    {"id": "C3", "candidate": "Sleeps after the final attempt.", "evidence": "retry.py:20-21 break before sleeping; test_retry.py:33 asserts 2 sleeps for 3 attempts."},
    {"id": "C4", "candidate": "Backoff exponent off by one.", "evidence": "First delay is base * 2**0; test_retry.py:20 expects [1, 2] for base=1, matching full jitter."}
  ]
}
```