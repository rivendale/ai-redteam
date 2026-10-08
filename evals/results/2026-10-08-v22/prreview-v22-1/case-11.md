# PR review: sliding-window rate limiter

**Review report**

**REVIEWED:** The PR adding `rate_limit.py` and `test_rate_limit.py`. No PR number, head SHA or merge base SHA was given, and I have no tools to read them. This review covers only the file contents pasted into this session. Record both SHAs before posting. If the PR head differs from what was pasted, this is not a review of that head.

**TIER: High.** The change controls who can call the production API and how often, which is access control and network exposure. Its key is the client IP address, which counts as personal data in many regimes. High needs two rounds, ideally from two vendors. **This is round 1 of 2.** The PR is not reviewed until a second round runs on an endpoint approved for this code. The code was reviewed inside this session and was not sent anywhere else.

**REVIEWERS:** Claude Opus 5.5 (`claude-opus-5-5`), a fresh instance that did not write the change. The author is unknown because no commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P0 | `rate_limit.py:12` | The limit is keyed on `request.remote_addr`, but the request requires a per-user limit. `user_id` is never read. Two failures follow. (a) 40 employees behind one office NAT share a single budget of 100 requests per minute, so request 101 from anyone in the office gets blocked for everyone. That is the exact case the request rules out. (b) If the API sits behind a load balancer or reverse proxy, `remote_addr` is the proxy's IP, so the whole API is capped at 100 requests per minute in total, which is an outage. In the other direction, a single user spread across many IPs (mobile, VPN, IPv6) gets 100 per minute per IP, so the per-user limit is not enforced. | Two requests with the same `remote_addr="10.0.0.1"` and `user_id` values `"u1"` and `"u2"`, `limit=3`. Send 3 as u1, then assert u2's first call returns `True`. This fails today. Add a mirror test: the same `user_id` from 4 different IPs, assert the 4th call returns `False`. |
| 2 | P1 | `rate_limit.py:8`, `rate_limit.py:15-19` | Entries in `_hits` are never removed. Every key ever seen keeps a dict entry, and every key that was ever active keeps up to `limit` timestamps. Expired entries are only filtered when the same key returns. An attacker rotating source addresses, which is trivial with an IPv6 /64, adds new keys without bound until the process runs out of memory. Keying by user later still grows without bound with the number of users. | Feed 100,000 distinct keys with one hit each, advance the clock past the window, make one more call, and assert `len(rl._hits)` stays bounded, for example ≤ 1. This fails today. |
| 3 | P1 | `rate_limit.py:8` (inferred: deployment config not provided) | The state is a per-process dict. With `gunicorn -w 4`, or with two or more app instances, each worker counts separately, so a user gets up to 100 × workers × instances requests per minute. The PR claims "100 requests per 60 seconds". | An integration test that starts 2 workers and sends 150 requests as one user, asserting at least 50 come back as 429. Alternatively, a design decision recorded in the PR to use a shared store such as Redis. |
| 4 | P2 | `rate_limit.py:14-19` | The read-filter-append-write sequence has no lock. In a threaded server, two concurrent requests for the same key both read 99 hits and both pass. Each writes its own list, and the last write wins, so one hit is lost. Sustained concurrency lets a key go over the limit and undercounts its history. | Use a clock and limiter shared across 50 threads, each calling `allow` once with `limit=10`. Run it repeatedly and assert exactly 10 `True` results. This fails intermittently today. |
| 5 | P1 (inferred: wiring files not provided) | `PR.md:1`, `rate_limit.py` (whole file) | The PR calls this "middleware", but the diff contains only a class. Nothing registers it in the API's request pipeline, and nothing turns `False` into an HTTP 429 with `Retry-After`. If no wiring exists elsewhere, the API has no rate limiting after merge. | A request-level test against the app: send 101 authenticated requests within 60 seconds and assert the 101st returns 429. |
| 6 | P3 | `test_rate_limit.py:7-21` | The "Tests added and passing" claim has not been seen running. Even if the tests pass, they use one IP and one user, so they cannot detect finding 1. The expiry test jumps to t=61 and skips the boundary at exactly t=60, where `now - t < self.window` should allow the request. | Add the tests from finding 1 and a boundary test: `limit=1`, hit at t=0, assert `False` at t=59.999 and `True` at t=60.0. |

**OPEN OWNER DECISION** (not a finding): the request only covers authenticated users. Once the key becomes `user_id`, requests with `user_id=None` must not all fall into a single `None` bucket. Doing that would let one anonymous client lock out every other anonymous client. The owner needs to decide: reject unauthenticated requests before the limiter, or limit them separately, for example by IP.

**FILES NEEDED BUT NOT PROVIDED:** the PR head and merge-base SHAs; the app or middleware registration that wires up `RateLimiter`; the deployment config (worker count, instance count, reverse proxy or load balancer); the commit log with trailers; CI results for the head.

---

**Close-out**

**ADJUDICATION:** pending. The author must decide every finding. The reviewer does not adjudicate its own findings. Findings 1, 2, 3 and 5 are P0 or P1 and cannot be deferred.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–6 | Pending | — |

**VERIFIED AFTER FIXES:** nothing yet. No fixes have been made.

**MERGE RECOMMENDATION: do not merge.**
- Finding 1 (P0) means the core requirement is not met: the limit is per IP, not per user, and an office NAT shares one budget.
- Findings 2, 3 and 5 are open P1s.
- The second High-tier round has not run.
- The SHAs are unrecorded.
- The CI checks have not been seen.
- The decision on unauthenticated requests is still with the owner.

```json
{
  "verdict": "do not merge",
  "findings": [
    {"severity": "P0", "evidence_level": "confirmed by reading code", "location": "rate_limit.py:12", "scenario": "Key is remote_addr, not user_id: users behind one office NAT (or all users behind a proxy) share one 100/min budget and block each other; one user across many IPs escapes the limit.", "fix": "Key on request.user_id for authenticated requests; add tests with two users on the same IP and one user across several IPs."},
    {"severity": "P1", "evidence_level": "confirmed by reading code", "location": "rate_limit.py:8", "scenario": "_hits never evicts keys; rotating source addresses (e.g. IPv6) or many users grow memory without bound until OOM.", "fix": "Delete keys whose filtered list is empty, sweep stale keys periodically or use a TTL store; test that the dict size stays bounded."},
    {"severity": "P1", "evidence_level": "inferred (deployment config not provided)", "location": "rate_limit.py:8", "scenario": "In-process dict: with N workers or instances each user gets 100*N requests/min.", "fix": "Use a shared store (e.g. Redis with atomic ops) or document and enforce a single-process deployment."},
    {"severity": "P2", "evidence_level": "confirmed by reading code", "location": "rate_limit.py:14-19", "scenario": "Unlocked read-modify-write: concurrent requests for the same key both pass at count 99 and one hit is lost, exceeding the limit.", "fix": "Guard with a lock (per key or global) or use an atomic shared-store operation; add a multithreaded test."},
    {"severity": "P1", "evidence_level": "inferred (wiring files not provided)", "location": "PR.md:1", "scenario": "Only a class is added; nothing shown registers it as middleware or returns 429, so the API may be unlimited after merge.", "fix": "Wire into the request pipeline, return 429 with Retry-After, add an end-to-end test."},
    {"severity": "P3", "evidence_level": "confirmed by reading code", "location": "test_rate_limit.py:7-21", "scenario": "Tests use a single IP and user, so they cannot detect the wrong key; the window boundary (t=60) is untested; the 'passing' claim was not seen run.", "fix": "Add per-user isolation tests and an exact-boundary test; attach the CI run."}
  ]
}
```