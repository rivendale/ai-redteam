**Note:** This is a single-reviewer, tool-less review. I had no subagent and could not run code. The work was not written in this conversation, so the anchoring risk is lower, but nothing was executed. Re-run it with tools before relying on it in production.

---

**VERDICT: REWORK.** The limiter counts by client IP address instead of by authenticated user. That is the opposite of what was asked: users behind the same office network will throttle each other.

**CONFIDENCE: medium.** The main finding is confirmed by reading the exact line. Confidence is limited because I had no tools (tests not run), the middleware wiring and deployment topology were not supplied, and only one reviewer ran.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, PR.md, rate_limit.py, test_rate_limit.py.
- **Not seen:** where `RateLimiter.allow` is wired into the request pipeline, and what response a blocked request gets (429, `Retry-After`). This matters: "add rate limiting to the API" is not shown to be done.
- **Not seen:** deployment topology (worker count, instance count, reverse proxy). This matters because in-process state and `remote_addr` behaviour both depend on it.
- **Not seen:** test run output. "Tests added and passing" is the author's claim. I traced it by hand only.

**COVERAGE**
- **Checked:** rate_limit.py (`RateLimiter.__init__`, `RateLimiter.allow`), test_rate_limit.py (both tests, traced by hand), the PR description claims, and the request's two requirements (per-user counting, no shared-network interference).
- **Not checked:** middleware integration, the response to blocked requests, multi-process deployment, and the real test run.

**SEATS AND GATE:** Local same-session reviewer only. No cross-vendor seats; no subagent tool was available. Sensitivity gate passed: no personal data, credentials or confidential material.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | rate_limit.py:12 `key = request.remote_addr` | The bucket key is the client IP. `user_id` is accepted but never used. The request requires counting per authenticated user, with no cross-user interference behind a shared network. | 101 colleagues behind one office NAT each send 1 request in a minute. The 101st colleague gets blocked despite having sent only one request. Behind a reverse proxy or load balancer, `remote_addr` is the proxy's IP, so **all users worldwide** share one bucket of 100/min. Meanwhile one user rotating IPs (mobile, VPN) gets 100/min per IP. | Key on `request.user_id` for authenticated requests. Decide explicitly how `user_id is None` is handled (see S1). **Repro:** `rl=RateLimiter(limit=1)`; `a=SimpleNamespace(remote_addr="10.0.0.1", user_id="u1")`; `b=SimpleNamespace(remote_addr="10.0.0.1", user_id="u2")`; `rl.allow(a)` then `rl.allow(b)`. Expected True, observed False. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B | test_rate_limit.py:9, 15 | Both tests use one user on one IP. Neither tests the request's core property (separate users on the same IP are independent). The tests pass with the bug in F1, and would equally pass with a fix, so they cannot detect the defect. | A reviewer trusts "tests added and passing" and ships F1 to production. | Add `test_same_ip_different_users_independent` (the F1 repro as an assertion: `u2` allowed after `u1` is exhausted). Also add `test_same_user_different_ips_shared` (`u1` from two IPs shares one budget of `limit`). Both must fail on the current code. | a✓ b✓ c✗ d✓ |
| F3 | Medium | PROBABLE | B | rate_limit.py:9, 14–19 | `self._hits` never evicts keys. Every distinct key ever seen keeps a list of up to `limit` timestamps forever. The read-filter-write sequence also has no lock. | A long-running process sees many distinct keys (IPv6 clients, or many users after the F1 fix) and memory grows without bound. Under a threaded server, two concurrent requests for one key each read the same `hits` list and both write. One write is lost, so the user can exceed 100/min. | Prune empty or expired keys (periodically, or delete when the filtered list is empty). Guard `allow` with a lock, or use an atomic shared store such as Redis. **Repro:** call `allow` with 1,000,000 distinct keys and observe `len(rl._hits)` stays at 1,000,000 after the clock advances past the window. | a✓ b✗ c✗ d✓ |
| F4 | Low | CONFIRMED | B | test_rate_limit.py:20 `clock[0] = 61` | The expiry test jumps 1s past the window, so it never exercises the `<` vs `<=` boundary at line 14. | Someone changes the boundary comparison and nothing goes red. | Add assertions at `t=59.999` (blocked) and `t=60` (allowed, matching the current `now - t < window` behaviour). | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION
- **S1:** What should happen to requests with `user_id is None`? The request only covers authenticated users. If F1 is fixed naively, every anonymous request shares one `None` bucket.
  - **Settles it:** whether the limiter runs before or after authentication, and the intended policy for unauthenticated traffic (reject, separate IP-based limit, or exempt).
- **S2:** In-process state may not enforce 100/min per user in production.
  - **Settles it:** the number of workers and instances. With N processes and no shared store, the effective limit is up to N×100/min per user, depending on load-balancer stickiness.
- **S3:** The PR says "middleware", but no wiring or 429 response is shown.
  - **Settles it:** the diff of the app or middleware registration file, and confirmation that a blocked request returns 429 (ideally with `Retry-After`).
- **S4:** "Tests passing" has not been seen.
  - **Settles it:** CI or local output of `python -m unittest test_rate_limit`. By hand trace, both tests should pass.

### REFUTED
- **R1:** "Rejected requests are not counted, so a client can hammer forever." Not a defect. Rejected requests are not appended (line 16 returns before line 18), so a blocked client regains access as old hits age out. That is standard sliding-window behaviour, and the request asks for 100 requests per minute, not a penalty.
- **R2:** "The window filter is off by one." The code `now - t < window` expires hits at exactly 60s. That is consistent with "per minute". The only gap is the untested boundary (F4), not a bug.

### WHAT HOLDS UP
- The sliding-window logic itself is correct for a single key. Expired hits are filtered and the count is compared with `>=` before appending, so exactly `limit` requests pass.
- The injectable clock is a good design choice for testability.
- Using `time.monotonic` avoids wall-clock jumps.

### UNVERIFIED CLAIMS
- **"Tests added and passing":** confirm with the test run output.
- **"Middleware":** confirm with the registration diff.
- **"100 requests per 60 seconds":** true per key in a single process only. Confirm the deployment topology (S2).

### QUESTIONS FOR THE AUTHOR
1. Why `remote_addr` instead of `user_id`, given the request's explicit office-network requirement?
2. Where is this wired in, does it run after authentication, and what does a blocked request receive?
3. How many processes or instances serve the API, and is there a shared store?

### DECISION-MAKER SUMMARY
Do not merge. The limiter counts by IP address rather than by user (F1), so it fails the exact scenario the request named, and the added tests cannot detect this (F2). If shipped behind a proxy or load balancer, every customer could share a single 100/min budget and real traffic would be broadly blocked.

### OWNER SUMMARY
The new request limit counts traffic by network address instead of by person. Colleagues sharing an office connection would block each other, and in some setups all customers could block each other. It needs to be changed to count per signed-in user, with tests that prove different users don't affect one another, before it goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "PR.md", "status": "seen", "matters": true},
    {"item": "rate_limit.py", "status": "seen", "matters": true},
    {"item": "test_rate_limit.py", "status": "seen", "matters": true},
    {"item": "middleware wiring / app registration diff", "status": "not_seen", "matters": true},
    {"item": "deployment topology (workers, instances, proxy)", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "file"},
      {"unit": "rate_limit.py", "kind": "file"},
      {"unit": "rate_limit.py:RateLimiter.allow", "kind": "function"},
      {"unit": "test_rate_limit.py", "kind": "file"},
      {"unit": "per-user counting requirement", "kind": "claim"},
      {"unit": "no cross-user interference on shared network", "kind": "claim"},
      {"unit": "Tests added and passing", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "middleware registration / 429 response", "reason": "not supplied"},
      {"unit": "multi-process deployment config", "reason": "not supplied"},
      {"unit": "actual test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rate_limit.py:12",
     "scenario": "Limiter keys on remote_addr, not user_id: 101 users behind one office NAT sending one request each causes the 101st to be blocked; behind a reverse proxy all users share one 100/min bucket.",
     "fix": "Key buckets on request.user_id for authenticated requests and define explicit handling for user_id None.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "rl=RateLimiter(limit=1); allow(remote_addr='10.0.0.1',user_id='u1') then allow(remote_addr='10.0.0.1',user_id='u2'); expect True, observe False."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_rate_limit.py:9,15",
     "scenario": "Tests use a single user on a single IP, so they pass with the IP-keying bug and give false assurance that the per-user requirement is met.",
     "fix": "Add tests asserting different users on one IP are independent and one user across IPs shares a budget; both must fail on current code.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test: exhaust u1@10.0.0.1 with limit=1, assert allow(u2@10.0.0.1) is True; observe failure on current code."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rate_limit.py:9,14-19",
     "scenario": "_hits never evicts keys, so memory grows unbounded with distinct keys; unlocked read-modify-write lets concurrent requests lose hits and exceed the limit under a threaded server.",
     "fix": "Prune empty/expired keys and guard allow() with a lock or use an atomic shared store.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Call allow() with 1,000,000 distinct remote_addr values, advance clock past window, observe len(rl._hits) remains 1,000,000."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_rate_limit.py:20",
     "scenario": "Expiry test jumps to t=61, so changing '<' to '<=' at rate_limit.py:14 would go undetected.",
     "fix": "Add boundary assertions at t=59.999 (blocked) and t=60 (allowed).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Change '<' to '<=' at rate_limit.py:14 and run tests; observe they still pass."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rate_limit.py:11",
     "suspicion": "After keying on user_id, all unauthenticated requests would share one None bucket.",
     "unresolved_fact": "Whether the limiter runs after authentication and the intended policy for unauthenticated traffic."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rate_limit.py:9",
     "suspicion": "In-process dict gives up to N x 100/min per user across N processes or instances.",
     "unresolved_fact": "Number of workers/instances serving the API and whether a shared store is used."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "PR.md",
     "suspicion": "Described as middleware but no wiring or 429 response is included.",
     "unresolved_fact": "The diff registering the middleware and the response returned when allow() is False."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "PR.md",
     "suspicion": "'Tests added and passing' is asserted, not shown.",
     "unresolved_fact": "Output of python -m unittest test_rate_limit."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Rejected requests are not counted, so a client can hammer indefinitely.",
     "evidence": "Line 16 returns False before appending; hits age out normally. Standard sliding-window behaviour and matches '100 requests per minute'."},
    {"id": "R2", "candidate": "Window filter is off by one.",
     "evidence": "now - t < window expires hits at exactly 60s, consistent with a per-minute window; only the test coverage gap remains (F4)."}
  ]
}
```