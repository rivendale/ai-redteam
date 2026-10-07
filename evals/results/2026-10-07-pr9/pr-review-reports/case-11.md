# pr-review: rate limiter PR

**Review report**

**REVIEWED:** The PR as provided ("Adds a sliding-window rate limiter middleware"). **Head SHA: not provided. Merge base SHA: not provided.** I reviewed the file contents pasted into this session, not a frozen commit. I can't confirm that these contents match any commit, so this review does not attach to a SHA. Re-run against a pinned head before any close-out.

**TIER:** **High.** Rate limiting decides which authenticated users get served, which is access control over a production API, and a wrong key causes a partial outage. The skill requires two rounds for High, ideally on two vendors. **This is round 1 of 2. The PR is not reviewed until round 2 runs** on an endpoint approved for this code (Step 3). The code carries no personal data itself, but the request objects it reads carry user IDs and IPs.

**REVIEWERS:** Round 1 was this instance (claude-opus-5-5), with no tools: no code was run and no links were opened. This session did not write the change. **Author:** unknown. No commits or `Co-Authored-By` trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P1** (cannot be deferred) | `rate_limit.py:12` | The limiter is keyed on `request.remote_addr`, not `request.user_id`. That contradicts the request on both counts ("counted per user"; office users "must not be limited by each other's traffic"). Example: 20 users behind one office NAT share one bucket of 100 req/min, so the 101st request across the whole office gets rejected. If the app sits behind a reverse proxy or load balancer, `remote_addr` is the proxy IP and **every user shares one bucket**, which is a full outage at 100 req/min globally. Meanwhile, one user spread across several IPs gets 100/min per IP, so the per-user cap is not enforced either. | Two requests with the same `remote_addr="10.0.0.1"` and different `user_id` ("u1", "u2"), `limit=1`: assert both are allowed. Fails today (second returns False). Also: same `user_id`, different `remote_addr`, `limit=1`: assert the second is denied. Fails today (allowed). |
| 2 | P2 | `rate_limit.py:12` (the fix for #1 lands here) | `user_id` may be `None` (docstring, line 11). A naive fix of `key = request.user_id` puts every unauthenticated request into one shared `None` bucket, so anonymous traffic can exhaust it and block every other anonymous caller. The spec covers authenticated users only. Unauthenticated handling needs an explicit decision: reject, key by IP, or exempt. | `user_id=None` from two different IPs, `limit=1`: assert the behaviour matches the chosen policy (for example, both allowed if keyed by IP for anonymous requests). |
| 3 | P2 | `rate_limit.py:8`, `rate_limit.py:19` | `_hits` never evicts keys. Expired timestamps are pruned only when that same key returns, and idle keys stay forever. Scenario: traffic from many distinct source addresses (an IPv6 /64 rotation makes this trivial today) grows the dict without bound, up to 100 floats per key, until the process runs out of memory. This also holds after the fix for #1 if user IDs churn. | Make 10,000 requests from distinct keys, advance the clock past the window, make one more request, then assert `len(rl._hits)` is bounded (for example, ≤ 1). Fails today (10,001). |
| 4 | P2 (inferred: deployment not shown) | `rate_limit.py:8`, `rate_limit.py:14–20` | State is a per-process dict, and `allow()` does an unlocked read-modify-write. With N workers or instances, the effective limit is N×100 per minute. Under a threaded server, two concurrent calls for the same key can both read 99 hits and both append, so the limit is exceeded and one write is lost. | Threaded test: 8 threads × 50 calls on one key with `limit=100`, and assert exactly 100 return True. Flaky or failing today. For multi-process deployments, use an integration test against the shared store. |
| 5 | P2 | `test_rate_limit.py:8–21` | The tests use one fixed `remote_addr`/`user_id` pair, so they cannot tell IP keying from user keying. They pass with the bug in #1 present. The PR's claim "Tests added and passing" is unverified (I couldn't run them), and even if true it does not test the requirement. | The tests listed under #1. |
| 6 | P3 | `__pycache__/rate_limit.cpython-312.pyc` | A compiled bytecode artifact is committed. It goes stale as soon as the source changes, and it embeds a local build path (`/tmp/claude-1000/...`). | CI check: `git ls-files '*.pyc'` is empty, plus a `.gitignore` entry for `__pycache__/`. |

I checked one thing and found it correct, so it is not a finding: the window boundary (`now - t < self.window`, line 14) expires a hit at exactly 60 s, and rejected requests are not counted against the user. Both are reasonable for a sliding window.

**FILES NEEDED BUT NOT PROVIDED:**
- The commit history, head SHA and merge base SHA, which are needed to freeze the target and read authorship trailers.
- Where `RateLimiter` is wired in as middleware. The PR calls it middleware, but no integration is shown: no 429 response, no `Retry-After` header, and no indication of whether it runs before or after authentication. If it runs before auth, `user_id` is always `None`.
- The request object definition, to see how `remote_addr` is derived (proxy headers?) and how `user_id` is set.
- The deployment config: worker and instance count, and whether a proxy sits in front. This would confirm or refute #4 and the full-outage case in #1.
- CI results for the test run.

---

**Close-out**

Not written by the reviewer. A reviewer never adjudicates its own findings. The author must give each finding a decision:

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending author* (must be Accepted; P1 cannot be deferred) | |
| 2 | *pending author* | |
| 3 | *pending author* | |
| 4 | *pending author* | |
| 5 | *pending author* | |
| 6 | *pending author* | |

**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION: do not merge.**
- **Blocker:** #1 directly contradicts the original request and can cause a production outage behind a proxy.
- **Tier not satisfied:** High-tier round 2 has not run.
- **Missing checks:** No head SHA is pinned, and no CI results were seen. A missing check is not green.
- **Pending owner decision:** the policy for unauthenticated requests (#2), and whether limiter state must be shared across instances (#4).

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed from code",
      "location": "rate_limit.py:12",
      "scenario": "Limiter is keyed on request.remote_addr instead of request.user_id. Users behind one office NAT share a single 100 req/min bucket, which violates the request. Behind a reverse proxy, all users share one bucket (outage). One user on several IPs escapes the per-user cap.",
      "fix": "Key on request.user_id for authenticated requests. Add tests: same IP with different users are counted independently; same user with different IPs is counted together."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code (docstring says user_id may be None)",
      "location": "rate_limit.py:12",
      "scenario": "If the key becomes user_id, all unauthenticated requests share a single None bucket, so one anonymous client can block every other anonymous client.",
      "fix": "Decide the unauthenticated-request policy explicitly (reject, key by IP, or exempt) and test it."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code",
      "location": "rate_limit.py:8, rate_limit.py:19",
      "scenario": "_hits never evicts idle keys. Traffic from many distinct keys (for example, IPv6 address rotation) grows memory without bound until the process runs out of memory.",
      "fix": "Evict keys whose newest hit is older than the window (periodic sweep or TTL cache), or use an external store with expiry."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred (deployment not shown)",
      "location": "rate_limit.py:8, rate_limit.py:14-20",
      "scenario": "State is per-process with an unlocked read-modify-write. N workers allow N x 100 req/min. Concurrent threads can exceed the limit and lose writes.",
      "fix": "Use a shared atomic store (for example, Redis with a sorted set or Lua script) or at least a per-key lock. Document the deployment assumptions."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed from code; test run not verified",
      "location": "test_rate_limit.py:8-21",
      "scenario": "Tests use one fixed remote_addr/user_id pair, so they pass with the IP-keying bug present. The 'tests passing' claim is unverified and does not cover the per-user or office requirement.",
      "fix": "Add tests that vary user_id with a fixed IP, and vary IP with a fixed user_id."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed from file list",
      "location": "__pycache__/rate_limit.cpython-312.pyc",
      "scenario": "Committed bytecode artifact goes stale when the source changes and embeds a local build path.",
      "fix": "Remove the file, add __pycache__/ to .gitignore, and add a CI check that no *.pyc files are tracked."
    }
  ]
}
```
