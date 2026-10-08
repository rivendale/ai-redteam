**Note:** This is a single-reviewer pass with no tools, so nothing was executed. The work was not written in this conversation, but no fresh subagent was available. Every finding below comes from reading and tracing the code. Re-run the reproductions in a scratch copy before acting on them.

## Pass 1: Reconstruct

`retry(fn, ...)` calls `fn()` up to `attempts` times. It catches only exceptions in `retry_on`. Between tries it sleeps `rng() * min(cap, base * 2**k)`, which is AWS-style full jitter. It never sleeps after the last try, and it re-raises the last caught error. `sleep` and `rng` are injectable.

For this to be correct, these must hold:
- the delay formula is evaluated safely for every allowed `attempts`;
- `retry_on` is something `except` accepts;
- injected values stay in range;
- the tests actually pin down the jitter behaviour.

The track is B (code).

## Pass 2 and Pass 3 (deep: confirm-or-refute on every candidate)

**VERDICT: SHIP WITH FIXES.** The core logic is correct. No High or Critical finding survived. There are four real weaknesses: two latent runtime failures, one hole in the tests, and missing input checks.

**CONFIDENCE: medium.** It is limited by having no tools (no tests or mutations were run), a single seat, and no production call sites.

**INPUTS LEDGER:**
- Seen: request.md, context.md, retry.py, test_retry.py.
- Not seen: the CI or test-run output behind "6 tests, all pass". This matters little, because I traced all six to pass.
- Not seen: the production jobs that call the helper. This matters for how likely F1 and F2 are, but not for whether they are true.

**COVERAGE:**
- Checked: `retry.py:retry` (main path, plus hostile inputs: attempts=1, attempts≥1026, list `retry_on`, negative base/cap, out-of-range rng, non-matching exception); all six tests in `test_retry.py`; the request's requirements (backoff, jitter, cap, N attempts, re-raise, injectable clock and rng); the context claim "6 tests pass".
- Not checked: execution of anything; async callables; callers' choice of `retry_on`.

**SEATS AND GATE:**
- Ran: the local Claude reviewer only.
- Refused: cross-vendor seats, because the user asked for "standard seats only".
- No subagent was available.
- Sensitivity gate: no sensitive data.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced; Python semantics) | B | retry.py:21 `base * (2 ** k)` | The ceiling is computed before `cap` is applied. With a float `base` (the default is 0.1), `2**1024` cannot convert to float, so `OverflowError` is raised inside the `except` handler. | A job sets a large `attempts` (≥1026), expecting "retry about 5 s apart for hours". At k=1024 it raises `OverflowError: int too large to convert to float` instead of continuing, and the caller never gets "the last error". | Carry the ceiling forward: start with `ceiling = min(cap, base)`, then after each sleep do `ceiling = min(cap, ceiling * 2)`. This gives the same values and cannot overflow. Repro: `retry(Flaky(10**6), attempts=1100, sleep=lambda s: None)` should raise ConnectionError but raises OverflowError. | Y/Y/Y/N |
| F2 | Medium | CONFIRMED (Python semantics) | B | retry.py:17 `except retry_on` | `retry_on` is not validated. A list (`[ConnectionError]`) passes every happy-path call. It only fails when `fn` first raises, because `except` with a list raises `TypeError: catching classes that do not inherit from BaseException is not allowed`. | A production job passes a list. It works until the first transient error, which then becomes a TypeError with no retries at all. | At entry, normalise with `retry_on = retry_on if isinstance(retry_on, type) else tuple(retry_on)` and check each item is a `BaseException` subclass. Repro: `retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None)` should return "ok" but raises TypeError. | Y/Y/N/N |
| F3 | Medium | CONFIRMED (traced mutation) | B | test_retry.py: all tests use `rng=lambda: 1.0` or a no-op sleep | Full jitter is the main requirement, and no test can detect its removal. If you change line 21 to `sleep(min(cap, base * (2 ** k)))` (dropping `rng()*`), all six tests still produce the same values and pass. | Someone later "simplifies" the jitter away or computes it wrongly (for example `rng()*cap`, or jitter only on a bounded part). CI stays green, and synchronized retries hit the downstream service together. | Add a test with a non-trivial rng, for example `rng=iter([0.5, 0.25]).__next__`, `base=1`, `cap=100`, and expect `slept == [0.5, 0.5]`. Confirm it goes red on the mutant above. | Y/Y/N/N |
| F4 | Low | CONFIRMED (Python semantics) | B | retry.py:14-15 | Only `attempts < 1` is checked. A negative `base` or `cap`, or an `rng` returning a negative value, gives a negative delay. With the real `time.sleep` that raises `ValueError: sleep length must be non-negative` inside the handler, hiding the original error. A non-int `attempts` (2.5) fails in `range`. | A misconfigured job (`base=-0.1`) raises ValueError on the first transient failure instead of retrying. | Validate at entry: `base >= 0`, `cap >= 0`, `attempts` is an int. Optionally clamp the delay at 0. Repro: `retry(Flaky(1), base=-1)` should return "ok" but raises ValueError. | Y/Y/N/N |

Severity note for F1: (a), (b) and (c) are all yes. The request's "re-raise the last error" breaks once attempts ≥1026. I read the four questions as necessary conditions, not sufficient ones, and did not escalate to Critical, because (d) is no: it needs an unusual configuration and the effect is a wrong exception type, not data loss. If the shared library's callers do use very large `attempts`, treat it as High.

### NEEDS VALIDATION
- **S1:** `retry_on=(Exception,)` by default means programming errors (TypeError, AttributeError) are retried with backoff. To settle it, find out whether the requester's "retry on chosen exceptions" means callers must choose, i.e. no default or a narrow default.
- **S2:** The request says "clock". Only `sleep` is injectable, and nothing reads the time. To settle it, find out whether the requester expected a time source (for example `time.monotonic`) for a total deadline. That is not stated in the request.

### REFUTED
- **"Sleeps after the final attempt."** Refuted: `if k == attempts - 1: break` runs before `sleep`, and `test_does_not_sleep_after_the_last_attempt` asserts 2 sleeps for 3 attempts.
- **"`raise last` can raise None."** Refuted: `attempts >= 1` is enforced. The loop either returns, propagates a non-matching error, or reaches `break` with `last` set.
- **"Retries KeyboardInterrupt or SystemExit."** Refuted: the default is `Exception`, not `BaseException`.
- **"Off-by-one in the exponent."** Refuted: the first delay is `base * 2**0 = base`, which matches the docstring and the standard full-jitter formula `random(0, min(cap, base·2^attempt))`.
- **"The cap is not applied."** Refuted: `min(cap, …)` is on line 21, and `test_cap_applies` traces to `[1, 2, 3, 3, 3]`.

### WHAT HOLDS UP
- Control flow is correct: return on success, immediate propagation of non-matching exceptions, no trailing sleep, last error re-raised with its traceback.
- The `attempts < 1` guard is present.
- `sleep` and `rng` are cleanly injectable.
- The function is stateless and safe to call from several threads.
- All six tests trace to pass. For example, the success test's `[1.0, 2.0] == [1, 2]` holds, and the cap test gives `[1, 2, 3, 3, 3]`.

### UNVERIFIED CLAIMS
- **"6 tests, all pass" (context).** I traced it but did not run it. Confirm with `python -m unittest test_retry -v` in a clean environment.

### QUESTIONS FOR THE AUTHOR
1. Should `retry_on` have a default at all (S1)?
2. Was "clock" meant to include a total-time deadline (S2)?
3. Do any production jobs set `attempts` in the thousands (decides F1's severity)?

### DECISION-MAKER SUMMARY
Ship after fixing F1 to F3. Each is a few lines, plus a jitter test that has been shown to go red on a mutant. Proceeding as-is carries latent risk: misconfigured or very long retry loops will fail with the wrong exception, and a future regression of the jitter would pass CI unnoticed.

### OWNER SUMMARY
The retry helper does what was asked, and its main logic is sound. It can still fail in confusing ways if it is set up unusually, for example with a very large number of retries or exceptions given as a list. Its tests would not notice if the randomized waiting were removed. These are small fixes and should be made before production jobs depend on it.

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
    {"item": "CI/test run output for '6 tests, all pass'", "status": "not_seen", "matters": false},
    {"item": "production call sites", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-local", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "retry.py", "kind": "file"},
      {"unit": "retry.py:retry", "kind": "function"},
      {"unit": "test_retry.py", "kind": "file"},
      {"unit": "test_retry.py:RetryTests", "kind": "function"},
      {"unit": "request: backoff, full jitter, cap, N attempts, re-raise, injectable clock and rng", "kind": "claim"},
      {"unit": "context: 6 tests, all pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation runs", "reason": "no tools in this session"},
      {"unit": "production call sites", "reason": "not supplied"},
      {"unit": "async callables", "reason": "out of scope of request"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:21",
     "scenario": "With float base (default 0.1) and attempts >= 1026, base * 2**1024 raises OverflowError inside the except handler before cap is applied, so the caller gets OverflowError instead of the last error.",
     "fix": "Carry the ceiling forward: ceiling = min(cap, base); after each sleep ceiling = min(cap, ceiling * 2).",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "retry(Flaky(10**6), attempts=1100, sleep=lambda s: None): expect ConnectionError, observe OverflowError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:17",
     "scenario": "A caller passes retry_on as a list; on the first exception from fn the except clause raises TypeError, so no retry happens and the original error is masked.",
     "fix": "Normalise retry_on to a tuple at entry and check each item is a BaseException subclass.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), retry_on=[ConnectionError], sleep=lambda s: None): expect 'ok', observe TypeError."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_retry.py (all tests use rng=lambda: 1.0 or a no-op sleep)",
     "scenario": "Removing jitter (sleep(min(cap, base * 2**k))) leaves all six tests green, so a regression of the core full-jitter requirement passes CI.",
     "fix": "Add a test with a fractional rng sequence, e.g. rng=iter([0.5, 0.25]).__next__, base=1, cap=100, expecting slept == [0.5, 0.5]; confirm it fails on the mutant.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Apply the mutant to a scratch copy and run python -m unittest test_retry: expect a failure, observe 6 passes."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:14-15",
     "scenario": "A negative base, cap or rng value gives a negative delay; time.sleep raises ValueError inside the handler and hides the original error. A non-int attempts fails in range().",
     "fix": "Validate base >= 0, cap >= 0 and integer attempts at entry; optionally clamp the delay at 0.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), base=-1): expect 'ok', observe ValueError: sleep length must be non-negative."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "retry.py:7 retry_on=(Exception,)",
     "suspicion": "The default retries programming errors such as TypeError with backoff.",
     "unresolved_fact": "Whether the requester's 'retry on chosen exceptions' means callers must choose, i.e. no default or a narrow default."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "retry.py:7 signature",
     "suspicion": "'Clock' may have meant an injectable time source for a total deadline, not only sleep.",
     "unresolved_fact": "Whether the requester expected a time-based deadline; the request text does not state one."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Sleeps after the final attempt.", "evidence": "if k == attempts - 1: break runs before sleep; test asserts 2 sleeps for 3 attempts."},
    {"id": "C2", "candidate": "raise last can raise None.", "evidence": "attempts >= 1 is enforced; the loop exits without return only via break with last set."},
    {"id": "C3", "candidate": "Retries KeyboardInterrupt or SystemExit.", "evidence": "The default retry_on is (Exception,), not BaseException."},
    {"id": "C4", "candidate": "Off-by-one in the backoff exponent.", "evidence": "The first delay is base * 2**0, matching the docstring and the standard full-jitter formula."},
    {"id": "C5", "candidate": "The cap is not applied.", "evidence": "min(cap, ...) on line 21; test_cap_applies traces to [1, 2, 3, 3, 3]."}
  ]
}
```