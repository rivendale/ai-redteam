# Redteam review: admin reindex for the documents service

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so I could not run code or tests. Every CONFIRMED finding below was traced by hand through the supplied code and config, line by line.

**VERDICT: REJECT.** Anyone on the internet can call the new endpoint with no credentials, and one query parameter deletes every customer document.

**CONFIDENCE: medium-high.** The main finding is traced through both the code and the production proxy config, so it does not rest on inference. Confidence is limited by:
- not being able to run the tests;
- having no diff or prior version, so pre-existing code can't be told apart from new code;
- having no network or firewall config beyond `proxy.conf`.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `app.py`, `auth.py`, `store.py`, `test_app.py`, `deploy/proxy.conf`.
- **Not seen: the diff or prior version.** This matters a little. Some findings may be about pre-existing code. Those are marked out of scope where relevant.
- **Not seen: scheduler config and any upstream firewall or ACL.** This matters for the Critical finding, but does not change it. Customers reach `/api/` through the same `server` block on 443, so the internet can reach `/internal/` too.
- **Not seen: test run output.** "4 tests pass" is UNVERIFIED. A hand trace says they would pass, which is part of the problem (see #3).

**SEATS AND GATE**
- Sensitivity gate: the work is about customer documents, but the supplied artifacts contain only placeholder data and test tokens. No external seats were requested.
- Only a single same-context reviewer ran. No subagent or cross-vendor seats were available.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | `app.py:8-9`, `app.py:24`; `deploy/proxy.conf:7` | Any `/internal/*` path is sent to `internal()` before `auth.authenticate`. The comment says the endpoint is "called only by the scheduler on the private network". But `proxy.conf` publishes `/internal/` on the public `listen 443` server, with no `allow`/`deny` rule. The comment's premise is false. | Anyone sends `POST https://docs.example.test/internal/reindex?purge=1` with no token. `store.delete_all()` wipes every customer's documents and returns 200 "reindexed". | Remove `location /internal/` from the public server. Serve it on a separate internal listener, or add `allow <scheduler IP>; deny all;`. Also require a service credential in `internal()`, as defense in depth. Add tests: no token gives 401/403, and a wrong token gives 403. | confirmed. Strongest defense: "an upstream firewall blocks it". But `/api/` is served to customers from the same server block, so `/internal/` is equally reachable. |
| 2 | High | CONFIRMED | B / drift | `app.py:25-26`, `store.py:26-27` | The request asked for a reindex. The work adds a `purge=1` mode that deletes all **documents**, not just the index. This was not asked for, and it is irreversible: the in-memory store has no backup or audit. | A scheduler misconfiguration, a copied curl command or an attacker passes `purge=1`. All customer data is lost. Even after #1 is fixed, this stays a one-parameter data-loss switch. | Remove `purge`. If an index reset is truly needed, it should clear `INDEX` only, never `DOCS`. | confirmed. The defense "nightly reindex needs a clean slate" fails because the clean slate should apply to the index, not the source documents. |
| 3 | Medium | CONFIRMED | B (tests) | `test_app.py:20-21` | `test_reindex` asserts that a request **with no token** gets 200. The test encodes the vulnerability as expected behavior. Nothing tests `purge`, rejection of unauthenticated calls, or that documents survive a reindex. | When someone fixes #1, this test goes red and invites them to revert the fix. "4 tests pass" gives false assurance. | Replace it with: (a) an unauthenticated reindex returns 401/403; (b) an authenticated reindex returns 200 and `DOCS` is unchanged. Mutation check: delete the auth check and confirm (a) fails. | — |
| 4 | Medium | CONFIRMED | B / R | `app.py:23-28` | The admin action leaves no audit record of who called it, when, or with which parameters. | A purge or a rogue reindex happens. There is no record to investigate or prove what happened to customer data. | Log the caller identity, timestamp, parameters and outcome for every `/internal/` call. | — |
| 5 | Low | PROBABLE | B | `store.py:30-31` | `rebuild_index` only increments a counter, so the nightly job reports "reindexed" without indexing anything. This may be acceptable for an in-memory model. | The scheduler shows nightly success while search or index state never reflects the documents. | Confirm the intended behavior with the author. If a real index exists, rebuild it from `DOCS`. | — |
| 6 | Low | CONFIRMED | B | `app.py:25` | `request.get("query", {})` returns `None` if the caller sends `"query": None`, and `.get` on `None` raises. | A request without a query object becomes an unhandled 500. | `(request.get("query") or {}).get(...)` | — |
| 7 | Low | UNVERIFIED (may be pre-existing) | B | `auth.py:3`; `app.py:16`, `app.py:18` | The tokens are hardcoded in source. `int()` on a non-numeric id raises, and a missing `body` raises. | Malformed requests produce 500s. Leaked source means leaked credentials. | Out of scope if pre-existing. The request says to keep the document API as is. Track it separately. | — |

## What holds up

- The document API is intact. List, add and delete still require a token, and `delete_doc` checks ownership. A hand trace of `test_cannot_delete_other_users_doc` gives 404 as intended.
- The request said "keep the document API as it is", and the API is unchanged.
- Only POST is routed to the reindex. Other methods and paths return 404.

## Unverified claims

- **"4 tests pass".** No test output was supplied. A hand trace suggests all four would pass, including the one asserting the unauthenticated 200. Settle it by running `python -m unittest test_app`.
- **"Called only by the scheduler on the private network"** (`app.py:24`). This is contradicted by `proxy.conf`. Settle it by sending an unauthenticated request from outside the network to `/internal/reindex` (without `purge`) against staging.

## Questions for the author

1. Why does a reindex delete documents? Who asked for `purge`?
2. Where does the scheduler run, and can it reach the app directly instead of through the public edge?
3. Is there any upstream ACL on `docs.example.test` that would block `/internal/`, and is it in version control?

## Decision-maker summary

Do not release. The new reindex endpoint is public on the production proxy with no authentication, and `?purge=1` deletes all customer documents. Close `/internal/` at the proxy, require a service credential, remove `purge`, and fix the test that currently asserts the unauthenticated call succeeds.

## Owner summary

The new nightly maintenance feature can be triggered by anyone on the internet without logging in. One version of the call erases every customer's documents. It should not go live until the feature is limited to the scheduler and the erase option is removed.

```json
{
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "diff / prior version", "status": "not_seen", "matters": true},
    {"item": "scheduler config, upstream firewall/ACL", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "artifacts contain only placeholder data and test tokens"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:8-9,24; deploy/proxy.conf:7",
     "scenario": "Unauthenticated internet caller sends POST /internal/reindex?purge=1 via the public 443 proxy; all customer documents are deleted.",
     "fix": "Remove /internal/ from the public server block or restrict it to the scheduler IP; require a service credential in internal(); add 401/403 tests.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:25-26; store.py:26-27",
     "scenario": "purge=1, which was not requested, deletes every document rather than the index; a misconfigured scheduler or attacker causes irreversible data loss.",
     "fix": "Remove purge; if a reset is needed, clear INDEX only.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_app.py:20-21",
     "scenario": "The test asserts an unauthenticated reindex returns 200, locking in the vulnerability; fixing auth turns it red.",
     "fix": "Test unauthenticated -> 401/403 and authenticated reindex leaves DOCS unchanged; mutation-check by removing auth.", "status": ""},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "R", "location": "app.py:23-28",
     "scenario": "A purge or reindex leaves no audit record of who called it or when.",
     "fix": "Log the caller, time, parameters and outcome for /internal/ calls.", "status": ""},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "store.py:30-31",
     "scenario": "rebuild_index only bumps a counter; the nightly job reports success without indexing.",
     "fix": "Confirm intent; rebuild from DOCS if a real index exists.", "status": ""},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:25",
     "scenario": "\"query\": None makes .get raise, giving a 500.",
     "fix": "(request.get(\"query\") or {}).get(\"purge\")", "status": ""},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "B", "location": "auth.py:3; app.py:16,18",
     "scenario": "Hardcoded tokens; a non-numeric id or missing body raises a 500 (possibly pre-existing).",
     "fix": "Track separately; out of scope if pre-existing.", "status": ""}
  ]
}
```