# Redteam report: `retry.py` / `test_retry.py`

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools and no subagent, so there was one reviewer, and nothing was executed. Every behaviour below comes from tracing the code by hand against Python 3 semantics.

**VERDICT: SHIP WITH FIXES.** The core behaviour matches the request and the six tests pass when traced by hand. But full jitter, the feature that defines the request, has no test that fails when it is removed. The helper also fails with the wrong error on large `attempts` and on a mistyped `retry_on`.

**CONFIDENCE: medium.** Nothing was run. Two findings rest on language semantics I could not execute (PROBABLE). There was no independent seat.

**INPUTS LEDGER**
- Seen: request.md, context.md, retry.py, test_retry.py.
- Not seen: the test run output behind "6 tests, all pass" (matters a little; I traced all six as passing). The production callers (matters for S1 and for how likely F2 and F3 are). The CI config (does not matter).

**COVERAGE**
- Checked: `retry.py:retry`, covering the main path, the give-up path, the non-matching path, the delay formula, and the validation. All six tests in `test_retry.py`, plus a mutation analysis of each one.
- Not checked: production call sites, behaviour under real `time.sleep`/`random`, async callers.

**SEATS AND GATE**
- Sensitivity gate: passed. This is generic library code with no personal data or secrets.
- Seats: same-session Claude only. Cross-vendor seats were not requested ("standard seats only"). No fresh subagent was available, so the deep confirm-or-refute round was done by me arguing as the code's defender.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `test_retry.py`: every sleep-asserting test uses `rng=lambda: 1.0`; `retry.py:22` | Jitter is untested. With `rng()` fixed at 1.0, multiplying by it does nothing, so removing the jitter changes no assertion. | A later edit drops `rng() *` or swaps it for `1`. All 6 tests stay green, and every production job retries in lockstep (thundering herd). | Mutation: change line 22 to `sleep(min(cap, base * (2 ** k)))`. All 6 tests still pass (traced: `[1,2]`, `[1,2,3,3,3]`, `len==2` are unchanged). Add a test with `rng=lambda: 0.5, base=1, cap=100, Flaky(2)` expecting `slept == [0.5, 1.0]`, and one with `rng=lambda: 0.0` expecting `[0, 0]`. | a✔ b✔ c✘ d✘ |
| F2 | Medium | PROBABLE (Python float semantics, not executed) | B | `retry.py:22` `base * (2 ** k)` | When `base` is a float (the default `0.1`) and `k ≥ 1024`, `float * int` converts `2**k` to float and raises `OverflowError`. The `min(cap, …)` never runs. | `retry(job, attempts=2000)` as a "retry for a long time" setting. On the 1025th failure the caller gets `OverflowError` (with the real error only as `__context__`) instead of more retries and then the last error. This breaks "stop after N attempts and re-raise the last error". | Keep a running ceiling instead of recomputing: `ceiling = base` before the loop, sleep `rng() * min(cap, ceiling)`, then `ceiling = min(cap, ceiling * 2)`. This also stops building huge ints when `base` is an int. Repro: `retry(Flaky(5000), attempts=1100, sleep=lambda s: None)`. Expected `ConnectionError`; predicted `OverflowError`. | a✔ b✘ c✔ d✘ |
| F3 | Medium | PROBABLE (Python semantics, not executed) | B | `retry.py:19` `except retry_on as e` | `retry_on` is never validated. A list such as `retry_on=[ConnectionError]`, or a non-exception class, is only rejected when an exception is actually being matched. | The config error stays hidden until the first transient failure in production. At that moment the job dies with `TypeError: catching classes that do not inherit from BaseException is not allowed` instead of retrying. | At entry: `retry_on = tuple(retry_on) if not isinstance(retry_on, type) else (retry_on,)`, then check that each item `issubclass(x, BaseException)`, raising `TypeError` or `ValueError` early. Repro: `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)`. Expected `"ok"`; predicted `TypeError`. | a✔ b✘ c✘ d✘ |
| F4 | Low | PROBABLE | B | `retry.py:7` signature; `:13-14` validation | Only `attempts` is validated. A negative `base` or `cap`, or a NaN, produces a negative or NaN delay, and `time.sleep` raises `ValueError` mid-retry. An injected `rng` returning a value above 1 silently exceeds `cap`. | `cap=-1` from a misread config: the first retry crashes with `ValueError` from `sleep`, masking the original error. | Validate `base >= 0`, `cap >= 0`, both finite, at entry. Optionally clamp the computed delay to `[0, cap]`. | a✔ b✘ c✘ d✘ |
| F5 | Low | CONFIRMED (code vs docstring) | B | `retry.py:7` default `retry_on=(Exception,)` | The request says "retry on *chosen* exceptions", but the default retries everything, including programming errors (`KeyError`, `TypeError`, `AttributeError`). | A bug in a production job is retried 5 times with backoff before surfacing. It still re-raises, but it is slower and its logs look like a transient fault. | Make `retry_on` a required keyword, or at least document the default as broad. A test with no `retry_on` that asserts the chosen behaviour. | a✔ b✔ c✘ d✘ |
| F6 | Low | CONFIRMED (docstring vs `random.random`) | B | `retry.py:11` docstring | The docstring says the delay is in `[0, min(cap, …)]` (closed). `random.random()` returns `[0, 1)`, so the upper bound is never reached by default. | No runtime harm, but a reader may write tests or reason about worst-case latency from the wrong bound. | Change the docstring to `[0, min(cap, base * 2**k))`. | a✘ b✔ c✘ d✘ |

## NEEDS VALIDATION
- **S1:** Do any production callers pass an `async def` function? `fn()` would return a coroutine without raising, so nothing would be retried and the caller gets an un-awaited coroutine. This is settled by grepping the call sites for `retry(` with coroutine functions.
- **S2:** Is any caller configured with `attempts > 1024` and a float `base`? This settles how likely F2 is in practice. It is settled by grepping the call sites and configs.

## REFUTED
- **"`raise last` could raise `None`"**: `attempts ≥ 1` is enforced. The loop exits only through `return` or through `break` after `last = e` is set. Unreachable.
- **"Drift: only `sleep` is injectable, not a clock"**: the request has no deadline or time-based stop. The only interaction with the clock is sleeping, and `sleep` is injectable. Injecting `rng` covers "the random source".
- **"Retries `KeyboardInterrupt`/`SystemExit`"**: the default is `Exception`, which excludes them. They propagate.
- **"Sleeps after the final attempt"**: the `k == attempts - 1` break comes before `sleep`, and `test_does_not_sleep_after_the_last_attempt` asserts it.

## WHAT HOLDS UP
- The backoff formula is the standard full-jitter form, `rand * min(cap, base * 2^k)`, with the first delay at `base`.
- Non-matching exceptions propagate on the first call. The last error is re-raised with its original traceback.
- There is no sleep after the final attempt, and `attempts < 1` is rejected.
- The give-up, cap, non-matching and zero-attempts tests assert real behaviour. I traced all six to pass, which is consistent with "6 tests, all pass".
- Both `sleep` and `rng` are injectable keyword arguments.

## UNVERIFIED CLAIMS
- **"6 tests, all pass"**: traced as passing, not run. Confirm with `python -m unittest test_retry -v`.
- The reproductions for F2 and F3 are predicted, not observed. Run each repro line in a REPL.

## QUESTIONS FOR THE AUTHOR
1. Should `retry_on` be required, given "chosen exceptions"? This decides F5.
2. Is there an upper bound on `attempts` in practice, and will any callers be async?

## DECISION-MAKER SUMMARY
The helper does what was asked on the normal path, and nothing here blocks shipping. Before production jobs depend on it, add a jitter test (F1) and fix the overflow (F2) and the input validation (F3), which together take under an hour. If it ships as is, a future change could silently remove jitter, and unusual configurations would fail with confusing errors exactly when retries are needed.

## OWNER SUMMARY
The retry helper works correctly for normal use and its tests pass. The tests would not notice if the random spreading of retries were accidentally removed, and a couple of unusual settings would cause a confusing crash instead of a retry. These are small fixes and worth making before shared production jobs rely on it.

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
    {"item": "test run output for '6 tests, all pass'", "status": "not_seen", "matters": false},
    {"item": "production call sites", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "generic library code; no personal data, secrets or client material"},
  "coverage": {
    "checked": [
      {"unit": "retry.py", "kind": "file"},
      {"unit": "retry.py:retry", "kind": "function"},
      {"unit": "test_retry.py", "kind": "file"},
      {"unit": "test_retry.py:RetryTests (all 6 tests, mutation-traced)", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "production call sites", "reason": "not supplied"},
      {"unit": "runtime execution of tests and repros", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_retry.py (all sleep-asserting tests use rng=lambda: 1.0); retry.py:22",
     "scenario": "If a later change removes the rng() multiplier, all 6 tests still pass and production jobs retry in lockstep without jitter.",
     "fix": "Add tests with rng=lambda: 0.5 (expect slept == [0.5, 1.0] for Flaky(2), base=1, cap=100) and rng=lambda: 0.0 (expect [0, 0]).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Change retry.py:22 to sleep(min(cap, base * (2 ** k))); run the suite; all 6 tests still pass (traced)."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "retry.py:22 base * (2 ** k)",
     "scenario": "With a float base (default 0.1) and attempts > 1024, the 1025th failure raises OverflowError converting 2**1024 to float, instead of retrying and then re-raising the last error.",
     "fix": "Track a running ceiling: ceiling = base before the loop; sleep rng() * min(cap, ceiling); then ceiling = min(cap, ceiling * 2).",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "retry(Flaky(5000), attempts=1100, sleep=lambda s: None): expected ConnectionError, predicted OverflowError."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "retry.py:19 except retry_on as e",
     "scenario": "retry_on=[ConnectionError] (a list) passes silently until the first transient failure, which then crashes the job with TypeError instead of retrying.",
     "fix": "Normalize retry_on to a tuple at entry and check that each item is a BaseException subclass, failing fast.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None): expected 'ok', predicted TypeError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "retry.py:7 signature; retry.py:13-14 validation",
     "scenario": "A negative or NaN base or cap yields a delay that time.sleep rejects with ValueError mid-retry, masking the original error; an rng returning more than 1 exceeds cap.",
     "fix": "Validate that base and cap are finite and >= 0 at entry; optionally clamp the delay to [0, cap].",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), cap=-1): expected 'ok', predicted ValueError from time.sleep."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:7 retry_on=(Exception,)",
     "scenario": "The default retries programming errors (KeyError, TypeError) 5 times with backoff before surfacing them, although the request says 'chosen exceptions'.",
     "fix": "Make retry_on a required keyword, or document the broad default and add a test for it.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(10, exc=KeyError), sleep=s.append) calls fn 5 times and sleeps 4 times."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:11 docstring",
     "scenario": "The docstring states a closed interval [0, min(...)], but random.random() is [0, 1), so readers mis-state the worst-case delay.",
     "fix": "Change the docstring to [0, min(cap, base * 2**k)).",
     "answers": {"a": false, "b": true, "c": false, "d": false},
     "reproduction": "Compare the docstring to the random.random documentation."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "retry.py:18 return fn()",
     "suspicion": "Async callers would get an un-awaited coroutine and no retries.",
     "unresolved_fact": "Whether any production caller passes a coroutine function."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "retry.py:22",
     "suspicion": "F2 may be triggered in production.",
     "unresolved_fact": "Whether any caller uses attempts > 1024 with a float base."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "raise last could raise None.",
     "evidence": "attempts >= 1 is enforced; the loop exits only via return or via break after last = e."},
    {"id": "R2", "candidate": "Drift: the clock is not injectable.",
     "evidence": "The request has no deadline; sleep is the only clock interaction and it is injectable."},
    {"id": "R3", "candidate": "KeyboardInterrupt and SystemExit are retried.",
     "evidence": "The default retry_on is Exception, which excludes BaseException-only classes."},
    {"id": "R4", "candidate": "Sleeps after the final attempt.",
     "evidence": "The k == attempts - 1 break precedes sleep; test_does_not_sleep_after_the_last_attempt asserts it."}
  ]
}
```