# pr-review: Rate limiter PR

**Review report**

**REVIEWED:** The rate-limiting PR ("Adds a sliding-window rate limiter middleware"). **No head SHA or merge base SHA was provided**, and I have no tools to read them. This review covers only the file contents shown in the inputs. If the PR's head differs from these contents, this is not a review of that head.

**TIER:** **High.** The change decides which authenticated users are refused service, which is a permissions and network-exposure control. A wrong key means one user can deny service to others. Production stakes were stated. High requires two rounds, ideally on two vendors. **This is round 1 of 2. The PR is not reviewed until round 2 runs.**

**REVIEWERS:** One fresh instance (claude-opus-5-5) that did not write the change. Author: unknown, because no commit trailers were provided. Data handling: the code was reviewed in this session only and nothing was sent elsewhere.

**Evidence limits:** I could not run code. "Tests added and passing" is an unverified claim. Findings marked *code-read* follow directly from the source. Findings marked *inferred* depend on deployment details I was not given.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `rate_limit.py:12` | `key = request.remote_addr` counts requests per IP, not per user, which contradicts the request ("counted per user… users behind the same office network must not be limited by each other's traffic"). Two users u1 and u2 behind one NAT at 10.0.0.1 share a single bucket. u1 sending 100 requests in a minute blocks u2 entirely, so one user causes an outage for the whole office. If the API sits behind a reverse proxy or load balancer, `remote_addr` is the proxy's IP. All users worldwide then share one 100/min bucket, and the API is down for everyone after 100 total requests per minute. The proxy case is *inferred*; the NAT case is *code-read*. | `rl=RateLimiter(limit=1)`. `a=NS(remote_addr="10.0.0.1", user_id="u1")`, `b=NS(remote_addr="10.0.0.1", user_id="u2")`. Assert `allow(a)` is True and `allow(b)` is True. This fails today. Also add the converse: the same `user_id` from two IPs shares one bucket. |
| 2 | P1 | `test_rate_limit.py:9`, `:15` | Both tests use the same `remote_addr` *and* the same `user_id`, so they pass whether the key is the IP or the user. The PR's "tests added and passing" therefore gives no evidence for the core requirement, and that gap is how finding 1 shipped. *Code-read.* | The two-users-one-IP test from finding 1, plus the one-user-two-IPs test. |
| 3 | P1 | `rate_limit.py:8`, `:16-19` | State is an in-process dict. Under a multi-worker server (gunicorn with N workers) or multiple replicas, each process keeps its own count, so a user gets up to N×100 requests per minute instead of 100. The "100 requests per minute" requirement is not met. *Inferred*: it depends on the deployment topology, which was not provided. | An integration test with two `RateLimiter` instances standing in for two workers sharing a backing store, asserting the 101st request across both is refused. Alternatively, document a single-process deployment as a requirement and assert it at startup. |
| 4 | P2 | `rate_limit.py:14-19` | `allow()` does an unsynchronised read, then filter, then write on `self._hits`. Under a threaded server, concurrent requests for the same key read the same list, and each appends to its own copy. Hits are lost and the limit is exceeded. *Code-read*, though the impact depends on the server using threads. | Run 200 threads calling `allow()` for one key with `limit=100` and a frozen clock. Assert exactly 100 return True. This fails intermittently today. |
| 5 | P2 | `rate_limit.py:8`, `:16`, `:19` | Keys are never evicted. Every distinct key ever seen keeps an entry, even after its window expires. With many clients (or, after the fix, many users) memory grows without bound over the life of the process. *Code-read.* | Call `allow()` for 10,000 distinct keys, advance the clock past the window, make one more call, and assert `len(rl._hits)` is small. This fails today. |
| 6 | P2 | `rate_limit.py:11-12` (after fix) | The docstring allows `user_id` to be `None`. A naive fix of `key = request.user_id` puts every unauthenticated request into a single shared `None` bucket, and anonymous traffic then throttles itself globally. The request covers only authenticated users, so the behaviour for `None` is an open owner decision: fall back to IP, reject, or exempt. *Code-read.* | Two requests with `user_id=None` from different IPs, `limit=1`. Assert whatever behaviour the owner chooses. |

**FILES NEEDED BUT NOT PROVIDED:** the middleware wiring (where `allow()` is called and what response a refused request gets, which should be 429 with `Retry-After`); the server and deployment config (worker count, replicas, proxy, and how `remote_addr` is derived, which matters for findings 1 and 3); the authentication layer (to confirm `user_id` is set before the limiter runs); CI results for the claimed passing tests; and the PR head and merge-base SHAs.

---

**Close-out**

**ADJUDICATION:** Pending. The author has not adjudicated these findings, and a reviewer does not adjudicate its own findings.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–6 | Awaiting author | — |

**VERIFIED AFTER FIXES:** None. There have been no fixes yet.

**MERGE RECOMMENDATION:** **Do not merge.**
- P0 finding 1 is open: the limiter keys on IP, which violates the explicit requirement and can lock out whole offices or every user behind a proxy.
- The High tier's second round has not run.
- The head and merge-base SHAs are unrecorded.
- No CI evidence was provided.
- An owner decision is pending on unauthenticated traffic (finding 6) and on whether multi-process enforcement is required (finding 3).

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code-read (NAT case); inferred (reverse-proxy case)",
      "location": "rate_limit.py:12",
      "scenario": "Key is request.remote_addr, not user_id. Users u1 and u2 behind the same office IP share one 100/min bucket, so one user blocks the whole office, directly violating the request. Behind a reverse proxy, every user shares the proxy IP's bucket, causing an API-wide outage after 100 requests per minute.",
      "fix": "Key on request.user_id for authenticated requests; add tests for two users on one IP (independent) and one user on two IPs (shared)."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read",
      "location": "test_rate_limit.py:9",
      "scenario": "Both tests use identical remote_addr and user_id, so they pass regardless of whether the limiter keys by IP or by user; the 'tests passing' claim gives no evidence for the per-user requirement.",
      "fix": "Add tests with same IP and different user_ids, and same user_id and different IPs."
    },
    {
      "severity": "P1",
      "evidence_level": "inferred (depends on deployment topology)",
      "location": "rate_limit.py:8",
      "scenario": "In-process dict state: with N workers or replicas each keeps its own count, so a user gets up to N*100 requests/min, violating the 100/min requirement.",
      "fix": "Use a shared store (e.g. Redis with atomic sliding-window ops) or document and enforce single-process deployment."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "rate_limit.py:14-19",
      "scenario": "Unsynchronised read-filter-write on self._hits; concurrent threads for the same key lose hits and exceed the limit.",
      "fix": "Guard allow() with a lock (or use an atomic store operation); add a 200-thread test asserting exactly 100 allowed."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "rate_limit.py:19",
      "scenario": "Keys are never evicted; _hits grows without bound with the number of distinct clients over the process lifetime.",
      "fix": "Delete keys whose filtered hit list is empty, or periodically sweep expired keys; test that dict size shrinks after the window passes."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read",
      "location": "rate_limit.py:11-12",
      "scenario": "user_id may be None; a naive per-user fix puts all unauthenticated traffic in one shared None bucket, throttling anonymous users globally. Behaviour for unauthenticated requests is unspecified and needs an owner decision.",
      "fix": "Owner decides: fall back to IP, reject, or exempt; implement explicitly and test with two None-user requests from different IPs."
    }
  ]
}
```