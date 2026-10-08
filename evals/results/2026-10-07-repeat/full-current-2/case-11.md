**Note:** This is a single reviewer in one session, with no subagent and no tools. Nothing was executed. Every claim about runtime behaviour comes from reading the code, and the test suite was not run.

**VERDICT: REWORK.** The limiter counts requests per client IP, not per user. That is exactly what the request forbids: everyone behind one office network shares a single 100/min budget.

**CONFIDENCE: medium.** The core defect is plain from the code, so that part is solid. Confidence is limited by:
- no tools: tests not run, no mutation check;
- no view of how the limiter is wired into the app or deployed.

**INPUTS LEDGER:**
- **Seen:**
  - the original request (`request.md`)
  - the context and PR description (`context.md`, `PR.md`)
  - `rate_limit.py`
  - `test_rate_limit.py`
- **Not seen, and it matters:**
  - Where `RateLimiter` is wired into the request pipeline, and how `remote_addr` and `user_id` are filled in. This matters because the PR calls it "middleware", but nothing hooks it in or returns a 429.
  - The deployment model (worker count, number of instances). This matters because the counter lives in process memory.
  - CI output behind "tests passing". This matters little: the tests would pass whether or not the main defect is fixed.

**SEATS AND GATE:**
- Seat: a single same-session reviewer.
- No cross-vendor seats: none were requested, and the stakes didn't require them.
- Sensitivity gate passed: the material contains no personal data or credentials.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B (drift) | `rate_limit.py`, `allow()`: `key = request.remote_addr` | The bucket key is the client IP. `user_id` is never read. The request requires counting "per user" and says office users "must not be limited by each other's traffic". | 30 people in one office sit behind one NAT IP. Together they make 100 requests in a minute, and every one of them gets blocked. That is the exact outcome the request prohibits. Separately, one user spread across several IPs (mobile plus VPN) gets 100/min on each. | Key on `request.user_id` for authenticated requests. Add a test: two users on the same IP each get the full limit, and one user on two IPs shares a single budget. | confirmed. Defence considered: "maybe `remote_addr` already holds the user". The docstring defines `remote_addr` and `user_id` as separate fields, so this fails. |
| 2 | High | CONFIRMED (by trace) | B (tests) | `test_rate_limit.py`, both tests | Each test reuses one object (`remote_addr="10.0.0.1", user_id="u1"`). Nothing tests separation by user or by IP. The tests pass with the wrong key and would still pass with the right one, so they cannot catch finding 1. "Tests added and passing" therefore proves nothing about the requirement. | A regression back to IP keying, or the current bug, ships with a green CI. | Add a test with two users on one IP (both allowed up to the limit) and one with one user on two IPs (shared limit). Confirm the new test fails against the current code before fixing it. | confirmed. Swapping the key cannot change either test's result. |
| 3 | Medium | PROBABLE | B | `allow()`: no handling of `user_id is None` | The request scopes the limit to authenticated users, but the unauthenticated case is undefined. The naive fix for finding 1 (`key = request.user_id`) would put every anonymous caller into one shared `None` bucket. | After the fix, all anonymous or health-check traffic shares 100/min, or unauthenticated traffic is never limited. Either way, the behaviour was never decided. | Decide explicitly how unauthenticated requests are handled: skip them, use a separate IP-based limiter, or reject them. Use a namespaced key such as `("user", id)`, and test the `None` case. | n/a |
| 4 | Medium | CONFIRMED | B (ops) | `self._hits = {}`; keys are never deleted | Old timestamps are pruned only when the same key comes back. Idle keys stay in memory forever. | Many distinct IPs or users (or spoofed `X-Forwarded-For` values, if `remote_addr` comes from a header) make memory grow without limit over the process lifetime. | Delete a key when its pruned list is empty, or sweep periodically, or use a TTL store. | n/a |
| 5 | Medium | UNVERIFIED | B (ops) | Module-level, in-process state | The count is per process. With N workers or instances, a user effectively gets N×100/min, depending on which worker serves each request. | A typical deployment (gunicorn with 4 workers, 3 pods) lets each user make about 1200 requests per minute. | Use a shared store, such as a Redis sorted set or counter with expiry, or state that the limit is per process. Settle by checking the deployment config. | n/a |
| 6 | Medium | PROBABLE | B (concurrency) | `allow()` read-modify-write on `_hits[key]` | There is no lock. Two concurrent threads can both read 99 hits and both be allowed, and one write can overwrite the other's appended timestamp. | Under a threaded server, the limit is exceeded and timestamps are lost, so later counting runs low. | Guard each key with a lock, or use an atomic shared store as in finding 5. | n/a |
| 7 | Medium | PROBABLE | B (requirement fit) | `PR.md` says "middleware"; only a class with `allow()` exists | Nothing wires it into the request pipeline, returns 429, or sets `Retry-After`. | If no other diff exists, the merged PR limits nothing in production. | Show the integration point and add an end-to-end test that the 101st request gets a 429. | n/a |
| 8 | Low | CONFIRMED | B (tests) | `test_window_expires`: `clock[0] = 61` | The window boundary (t = 60 exactly, and t = 59.9) is not tested. The test passes even if `<` becomes `<=`. | An off-by-one change at the boundary goes unnoticed. | Assert that the request is denied at 59.9 and allowed at 60.0. | n/a |

## WHAT HOLDS UP

- The sliding-log logic is sound for a single key:
  - It prunes with `now - t < window`.
  - Rejected requests are not recorded, so a blocked client recovers as the window slides.
  - It uses a monotonic clock, which avoids wall-clock jumps.
- Injecting the clock makes the code testable.
- The defaults of 100/60 match the requested numbers.

## UNVERIFIED CLAIMS

- "Tests added and passing": not run here. By reading the code they would pass, but they do not test the requirement (finding 2). To settle it, run the suite and add the per-user test.
- "Middleware": not shown. To settle it, provide the integration diff.

## QUESTIONS FOR THE AUTHOR

1. Where is `RateLimiter.allow` called, and what response does the caller send when it returns `False`?
2. How many processes or instances serve the API?
3. What should happen to unauthenticated requests?

## DECISION-MAKER SUMMARY

Do not merge. The limiter counts by IP address, so whole offices will block each other, which is the specific failure the request ruled out. The tests cannot detect this. Fix the keying and add a two-users-one-IP test first. Then answer the questions on wiring, multiple processes, and unauthenticated traffic before relying on it in production.

## OWNER SUMMARY

The new limit counts requests by network address instead of by person. Colleagues sharing an office connection would use up one shared allowance and get blocked together. The checks that were added would not catch this, so the change needs rework before release.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md / PR.md", "status": "seen", "matters": true},
    {"item": "rate_limit.py", "status": "seen", "matters": true},
    {"item": "test_rate_limit.py", "status": "seen", "matters": true},
    {"item": "middleware integration / app wiring", "status": "not_seen", "matters": true},
    {"item": "deployment config (workers/instances)", "status": "not_seen", "matters": true},
    {"item": "CI test output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "rate_limit.py allow(): key = request.remote_addr",
     "scenario": "Users behind one office NAT share a single 100/min bucket and block each other; request requires per-user counting and forbids this.",
     "fix": "Key on request.user_id for authenticated requests; test two users on one IP and one user on two IPs.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_rate_limit.py (both tests use one identical request)",
     "scenario": "Tests pass whether keyed by IP or user, so the per-user requirement is untested and the drift ships green.",
     "fix": "Add per-user isolation test; confirm it fails on current code before fixing.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rate_limit.py allow(): user_id None unhandled",
     "scenario": "After switching to user_id, all unauthenticated callers share one None bucket, or behavior is undefined.",
     "fix": "Define unauthenticated policy explicitly; namespace keys; test None.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "rate_limit.py self._hits never evicts keys",
     "scenario": "Unbounded memory growth with many distinct keys over process lifetime.",
     "fix": "Delete empty keys or use TTL store.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "rate_limit.py in-process state",
     "scenario": "With N workers/instances the effective limit is N x 100 per user.",
     "fix": "Shared store (e.g. Redis) or document per-process scope; check deployment config.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rate_limit.py allow() read-modify-write",
     "scenario": "Concurrent threads both pass at 99 hits and lose appended timestamps.",
     "fix": "Per-key lock or atomic shared store.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "PR.md 'middleware' vs class-only implementation",
     "scenario": "No integration or 429 response shown; if none exists, nothing is limited in production.",
     "fix": "Show wiring; end-to-end test that request 101 returns 429.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "test_rate_limit.py test_window_expires clock=61",
     "scenario": "Boundary off-by-one (< vs <=) goes undetected.",
     "fix": "Assert denied at 59.9, allowed at 60.0.", "status": "n/a"}
  ]
}
```