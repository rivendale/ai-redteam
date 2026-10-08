**Note on independence:** this is a single-reviewer pass with no tools. I did not write this work, but no independent seat ran and no code was executed. Every trace below is from reading the supplied files. Re-run the reproductions in a scratch copy before relying on them.

---

**VERDICT: REWORK.** Anyone on the internet can call `POST https://docs.example.test/internal/reindex?purge=1` without a token and permanently delete every customer's documents.

**CONFIDENCE: medium.** No tools were available, so nothing was run. Three inputs are missing: the scheduler's configuration, any network layer in front of the proxy, and the prior version of `app.py`. The core finding rests on lines quoted exactly, so it does not depend on those gaps.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, app.py, auth.py, store.py, test_app.py, deploy/proxy.conf.
- **Not seen: the scheduler job or cron config.** It matters, because it decides whether the nightly call sends `purge=1` and which network it calls from.
- **Not seen: network controls in front of the proxy** (firewall, WAF, security groups). This matters a little. The proxy's own comment says the scheduler goes "through the same proxy", which argues against a private path existing.
- **Not seen: the pre-change `app.py`.** This matters for "keep the document API as it is". I cannot confirm that the `/api/` routes are unchanged.
- **Not seen: the production request adapter** (how `query` gets filled in). This matters for one item under NEEDS VALIDATION.

**COVERAGE**
- **Checked:** `app.py:handle` and `app.py:internal`; `auth.py:authenticate`; every `store.py` function; all four tests; both `location` blocks in `proxy.conf`; the request's "admin" requirement and its "keep API as is" requirement.
- **Not checked:** the scheduler config, the network layer, the previous `app.py`, and the server adapter, because none were supplied. Nothing was executed.

**SEATS AND GATE:** One local reviewer ran, with no tools. No cross-vendor seats ran because none were requested and none were available. Sensitivity gate: not sensitive. The code has only fixture tokens and data, with no real personal data.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `app.py:8-9`, `app.py:24-27`, `deploy/proxy.conf:7` | `/internal/` is routed before `auth.authenticate` and needs no token. The production edge proxy forwards `/internal/` from public port 443 to the app. The request asked for an *admin* reindex, and there is no admin check anywhere. `auth.py` has no notion of roles at all. | Conditions: production runs proxy.conf as supplied, and an attacker can reach docs.example.test:443. The attacker sends `POST /internal/reindex?purge=1` with no token. `store.delete_all()` clears every customer's documents, and the 200 "reindexed" response confirms it. Even without `purge`, anyone can trigger reindexes without limit. | 1. Remove `location /internal/` from the public server block. Expose it only on an internal listener, or add `allow <scheduler IP>; deny all;`. 2. In `internal()`, authenticate the caller and require an admin or service identity (add roles to `auth`). Return 401 or 403 otherwise. **Repro (test):** `r = req("/internal/reindex","POST")`. Expected 401/403; the current code returns 200. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | B, A | `app.py:26-27`, `store.py:29-30` | There is an unrequested `purge=1` mode that calls `DOCS.clear()` on every user's documents. The request asked only for a reindex. The store is in-memory, so there is no backup, no audit record and no undo. | Conditions: an authorised caller sends `purge=1`. That could be a scheduler job copied from a runbook, a mistyped manual call, or a retry tool that keeps the query string. Every customer document is permanently lost. This stays true even after F1 is fixed. | Delete the purge branch, since it was not asked for. If a purge is ever needed, make it a separate, audited operation that requires confirmation. **Repro (test):** `req("/internal/reindex","POST",query={"purge":"1"})`, then `req("/api/docs",token="tok-ann")["body"]`. Expected `[{"id":1,...,"title":"plan"}]`; the current code returns `[]`. | a✓ b✓ c✓ d✗ |
| F3 | Medium | CONFIRMED | B | `test_app.py:20-21` | `test_reindex` asserts that an **unauthenticated** reindex returns 200, so the test encodes the vulnerability. No test covers rejection of a missing or non-admin token, and none covers purge. "4 tests pass" therefore says nothing about the new endpoint's safety. | Conditions: F1 is fixed, and a later change reopens the endpoint (for example, the route moves above the auth check again). CI stays green. | Replace the test with: unauthenticated → 401; `tok-ann` (non-admin) → 403; admin → 200 and `INDEX["version"]` incremented; `purge` → ignored or rejected, with documents intact. Mutation check: delete the auth check, and each new test must go red. Also reset `store.DOCS` and `store.INDEX` in `setUp`, because the tests share module globals. | a✓ b✓ c✗ d✗ |
| F4 | Medium | CONFIRMED | R, B | `app.py:24` vs `deploy/proxy.conf:7` | The code comment asserts a control that does not exist. It says "Called only by the scheduler on the private network, so no token is required". The proxy config's own comment says the scheduler calls it "through the same proxy", which is public. | Conditions: a reviewer or auditor relies on the code comment. They approve the missing authentication on the strength of a network boundary that is not there. This is how F1 got through. | Delete the claim, or make it true by enforcing it in the proxy and adding app-level auth. Then state the real control in the comment. | a✓ b✓ c✗ d✓ |

### NEEDS VALIDATION
- **S1: does the scheduler send `purge=1` nightly?** If it does, every nightly run wipes all documents. To settle it: read the scheduler job definition.
- **S2: is `/internal/` reachable from the internet in practice?** The finding stands as written, but the exposure depends on whether anything upstream blocks it. To settle it: run `curl -X POST https://docs.example.test/internal/reindex` from outside the network against a non-production instance, or inspect the firewall/WAF rules.
- **S3: is the document API unchanged?** The request says "keep the document API as it is", and I cannot diff against the prior version. To settle it: `git diff` the prior `app.py` for the `/api/` branches.
- **S4: does `request.get("query", {}).get(...)` crash in production?** `app.py:26` raises `AttributeError` if the server adapter sets `query` to `None` rather than omitting it. To settle it: check how the production adapter fills in `query`.
- **S5: crashes on malformed input.** `int(path.rsplit(...))` at `app.py:18` and `request["body"]["title"]` at `app.py:16` crash on a non-numeric id or a missing body. I could not tell whether this is pre-existing (and so out of scope) or new. To settle it: compare with the prior version.
- **S6: are the hardcoded tokens deployed?** `auth.py:3` has hardcoded tokens. To settle it: check whether this `auth.py` is what runs in production or is only a fixture.
- **S7: does `rebuild_index()` do anything?** It only increments a version counter. To settle it: check whether a real search index exists in production that this is supposed to rebuild.

### REFUTED
- **Candidate: the `/internal/` prefix lets an attacker reach `/api/` handlers without auth.** Refuted: `internal()` only matches `/internal/reindex` exactly and returns 404 for everything else (`app.py:25,29`).
- **Candidate: `delete_doc` lets a user delete another user's document.** Refuted: the ownership check at `store.py:19`, and the test at `test_app.py:17-18`.

### WHAT HOLDS UP
- The `/api/docs` list, create and delete paths check the token and scope every operation to the owner (`store.py:7-8`, `store.py:19`).
- An unknown or missing token returns 401 before any `/api/` handler runs.

### UNVERIFIED CLAIMS
- **"4 tests pass."** I did not run them. To confirm: `python3 -m unittest test_app`.
- **"Called only by the scheduler on the private network."** This is contradicted by proxy.conf (see F4). To confirm the real path: check the scheduler config and the network layout.

### QUESTIONS FOR THE AUTHOR
1. Why does `purge` exist, and does the scheduler ever send it?
2. What identity should the scheduler authenticate as, and where does "admin" get defined?
3. Can the scheduler reach the app directly, avoiding the public proxy?

### DECISION-MAKER SUMMARY
Do not release. The new reindex endpoint is open to the public internet with no login, and one parameter on it erases every customer's documents permanently. Fix F1 and F2: close the route at the proxy, require an admin identity, and remove purge. Then replace the test that currently asserts the open behaviour. Releasing as is risks total, unrecoverable loss of customer data by anyone who finds the URL.

### OWNER SUMMARY
The new nightly maintenance feature can be triggered by anyone on the internet without logging in. One option on it deletes every customer's documents with no way to recover them. It must be locked down, and that delete option removed, before release.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "deploy/proxy.conf", "status": "seen", "matters": true},
    {"item": "scheduler job configuration", "status": "not_seen", "matters": true},
    {"item": "network/firewall controls in front of the proxy", "status": "not_seen", "matters": true},
    {"item": "prior version of app.py", "status": "not_seen", "matters": true},
    {"item": "production request adapter", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Fixture tokens and toy data only; no real personal data supplied."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "app.py:internal", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:authenticate", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "deploy/proxy.conf", "kind": "config"},
      {"unit": "request: admin-only reindex", "kind": "assumption"},
      {"unit": "request: document API unchanged", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "scheduler job configuration", "reason": "not supplied"},
      {"unit": "upstream network controls", "reason": "not supplied"},
      {"unit": "prior app.py", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:8-9, app.py:24-27, deploy/proxy.conf:7",
     "scenario": "With proxy.conf as supplied running in production, an unauthenticated internet client sends POST https://docs.example.test/internal/reindex?purge=1; the request bypasses authenticate() and store.delete_all() wipes every customer's documents. The request asked for an admin reindex; no admin check exists.",
     "fix": "Remove the public location /internal/ (or restrict it to the scheduler's address with deny all) and require an authenticated admin/service identity in internal(), returning 401/403 otherwise.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/internal/reindex','POST') -> expected 401/403, observed 200 (by trace)."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:26-27, store.py:29-30",
     "scenario": "Unrequested purge=1 mode clears all users' documents from an in-memory store with no backup or audit; any authorised caller sending purge=1 (misconfigured scheduler, copied runbook) causes permanent loss of all customer documents, even after F1 is fixed.",
     "fix": "Remove the purge branch; if ever needed, make it a separate, audited, confirmed operation.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "req('/internal/reindex','POST',query={'purge':'1'}); req('/api/docs',token='tok-ann')['body'] -> expected ann's 'plan' doc, observed [] (by trace)."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:20-21",
     "scenario": "test_reindex asserts unauthenticated reindex returns 200, encoding the vulnerability; no test covers rejection or purge, so a later regression reopening the endpoint passes CI.",
     "fix": "Replace with tests: no token -> 401, non-admin -> 403, admin -> 200 with INDEX version incremented, purge ignored/rejected with docs intact; reset store globals in setUp; confirm tests go red when the auth check is removed.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Remove nothing; observe test_reindex passes while the endpoint is unauthenticated."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "R",
     "location": "app.py:24 vs deploy/proxy.conf:7",
     "scenario": "Comment claims the endpoint is reachable only on the private network, but proxy.conf routes it through the public edge proxy; a reviewer relying on the comment approves the missing auth.",
     "fix": "Delete the claim or make it true (proxy restriction plus app auth) and document the real control.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Compare app.py:24 comment with proxy.conf:7 comment 'the scheduler calls this through the same proxy'."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "scheduler config (not supplied)",
     "suspicion": "The nightly scheduler call may send purge=1, wiping all documents every night.",
     "unresolved_fact": "The scheduler job's exact request and query string."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "deploy/proxy.conf:7",
     "suspicion": "Exposure depends on no upstream firewall blocking /internal/.",
     "unresolved_fact": "Result of an external POST to /internal/reindex against a non-production instance, or the firewall/WAF rules."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "app.py:10-20",
     "suspicion": "The document API may have changed despite the request to keep it as is.",
     "unresolved_fact": "git diff of app.py against the pre-change version."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "app.py:26",
     "suspicion": "request.get('query', {}).get raises AttributeError if query is None.",
     "unresolved_fact": "How the production adapter populates query."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "app.py:16, app.py:18",
     "suspicion": "Non-numeric doc id or missing body raises an unhandled exception.",
     "unresolved_fact": "Whether this behaviour is pre-existing (out of scope) or new."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "auth.py:3",
     "suspicion": "Hardcoded bearer tokens may be the production auth.",
     "unresolved_fact": "Whether this auth.py is deployed or a fixture."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The /internal/ prefix lets an attacker reach /api/ handlers without auth.",
     "evidence": "internal() matches only /internal/reindex and returns 404 otherwise (app.py:25,29)."},
    {"id": "C2", "candidate": "A user can delete another user's document.",
     "evidence": "Owner check at store.py:19; covered by test_app.py:17-18."}
  ]
}
```