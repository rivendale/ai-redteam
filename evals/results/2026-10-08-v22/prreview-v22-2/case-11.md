# PR Review: sliding-window rate limiter

**Review report**

**REVIEWED:** PR "Adds a sliding-window rate limiter middleware" (`PR.md`, `rate_limit.py`, `test_rate_limit.py`).
- **Head SHA:** not provided.
- **Merge base SHA:** not provided.
- The code was supplied inline and I had no tools, so I could not freeze a commit, check out a worktree or run the tests. This review covers only the text shown above. Any commit that differs from it was not reviewed.

**TIER:** High. The change decides who is allowed to reach a production API and who gets refused. A wrong key here locks out legitimate users, so this is network exposure and access control, not ordinary code.
- High tier needs **two rounds, ideally on two vendors**. This report is **round 1 of 2 only**, so the PR is **not yet reviewed** under this skill.

**DATA (Step 3):** The code holds no secrets or personal data beyond opaque user IDs and IP addresses, both in memory. Reviewing it in this session raises no data-handling concern. An approved endpoint for round 2 still has to be chosen.

**REVIEWERS:**
- Reviewer: this session (Claude, claude-opus-5-5). It has no part in authoring the change.
- Author: unknown. No commit trailers were provided.

**FINDINGS:**

**1. P0: the limiter counts per IP address, not per user** (`rate_limit.py:12`, `key = request.remote_addr`)
- **Failure scenario:** The request says the count is per authenticated user and that users on the same office network must not limit each other. The code ignores `user_id` and counts by IP.
  - 30 users behind one office NAT share a single bucket of 100 requests per minute. Request 101 from anyone in the office returns `False` for everyone.
  - One heavy user, or an attacker on the same NAT, carrier-grade NAT or VPN egress, can lock out all the others.
  - If the app sits behind a reverse proxy or load balancer, `remote_addr` is the proxy's IP. Then every user in production shares one bucket, and the whole API allows 100 requests per minute in total, which is an outage.
  - A single user who switches IPs (mobile and wifi, IPv6 privacy addresses) gets a fresh 100 for each address.
- **Suggested test:** Use the same `remote_addr="10.0.0.1"` with `user_id="u1"` and `user_id="u2"`, and `limit=3`. Make 3 calls as u1, then assert that u2's first call returns `True`. This fails today. Also add the inverse: u1 on two different IPs exhausts one shared bucket.

**2. P1: the tests cannot tell an IP key from a user key, so "tests added and passing" proves nothing about the requirement** (`test_rate_limit.py:9`, `test_rate_limit.py:15`)
- **Failure scenario:** Both tests use one fixed request with the same `remote_addr` and the same `user_id`. Any keying scheme passes them, including the wrong one that shipped.
  - The PR's claim that tests were added and are passing is accurate. It is also irrelevant to the core requirement.
  - I could not run the tests myself.
- **Suggested test:** The isolation test from finding 1, plus an assertion that the key comes from `user_id`.

**3. P2: behavior when `user_id` is `None` is undefined** (`rate_limit.py:11`, the docstring allows `None`)
- **Failure scenario:** The request only covers authenticated users. Once the code is keyed on `user_id` (the fix for finding 1), every unauthenticated request would share one `None` bucket. Without that fix, they silently stay keyed by IP.
  - Either way, the policy for anonymous traffic is unstated, and it needs an owner decision: reject, key by IP, or skip limiting.
- **Suggested test:** Two requests with `user_id=None` from different IPs. Assert the behavior the owner chooses.

**4. P2: keys are never evicted, so memory grows without bound** (`rate_limit.py:9`, `rate_limit.py:15-19`)
- **Failure scenario:** `_hits` gains one entry per distinct key and never drops it. Expired timestamps are pruned only when that same key makes another request.
  - With IP keys, a scan from many source addresses (trivial with IPv6) grows the dict forever, until the process runs out of memory.
  - With user keys the growth is bounded by the number of users, but still never shrinks.
- **Suggested test:** Make 10,000 requests from distinct keys, advance the clock past the window, make one more request, and assert `len(rl._hits)` is small.

**5. P2: no locking, so concurrent requests can exceed the limit** (`rate_limit.py:14-20`)
- **Failure scenario:** On a threaded or async-with-threadpool server, two requests for the same key can both read 99 hits and both append. Each then writes back its own list, so one hit is lost. A burst under concurrency gets past 100.
- **Suggested test:** 50 threads × 10 calls against `limit=100`. Assert that exactly 100 calls return `True`. This is flaky today and deterministic once a lock is added.

**6. P2: the state lives in one process, so the effective limit is 100 × the number of workers** (`rate_limit.py:9`)
- **Failure scenario:** Under gunicorn or uwsgi with N workers, or with N replicas, each process keeps its own `_hits`. A user gets up to N × 100 requests per minute, which breaks the stated limit.
  - This is inferred: the deployment configuration was not provided.
- **Suggested test:** Two `RateLimiter` instances standing in for two workers, sharing the intended backing store. Assert a combined limit of 100. This needs a shared store such as Redis.

**7. P3: the window boundary at exactly 60 seconds is untested** (`test_rate_limit.py:20`)
- **Failure scenario:** The test jumps to `t=61`. Changing `now - t < self.window` to `<=` would go unnoticed, and an off-by-one at the boundary would ship.
- **Suggested test:** Hit at `t=0`, with `limit=1`. At `t=59.999`, assert `False`. At `t=60.0`, assert `True`.

**FILES NEEDED BUT NOT PROVIDED:**
- The middleware wiring: the PR calls this middleware, but no code registers it or turns a `False` into a 429 / `Retry-After` response.
- The request object, to confirm how `user_id` is set and whether authentication runs before the limiter.
- Proxy and load-balancer configuration, to know what `remote_addr` contains.
- Worker and replica configuration.
- CI results.
- Head and merge-base SHAs.
- Commit trailers.

---

**Close-out**

I am the reviewer, so I do not adjudicate my own findings. This section is for the author or whoever closes the PR.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending (P0, cannot be deferred) | |
| 2 | pending (P1, cannot be deferred) | |
| 3 | pending (needs an owner decision) | |
| 4–7 | pending | |

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION: do not merge.**
- Finding 1 is an open P0: the implementation does the opposite of the explicit requirement.
- Round 2 of 2, required for High tier, has not run.
- No SHAs were recorded and no CI checks were seen, so nothing is known to be green.
- An owner decision is pending on anonymous traffic (finding 3) and on whether the limit must hold across workers (finding 6).

```json
{
  "verdict": "do not merge",
  "findings": [
    {"severity": "P0", "evidence_level": "confirmed from code", "location": "rate_limit.py:12", "scenario": "Key is request.remote_addr, not user_id. Users behind one office NAT (or all users behind a reverse proxy) share one 100/min bucket and lock each other out, violating the explicit requirement. One user rotating IPs gets multiple buckets.", "fix": "Key on request.user_id for authenticated requests; add an isolation test with the same IP and different users."},
    {"severity": "P1", "evidence_level": "confirmed from code", "location": "test_rate_limit.py:9", "scenario": "Both tests use one fixed IP and user, so they pass whether the key is the IP or the user; 'tests passing' does not cover the per-user requirement.", "fix": "Add tests: same IP with different users are independent; same user on different IPs shares one bucket."},
    {"severity": "P2", "evidence_level": "confirmed from code", "location": "rate_limit.py:11", "scenario": "user_id may be None. Once keyed by user, all anonymous traffic shares one None bucket; the policy for unauthenticated requests is unspecified.", "fix": "Owner decides: reject, key anonymous traffic by IP, or exempt it; then test that choice."},
    {"severity": "P2", "evidence_level": "confirmed from code", "location": "rate_limit.py:9", "scenario": "_hits never evicts keys; many distinct keys (e.g. an IPv6 scan) grow memory without bound.", "fix": "Delete keys whose pruned list is empty, or sweep periodically, or use a TTL store."},
    {"severity": "P2", "evidence_level": "inferred (server model not shown)", "location": "rate_limit.py:14-20", "scenario": "Unlocked read-modify-write; concurrent requests for the same key can each see 99 hits and both pass, and appends can be lost.", "fix": "Guard allow() with a lock, per key or global."},
    {"severity": "P2", "evidence_level": "inferred (deployment not shown)", "location": "rate_limit.py:9", "scenario": "In-process state: with N workers or replicas, the effective limit is N x 100 per user.", "fix": "Use a shared store (e.g. Redis sorted set or atomic counter) if the limit must be global."},
    {"severity": "P3", "evidence_level": "confirmed from code", "location": "test_rate_limit.py:20", "scenario": "The window boundary at exactly 60 s is untested; changing < to <= would not be caught.", "fix": "Add assertions at t=59.999 (blocked) and t=60.0 (allowed)."}
  ]
}
```