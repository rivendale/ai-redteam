# pr-review: rate limiter PR

## Review report

**REVIEWED:** The rate-limiter PR described in `PR.md`. **Head SHA and merge base SHA are not available.** I got the files inline, with no repository, PR number or commit. I can't freeze the target (Step 1), so this report covers only the three files shown above. Any SHA later attached to this review has to be checked against these file contents.

**TIER: High.** The change decides who gets cut off from a production API. The key choice (IP or user) determines whether one party's traffic can lock out others, which is access control and network exposure. Step 2 says to take the higher tier when unsure. **This is round 1 of 2.** The PR is not reviewed until a second independent round has run, ideally on a different vendor.

**REVIEWERS:** Claude Opus 5.5 (`claude-opus-5-5`), a fresh session with no part in writing the change. **Author unknown:** no commit or `Co-Authored-By` trailers were provided.

**DATA (Step 3):** No code was sent anywhere beyond this session. The diff holds no secrets or personal data.

**METHOD:** Static reading only. I had no tools, so I could not run the test suite. The PR's "Tests added and passing" claim is unverified.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P1** (confirmed from code) | `rate_limit.py:12` `key = request.remote_addr` | The limiter counts per client IP, not per user. That reverses the core requirement. Example: 30 users in one office share a NAT address. Together they make 100 requests in a minute, and from then on every user in that office gets `False` (blocked), including users who have sent nothing. This is exactly the case the request says must not happen. The reverse also holds: one user spreading requests across several IPs (phone plus laptop, or rotating proxies) gets 100/min per IP. | Make two requests with the same `remote_addr="10.0.0.1"` and different `user_id`s (`"u1"`, `"u2"`), with `limit=3`. Send 3 as u1, then assert u2's first request is allowed. This fails today. Add a second test: same `user_id`, different `remote_addr`s, assert the 4th request is blocked. |
| 2 | **P0** (conditional on deployment; inferred) | `rate_limit.py:12` | Production APIs usually sit behind a load balancer or reverse proxy. If this one does, `remote_addr` is the proxy's address for every request. All users then share a single bucket, and the whole API stops serving after 100 requests per minute in total. That is an outage. The fix for #1 removes this too, but the deployment topology needs confirming so the fix does not move to `X-Forwarded-For` instead. That header is client-spoofable and is still not per-user. | Same as #1. Also add a test where all requests share one `remote_addr` and use 101 distinct `user_id`s: assert all 101 are allowed. |
| 3 | **P2** (confirmed from code; impact inferred) | `rate_limit.py:9` `self._hits = {}`, together with lines 14-19 | Keys are never evicted. A key's list is pruned only when that same key comes back. With IP keys, an attacker cycling through source addresses (an IPv6 /64 gives effectively unlimited addresses) creates one dict entry per address. The entries are never freed, memory grows without bound, and the worker can run out of memory. Per-user keys bound the growth by user count, but stale users still accumulate. | Use a fake clock. Call `allow` with 10,000 distinct keys, advance the clock past `window`, make one more call, and assert `len(rl._hits)` is bounded (for example, ≤ 1 after a sweep). |
| 4 | **P2** (inferred; deployment not seen) | `rate_limit.py:9`, `14-19` | State lives in memory in a single process. Under N worker processes or replicas, each keeps its own counts, so the real limit is about N×100 per minute, and which worker handles a request changes the result. Under a threaded server, the read-filter-append-write sequence in `allow` has no lock. Concurrent requests for the same key can each read 99 hits and all be allowed, or overwrite each other's appends. | Run two `RateLimiter` instances, standing in for two workers, and assert they share counts. That needs a shared store such as Redis or an injected backend. For the threading issue, fire `limit*2` concurrent `allow` calls for one key and assert exactly `limit` return `True`. |
| 5 | **P2** (confirmed from code) | `test_rate_limit.py:9`, `:15` | Both tests use one `remote_addr` and one `user_id`, so they pass whether the key is the IP or the user. The suite cannot detect finding #1, which is why "tests added and passing" did not catch the requirement being reversed. | The tests from #1. They fail against the current `key = request.remote_addr` and pass once the key is `user_id`. |

**Fix direction for #1 and #2**, for the author to decide: key on `request.user_id`. The request only covers authenticated users, so the PR should state what happens when `user_id is None`. It must not silently put every anonymous request into one shared `None` bucket. Options are rejecting the request, skipping the limiter, or applying a separate IP-based policy. The middleware must also run **after** authentication, or `user_id` will always be `None`.

### FILES NEEDED BUT NOT PROVIDED

- The PR number, head SHA and merge base SHA.
- The middleware registration and ordering: where `allow()` is called, what the caller does with `False` (status code, `Retry-After` header), and whether it runs after auth populates `user_id`.
- The deployment config: worker or process count, replicas, and whether a proxy or load balancer sits in front. This decides #2 and #4.
- The commit trailers, to identify the author.
- CI results for this head. Without them, the passing-tests claim stays unverified.

---

## Close-out

Not written. Under the skill, the reviewer does not adjudicate its own findings. The author must give each finding a decision: Accepted with fix commit and regression test, Deferred (#3, #4 and #5 only, with an issue link), or Rejected with evidence. **#1 and #2 cannot be deferred.**

**ADJUDICATION:** pending, author to complete.
**VERIFIED AFTER FIXES:** nothing yet.

**MERGE RECOMMENDATION: do not merge.**
- #1 (P1) is open, and it is a direct violation of the stated requirement.
- #2 is a potential P0 outage, pending confirmation of the deployment topology.
- The High tier needs a second independent round, which has not run.
- No SHA is frozen, CI is unseen, and the passing-tests claim is unverified.
- An owner decision is pending on unauthenticated traffic and on multi-worker shared state.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed_by_code_reading",
      "location": "rate_limit.py:12",
      "scenario": "Limiter keys on request.remote_addr instead of user_id. Users sharing an office NAT IP share one 100/min bucket, so one user's traffic blocks colleagues, which the request explicitly forbids. Conversely, one user on multiple IPs gets 100/min per IP.",
      "fix": "Key on request.user_id; define explicit handling for user_id None; ensure the middleware runs after authentication. Add a test with the same remote_addr and different user_ids asserting independent limits."
    },
    {
      "severity": "P0",
      "evidence_level": "inferred_conditional_on_deployment",
      "location": "rate_limit.py:12",
      "scenario": "Behind a reverse proxy or load balancer, remote_addr is the proxy IP for all requests, so the entire API is capped at 100 requests/minute total: a production outage.",
      "fix": "Same as the per-user keying fix; do not switch to X-Forwarded-For (spoofable, not per-user). Add a test with one remote_addr and 101 distinct user_ids, all allowed."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_by_code_reading",
      "location": "rate_limit.py:9",
      "scenario": "The _hits dict never evicts keys; a key's list is pruned only on its next request. Rotating source IPs (e.g. an IPv6 range) grows memory without bound, risking worker OOM.",
      "fix": "Evict keys whose newest hit is older than the window (periodic sweep or TTL store). Test: 10,000 distinct keys, advance the clock past the window, assert the dict size is bounded."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred_deployment_not_seen",
      "location": "rate_limit.py:9,14-19",
      "scenario": "Per-process in-memory state: with N workers or replicas the effective limit is about N*100/min. Under threaded servers, the unlocked read-modify-write in allow() lets concurrent requests exceed the limit or lose hits.",
      "fix": "Use a shared atomic store (e.g. Redis with sliding-window script) or at minimum a lock plus a documented single-process constraint. Concurrency test asserting exactly `limit` allows."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_by_code_reading",
      "location": "test_rate_limit.py:9",
      "scenario": "Tests use a single remote_addr and a single user_id, so they pass under IP keying and user keying alike. The suite cannot detect the requirement violation in finding 1; the 'tests passing' claim provides no evidence for per-user behavior.",
      "fix": "Add tests that vary remote_addr and user_id independently (shared IP with different users stays independent; same user across IPs shares a limit)."
    }
  ]
}
```