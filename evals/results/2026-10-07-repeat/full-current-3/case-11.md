**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing was run. Findings come from reading the code. Where I say CONFIRMED, it is traced to an exact line.

VERDICT: **REWORK**. The limiter counts requests per IP address instead of per user, which is the opposite of the request's central requirement. The tests are built so they cannot detect this.

CONFIDENCE: **medium**. The core defect is certain from the source text. Confidence is limited because I could not run the tests, could not see how the class is wired in as middleware, and do not know the deployment topology (workers or instances).

INPUTS LEDGER:
- **Seen:** request.md, context.md, PR.md, rate_limit.py, test_rate_limit.py.
- **Not seen:** where `RateLimiter` is registered as middleware and what it returns on denial (matters, see F7). How `request.user_id` and `remote_addr` are populated, including proxy headers and the auth layer (matters for F1 and F3). The server and worker model (matters for F5 and F6). Test run output; "passing" is UNVERIFIED but does not change the verdict.

SEATS AND GATE: Sensitivity gate passed; there is no personal or confidential data. Same-context local review only. No subagent and no cross-vendor seats were available or requested.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B (drift) | rate_limit.py `allow`: `key = request.remote_addr` | The bucket key is the client IP. The request requires "counted per user" and "users behind the same office network must not be limited by each other's traffic." `user_id` is never read. | 30 staff behind one office NAT share a single 100/min budget. Once it is spent, every one of them gets denied. A single user spread across many IPs (mobile plus VPN) gets 100/min per IP, so the per-user limit is not enforced either. | Key on `request.user_id` for authenticated requests. Add a test where two users share one `remote_addr` and one user's traffic does not block the other. | confirmed. Strongest defense: maybe upstream sets `remote_addr` to the user ID. Refuted by the docstring, which treats `remote_addr` and `user_id` as distinct fields. |
| 2 | High | CONFIRMED | B (tests) | test_rate_limit.py, both tests use `remote_addr="10.0.0.1", user_id="u1"` | Every request in both tests has the same IP and the same user. The tests pass identically whether the key is IP or user, so they cannot catch F1. "Tests added and passing" gives false assurance about the stated requirement. | A reviewer trusts the green tests and ships F1. A future fix to user keying could also regress silently. | Add (a) same IP with different users, both allowed independently; (b) same user with different IPs, sharing one budget. Mutation check: switch the key between `remote_addr` and `user_id`. Today both tests stay green either way, which is CONFIRMED by inspection. They must go red. | confirmed |
| 3 | Medium | PROBABLE | B | rate_limit.py `allow`; docstring says `user_id (str or None)` | Unauthenticated requests are not handled. The request scopes the limit to authenticated users. After a naive fix (`key = request.user_id`), every anonymous request lands in one shared `None` bucket. | Anonymous traffic collectively exhausts one 100/min bucket, or anonymous traffic goes unlimited, depending on the fix. Either way the behaviour is undefined. | Decide the policy explicitly: reject, separate per-IP limit, or skip. Test the `user_id=None` case. | n/a |
| 4 | Medium | PROBABLE | B (ops) | rate_limit.py `self._hits = {}` | Keys are never evicted. Stale timestamp lists are pruned only when that same key is seen again. | Memory grows with every distinct key ever seen: IPs now, users after the fix. On a long-lived process with many clients, or IPv6 address rotation, this leaks indefinitely. | Periodically sweep keys whose newest hit is older than the window, or use a TTL store. | n/a |
| 5 | Medium | PROBABLE | B (concurrency) | rate_limit.py `allow`: read, filter, append, write with no lock | The read-modify-write is not atomic. Under a threaded server, concurrent calls for one key can both read 99 hits and both append. Lost updates then under-count. | A burst of parallel requests from one client exceeds 100/min. | Add a `threading.Lock` (or a per-key lock) around the update, or use an atomic store. Test with concurrent calls. | n/a |
| 6 | Medium | UNVERIFIED | B (ops) | rate_limit.py, in-process `_hits` dict | State is per process. With N workers or instances behind a load balancer, the effective limit is about N×100 per key. | The production limit is several times what was asked, and varies with the worker count. | Confirm the deployment model. If there is more than one process, use a shared store (Redis sliding window or similar). | n/a |
| 7 | Medium | UNVERIFIED | B (requirement fit) | PR.md says "middleware"; rate_limit.py has only a `RateLimiter.allow` method | No middleware integration is in the diff. There is no 429 response, no `Retry-After` header, and no registration. | The class is either not wired in at all, or it is wired somewhere unseen that returns the wrong status. | Show the integration. Return 429 with `Retry-After`. Add an integration test through the framework. | n/a |
| 8 | Low | CONFIRMED | B (tests) | test_window_expires: `clock[0] = 61` | The window boundary is not tested. The code uses `now - t < window`, so a hit expires at exactly 60s, but the test jumps to 61. | An off-by-one change (`<=`) would go unnoticed. | Test at t=59.999 (denied) and t=60 (allowed). | n/a |

### WHAT HOLDS UP
- The sliding-window logic per key is sound. It prunes hits older than the window, counts before appending, and does not count denied requests, so a blocked client is not penalized further.
- The injectable clock is good design for testing.
- Per-key memory is bounded by `limit`, about 100 timestamps per key.

### UNVERIFIED CLAIMS
- **"Tests added and passing":** I could not run them. Running `python -m unittest test_rate_limit` would settle it. Even if they pass, they do not cover the requirement (F2).
- **"middleware":** settled by showing the registration and response path (F7).

### QUESTIONS FOR THE AUTHOR
1. Why `remote_addr` and not `user_id`? Is there an upstream layer that changes what these fields mean?
2. What should happen to unauthenticated requests?
3. How many processes or instances serve the API in production?

### DECISION-MAKER SUMMARY
Do not merge. The limiter counts by IP address, so colleagues on one office network will block each other, which is exactly what the request forbids. The tests cannot detect this. Fix the key, add the two-users-one-IP test, and confirm the multi-worker deployment before shipping.

### OWNER SUMMARY
The new limit counts traffic by network location instead of by person. People sharing an office connection would lock each other out after 100 combined requests a minute. The change needs to be reworked to count each person separately, with tests proving it, before it goes live.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "middleware registration / 429 response path", "status": "not_seen", "matters": true},
    {"item": "auth layer populating user_id / proxy handling of remote_addr", "status": "not_seen", "matters": true},
    {"item": "deployment worker/instance model", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "rate_limit.py allow(): key = request.remote_addr",
     "scenario": "Users behind one office NAT share a single 100/min bucket and block each other; one user across many IPs gets 100/min per IP. Directly violates 'counted per user' and the office-network requirement.",
     "fix": "Key on request.user_id for authenticated requests; add test with two users sharing one remote_addr.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_rate_limit.py both tests (same remote_addr and user_id)",
     "scenario": "Tests pass identically whether keyed by IP or user, so they cannot catch the Critical defect; 'tests passing' gives false assurance.",
     "fix": "Add same-IP/different-user and same-user/different-IP tests; verify they go red when the key is switched.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rate_limit.py allow(); user_id may be None",
     "scenario": "After keying on user_id, all unauthenticated requests share one None bucket (or go unlimited); policy undefined.",
     "fix": "Define and test behaviour for user_id=None.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rate_limit.py self._hits = {}",
     "scenario": "Keys are never evicted; memory grows with every distinct client over process lifetime.",
     "fix": "Periodic sweep of expired keys or TTL store.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "rate_limit.py allow() read-modify-write",
     "scenario": "Concurrent requests for one key race and under-count, letting bursts exceed 100/min under threaded servers.",
     "fix": "Lock around the update or use an atomic shared store; add concurrency test.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "rate_limit.py in-process _hits",
     "scenario": "With N workers/instances the effective limit is about N x 100 per key.",
     "fix": "Confirm deployment; use shared store (e.g. Redis) if multi-process.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "PR.md 'middleware' vs rate_limit.py (class only)",
     "scenario": "No integration shown: limiter may not be wired in, or returns wrong status without Retry-After.",
     "fix": "Show registration; return 429 with Retry-After; add integration test.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "test_window_expires clock[0] = 61",
     "scenario": "Exact 60s boundary untested; an off-by-one change would pass.",
     "fix": "Test at t=59.999 (denied) and t=60 (allowed).", "status": "n/a"}
  ]
}
```