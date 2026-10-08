VERDICT: **REWORK.** The limiter counts requests per IP address, not per user, so users behind the same office network share one 100/min budget. That is the exact behavior the request forbids.

CONFIDENCE: **medium.** The core finding is certain from the code itself. Confidence is limited because this session has no tools (nothing was run), I could not see the rest of the repository, and this is a single reviewer with no fresh subagent. The work was not written in this conversation, so the anchoring risk is lower, but for production stakes, re-run it in a fresh session with tools.

**INPUTS LEDGER**
- **Seen:**
  - `request.md` (original request, verbatim)
  - `context.md` (stakes: production; author's PR description)
  - `PR.md`
  - `rate_limit.py`
  - `test_rate_limit.py`
- **Not seen:**
  - **App or middleware registration code.** This matters: nothing shown calls `RateLimiter.allow` or returns a 429.
  - **Deployment topology (workers, processes, instances).** This matters because the state is in-process.
  - **Auth layer.** This matters because it decides whether `user_id` is populated before the limiter runs.
  - **CI output for "tests passing".** This matters little: tracing shows both tests would pass, and that is itself the problem.

**COVERAGE**
- **Checked:**
  - `rate_limit.py` (`RateLimiter.__init__`, `RateLimiter.allow`)
  - `test_rate_limit.py` (both tests)
  - `PR.md` claims ("sliding-window", "100 per 60 seconds", "tests added and passing")
  - The request's two requirements (per-user counting; no cross-user limiting on a shared network)
- **Not checked:**
  - App wiring
  - Deployment config
  - Auth middleware ordering

**SEATS AND GATE:** One reviewer only, this session, with no subagent or tools. No cross-vendor seats were run because none were requested and none were available. Sensitivity gate passed: the work contains no personal data, credentials or confidential material.

## Pass 1: Reconstruct

The PR claims to add a sliding-window limiter allowing 100 requests per 60 seconds, with passing tests. For it to satisfy the request, three things must be true:
- The counting key must be the authenticated user's identity.
- Two users sharing an IP must have independent budgets.
- The limiter must actually be applied to API requests.

Load-bearing assumptions:
- `user_id` is populated before `allow()` runs.
- The service runs in a single process (or shared state is acceptable).
- Unauthenticated traffic is handled elsewhere.

Tracks: **B** (code), with **A** (requirement fit).

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B/A | `rate_limit.py`, `allow`: `key = request.remote_addr` | The bucket key is the client IP. `user_id` is documented in the docstring but never used. This drifts directly from "counted per user" and "must not be limited by each other's traffic". | An office of 20 users behind one NAT IP: after their combined 100th request in a minute, every one of them gets refused, including a user who sent one request. A single user on two networks also gets 2× the budget. | Key on `request.user_id`. Decide explicitly what happens when it is `None` (see S1). **Repro:** `rl = RateLimiter(limit=1)`; `rl.allow(NS(remote_addr="10.0.0.1", user_id="u1"))` → True; `rl.allow(NS(remote_addr="10.0.0.1", user_id="u2"))` → expected True, observed **False**. | a✔ b✔ c✔ d✔ |
| F2 | **High** | CONFIRMED | B | `test_rate_limit.py`, both tests | Each test uses a single request object with the same IP and the same user, so neither test can tell per-IP keying from per-user keying. The suite passes on the buggy code and would also pass after the fix. It guards neither requirement in the request. "Tests added and passing" is true and proves nothing. | A future refactor reintroduces IP keying (or the fix in F1 is never made), and CI stays green. | Add (1) a test where two users on the same IP each get a full independent budget, and (2) a test where one user on two IPs shares one budget. **Mutation check:** both new tests must go red against the current `key = request.remote_addr`. | a✔ b✔ c✘ d✔ |
| F3 | Medium | PROBABLE | B | `rate_limit.py`, `self._hits` / `allow` | The read-modify-write on `self._hits[key]` is not locked. Under a threaded server, concurrent requests for the same key can each read the same list and overwrite each other's append. | Under burst concurrency, a user exceeds 100/min because writes are lost and some hits are never recorded. | Guard `allow` with a `threading.Lock` (or per-key locks), or move to an atomic store (Redis `INCR` / sorted-set with `MULTI`). **Repro:** 200 threads calling `allow` on one key with `limit=100` and a frozen clock; expect exactly 100 True, and you may observe more. | a✔ b✘ c✘ d✘ |
| F4 | Medium | PROBABLE | B | `rate_limit.py`, `self._hits` | Keys are never evicted. A key whose traffic stops keeps its entry forever, and its list is only pruned when that same key is seen again. | Memory grows with the number of distinct keys ever seen. With IP keying, any client rotating source addresses inflates it without bound. It persists with user keying too, more slowly. | Periodically drop keys whose newest hit is older than `window`, or use a store with TTL. **Repro:** call `allow` for 1M distinct keys, advance the clock past the window, and observe that `len(rl._hits)` is still 1M. | a✔ b✘ c✘ d✘ |

## Needs validation

These have no severity and do not set the verdict.

- **S1, unauthenticated requests** (`allow`, `user_id: str or None`). Once keyed on `user_id`, every `None` request would share one global bucket.
  - **Settles it:** whether unauthenticated requests can reach this limiter, and what the intended policy for them is. Options include rejecting them, falling back to IP keying, or exempting them.
- **S2, multi-process or multi-instance deployment.** State lives in one Python process, so N workers or instances would give each user about N×100 per minute.
  - **Settles it:** the production worker and instance count, and whether a shared store is required.
- **S3, wiring.** `PR.md` says "middleware", but the diff contains only a class with `allow()`. There is no registration, no 429 response and no `Retry-After` header.
  - **Settles it:** whether another file in the PR or repo calls `RateLimiter.allow` on API routes and what it returns when the call yields False.

## Refuted

- **C1, window boundary off-by-one.** The check `now - t < self.window` expires a hit at exactly 60 s, which is a correct sliding-window log. `test_window_expires` at t=61 is consistent with that.
- **C2, wall-clock skew.** The clock is `time.monotonic`, so NTP jumps cannot reset or extend windows.

## What holds up

- The sliding-window log algorithm itself is correct: it prunes old hits, refuses at `>= limit`, and does not record refused requests.
- The injectable clock makes the tests deterministic.
- The defaults match the request's numbers (100 per 60 s).

## Unverified claims

- **"Tests added and passing."** I did not run the tests. By tracing, both would pass. Confirm by running `python -m unittest test_rate_limit`.
- **"Middleware."** Nothing in the diff shows the class wired in as middleware. Confirm by locating where it is registered (S3).

## Questions for the author

1. What should happen to requests without a `user_id`?
2. How many worker processes or instances serve the API in production?
3. Where is `RateLimiter` registered, and what response does a refused request get?

## Decision-maker summary

Do not merge. The limiter counts by IP address instead of by user, which breaks the request's central requirement, and the tests cannot detect it. If shipped, whole offices will be locked out together during normal use.

## Owner summary

The new rate limit counts traffic by network address instead of by person, so everyone in the same office shares one small allowance and will be blocked together. The tests that came with it don't check for this, so they pass anyway. It needs to be changed to count each person separately, with tests that prove it, before release.

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
    {"item": "app/middleware registration code", "status": "not_seen", "matters": true},
    {"item": "deployment topology (workers/instances)", "status": "not_seen", "matters": true},
    {"item": "auth layer ordering", "status": "not_seen", "matters": true},
    {"item": "CI test output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "PR.md", "kind": "file"},
      {"unit": "rate_limit.py", "kind": "file"},
      {"unit": "rate_limit.py:RateLimiter.__init__", "kind": "function"},
      {"unit": "rate_limit.py:RateLimiter.allow", "kind": "function"},
      {"unit": "test_rate_limit.py", "kind": "file"},
      {"unit": "test_rate_limit.py:test_blocks_after_limit", "kind": "function"},
      {"unit": "test_rate_limit.py:test_window_expires", "kind": "function"},
      {"unit": "PR claim: tests added and passing", "kind": "claim"},
      {"unit": "Request: counted per user; shared network not cross-limited", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "app/middleware registration", "reason": "not supplied"},
      {"unit": "deployment config", "reason": "not supplied"},
      {"unit": "auth middleware ordering", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "rate_limit.py:RateLimiter.allow (key = request.remote_addr)",
     "scenario": "Users behind one office NAT IP share a single 100/min bucket; once their combined traffic hits 100 in a minute, all of them are refused, which the request explicitly forbids.",
     "fix": "Key the bucket on request.user_id and define handling for user_id None.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "rl=RateLimiter(limit=1); rl.allow(NS(remote_addr='10.0.0.1', user_id='u1')) -> True; rl.allow(NS(remote_addr='10.0.0.1', user_id='u2')) expected True, observed False."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_rate_limit.py:test_blocks_after_limit, test_window_expires",
     "scenario": "Both tests use one IP and one user, so they pass whether keying is per-IP or per-user; the F1 defect ships with green CI and any regression stays undetected.",
     "fix": "Add tests: two users on one IP each get a full budget; one user on two IPs shares one budget.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run the proposed two-users-same-IP test against current code; expect it to fail (second user refused)."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rate_limit.py:RateLimiter.allow (_hits read-modify-write)",
     "scenario": "Under a threaded server, concurrent requests for one key read the same list and overwrite each other's appends, letting a user exceed the limit.",
     "fix": "Protect allow() with a lock or use an atomic shared store.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "200 threads call allow() on one key with limit=100 and a frozen clock; expect exactly 100 True, may observe more."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "rate_limit.py:RateLimiter._hits",
     "scenario": "Keys are never evicted, so memory grows with every distinct key ever seen; rotating source IPs grows it without bound.",
     "fix": "Evict keys whose newest hit is older than the window, or use a TTL store.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Call allow() for 1M distinct keys, advance clock past window, observe len(rl._hits) remains 1M."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "rate_limit.py:RateLimiter.allow",
     "suspicion": "Once keyed on user_id, all unauthenticated (None) requests would share one global bucket.",
     "unresolved_fact": "Whether unauthenticated requests reach this limiter and what policy is intended for them."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "rate_limit.py:RateLimiter._hits",
     "suspicion": "In-process state gives each user N x 100/min across N workers or instances.",
     "unresolved_fact": "Production worker/instance count and whether a shared store is required."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "PR.md ('middleware')",
     "suspicion": "No code in the diff registers the limiter or returns 429 on refusal.",
     "unresolved_fact": "Whether another file calls RateLimiter.allow on API routes and what it returns on False."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Window boundary off-by-one.", "evidence": "now - t < self.window expires a hit at exactly 60 s, correct for a sliding-window log."},
    {"id": "C2", "candidate": "Wall-clock skew resets windows.", "evidence": "Default clock is time.monotonic."}
  ]
}
```