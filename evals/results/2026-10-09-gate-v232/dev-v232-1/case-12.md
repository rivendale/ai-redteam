VERDICT: **SHIP WITH FIXES**. The helper does what was asked on the normal path. Three Medium defects should be fixed first: a float overflow at high attempt counts, jitter that no test checks, and a catch-everything default.

CONFIDENCE: **medium**. No tools were available, so nothing was run. Every finding comes from tracing the code and Python semantics by hand. There was one reviewer only, with no fresh subagent and no cross-vendor seats. I did not author this work, so the anchoring risk is limited to the author's framing in the context.

INPUTS LEDGER:
- Seen: `request.md` (the original request, verbatim), `context.md`, `retry.py`, `test_retry.py`.
- Not seen: the test run output behind "6 tests, all pass". This matters a little, because the pass/fail state is unverified. It does not change the verdict, since the findings concern what the tests fail to assert.
- Not seen: the callers in "production jobs". This matters for how severe the `retry_on` default is, because that depends on whether callers pass `retry_on` and whether their `fn` is idempotent.

COVERAGE: whole work (both files).
- Checked:
  - `retry.py`: every line, including the validation, loop, exception filter, delay formula and final raise.
  - `test_retry.py`: all 6 tests, plus a by-hand mutation analysis of each.
  - The request, against each requirement: chosen exceptions, exponential backoff, full jitter, cap, N attempts, re-raise last, injectable clock and random source.
  - The context document.
- Not checked:
  - Actual execution of the tests (`no_tools`).
  - Production callers (`not_supplied`).

SEATS AND GATE: one local Claude reviewer ran. Cross-vendor seats were not run because the user asked for standard seats only. No subagent was available. The sensitivity gate passed: the work contains no personal data, credentials or confidential material.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced, not executed) | B | `retry.py:22` | `base * (2 ** k)` multiplies a float by an unbounded int. Once `k` reaches 1024, Python cannot convert `2**1024` to a float and raises `OverflowError`. | A job uses `attempts=2000` (for example, "keep trying for a long time" with `cap=5`) and keeps the default float `base=0.1`. The dependency stays down. At the failure with `k=1024`, the helper raises `OverflowError: int too large to convert to float` instead of sleeping. The caller gets the wrong exception type after 1025 calls, not 2000. That breaks "stop after N attempts and re-raise the last error", and handlers that catch `ConnectionError` miss it. | **Fix:** saturate the exponent, e.g. `min(cap, base * 2 ** min(k, 64))`, or stop growing once the ceiling reaches `cap`. **Repro:** `f = Flaky(10**6)`, then `retry(f, attempts=1026, sleep=lambda s: None)`. Expected: `ConnectionError` with `f.calls == 1026`. Observed (by trace): `OverflowError` with `f.calls == 1025`. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED | B | `test_retry.py:19`, `:32`, `:44` | Every test that checks delays injects `rng=lambda: 1.0`. That is the one value where jitter has no effect, so full jitter (a stated requirement) is never asserted. | Someone "simplifies" line 22 to `sleep(min(cap, base * (2 ** k)))`, removing the jitter. All 6 tests still pass: `[1, 2]`, `len == 2` and `[1, 2, 3, 3, 3]` are unchanged. Jobs then retry in lockstep against a recovering dependency, which is the thundering herd that jitter exists to prevent. | **Fix:** add a test with `rng=lambda: 0.5, base=1, cap=100` on `Flaky(2)`, asserting `slept == [0.5, 1.0]`. Also add one with `rng=lambda: 0.0` asserting zero delays. **Repro:** apply the mutation above to a scratch copy and run the suite. Expected: red. Observed (by trace): all green. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED | B | `retry.py:6` (`retry_on=(Exception,)`) | The request says "retry on **chosen** exceptions", but the default retries every `Exception`, including programming errors like `TypeError`, `KeyError` and `AttributeError`. | A production job calls `retry(push_record)` without `retry_on`. A bug raises `KeyError` after a partial side effect, such as a row written before the crash. The helper re-runs it 4 more times with sleeps, repeating the side effect and delaying the real failure. In a shared library, omitting the argument is the easy path. | **Fix:** make `retry_on` a required keyword-only argument with no default, or default to a narrow transient set and document it. **Repro:** `f = Flaky(5, exc=KeyError)`, then `retry(f, sleep=lambda s: None)`. Observed (by trace): `f.calls == 5`. Desired: `f.calls == 1`, or a `TypeError` for the missing argument. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (traced, not executed) | B | `retry.py:18` | `except retry_on` checks its type only when an exception is actually being matched. If `retry_on` is a list, as in `[ConnectionError]`, the first failure raises `TypeError: catching classes that do not inherit from BaseException is not allowed`. That error hides the real one. The success path never reveals this. | A caller writes `retry_on=[ConnectionError, TimeoutError]`. Their tests only cover success. In production, the first transient error becomes a `TypeError` with no retry. | **Fix:** at entry, coerce with `retry_on = tuple(retry_on) if isinstance(retry_on, list) else retry_on`, or validate that every element is a `BaseException` subclass and raise a `ValueError`. **Repro:** `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)`. Expected: `"ok"`. Observed (by trace): `TypeError`. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED (traced, not executed) | B | `retry.py:6`, `:22` | `base` and `cap` are not validated. A negative value makes the delay negative, and `time.sleep` then raises `ValueError` inside the except block. | Config read from the environment sets `cap=-1` by mistake. The first transient failure surfaces as `ValueError: sleep length must be non-negative` with no retry. | **Fix:** raise `ValueError` at entry if `base < 0` or `cap < 0`, as is already done for `attempts`. **Repro:** `retry(Flaky(1), cap=-1)` with the real `time.sleep`. Expected: a `ValueError` at entry, or `"ok"`. Observed (by trace): a `ValueError` from `sleep` after the first failure. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

None.

## REFUTED

- **"The clock is not injectable."** The helper's only time dependency is `sleep` (line 22), and it is injectable. Nothing reads the time, so there is no other clock to inject. If the author meant a wall-clock deadline, that is a question about the request, not a defect.
- **"`raise last` can raise `None`."** Each iteration either returns, or catches an exception and sets `last`. The final iteration always `break`s with `last` set, and `attempts < 1` is rejected at line 12.
- **"It sleeps after the last attempt."** The `break` at lines 20–21 runs before the sleep, and `test_does_not_sleep_after_the_last_attempt` asserts this.
- **"It swallows `KeyboardInterrupt` or `SystemExit`."** Both are `BaseException` subclasses, so the default `(Exception,)` does not catch them.
- **"The re-raised error loses its traceback."** `last.__traceback__` is preserved when it is re-raised outside the handler.
- **"The jitter formula is wrong."** `rng() * min(cap, base * 2**k)` matches the full-jitter definition, `random(0, min(cap, base·2^k))`.

## WHAT HOLDS UP

- The attempt counting is right (exactly `attempts` calls).
- It re-raises the last error, not the first; `test_gives_up_and_raises_last_error` asserts `"boom 3"`.
- Non-matching exceptions propagate immediately.
- The cap is applied.
- `attempts < 1` is rejected.
- `sleep` and `rng` are both injected.
- The tests catch these mutations, by trace: an off-by-one in the exponent, sleeping after the last attempt, raising the first error instead of the last, removing the cap, and removing the attempts guard.
- Nothing extra was built beyond the request.

## UNVERIFIED CLAIMS

- **"6 tests, all pass."** The count of 6 is confirmed by reading the file. The pass state is not, because nothing was run. To confirm, run `python3 -m unittest test_retry` in a clean copy.

## QUESTIONS FOR THE AUTHOR

1. Should callers be forced to choose `retry_on` (F3)? Do any current production callers rely on the catch-everything default?
2. Did "injectable clock" mean only `sleep`, or also a time source for a total-deadline cap?

## DECISION-MAKER SUMMARY

The helper is correct on the normal path, and no High or Critical issue survived review. Before wider rollout:
- Saturate the backoff exponent (F1).
- Add a test that actually exercises jitter (F2).
- Require callers to name `retry_on` (F3).

Shipping as is risks a wrong-exception crash on very long retry loops, a silent loss of jitter in a future edit, and retries of real bugs in callers who omit `retry_on`.

## OWNER SUMMARY

The retry helper works as requested for ordinary use, and nothing serious is broken. Three small fixes are recommended: prevent a crash when a job retries more than about a thousand times, add a test confirming the random spacing between retries really happens, and make callers say which errors to retry instead of retrying everything. A few input checks would also make configuration mistakes fail clearly.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "retry.py", "status": "seen", "matters": true},
    {"item": "test_retry.py", "status": "seen", "matters": true},
    {"item": "test run output (6 tests, all pass)", "status": "not_seen", "matters": false},
    {"item": "production callers", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "retry.py", "kind": "file"},
      {"unit": "retry.py:retry", "kind": "function"},
      {"unit": "test_retry.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no_tools"},
      {"unit": "production callers", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:22",
     "scenario": "With attempts >= 1026 and the default float base, base * 2**1024 raises OverflowError on the 1025th failure; the caller gets OverflowError instead of the last retried error after N attempts.",
     "fix": "Saturate the exponent: min(cap, base * 2 ** min(k, 64)).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "f = Flaky(10**6); retry(f, attempts=1026, sleep=lambda s: None). Expected ConnectionError with f.calls == 1026; observed by trace OverflowError with f.calls == 1025 (not executed: no tools)."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_retry.py:19,32,44",
     "scenario": "Every delay test uses rng=lambda: 1.0, so removing the rng() multiplier from retry.py:22 leaves all 6 tests green; jitter could be lost silently, causing synchronized retries.",
     "fix": "Add a test with rng=lambda: 0.5, base=1, cap=100 on Flaky(2) asserting slept == [0.5, 1.0], plus one with rng=lambda: 0.0.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy, change retry.py:22 to sleep(min(cap, base * (2 ** k))) and run the suite; expected red, observed by trace all green."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:6",
     "scenario": "A caller omits retry_on; a programming error (KeyError) after a partial side effect is retried 4 more times, repeating the side effect and delaying the real failure.",
     "fix": "Make retry_on a required keyword-only argument (no default) or default to a narrow transient set.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "f = Flaky(5, exc=KeyError); retry(f, sleep=lambda s: None); observed by trace f.calls == 5, desired 1 or a TypeError for the missing argument."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:18",
     "scenario": "retry_on passed as a list makes the first failure raise TypeError from the except clause, masking the real error with no retry.",
     "fix": "Validate or coerce retry_on to a tuple of BaseException subclasses at entry.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None); expected 'ok', observed by trace TypeError."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:6,22",
     "scenario": "A negative cap or base yields a negative delay; time.sleep raises ValueError on the first failure, masking the retried error.",
     "fix": "Raise ValueError at entry if base < 0 or cap < 0.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), cap=-1) with real time.sleep; expected ValueError at entry or 'ok', observed by trace ValueError from sleep after the first failure."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The clock is not injectable.", "evidence": "The only time dependency is sleep (retry.py:22), which is an injected parameter; nothing reads the time."},
    {"id": "C2", "candidate": "raise last can raise None.", "evidence": "The final iteration always sets last before break; attempts < 1 is rejected at retry.py:12."},
    {"id": "C3", "candidate": "It sleeps after the last attempt.", "evidence": "The break at retry.py:20-21 precedes the sleep; test_does_not_sleep_after_the_last_attempt asserts it."},
    {"id": "C4", "candidate": "It catches KeyboardInterrupt or SystemExit.", "evidence": "Both are BaseException subclasses, not caught by (Exception,)."},
    {"id": "C5", "candidate": "The jitter formula is wrong.", "evidence": "rng() * min(cap, base * 2**k) matches the full-jitter definition."}
  ]
}
```