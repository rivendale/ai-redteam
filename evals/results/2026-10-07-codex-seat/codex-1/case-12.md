same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.

**VERDICT: SHIP WITH FIXES** — The normal retry path matches the request, but capped backoff can overflow, invalid delays can replace the original error, and the tests do not protect jitter behavior.

**CONFIDENCE: medium** — Findings come from static inspection. No tests or mutation checks were executed.

**INPUTS LEDGER**
- Seen: original request, production-library context, complete supplied `retry.py` and six tests.
- Not seen: actual test results, supported Python versions, configuration constraints, or production callers. These gaps limit operational confidence.
- The skill’s referenced supporting documents were unavailable; this review uses the supplied instructions.

**SEATS AND GATE:** One local reviewer ran. No additional seats were available under the no-tools constraint. Cross-vendor seats were excluded as requested. No sensitive information appears in the supplied work.

**RECONSTRUCTION**

The helper calls `fn()` up to `attempts` times, catches selected exceptions, and sleeps between failures using an injected sleeper and random source. It claims exponential backoff with full jitter and a maximum delay, then raises the last matching exception. Correctness assumes an integer attempt count, suitable numeric delay settings, an RNG returning values between zero and one, and functioning injected dependencies. Tracks B and C apply, including scrutiny of the claim that six passing tests establish correctness.

**FINDINGS**

Locations below count the first supplied line of each file as line 1.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED | B | `retry.py:23` | The exponential is calculated before the cap protects it. | With default `base`, `attempts=1100`, and persistent matching failures, `k=1024` requires converting `2**1024` to float. That raises `OverflowError`, replacing the function’s error despite the five-second cap. | Maintain a bounded backoff iteratively, avoiding unbounded exponentiation. Test more than 1,025 failures using a recording sleeper. | confirmed by static trace; execution unavailable |
| 2 | Medium | CONFIRMED | B | `retry.py:12–13,23` | Delay settings are not validated before calling `fn`. | With `base=-1`, a matching failure, and an RNG returning a positive value, the default sleeper receives a negative delay and raises `ValueError`. The promised retries stop and the original error is replaced. Negative `cap` has the same problem. | Validate supported numeric types and finite, nonnegative delay settings before invoking `fn`. Test rejection before any function call. | confirmed by static trace |
| 3 | Medium | CONFIRMED | B | `test_retry.py:17–52` | The suite cannot detect removal of jitter. All asserted delay sequences use an RNG returning `1.0`. | Replacing `rng()` with literal `1.0` would preserve every supplied assertion while eliminating full jitter in production. | Add deterministic zero and fractional RNG cases, including after the cap is reached. In a scratch copy, make that mutation and confirm the tests fail. | confirmed by inspection; mutation execution unavailable |

The first two findings concern configuration boundaries; neither demonstrates failure for ordinary valid settings and small attempt counts. They do not justify a High or Critical finding.

**WHAT HOLDS UP**

- The normal path uses the requested exponential schedule and caps each computed delay.
- A successful result returns immediately.
- Nonmatching exceptions propagate immediately.
- Exhaustion raises the last captured exception, with no sleep after the final call.
- Both the sleep function and random source are injectable.
- No reviewer-directed instructions or apparent secrets occur in the work.

**UNVERIFIED CLAIMS**

- “Six tests, all pass”: run the supplied suite on supported Python versions.
- Effective test coverage: execute deliberate mutations in a throwaway copy; no test was demonstrated to fail here.
- Production configuration safety: inspect callers for attempt limits and delay validation.
- Actual jitter distribution: the expression is consistent with full jitter for the default RNG, but runtime behavior was not measured.

**QUESTIONS FOR THE AUTHOR**

Are callers already guaranteed to supply finite, nonnegative delays and a bounded positive integer attempt count? Evidence of those enforced constraints would reduce the operational importance of the first two findings.

**DECISION-MAKER SUMMARY**

Fix bounded backoff calculation and validate delay settings before production adoption. Add tests that would fail if jitter were removed. Proceeding unchanged leaves configuration-dependent failures and a test suite that can miss a central requirement.

**OWNER SUMMARY**

The helper works for ordinary settings, but some settings can make it stop with the wrong error. Its tests also miss whether random delays are actually used. Address those gaps before shared production use.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "original request, context, retry.py, test_retry.py", "status": "seen", "matters": true},
    {"item": "test execution and mutation results", "status": "not_seen", "matters": true},
    {"item": "production callers and configuration constraints", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "OpenAI", "status": "ran_static_review", "cross_vendor": false}
  ],
  "sensitivity_gate": {
    "sensitive": false,
    "reason": "No sensitive material apparent; cross-vendor seats excluded by request."
  },
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "retry.py:23",
      "scenario": "With attempts=1100 and persistent failures, the uncapped exponential causes OverflowError at k=1024, replacing the function error.",
      "fix": "Calculate bounded backoff without unbounded exponentiation; test a long failure sequence with an injected sleeper.",
      "status": "confirmed"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "retry.py:12-13,23",
      "scenario": "A negative base or cap produces a negative sleep duration, causing ValueError after fn has already run.",
      "fix": "Validate finite, nonnegative delay settings before calling fn; test that invalid configuration causes no function calls.",
      "status": "confirmed"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "test_retry.py:17-52",
      "scenario": "Replacing rng() with 1.0 preserves all supplied assertions while removing full jitter.",
      "fix": "Test zero and fractional random values before and after capping; confirm the mutation fails in a scratch copy.",
      "status": "confirmed"
    }
  ]
}
```