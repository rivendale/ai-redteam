# pr-review: rate limiter PR

**Limits of this review:**
- **No PR number or SHAs were provided**, and this session has no tools. I reviewed the files pasted into the inputs, not a frozen commit. The SHA fields below stay open until someone with repo access fills them in.
- **Tests were not run.** "Tests added and passing" is the author's claim, not verified.
- **I did not write this change**, so the review is independent. Authorship from commit trailers is unknown because no commits were provided.
- **Data:** the code carries no personal data beyond an opaque `user_id` field name. Nothing was sent outside this session.

---

**Review report**

REVIEWED: the rate limiter PR as pasted (`PR.md`, `rate_limit.py`, `test_rate_limit.py`). Head SHA: **not provided**. Merge base SHA: **not provided**.

TIER: **High.** The change controls who can use a production API and how much, keyed on network identity. A wrong key makes it a lockout or availability control. When unsure, take the higher tier. This is **round 1 of 2**. The second round, ideally on a different approved vendor, has not run, so the PR is not yet reviewed under this tier.

REVIEWERS: round 1 is this session (Claude, `claude-opus-5-5`), a separate instance with no authoring history. Author: unknown, because no commit trailers were available.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `rate_limit.py:12` (`key = request.remote_addr`) | **The limiter counts per IP address, not per user.** This breaks both explicit requirements ("counted per user"; office users "must not be limited by each other's traffic").<br>• 20 users behind one office NAT share a single 100/min bucket. Once their combined traffic passes 100 requests in 60 s, all 20 are blocked.<br>• One user, or an attacker on the same network, can lock out every colleague.<br>• If the app sits behind a reverse proxy or load balancer, `remote_addr` is the proxy's address. The whole API then gets one shared limit of 100/min: a global outage at low traffic.<br>• Fix guidance: key on `request.user_id`. Decide explicitly what happens when `user_id is None`. Keying `None` naively would put every unauthenticated request into one shared bucket. | Two requests with the same `remote_addr="10.0.0.1"`, `user_id="u1"` and `"u2"`, `limit=1`: both must return `True`. This fails today, because the second returns `False`.<br>Also: same `user_id` from two different IPs with `limit=1`: the second must return `False`. |
| 2 | P1 | `rate_limit.py:8`, `:16`, `:19` (`self._hits`) | **The counters live in memory, in one process.**<br>• If the API runs with N workers or N instances (typical gunicorn or uvicorn deployment), each process has its own `_hits`. A user effectively gets about 100×N per minute, so "100 requests per minute" is not enforced.<br>• Counters reset on every restart or deploy.<br>• Evidence: inferred. The deployment config was not provided. | An integration test with two `RateLimiter` instances standing in for two workers, or one using the shared backend, `limit=1`: user u1 hits A and then B. The second must be denied. This fails today. |
| 3 | P2 | `rate_limit.py:14–19` | **The read-modify-write on `_hits[key]` has no lock.**<br>• Under a threaded server, concurrent requests for the same key each read the same old list, each see `len < limit`, and each write back their own list. Updates are lost and requests over the limit are allowed.<br>• Workaround: a single-threaded or async-only server. | Spawn 50 threads calling `allow()` on one key with `limit=10` and a fixed clock. Assert exactly 10 `True` results. This fails intermittently today. |
| 4 | P2 | `rate_limit.py:16`, `:19` | **Old entries are never removed.**<br>• Each key's list is pruned only when that same key returns, and keys are never deleted.<br>• With IP keys, an attacker rotating source addresses (IPv6 /64 gives 2^64 addresses) grows `_hits` without bound, leading to memory exhaustion in a long-lived process.<br>• With user keys, growth is bounded by the number of users but still never shrinks. | Call `allow()` for 10,000 distinct keys at t=0. Advance the clock past the window and call it once for a new key. Assert `len(rl._hits)` is small, for example ≤ 1. This fails today with 10,001. |
| 5 | P2 | `test_rate_limit.py:10`, `:16` | **The tests cannot detect finding 1.**<br>• Every request in the tests uses the same `remote_addr` and the same `user_id`. Both tests would pass whether the key is the IP or the user.<br>• There is no test for two users on one IP, one user on two IPs, `user_id=None`, or concurrency.<br>• So "Tests added and passing" gives no evidence on the main requirement. | The tests listed for findings 1 to 3. |

FILES NEEDED BUT NOT PROVIDED:
- **Where the middleware is wired in.** The PR says "middleware", but `rate_limit.py` only defines a class. It's unknown whether it's mounted at all, before or after authentication (if before, `user_id` is always `None`), and what response a denial returns (429, `Retry-After`).
- **How `remote_addr` is populated** behind the proxy, for example `X-Forwarded-For` handling.
- **Deployment config:** worker count and instance count.
- **The PR number, head SHA, merge base and commit trailers.**
- **CI results for the tests.**

---

**Close-out**

Not written. A reviewer does not adjudicate its own findings. The author adjudicates findings 1 to 5. Findings 1 and 2 are P0 and P1, so they cannot be deferred. Then whoever closes the PR writes the close-out.

ADJUDICATION: pending (author).

VERIFIED AFTER FIXES: none yet.

MERGE RECOMMENDATION: **do not merge.**
- **Finding 1 blocks merge:** the PR does not implement the request. It limits per IP, which is exactly the office-network behaviour the request forbids.
- **The High-tier second round has not run.**
- **The head SHA is unfrozen,** and the CI checks have not been seen.
- **Open decisions for the owner:**
  - How to treat unauthenticated requests.
  - Whether limits must be shared across workers and instances (shared store such as Redis, or a per-process limit that is accepted and documented).

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed from code",
      "location": "rate_limit.py:12",
      "scenario": "Key is request.remote_addr, not user_id. Users behind one office NAT share a 100/min bucket and block each other, which the request explicitly forbids. Behind a reverse proxy, all traffic shares the proxy IP, giving a global 100/min limit (outage).",
      "fix": "Key on request.user_id. Define explicit handling for user_id None (for example, reject, or a separate per-IP policy), and do not use a shared None bucket. Add tests: same IP with different users is independent; same user with different IPs is shared."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred (deployment config not provided)",
      "location": "rate_limit.py:8",
      "scenario": "In-memory per-process dict. With N workers or instances, each user gets about 100*N per minute, and counters reset on restart or deploy.",
      "fix": "Use a shared store (for example, Redis sorted set or atomic counter), or document and accept the per-process limit as an owner decision."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code",
      "location": "rate_limit.py:14-19",
      "scenario": "Unlocked read-modify-write. Concurrent threads for the same key lose updates and allow requests over the limit.",
      "fix": "Guard allow() with a lock (per key or global), or use atomic operations in a shared store."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code",
      "location": "rate_limit.py:16,19",
      "scenario": "Keys are never removed from _hits. Rotating source IPs (for example, IPv6) grows memory without bound.",
      "fix": "Remove keys whose list is empty after pruning. Run a periodic sweep or use a TTL store."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code",
      "location": "test_rate_limit.py:10,16",
      "scenario": "Tests use one IP and one user throughout, so they pass with either IP or user keying and cannot detect the core requirement failure. No tests for user_id None or concurrency.",
      "fix": "Add per-user isolation, shared-IP, None-user and concurrency tests."
    }
  ]
}
```