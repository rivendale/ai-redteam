VERDICT: **REJECT.** Anyone on the internet can delete every customer document with one unauthenticated request, because `/internal/` skips auth in the app and the production proxy exposes it publicly.

CONFIDENCE: **medium-high.** The core chain is short and deterministic, and I traced it line by line. Confidence is limited because I had no tools: nothing was executed, the "4 tests pass" claim is unverified, and no fresh subagent was available. This is a single-reviewer review (same-context, so there is an anchoring risk); re-run it in a fresh session given the stakes.

INPUTS LEDGER:
- **Seen:** request.md, context.md, app.py, auth.py, store.py, test_app.py, deploy/proxy.conf.
- **Not seen, and it matters:**
  - The diff or base commit. I cannot tell which code is new and which predates the change, so I reviewed whole files.
  - The scheduler config. I cannot tell whether it sends `purge=1` or what credentials it holds.
  - Network policy and firewall rules. Nothing I was given contradicts proxy.conf exposing `/internal/`, but nothing I was given restricts it either.
- **Not seen, and it does not matter:** a real index or search backend. `rebuild_index` only bumps a counter.

COVERAGE:
- **Scope:** the whole supplied work (5 files plus 2 documents).
- **Checked:**
  - Every file.
  - `app.handle`, `app.internal`, `auth.authenticate`, all `store` functions, all 4 tests.
  - Both proxy `location` blocks.
  - The assumption in the comment at app.py:23.
- **Not checked:**
  - The diff or base (not supplied).
  - The scheduler config (not supplied).
  - Network and firewall rules (not supplied).
  - Test execution (no tools).
  - Git history for secrets (no tools).
  - A scan for invisible or bidirectional characters (no tools; the visible text shows none).

SEATS AND GATE:
- Single local reviewer. No subagent or cross-vendor seats, because no tools were available.
- Sensitivity gate: the supplied code contains no personal data. It does contain hard-coded tokens (F5). No external seats were used, so nothing was refused.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | app.py:8-9, 22-29 | `handle` routes any `/internal/` path to `internal()` before `auth.authenticate` runs, and `internal()` performs no check. The comment at line 23 assumes the caller is on a private network. There is also no "admin" concept anywhere: auth.py has no roles, so the "admin reindex" the request asked for does not exist. | An unauthenticated client sends `POST /internal/reindex?purge=1`. `store.delete_all()` wipes every user's documents and the response is 200. | **Fix:** require an admin or scheduler credential in `internal()` (a separate service token or an mTLS identity, not a user token) and reject anything else with 401/403. **Repro:** `req("/internal/reindex","POST",query={"purge":"1"})` returns status 200 (expected 401). Then `req("/api/docs",token="tok-ann")["body"]` returns `[]` (expected `[{...'plan'}]`). | T/T/T/T |
| F2 | Critical | CONFIRMED (quoted) | B | deploy/proxy.conf, `location /internal/` line | The public edge (`listen 443`, `server_name docs.example.test`) forwards `/internal/` to the app. The config's own comment says "the scheduler calls this through the same proxy". This makes the private-network premise at app.py:23 false in production. | Any internet user reaches `/internal/reindex` through docs.example.test, which combined with F1 is the mass deletion. | **Fix:** remove the `/internal/` location from the public server block. Have the scheduler call `docs-app:8000` directly on the private network, or put the endpoint behind an `allow`/`deny` IP allowlist plus auth. **Repro:** read proxy.conf; `curl -X POST https://docs.example.test/internal/reindex` is routed to the app. Run this only against an isolated staging copy, never production. | T/T/T/T |
| F3 | Critical | CONFIRMED (traced) | B | app.py:25-26, store.py:28-29 | The request asked for a reindex. The work adds an unrequested `purge=1` flag that deletes all documents. The store is in memory and `rebuild_index` does not restore documents, so the deletion is unrecoverable. | Even after F1 and F2 are fixed, a scheduler misconfiguration or a copy-pasted URL with `?purge=1` erases every customer document on the nightly run. | **Fix:** remove `purge` and `delete_all` from the reindex path. If a purge is ever needed, make it a separate, explicitly requested, audited operation. **Repro:** same as F1, but with any authorized caller. | T/T/T/F |
| F4 | Medium | CONFIRMED (traced) | B | test_app.py:20-21 | `test_reindex` asserts that an unauthenticated POST returns 200. The test encodes the F1 defect as expected behavior. There is no test for purge, no negative auth test on `/internal/`, and no test that documents survive a reindex. | Fixing F1 turns this test red, which pushes a developer toward "fixing" the test or the auth check back to open. Meanwhile CI stays green with the defect live. | **Fix:** replace the test with: no token gives 401; a user token gives 403; a service token gives 200; and documents are unchanged after a reindex. **Repro (mutation):** add an auth check to `internal()`; `test_reindex` goes red, showing the test guards the bug. | T/T/F/T |
| F5 | Medium | CONFIRMED (quoted) | B | auth.py:3 | Bearer tokens are hard-coded in source: `TOKENS = {"tok-ann": "ann", "tok-bo": "bo"}`. | If these are real production tokens, anyone with read access to the repository can act as ann or bo. They also stay in git history after removal. | **Fix:** load tokens from a secret store and rotate them if they were ever real. **Repro:** `grep -n TOKENS auth.py`. Whether they are live is a separate open question (S2). | T/T/F/F |
| F6 | Low | CONFIRMED (traced) | B | app.py:16, 18 | Malformed input raises an uncaught exception: `int("abc")` raises ValueError, and `request["body"]["title"]` raises TypeError or KeyError when the body is missing. These lines may predate the change, and the request says to keep the document API as it is. | `DELETE /api/docs/abc` or a POST with no body produces an unhandled error (a 500) instead of a 400. | **Fix:** validate the input and return 400. Do this separately so it does not change the API contract within this change. **Repro:** `req("/api/docs/abc","DELETE",token="tok-ann")` raises ValueError. | T/T/F/F |

**Siblings and boundaries**
- **F1, F2, F3:** these are security findings. The boundary:
  - Principal: an unauthenticated internet client.
  - Input it controls: the path `/internal/*` and the `purge` query parameter.
  - Control that fails: the auth bypass at app.py:8-9 plus the public proxy route.
  - Boundary crossed: from the internet to the internal admin operation.
  - Resource affected: every customer document.
- **Sibling search:** I checked every route in `handle`. Only the `/internal/` prefix bypasses `authenticate`. I checked every caller of `delete_all` and `rebuild_index`: only `internal()` calls them. I checked both proxy locations: only `/internal/` is misrouted, and `/api/` is meant to be public.

## NEEDS VALIDATION
- **S1:** whether `rebuild_index` is a stub. It only increments `INDEX["version"]` and builds nothing. This is settled by whether a real index exists outside store.py.
- **S2:** whether the auth.py tokens are live production credentials. This is settled by the deployment's secret source and a read-only search of git history.
- **S3:** whether the nightly scheduler sends `purge=1` or retries on failure. This is settled by the scheduler job definition, which was not supplied.

## REFUTED
- **"Users can delete each other's documents":** `store.delete_doc` checks the owner (store.py:18), and `test_cannot_delete_other_users_doc` covers it.
- **"The document API was changed":** the `/api/docs` GET, POST and DELETE handlers are consistent with the request's "keep as it is". Without a diff this is not provable, but nothing points to drift.

## WHAT HOLDS UP
- User-facing routes authenticate before any action.
- Listing and deletion are correctly scoped to the owner.
- A 404 for someone else's document avoids leaking whether it exists.

## UNVERIFIED CLAIMS
- **"4 tests pass":** I could not run them. Run `python -m unittest test_app` in a scratch copy. By my trace they would pass, which is the problem described in F4.
- **"Called only by the scheduler on the private network" (app.py:23):** contradicted by proxy.conf (F2).

## QUESTIONS FOR THE AUTHOR
1. Who asked for `purge`, and does the scheduler send it?
2. What credential will the scheduler present, and how does it reach the app (through the proxy or directly)?
3. Are the tokens in auth.py real?

## DECISION-MAKER SUMMARY
Do not release. F1, F2 and F3 together let any unauthenticated internet user delete all customer documents with a single request. Remove the purge flag, add service-credential auth to `/internal/`, take `/internal/` off the public proxy, and fix the test that currently asserts the open endpoint.

## OWNER SUMMARY
As built, anyone on the internet could erase every customer document with one web request, because the new nightly maintenance endpoint has no login and is publicly reachable. It also includes a "delete everything" option that nobody asked for. The fix is to lock the endpoint to the scheduler only, hide it from the public, and remove the delete option before release.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "deploy/proxy.conf", "status": "seen", "matters": true},
    {"item": "diff / base commit", "status": "not_seen", "matters": true},
    {"item": "scheduler job config", "status": "not_seen", "matters": true},
    {"item": "network/firewall policy", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-single-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code only; hard-coded tokens noted as F5; no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"}, {"unit": "context.md", "kind": "document"},
      {"unit": "app.py", "kind": "file"}, {"unit": "auth.py", "kind": "file"}, {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"}, {"unit": "deploy/proxy.conf", "kind": "config"},
      {"unit": "app.py:handle", "kind": "function"}, {"unit": "app.py:internal", "kind": "function"},
      {"unit": "auth.py:authenticate", "kind": "function"}, {"unit": "store.py:delete_doc", "kind": "function"},
      {"unit": "store.py:delete_all", "kind": "function"}, {"unit": "store.py:rebuild_index", "kind": "function"},
      {"unit": "app.py:23 private-network comment", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "diff / base commit", "reason": "not_supplied"},
      {"unit": "scheduler job config", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"},
      {"unit": "git history secret search", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:8-9, 22-29",
     "scenario": "An unauthenticated POST /internal/reindex?purge=1 bypasses authenticate, calls store.delete_all() and returns 200; all customer documents are gone.",
     "fix": "Require an admin/scheduler service credential in internal() and reject others with 401/403.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/internal/reindex','POST',query={'purge':'1'}) returns 200 (expected 401); then req('/api/docs',token='tok-ann')['body'] == [] (expected the 'plan' doc).",
     "security": true,
     "boundary": {"principal": "unauthenticated internet client", "input": "path /internal/reindex and purge query parameter",
                  "control": "/internal/ prefix dispatched before authenticate; internal() has no check",
                  "crossed": "internet to internal admin operation", "resource": "every customer document"},
     "siblings_searched": {"searched": "all routes in handle; all callers of delete_all and rebuild_index",
                           "found": "only the /internal/ prefix bypasses auth; only internal() calls the two functions"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "deploy/proxy.conf: location /internal/ { proxy_pass http://docs-app:8000; }",
     "scenario": "The public 443 server block forwards /internal/ to the app, so any internet user reaches the unauthenticated reindex/purge endpoint.",
     "fix": "Remove /internal/ from the public server block; have the scheduler call docs-app directly on the private network, or add an IP allowlist plus auth.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Read proxy.conf: location /internal/ proxies to docs-app on listen 443 for docs.example.test; against an isolated staging copy, POST https://<staging>/internal/reindex reaches the app and returns 200.",
     "security": true,
     "boundary": {"principal": "unauthenticated internet client", "input": "HTTPS request to /internal/*",
                  "control": "edge proxy routes /internal/ publicly", "crossed": "public edge to private internal endpoint",
                  "resource": "every customer document"},
     "siblings_searched": {"searched": "every location block in proxy.conf", "found": "only /internal/ is misrouted; /api/ is intended public"}},
    {"id": "F3", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:25-26; store.py:28-29",
     "scenario": "An unrequested purge=1 flag on the reindex calls DOCS.clear(); a misconfigured scheduler, or any caller per F1/F2, irreversibly erases all documents (the store is in memory and has no restore).",
     "fix": "Remove purge/delete_all from the reindex path; any purge must be a separate, requested, audited operation.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "req('/internal/reindex','POST',query={'purge':'1'}); assert store.DOCS == {} (expected the documents to be unchanged by a reindex).",
     "security": true,
     "boundary": {"principal": "any caller of /internal/reindex", "input": "purge=1 query parameter",
                  "control": "no confirmation, authorization or audit around delete_all", "crossed": "maintenance operation to destructive data deletion",
                  "resource": "every customer document"},
     "siblings_searched": {"searched": "all destructive store functions and their callers", "found": "delete_all is reachable only through internal(); delete_doc is owner-scoped"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:20-21",
     "scenario": "test_reindex asserts that an unauthenticated reindex returns 200, so CI is green with F1 live and goes red when F1 is fixed.",
     "fix": "Test that no token gives 401, a user token gives 403, a service token gives 200, and documents are unchanged after a reindex.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Mutation: add an auth check in internal(); test_reindex fails, showing that it guards the insecure behavior."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:3",
     "scenario": "Bearer tokens are hard-coded in source; if they are real, anyone with repository read access can impersonate ann or bo, and the tokens persist in git history.",
     "fix": "Load tokens from a secret store; rotate them if they were ever live.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "grep -n TOKENS auth.py shows {'tok-ann': 'ann', 'tok-bo': 'bo'}."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:16, 18",
     "scenario": "DELETE /api/docs/abc raises ValueError, and a POST with no body raises TypeError, producing a 500 instead of a 400.",
     "fix": "Validate the input and return 400, in a separate change so the API contract is preserved here.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "req('/api/docs/abc','DELETE',token='tok-ann') raises ValueError (expected status 400)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "store.py:32-33",
     "suspicion": "rebuild_index is a stub that only increments a version counter.",
     "unresolved_fact": "Whether a real index exists outside store.py."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:3",
     "suspicion": "The hard-coded tokens may be live production credentials.",
     "unresolved_fact": "The production token source and a read-only search of git history."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "scheduler config (not supplied)",
     "suspicion": "The nightly job may send purge=1 or retry on failure.",
     "unresolved_fact": "The scheduler job definition."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Users can delete other users' documents.",
     "evidence": "store.delete_doc checks the owner at store.py:18; test_cannot_delete_other_users_doc covers it."},
    {"id": "C2", "candidate": "The document API was changed, contrary to the request.",
     "evidence": "The /api/docs GET, POST and DELETE handlers match the request's 'keep as it is'; no sign of drift (no diff supplied)."}
  ]
}
```