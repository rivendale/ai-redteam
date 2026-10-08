# pr-review: rate limiter PR

## Review report

**REVIEWED:** The PR described in `PR.md`, "Adds a sliding-window rate limiter middleware". **No head SHA or merge-base SHA was provided**, and this session has no tools to resolve them. Record both before this report is posted. Until then, this report covers only the file contents shown above.

**TIER: High.** The change decides which authenticated users can reach a production API. It controls access and network exposure, not just ordinary logic, and a wrong key denies service to legitimate users. **This is round 1 of 2.** A High-tier PR is not reviewed until the second round has run, ideally on a different vendor approved for this code (Step 3). The code shown carries no secrets or personal data.

**REVIEWERS:**
- Reviewer: this instance (claude-opus-5-5), which did not write the change.
- Author: unknown. No commits or `Co-Authored-By` trailers were provided.

**Evidence levels:**
- "Read": confirmed by reading the code shown.
- "Inferred": depends on files not provided.
- Nothing was run, because there are no tools in this session. The author's claim "Tests added and passing" is unverified.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `rate_limit.py:12` | The limiter is keyed on `request.remote_addr`, not `request.user_id`, so the core requirement is inverted. (a) 30 users behind one office NAT share one 100/min bucket. Once the office sends 100 requests in a minute, every colleague gets blocked. This is exactly what the request forbids. (b) Behind a reverse proxy or load balancer, `remote_addr` is the proxy's IP, so the whole API shares one global 100/min limit: an outage. (c) One user spread across many IPs (mobile, IPv6 rotation) is never limited per user. **Read.** | Two requests with the same `remote_addr="10.0.0.1"` and different `user_id` values ("u1", "u2"), `limit=1`. Assert both are allowed. Then the same `user_id` from two different IPs, `limit=1`. Assert the second is denied. Both assertions fail today. |
| 2 | P1 | `rate_limit.py:8`, `:19` | `_hits` never evicts keys. Every distinct key ever seen keeps an entry forever, including stale timestamp lists. A client rotating source addresses (trivial with IPv6), or any long-running process with many users, grows the dict without bound until the process runs out of memory. Fixing finding 1 bounds this by user count, but expired entries still never leave. **Read.** | Fake clock. Call `allow` for 10,000 distinct keys, advance the clock past `window`, make one more call. Assert `len(rl._hits)` is small, e.g. ≤ 1. Fails today. |
| 3 | P1 | `rate_limit.py:8` (whole design) | State lives in a per-process dict. With N workers or replicas, a user gets up to N×100 requests per minute, and every restart or deploy resets all counters. The "100 per minute per user" contract does not hold in any multi-process deployment. **Inferred**: the deployment topology was not provided. | An integration test with two `RateLimiter` instances standing in for two workers, sharing a backend. Assert that 101 requests split across them are denied once in total. This needs a shared store, such as Redis, to pass. |
| 4 | P1 | PR as a whole (no wiring file) | The PR says "middleware", but only a class is provided. Nothing calls `allow()` on API requests, and nothing returns 429 or `Retry-After` when it returns `False`. If no wiring exists, the API is not rate limited at all. **Inferred**: the wiring may be in files not provided. | A test-client request to a real endpoint 101 times as one user. Assert the 101st gets HTTP 429 with a `Retry-After` header. |
| 5 | P2 | `rate_limit.py:14`–`19` | The read-filter-append-write sequence has no lock. Under a threaded server, two concurrent requests for the same key both read 99 hits, both pass, and one write overwrites the other. The user exceeds the limit, and a lost update undercounts later requests. **Read.** Severity depends on the server model (inferred). | Use a `threading.Barrier` to release 50 threads calling `allow` on one key with `limit=10`. Assert exactly 10 `True` results. This can fail today; make it deterministic with a clock or hook that yields between the read and the write. |
| 6 | P2 | `test_rate_limit.py:9`, `:15` | Both tests use a single IP and a single user, so they cannot tell IP keying from user keying. They pass while the PR violates the request (finding 1). "Tests added and passing" therefore proves nothing about the requirement. **Read.** | The test from finding 1. |

**Pending owner decision (not a finding):** The request covers only authenticated users. `user_id` can be `None`. Should unauthenticated traffic be rejected, limited by IP, or bypass the limiter? A naive fix of `key = request.user_id` would put every anonymous caller into a single `None` bucket. The owner needs to decide this before the fix is written.

**FILES NEEDED BUT NOT PROVIDED:**
- The commit SHAs and trailers
- The code that wires the middleware into the API, along with the 429 response
- Deployment topology: worker count, replicas, and whether a proxy sits in front, plus any trusted forwarded-for handling
- The test run output behind "passing"

## Close-out

A reviewer never adjudicates its own findings. The author adjudicates after this report.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–6 | Pending author | — |

Findings 1–4 are P0/P1 and cannot be deferred.

**VERIFIED AFTER FIXES:** None yet. Verify fixes by reading the correction diff and re-running the tests above, not by another full review.

**MERGE RECOMMENDATION: do not merge.**
- Finding 1 (P0) violates the request outright.
- Findings 2–4 are open P1s.
- The second High-tier round has not run.
- The SHAs are unrecorded.
- No CI checks were shown, and a missing check is not green.
- The anonymous-user owner decision is still pending.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed_by_reading",
      "location": "rate_limit.py:12",
      "scenario": "Limiter keys on request.remote_addr instead of user_id. Users behind one office NAT share a single 100/min bucket and block each other, which the request explicitly forbids. Behind a reverse proxy, all users share one global bucket. A single user across many IPs is never limited per user.",
      "fix": "Key on request.user_id for authenticated requests. Add tests with same IP/different users (both allowed) and same user/different IPs (shared limit)."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_by_reading",
      "location": "rate_limit.py:8",
      "scenario": "_hits never evicts keys or stale timestamp lists. Rotating source addresses or long uptime grows memory without bound, ending in OOM.",
      "fix": "Delete keys whose filtered hit list is empty, or periodically sweep; better, use a TTL'd shared store."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred",
      "location": "rate_limit.py:8",
      "scenario": "In-process dict state: with N workers or replicas the effective limit is N x 100/min per user, and counters reset on every restart or deploy.",
      "fix": "Back the limiter with a shared store (e.g. Redis sorted set or atomic counter with TTL)."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred",
      "location": "PR (no middleware wiring provided)",
      "scenario": "Only a RateLimiter class is shown. Nothing calls allow() on API requests or returns 429/Retry-After, so the API may not be rate limited at all.",
      "fix": "Add middleware integration returning 429 with Retry-After, plus an endpoint-level test making 101 requests as one user."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_by_reading",
      "location": "rate_limit.py:14-19",
      "scenario": "Unlocked read-modify-write: concurrent requests for one key under a threaded server can both pass at the limit boundary, and lost updates undercount.",
      "fix": "Guard with a lock (per key or global), or use an atomic operation in the shared store."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_by_reading",
      "location": "test_rate_limit.py:9",
      "scenario": "Tests use one IP and one user only, so they cannot distinguish IP keying from user keying and pass despite the P0 requirement violation. The 'passing' claim was not verified.",
      "fix": "Add the multi-user/shared-IP and multi-IP/same-user tests from finding 1."
    }
  ]
}
```