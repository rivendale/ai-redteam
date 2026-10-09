**Review conditions:** I reviewed this myself in a single pass. No tools were available, so nothing was executed and every reproduction below is a traced, unexecuted test case. No subagent was available. The work was not written in this conversation, so I share no authoring context with it.

---

**VERDICT: REWORK.** Any unauthenticated user on the internet can POST `https://docs.example.test/internal/reindex?purge=1` and permanently delete every customer's documents. The public proxy forwards `/internal/` and the app skips authentication for that prefix.

**CONFIDENCE: medium.** The Critical findings come from a short, unambiguous trace through four lines of code and one proxy rule, so they are firm. Confidence is limited because:
- no tools were available, so nothing was run;
- there was no diff or base version to separate new code from existing code;
- I did not see the scheduler config, the network topology, or whether `store.py` is the real production store.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| app.py | seen | yes |
| auth.py | seen | yes |
| store.py | seen | yes |
| test_app.py | seen | yes |
| deploy/proxy.conf | seen | yes |
| Diff or base version of the document API | not supplied | yes: "Keep the document API as it is" cannot be checked without the prior version |
| Scheduler config or job definition | not supplied | yes: it determines whether `purge=1` is ever sent and from which network |
| Network topology or firewall rules for docs-app:8000 | not supplied | partly: the proxy alone already exposes the route publicly |
| Test run output ("4 tests pass") | not supplied | low: the trace agrees, and the passing reindex test encodes the bug (F3) |
| Production request adapter (shape of `query` and `body`) | not supplied | yes for S2 |

**COVERAGE**
- Scope: the whole supplied work (5 files) plus the request and context.
- Checked:
  - every route in `handle()` and `internal()`;
  - `auth.authenticate`;
  - every function in `store.py`;
  - all 4 tests;
  - both proxy `location` blocks;
  - the claim in the comment at app.py:24;
  - the claim "Tests: 4 tests pass";
  - the requirement "admin reindex";
  - the requirement "Keep the document API as it is".
- Not checked:
  - git history for secrets (no tools);
  - TLS and certificate config (no `ssl_certificate` lines supplied);
  - the scheduler (not supplied);
  - runtime and concurrency model (not supplied).

**SEATS AND GATE**
- One local reviewer ran, same vendor.
- No cross-vendor seats ran. None were requested, and the work handles customer documents, so the sensitivity gate would restrict external seats anyway.
- Sensitive: the code contains hardcoded bearer tokens (auth.py:3). They look like test fixtures, but I treated them as credentials.

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | app.py:8-9, app.py:23-29; deploy/proxy.conf:7 | Any path under `/internal/` is dispatched before `auth.authenticate`, and `internal()` performs no auth check. The production edge proxy forwards `/internal/` on public port 443. The comment at app.py:24 ("only by the scheduler on the private network") contradicts proxy.conf:7 ("the scheduler calls this through the same proxy"). The "admin" requirement is not implemented: there is no admin role anywhere. | An anonymous internet client sends `POST https://docs.example.test/internal/reindex?purge=1`. It receives 200 and `DOCS` is cleared for all customers. Without `purge`, anyone can trigger reindexing at will. | **Fix:** remove `location /internal/` from the public server, or restrict it with `allow <scheduler IP>; deny all;`. Also require a dedicated scheduler or admin credential inside `internal()`, checked before any action, so the protection does not rely on network placement. **Repro (unexecuted):** `req("/internal/reindex","POST",query={"purge":"1"})` with no token. Expected 401 or 403; the trace gives 200 and `store.DOCS == {}`. | a Y, b Y, c Y, d Y |
| F2 | Critical | CONFIRMED (traced) | B | app.py:26-27; store.py:24-25 | The request asked only for a reindex. The work adds an unrequested `purge=1` mode that calls `store.delete_all()`, which wipes every user's documents. There is no confirmation, backup, or audit trail. | Even after F1 is fixed, any caller holding the scheduler credential triggers an irreversible wipe of all customer data with one query parameter. Examples: a copied URL, a misconfigured job, or a leaked scheduler credential. | **Fix:** remove the purge branch. If a purge is genuinely needed, specify it separately, with its own authorization, an audit record, and a backup or soft delete. **Repro (unexecuted):** authenticate however F1's fix requires, then call `req("/internal/reindex","POST",query={"purge":"1"})`. Assert `store.DOCS` is unchanged; the trace gives `{}`. | a Y, b Y, c Y, d N |
| F3 | Medium | CONFIRMED | B | test_app.py:19-20 | `test_reindex` asserts that an unauthenticated POST returns 200. The test enshrines the F1 vulnerability. There is no test for the purge branch, no test that `/internal/*` rejects anonymous callers, and no test that the reindex actually changes the index. | A correct fix for F1 turns this test red, which invites someone to "fix" the fix. The current green suite gives false assurance about release readiness. | **Fix:** replace it with tests for (1) anonymous call → 401/403, (2) scheduler credential → 200 and `INDEX["version"]` incremented, (3) purge absent or rejected. **Repro:** the existing test passes against vulnerable code; a test asserting 401 for an anonymous reindex fails on the current code (traced). | a Y, b Y, c N, d Y |
| F4 | Low | CONFIRMED | B | auth.py:3 | Bearer tokens are hardcoded in source. | Anyone with read access to the repository can act as ann or bo. Removing the tokens later does not remove them from git history. | **Fix:** load tokens or keys from a secret store, and rotate them if these are real. **Repro:** `auth.authenticate("tok-ann") == "ann"` using only repository contents. History was not searched (no tools). | a Y, b Y, c Y, d N |
| F5 | Low | CONFIRMED (traced) | B | app.py:17-18; app.py:15-16 | `DELETE /api/docs/abc` raises a ValueError from `int()`. A POST with no body or no title raises a TypeError or KeyError. Both produce an unhandled exception instead of a 400. This may predate the change. | An authenticated user sends a malformed id and gets a 500 or a crashed worker, depending on the server. | **Fix:** validate input and return 400. **Repro (unexecuted):** `req("/api/docs/abc","DELETE",token="tok-ann")` raises ValueError; the expected response is status 400. | a Y, b Y, c N, d N |

**Siblings for F1 and F2.**
- Searched every branch of `internal()`, every route in `handle()`, both proxy `location` blocks, every caller of `store.delete_all` and `store.rebuild_index`, and `auth.py` for any role or admin concept.
- Found that the `startswith("/internal/")` bypass covers every future `/internal/*` route, so any internal endpoint added later is publicly exposed without auth.
- `delete_all` has only one caller (app.py:27).
- No admin role exists.
- `/api/` routes all pass through authentication.

**Security boundaries.**
- **F1:**
  - Principal: an unauthenticated internet client.
  - Input it controls: the request path `/internal/reindex` and the query string.
  - Control that fails: the auth check, which is skipped at app.py:8. Network isolation is also absent (proxy.conf:7).
  - Boundary crossed: anonymous internet to scheduler/admin.
  - Resource affected: the index and all customer documents.
- **F2:**
  - Principal: any holder of the scheduler path. Today that is anyone, because of F1.
  - Input it controls: `query.purge=1`.
  - Control that fails: none exists.
  - Boundary crossed: maintenance to destructive data deletion.
  - Resource affected: every user's documents.

### NEEDS VALIDATION
- **S1:** whether the document API is unchanged as the request requires. Settled by a diff against the previous app.py and store.py.
- **S2:** whether `request["query"]` can be `None` in production. If it can, `.get("purge")` at app.py:26 raises AttributeError. Settled by the production request adapter.
- **S3:** whether `store.rebuild_index` is real. It only increments a counter that nothing reads, so the nightly job may do nothing useful. Settled by confirming whether `store.py` is the production store or a stand-in.
- **S4:** whether reindex and purge can race with concurrent writes (no locking around `DOCS`). Settled by the server's worker and thread model.
- **S5:** whether the scheduler is configured to send `purge=1`. Settled by the scheduler job definition.

### REFUTED
- **C1:** "a user can delete another user's document." Refuted: store.py:18 checks ownership before deleting, and test_app.py:16-17 covers it.
- **C2:** "list_docs leaks other users' documents." Refuted: store.py:8 filters on `owner == user`.
- **C3:** "path tricks such as `/api/../internal/` bypass routing." Moot: the direct `/internal/` route is already open (F1). This adds nothing.

### WHAT HOLDS UP
- Authentication and ownership checks on `/api/docs` GET, POST, and DELETE are applied consistently.
- A missing or unknown token returns 401.
- Document ids from `add_doc` cannot collide in a single-threaded run, because of `max(..., default=0)`.

### UNVERIFIED CLAIMS
- "4 tests pass." Not run; tracing suggests they do. Confirm by running `python -m unittest test_app` in an isolated copy.
- "Called only by the scheduler on the private network" (app.py:24). Contradicted by proxy.conf:7, so it is false as deployed.

### QUESTIONS FOR THE AUTHOR
1. Who asked for `purge`, and does the scheduler ever send it?
2. What credential or network control was meant to make this endpoint "admin"?
3. Does the scheduler have to go through the public proxy, or can it reach docs-app:8000 directly?

### DECISION-MAKER SUMMARY
Do not release. The new reindex endpoint is publicly reachable with no authentication, and a single URL parameter deletes every customer's documents. Remove the purge option, lock `/internal/` down at the proxy and in code, and replace the test that currently asserts the hole is open. Releasing as is risks total loss of customer data to any anonymous visitor.

### OWNER SUMMARY
The new nightly maintenance feature can be triggered by anyone on the internet without logging in. One version of it erases all customer documents. It needs to be locked down and the erase option removed before it goes live.

```json
{
  "schema_version": "2.3",
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
    {"item": "diff or base version of the document API", "status": "not_seen", "matters": true},
    {"item": "scheduler job config", "status": "not_seen", "matters": true},
    {"item": "network/firewall rules for docs-app:8000", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Customer-document service with hardcoded bearer tokens in auth.py; no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "app.py:internal", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "deploy/proxy.conf", "kind": "config"},
      {"unit": "app.py:24 private-network claim", "kind": "claim"},
      {"unit": "4 tests pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "git history for secrets", "reason": "no_tools"},
      {"unit": "scheduler config", "reason": "not_supplied"},
      {"unit": "base version / diff", "reason": "not_supplied"},
      {"unit": "TLS settings", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:8-9, app.py:23-29; deploy/proxy.conf:7",
     "scenario": "An anonymous internet client POSTs https://docs.example.test/internal/reindex?purge=1; the proxy forwards it, handle() skips auth for /internal/, internal() has no check, and every customer's documents are deleted.",
     "fix": "Remove or IP-restrict location /internal/ at the public proxy and require a scheduler/admin credential inside internal() before any action.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Unexecuted: req('/internal/reindex','POST',query={'purge':'1'}) with no token; expect 401/403, trace gives 200 and store.DOCS == {}.",
     "security": true,
     "boundary": {"principal": "unauthenticated internet client", "input": "request path /internal/reindex and query string",
                  "control": "auth skipped at app.py:8 and no network restriction at proxy.conf:7", "crossed": "anonymous internet to scheduler/admin",
                  "resource": "document index and all customer documents"},
     "siblings_searched": {"searched": "all branches of internal(), all routes in handle(), both proxy location blocks, auth.py for roles",
                           "found": "the startswith('/internal/') bypass covers every future /internal/* route; no admin role exists; /api/ routes are authenticated"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:26-27; store.py:24-25",
     "scenario": "Any caller of the reindex endpoint (today anyone, per F1; after F1 is fixed, any holder of the scheduler credential or a misconfigured job) passes purge=1 and irreversibly wipes all users' documents; the request asked only for a reindex.",
     "fix": "Remove the purge branch; if a purge is needed, specify it separately with its own authorization, audit record and backup or soft delete.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "Unexecuted: call req('/internal/reindex','POST',query={'purge':'1'}) authenticated however F1's fix requires; assert store.DOCS is unchanged; trace gives {}.",
     "security": true,
     "boundary": {"principal": "any caller able to reach the reindex endpoint", "input": "query parameter purge=1",
                  "control": "none exists", "crossed": "maintenance to destructive data deletion",
                  "resource": "every user's documents"},
     "siblings_searched": {"searched": "callers of store.delete_all and other destructive store functions",
                           "found": "app.py:27 is the only caller of delete_all; delete_doc is owner-checked"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:19-20",
     "scenario": "test_reindex asserts an unauthenticated reindex returns 200, so the suite is green on vulnerable code and turns red on a correct fix for F1; there is no test for purge or for rejecting anonymous callers.",
     "fix": "Replace with tests: anonymous call returns 401/403; scheduler credential returns 200 and increments INDEX['version']; purge absent or rejected.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "A test asserting req('/internal/reindex','POST')['status'] == 401 fails on the current code (traced, unexecuted)."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:3",
     "scenario": "Anyone with repository read access can authenticate as ann or bo using the hardcoded tokens; removing them later leaves them in git history.",
     "fix": "Load tokens or keys from a secret store and rotate them if real.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "auth.authenticate('tok-ann') returns 'ann' using only repository contents."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:17-18; app.py:15-16",
     "scenario": "An authenticated user sends DELETE /api/docs/abc or a POST without a body or title; int() or the body lookup raises an unhandled exception instead of returning 400.",
     "fix": "Validate the path id and request body and return 400 on malformed input.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Unexecuted: req('/api/docs/abc','DELETE',token='tok-ann') raises ValueError; expected status 400."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "app.py:13-19",
     "suspicion": "The document API may have changed, contrary to the request.",
     "unresolved_fact": "A diff against the previous app.py and store.py."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:26",
     "suspicion": "request['query'] may be None in production, making .get('purge') raise AttributeError.",
     "unresolved_fact": "The shape of the production request adapter."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "store.py:28-29",
     "suspicion": "rebuild_index only increments a counter nothing reads, so the nightly job may do nothing useful.",
     "unresolved_fact": "Whether store.py is the production store or a stand-in."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "store.py:3, store.py:24-29",
     "suspicion": "Reindex or purge may race with concurrent writes to DOCS (no locking).",
     "unresolved_fact": "The server's worker and thread model."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "app.py:26",
     "suspicion": "The scheduler may be configured to send purge=1 nightly.",
     "unresolved_fact": "The scheduler job definition."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A user can delete another user's document.", "evidence": "store.py:18 checks ownership before deleting; test_app.py:16-17 covers it."},
    {"id": "C2", "candidate": "list_docs leaks other users' documents.", "evidence": "store.py:8 filters on owner == user."},
    {"id": "C3", "candidate": "Path normalization such as /api/../internal/ bypasses routing.", "evidence": "Moot: the direct /internal/ route is already open (F1); nothing additional is exposed."}
  ]
}
```

I could not run `tools/validate_findings.py` against this block in this session, so its schema validity is unchecked.