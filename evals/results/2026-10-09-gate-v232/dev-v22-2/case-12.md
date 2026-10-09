# Redteam report: `retry.py` and `test_retry.py`

**Note on independence.** This session has no tools and no subagent, so I reviewed the code myself. I did not write the work, so there is no author anchoring. But I could not execute anything: every behavior below was traced by hand against Python semantics, not run.

**VERDICT: SHIP WITH FIXES.** The helper meets the request on every realistic path, but the jitter it promises has no test, and the delay calculation crashes on very large attempt counts.

**CONFIDENCE: medium.** Three things limit it: the code was not executed, the "6 tests pass" claim was traced rather than run, and the mutation test was done on paper.

**INPUTS LEDGER:**
- Seen: request.md, context.md, retry.py, test_retry.py.
- Not seen: CI output for "6 tests, all pass", and the production call sites of this shared library.
  - The CI output gap does not matter: I traced all 6 tests and each passes.
  - The call-site gap matters only for F3, which depends on whether callers rely on the default `retry_on`.

**COVERAGE:**
- Checked: `retry.py:retry` (main path, plus empty, huge and malformed inputs), every test in `test_retry.py`, and each requirement in the request.
- Not checked: execution, concurrency (not applicable, since the function has no shared state beyond the global `random`), and call sites.

**SEATS AND GATE:**
- Ran: one local Claude reviewer, same session.
- Cross-vendor seats: not run, because the context says "standard seats only".
- Sensitivity: none (generic library code).
- Confirm-or-refute round: run on the High candidate F3, which was downgraded.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced, not executed) | B | retry.py:22, `base * (2 ** k)` | `2**k` is an int. Multiplying it by a float converts it to float, and that conversion overflows once k ≥ 1024. `min(cap, …)` runs too late to prevent it. | With `attempts ≥ 1026`, the backoff after the 1025th failure raises `OverflowError: int too large to convert to float`. The error is chained inside the handler, so the caller gets an `OverflowError` instead of the last retried error, which breaks "re-raise the last error". | **Fix:** clamp the exponent, e.g. `min(cap, base * 2 ** min(k, 62))`. **Repro:** `retry(Flaky(2000), attempts=1100, sleep=lambda s: None)`. Expect `ConnectionError("boom 1100")`; you get `OverflowError`. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED (mutation traced) | B | test_retry.py: every sleep assertion uses `rng=lambda: 1.0` | Full jitter, a core requirement, is never exercised. With `rng()` fixed at 1.0, multiplying by it changes nothing. | Someone deletes `rng() *` or swaps the random source for a constant. All 6 tests still pass, and production jobs lose jitter, which brings back synchronized retry storms. | **Fix:** add a test with `rng=lambda: 0.5`, `base=1`, `cap=100`, `Flaky(2)` and expect `slept == [0.5, 1.0]`. Also assert that `rng` is actually called. **Repro (mutation):** replace line 22 with `sleep(min(cap, base * (2 ** k)))` and run the suite; it stays green. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | B | retry.py:6, `retry_on=(Exception,)` | The request says "retry on chosen exceptions", but the default retries every exception, including programming errors. | A caller omits `retry_on`. A `TypeError` from a bug, or a mid-way failure in a non-idempotent `fn`, is then re-executed up to 5 times, repeating partial side effects. | **Fix:** make `retry_on` a required keyword argument. **Repro:** `retry(lambda: 1/0, sleep=s.append)` makes 5 calls and 4 sleeps. | a✓ b✓ c✗ d✗ (d unknown without call sites; see Q1) |
| F4 | Low | CONFIRMED (traced) | B | retry.py:12–13 | Only `attempts` is validated. `base`, `cap` and `retry_on` are not. | `cap=-1`, or an `rng` returning a negative value, makes `time.sleep` raise `ValueError`, which masks the retryable error. Passing `retry_on=[ConnectionError]` (a list) raises `TypeError` only on the first failure, not at call time. | **Fix:** validate `base >= 0`, `cap >= 0`, and that `retry_on` is a class or tuple of `BaseException` subclasses. **Repro:** `retry(Flaky(1), cap=-1)` raises `ValueError: sleep length must be non-negative`. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1 – the "clock" requirement.** The request asks for an injectable "clock". The work injects `sleep` only, with no time source. That is enough for backoff without a deadline. The fact that would settle it: did the requester want a total-time or deadline cap (which needs a `now()` source), or only injectable sleeping?

## REFUTED
- **"`raise last` could raise `None`."** Refuted. `attempts ≥ 1` is enforced. Every iteration either returns, propagates a non-matching error, or sets `last`. The final iteration breaks with `last` set.
- **"Sleeps after the final attempt."** Refuted. Line 20 breaks before the sleep when `k == attempts - 1`, and `test_does_not_sleep_after_the_last_attempt` covers this.
- **"Swallows `KeyboardInterrupt` or `SystemExit`."** Refuted. The default catches `Exception`, not `BaseException`.
- **"Default retry_on is High (realistic misuse)."** Downgraded to Low (F3) in the confirm-or-refute round. Whether callers rely on the default is unknown, and the original error is still re-raised afterwards.

## WHAT HOLDS UP
- The backoff formula matches full jitter: `rng() * min(cap, base·2^k)`.
- The cap is applied, and the sleep count is attempts − 1.
- Non-matching exceptions propagate on the first call.
- The last error is re-raised with its traceback intact.
- `attempts < 1` is rejected.
- Both `sleep` and `rng` are injectable.
- All 6 tests trace to pass. For example, `[1.0, 2.0] == [1, 2]` holds, and the cap test yields `[1, 2, 3, 3, 3]`.

## UNVERIFIED CLAIMS
- **"6 tests, all pass."** Traced by hand, not run. To confirm, run `python -m unittest test_retry`.

## QUESTIONS FOR THE AUTHOR
1. Do any production callers rely on the default `retry_on`? If so, F3 rises.
2. Was a deadline (total-time cap) expected under "injectable clock"?

## DECISION-MAKER SUMMARY
The helper is correct for realistic settings. Before release, add a jitter test with `rng ≠ 1` (F2) and clamp the exponent (F1). Shipping without them risks an unnoticed regression to synchronized retries across production jobs.

## OWNER SUMMARY
The retry tool does what was asked in normal use. Its tests never check the randomness that keeps many jobs from retrying at the same moment, so that could break without anyone noticing. Add one small test and a guard for extremely large retry counts before relying on it.

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
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "generic library code, no personal or confidential data"},
  "coverage": {
    "checked": [
      {"unit": "retry.py", "kind": "file"},
      {"unit": "retry.py:retry", "kind": "function"},
      {"unit": "test_retry.py", "kind": "file"},
      {"unit": "request: injectable clock and random source", "kind": "claim"},
      {"unit": "context: 6 tests all pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "execution of retry.py and test_retry.py", "reason": "no tools in this session"},
      {"unit": "production call sites", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:22",
     "scenario": "With attempts >= 1026, base * 2**k overflows int-to-float at k = 1024 and raises OverflowError inside the handler instead of re-raising the last retried error.",
     "fix": "Clamp the exponent: min(cap, base * 2 ** min(k, 62)).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(2000), attempts=1100, sleep=lambda s: None): expect ConnectionError('boom 1100'), observe OverflowError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_retry.py: all sleep assertions use rng=lambda: 1.0",
     "scenario": "Removing rng() * from retry.py:22 leaves all 6 tests green, so jitter can silently regress and production jobs retry in lockstep.",
     "fix": "Add a test with rng=lambda: 0.5, base=1, cap=100, Flaky(2) expecting slept == [0.5, 1.0], and assert that rng is called.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace line 22 with sleep(min(cap, base * (2 ** k))) and run python -m unittest test_retry: all pass."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:6 retry_on=(Exception,)",
     "scenario": "A caller who omits retry_on gets programming errors (TypeError, ZeroDivisionError) retried up to 5 times, re-running non-idempotent side effects.",
     "fix": "Make retry_on a required keyword argument.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "s=[]; retry(lambda: 1/0, sleep=s.append) makes 5 calls and len(s) == 4 before ZeroDivisionError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "retry.py:12-13",
     "scenario": "cap=-1 or a negative rng makes time.sleep raise ValueError that masks the retryable error; retry_on given as a list raises TypeError only on the first failure.",
     "fix": "Validate base >= 0, cap >= 0, and that retry_on is a BaseException subclass or a tuple of them, at call time.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "retry(Flaky(1), cap=-1): expect 'ok' after one backoff, observe ValueError: sleep length must be non-negative."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "retry.py:6 sleep parameter",
     "suspicion": "'Injectable clock' may have meant a time source for a deadline, not only sleep.",
     "unresolved_fact": "Whether the requester wanted a total-time or deadline cap that needs an injectable now()."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "raise last could raise None.", "evidence": "attempts >= 1 is enforced at lines 12-13, and every loop exit without a return sets last before line 23."},
    {"id": "C2", "candidate": "Sleeps after the final attempt.", "evidence": "Line 20 breaks before the sleep when k == attempts - 1; covered by test_does_not_sleep_after_the_last_attempt."},
    {"id": "C3", "candidate": "Swallows KeyboardInterrupt or SystemExit.", "evidence": "The default retry_on is Exception, not BaseException."},
    {"id": "C4", "candidate": "Default retry_on is a High finding.", "evidence": "Downgraded to Low (F3) in confirm-or-refute: realistic reliance on the default is unknown, and the original error is still re-raised."}
  ]
}
```