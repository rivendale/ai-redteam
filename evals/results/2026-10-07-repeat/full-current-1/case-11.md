# Redteam review: rate limiter PR

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. Nothing was run; every point comes from reading the source.

**VERDICT: REWORK.** The limiter counts requests per IP address instead of per user. That is the exact behaviour the request forbids: everyone behind one office network shares a single 100/min budget.

**CONFIDENCE: medium.** The central finding is confirmed by reading the code. Confidence is limited because:
- I could not run the tests.
- I was not shown the app or middleware wiring, or the deployment topology.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md, PR.md | seen | yes |
| rate_limit.py | seen | yes |
| test_rate_limit.py | seen | yes |
| `__pycache__/rate_limit.cpython-312.pyc` | seen; strings match the source, including the `remote_addr` key | low |
| Where `RateLimiter` is wired into the API (middleware registration, 429 response) | not seen | yes: if it is not wired in, nothing is limited |
| Deployment (worker processes, threads, hosts) | not seen | yes: in-process state is per process |
| Test run output for "Tests added and passing" | not seen | medium |

**SEATS AND GATE:** I ran as a single same-context reviewer, with no subagent available. No cross-vendor seats ran. The sensitivity gate found no personal data, credentials or confidential material.

## Pass 1: Reconstruct

The PR claims a sliding-window limiter of 100 requests per 60 s, with passing tests. To meet the request, three things must be true:
1. The count is keyed on the authenticated user.
2. Users sharing an IP do not affect each other.
3. The limiter actually runs in front of the API and is enforced consistently across however many processes serve it.

Unstated assumptions:
- The API runs as a single process.
- `allow()` is invoked on every request.
- The number of distinct keys stays small.

This review uses Track B (code), with a Track A check on requirement fit.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B/A | `rate_limit.py:12` `key = request.remote_addr` | The limiter keys on client IP. `user_id` is documented on line 11 and then ignored. This is drift from "counted per user" and directly breaks "users behind the same office network must not be limited by each other's traffic." | 20 employees behind one NAT IP each send 10 req/min, 200 in total. After the first 100, every employee gets blocked, although no user is near 100. In the other direction, one user spread across several IPs (mobile plus office) gets more than 100/min. | Key on `request.user_id` for authenticated requests. Decide and document unauthenticated handling (reject, or a separate per-IP limit). Add a test: two users on the same `remote_addr` each get their full limit. Add another: one user on two IPs shares one limit. | confirmed. The strongest defence would be that `remote_addr` stands in for the user upstream, but the docstring itself names a separate `user_id` field, and the request explicitly rules out IP as the identity. |
| 2 | High | CONFIRMED (test content); coverage gap | B | `test_rate_limit.py:9,17` | Both tests use the same IP and the same user, so they cannot tell IP keying from user keying. They pass against the buggy code. "Tests added and passing" proves nothing about the requirement. | A regression or the current bug in the keying logic ships green. CI gives false assurance on production. | Add the two isolation tests from #1. Mutation check: with `key = request.remote_addr`, the new same-IP/two-users test must fail; with `user_id` keying, it must pass. | confirmed. Nothing in either test varies `remote_addr` or `user_id`. |
| 3 | High | UNVERIFIED | B | PR.md ("middleware"); integration code not supplied | The PR calls this middleware, but only a class with `allow()` is shown. I saw no registration in the request pipeline, no 429 response and no `Retry-After` header. | If it is not wired in, the API is not rate limited at all, while the PR reads as done. | Supply the integration diff. Add an end-to-end test: request 101 within 60 s returns 429. | Held as UNVERIFIED, not confirmed. It is a missing input, and it decides whether anything ships. |
| 4 | Medium | PROBABLE | B | `rate_limit.py:8` `self._hits = {}` | State lives in process memory. | Behind N gunicorn/uvicorn workers or several hosts, each process counts separately. The effective limit becomes up to 100×N per user and varies with load-balancer routing. Counts also reset on every deploy or restart. | Use a shared store (for example Redis with a sorted-set sliding log or a token bucket), or document and enforce single-process deployment. | Not a High/Critical candidate. Severity depends on the deployment, which I did not see. |
| 5 | Medium | PROBABLE | B | `rate_limit.py:14-20` | The read-modify-write on `_hits` has no lock. | Under a threaded server, concurrent requests for the same key both read 99 hits and both append. That allows slight overruns, and one list can overwrite the other so hits are lost. | Wrap in `threading.Lock`, or use atomic operations in a shared store. | — |
| 6 | Medium | CONFIRMED | B | `rate_limit.py:8,15-20` | Keys are never evicted. Each key's list is capped at about `limit` entries, but the dict grows with every distinct key ever seen. | With per-IP keying, scanners or spoofed-source traffic through a proxy grow memory without bound. With per-user keying, the growth tracks total users. In a long-lived process this is a slow leak. | Delete keys whose filtered list is empty, or sweep periodically, or use a store with TTLs. | — |
| 7 | Low | CONFIRMED | B | `__pycache__/rate_limit.cpython-312.pyc` | A compiled bytecode artifact is committed. | It can go stale relative to the source and adds review noise. | Remove it and add `__pycache__/` to `.gitignore`. | — |

## What holds up

- **Sliding-log logic.** `now - t < self.window` correctly expires entries older than the window. Blocked requests are not appended, so a client cannot extend its own lockout, and the per-key list is bounded by `limit`.
- **Monotonic clock.** `time.monotonic` is the right choice: it is immune to wall-clock jumps.
- **Testable design.** The injectable clock makes the window logic deterministic to test.
- **Existing tests.** The two tests correctly exercise the limit and window expiry for a single key.

## Unverified claims

- **"Tests added and passing."** I did not run them. To settle it, run `python -m unittest test_rate_limit` and attach the output. Note that passing would still not show the per-user requirement is met (#2).
- **"Middleware."** To settle it, show where `RateLimiter.allow` is called in the request path and what response a blocked request gets.

## Questions for the author

1. Where is `allow()` called, and what does a blocked client receive?
2. How many processes or hosts serve the API in production?
3. What should happen to unauthenticated requests (`user_id is None`)?

## Decision-maker summary

Do not merge. The limiter counts per IP, not per user, so office users sharing a network will block each other, which is precisely what was forbidden. The tests cannot detect this. Rework it to key on user ID, add isolation tests, and confirm it is actually wired in and shared across workers. Shipping as is risks legitimate customers being throttled in production.

## Owner summary

The new limit is applied to whole networks instead of to individual people. Colleagues in the same office would therefore use up each other's allowance and get blocked. The tests that were added do not check this, so they passed anyway. It needs to be changed to count each signed-in person separately before it goes live.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "rate_limit.py", "status": "seen", "matters": true},
    {"item": "test_rate_limit.py", "status": "seen", "matters": true},
    {"item": "middleware/app integration code", "status": "not_seen", "matters": true},
    {"item": "deployment topology (workers/hosts)", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "rate_limit.py:12",
     "scenario": "Limiter keys on request.remote_addr instead of user_id; many users behind one office NAT share a single 100/min budget and block each other, violating the explicit requirement; one user on several IPs exceeds 100/min.",
     "fix": "Key on request.user_id for authenticated requests; define unauthenticated handling; add same-IP/different-user and same-user/different-IP tests.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_rate_limit.py:9,17",
     "scenario": "Both tests use one IP and one user, so they pass with IP keying; the per-user requirement is untested and the 'tests passing' claim gives false assurance.",
     "fix": "Add isolation tests; confirm the same-IP/two-users test fails against current code and passes after the fix.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "B", "location": "PR.md ('middleware'); integration not supplied",
     "scenario": "Only a RateLimiter class is shown; if it is not registered in the request pipeline with a 429 response, the API is not rate limited at all.",
     "fix": "Supply the integration diff; add an end-to-end test that request 101 within 60s returns 429.", "status": "unverified"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rate_limit.py:8",
     "scenario": "In-process dict: with N workers or hosts the effective limit is up to 100xN and resets on restart.",
     "fix": "Use a shared store such as Redis, or document and enforce single-process deployment."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rate_limit.py:14-20",
     "scenario": "Unlocked read-modify-write under a threaded server allows overruns and lost hits for concurrent requests on one key.",
     "fix": "Add a threading.Lock or use atomic store operations."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "rate_limit.py:8,15-20",
     "scenario": "Keys are never evicted; the dict grows with every distinct key, so a long-lived process leaks memory.",
     "fix": "Drop keys with empty filtered lists, sweep periodically, or use TTLs in a store."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "__pycache__/rate_limit.cpython-312.pyc",
     "scenario": "A committed bytecode artifact can go stale against the source and adds review noise.",
     "fix": "Remove it and add __pycache__/ to .gitignore."}
  ]
}
```
