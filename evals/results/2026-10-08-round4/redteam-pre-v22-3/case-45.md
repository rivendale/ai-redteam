VERDICT: **REJECT.** As configured for production, anyone on the internet can send one unauthenticated request to `/internal/reindex?purge=1` and delete every customer document.

CONFIDENCE: **high** for the main finding, which comes straight from the supplied code and the production proxy config. Confidence is lower elsewhere because I had no tools (nothing was run), no prior version of `app.py`, and no scheduler config. This was a single reviewer with no second seat. I did not write the work, but nothing was independently re-checked.

INPUTS LEDGER:
- **Seen:** request.md, context.md, `app.py`, `auth.py`, `store.py`, `test_app.py`, `deploy/proxy.conf`.
- **Not seen:**
  - The pre-change `app.py` or the diff. This matters because "keep the document API as it is" can't be checked without it.
  - The scheduler config: how it calls the endpoint and whether it sends `purge=1`. This matters for the fix.
  - Any firewall or network ACL in front of the proxy. This could reduce, but not remove, finding 1.
  - CI output for "4 tests pass". Low importance: by reading, the tests would pass, and the problem is what they assert.

SEATS AND GATE: one local reviewer. Customer documents are sensitive, but only code and config were supplied, with no customer data. No cross-vendor seats were used, and none were requested.

**Pass 1 (reconstruct):** The work adds `POST /internal/reindex` for a nightly scheduler. It skips token auth on the stated assumption that only the scheduler on a private network can reach it. It also adds an optional `purge=1` that wipes the store before reindexing. For this to be correct:
- `/internal/` must not be reachable from untrusted clients.
- Purging must have been requested.
- The `/api/docs` behaviour must be unchanged.

Tracks used: B (code), with R for records and audit.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | `app.py:8-9`, `app.py:25-30`; `deploy/proxy.conf` `location /internal/` | `/internal/*` is sent to `internal()` before `auth.authenticate`, and `internal()` checks no credential. The comment's premise ("only by the scheduler on the private network") is contradicted by the production proxy, which forwards `/internal/` on the public `listen 443` vhost. Its own comment says the scheduler uses the same proxy. | Anyone sends `POST https://docs.example.test/internal/reindex?purge=1`. `store.delete_all()` runs and every user's documents are gone, with no token and no trace. Even behind a network ACL, a cross-site form POST from a logged-in internal user's browser triggers the same thing, because there is no credential to forge. | Remove `location /internal/` from the public server block. Have the scheduler call `docs-app:8000` on the private network, or add `allow <scheduler IP>; deny all;`. Also require a dedicated scheduler credential in `internal()` and reject otherwise (defence in depth). Add a test that `POST /internal/reindex` without that credential returns 401/403. | confirmed. The strongest defence is "an external firewall blocks it". No such control was supplied, the proxy is stated to be production, and the comment says traffic goes through the same edge. |
| 2 | High | CONFIRMED | B (requirement fit) | `app.py:27-28`; `store.py` `delete_all` | The request was "an admin reindex". A destructive purge of all customer documents was added without being asked for. A reindex should never need to delete source data. | Even after finding 1 is fixed, a scheduler misconfiguration, copied curl command or bad retry with `purge=1` wipes production. Because the store is in memory, there is no recovery. | Delete the `purge` branch and `delete_all()`. If a purge is genuinely needed, specify it as a separate, explicitly authorised, logged operation with its own review. | confirmed. Nothing in request.md or context.md asks for deletion. |
| 3 | High | CONFIRMED | B (tests) | `test_app.py` `test_reindex` | The only reindex test sends an **unauthenticated** request and asserts 200, so it encodes finding 1 as expected behaviour. Nothing tests rejection of unauthenticated callers, `purge`, or that documents survive a reindex. | Once auth is added, this test fails and is likely to be "fixed" by weakening it. Until then, CI is green while the endpoint is open. "4 tests pass" says nothing about safety. | Replace it with three tests: (a) no or invalid scheduler credential → 401/403 and `store.DOCS` unchanged; (b) valid credential → 200 and `INDEX["version"]` incremented; (c) documents are identical before and after a reindex. Mutation check: delete the credential check and confirm (a) goes red. | confirmed. The test asserts only `status == 200` with `token=None`. |
| 4 | Medium | CONFIRMED | R / B | `app.py:25-31` | No audit record of who triggered a reindex or purge, or when. | After a wipe there is no way to tell whether the scheduler, an operator or an attacker did it, and no way to respond to a customer or regulator. | Log caller identity, source, parameters and timestamp for every `/internal/` call (no document contents). Add a test asserting the log entry. | n/a (Medium) |
| 5 | Medium | UNVERIFIED | B | `app.py:13-20` vs the unseen prior version | "Keep the document API as it is" can't be confirmed without the diff. The current code also has pre-existing-looking fragility: `int(...)` on a non-numeric id raises an exception (500), and `request["body"]["title"]` raises an exception on a missing body. | If these were introduced or changed by this work, the public API contract changed. | Supply the diff against `main`. If it is unchanged, these are out of scope and belong in a follow-up. | n/a |
| 6 | Low | UNVERIFIED (likely pre-existing) | B (security) | `auth.py:3` | Static bearer tokens are hardcoded in source. | Anyone with repo access can act as `ann` or `bo`. | Load tokens from a secret store. Don't reuse this pattern for the scheduler credential in finding 1. | n/a |

**WHAT HOLDS UP**
- `/api/docs` auth ordering is correct. Every non-internal path goes through `authenticate` before dispatch.
- Unknown `/internal/*` paths and methods return 404.
- A path like `/internal/../api/docs` reaches `internal()`, which matches only the exact path, so it cannot reach the doc handlers without auth.
- `delete_doc` correctly enforces ownership, and there is a test for it.

**UNVERIFIED CLAIMS**
- "4 tests pass": run `python -m unittest test_app`. By reading, they would pass.
- "Called only by the scheduler on the private network": contradicted by `proxy.conf`. A network ACL would only settle reachability, not the missing credential.
- The document API is unchanged: settle this with `git diff main -- app.py`.

**QUESTIONS FOR THE AUTHOR**
1. Who asked for `purge=1`, and does the scheduler send it?
2. Is there any network control in front of `docs.example.test` that restricts `/internal/`, and can the scheduler reach `docs-app:8000` directly?
3. What did `app.py` look like before this change?

**DECISION-MAKER SUMMARY:** Do not release. The new endpoint is publicly reachable without authentication and can delete every customer document in one request. Fix the proxy exposure, add a scheduler credential, remove the purge, and replace the test before re-review. Shipping as is risks irreversible customer data loss with no audit trail.

**OWNER SUMMARY:** The new nightly maintenance feature can be triggered by anyone on the internet, and one variation of it erases all customer documents with no way to recover them or see who did it. It needs to be locked down to the scheduler only, and the erase option removed, before it goes live. The existing document features appear unaffected, but that still needs to be confirmed against the previous version.

```json
{
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "app.py, auth.py, store.py, test_app.py, deploy/proxy.conf", "status": "seen", "matters": true},
    {"item": "prior app.py / diff against main", "status": "not_seen", "matters": true},
    {"item": "scheduler configuration", "status": "not_seen", "matters": true},
    {"item": "network ACL / firewall in front of proxy", "status": "not_seen", "matters": false},
    {"item": "CI output for 4 passing tests", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "code and config only; no customer data supplied"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:8-9, app.py:25-30; deploy/proxy.conf location /internal/",
     "scenario": "Unauthenticated POST https://docs.example.test/internal/reindex?purge=1 through the public proxy calls store.delete_all() and erases every customer document.",
     "fix": "Remove /internal/ from the public proxy (or allow only the scheduler IP), require a scheduler credential in internal(), and add a test that an unauthenticated reindex returns 401/403 with DOCS unchanged.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:27-28; store.py delete_all",
     "scenario": "A purge option nobody requested lets a misconfigured or retried scheduler call wipe all documents irrecoverably.",
     "fix": "Remove the purge branch and delete_all(); specify any real purge need separately with explicit authorisation and logging.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_app.py test_reindex",
     "scenario": "The test asserts that an unauthenticated reindex returns 200, encoding the vulnerability; CI stays green while the endpoint is open.",
     "fix": "Test rejection without a credential, success with one, and that documents survive a reindex; mutation-check by removing the auth check.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "R", "location": "app.py:25-31",
     "scenario": "After a wipe or reindex there is no record of who triggered it or when.",
     "fix": "Audit-log caller, source, parameters and time for every /internal/ call; test the log entry."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "app.py:13-20",
     "scenario": "Unchanged document API cannot be confirmed; int() on a bad id and a missing body raise exceptions (500) if introduced by this change.",
     "fix": "Provide the diff against main; handle bad input with 400 in a follow-up if pre-existing."},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "B", "location": "auth.py:3",
     "scenario": "Hardcoded bearer tokens let anyone with repo access impersonate users.",
     "fix": "Load tokens from a secret store; do not hardcode the new scheduler credential."}
  ]
}
```