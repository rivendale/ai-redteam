# Redteam report: admin reindex for the documents service

**Review setup:** Single reviewer with no tools, so no code was run. Every finding below comes from reading the exact supplied lines. Re-run with tools for anything high-stakes.

**VERDICT: REWORK.** The new reindex endpoint has no authentication, and the production proxy exposes it to the internet. With `?purge=1`, any anonymous caller can delete every customer document.

**CONFIDENCE: medium.**
- The main finding comes straight from the code and config lines quoted below.
- Confidence is limited because nothing was executed, the previous version of the API was not supplied, and the scheduler's real request format and network path were not supplied.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | — |
| app.py, auth.py, store.py, test_app.py, deploy/proxy.conf | seen | — |
| Previous version of app.py (the baseline for "keep the document API as it is") | not seen | yes, for checking drift |
| Scheduler config (how it calls the endpoint and from where) | not seen | yes, it decides whether a private path exists |
| Network or firewall config for docs-app:8000 | not seen | yes |
| Test run output ("4 tests pass") | not seen | low; passing tests do not show the change is correct |

## COVERAGE

**Checked:**
- `app.py:handle`
- `app.py:internal`
- `auth.py:authenticate`
- every function in `store.py`
- all 4 tests in `test_app.py`
- both `location` blocks in `deploy/proxy.conf`

**Not checked:**
- Runtime behaviour (no tools)
- How the real HTTP adapter shapes `request` (for example whether `query` can be `None`)
- The scheduler
- Network ACLs

## SEATS AND GATE

- **Seats:** One local reviewer ran. No subagent or cross-vendor seats were available because the session has no tools.
- **Sensitivity gate:** No real personal data was supplied. `auth.py` holds what look like fixture tokens. No external seat was used, so nothing was refused.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `app.py:8-9`, `app.py:24-28`, `deploy/proxy.conf:7` | `handle` sends `/internal/*` to `internal()` before calling `auth.authenticate`. `internal()` checks no token. The comment says "Called only by the scheduler on the private network", but the production proxy exposes `location /internal/` on public `listen 443`, and its own comment says the scheduler goes through that same proxy. | An anonymous internet client sends `POST https://docs.example.test/internal/reindex?purge=1`. `store.delete_all()` runs `DOCS.clear()`, and every customer's documents are gone. Without `purge`, anyone can trigger reindexing as often as they like. | Remove `location /internal/` from the public proxy and have the scheduler call `docs-app:8000` on the private network. Also require a scheduler credential inside `internal()` (defence in depth). **Repro:** `req("/internal/reindex","POST",query={"purge":"1"})` with no token gives 200 and `store.DOCS == {}`. It should give 401. | y/y/y/y |
| F2 | High | CONFIRMED | B | `app.py:26-27` | A destructive `purge` option was added that the request never asked for ("Add an admin reindex"). It is controlled by a single query flag, with no confirmation and no backup. | Even after F1 is fixed, a scheduler misconfiguration or one mistyped manual call wipes all customer data. There is no recovery path, because the store is in memory. | Remove `purge`. If it is truly needed, make it a separate, separately authorised operation with a backup step. **Repro:** the same call as F1 with a valid scheduler credential still wipes `DOCS`. | y/y/y/n |
| F3 | Medium | CONFIRMED | B | `test_app.py:20-21` | `test_reindex` only checks for a 200 on an unauthenticated call, so it confirms the bug in F1. There is no test for rejecting a missing credential, and no test for `purge`. Mutation check (not run): this test cannot go red for an auth regression, because there is no auth to remove. | A future change that leaves the endpoint open passes CI. "4 tests pass" gives false assurance. | Add a test that no token or a user token on `/internal/reindex` gives 401/403. Add a test that a user token cannot purge. After the fix, the current test should fail until it supplies a credential. | y/y/n/y |
| F4 | Medium | PROBABLE | B | `auth.py:3` | Bearer tokens are hardcoded in source as `{"tok-ann": "ann", "tok-bo": "bo"}`. | If this module ships as-is, anyone who can read the repo can authenticate as `ann` or `bo` and read or delete their documents. | Load credentials from a secret store. Confirm whether this file is a fixture or the production module. | y/n/y/n |

## NEEDS VALIDATION

- **S1. Drift from "keep the document API as it is":** whether `handle`'s `/api/*` branches differ from the previous version. Settled by a diff against the pre-change `app.py`, which was not supplied.
- **S2. Crash when `query` is `None`:** `request.get("query", {}).get(...)` at `app.py:26` raises if the adapter passes `"query": None`. That would turn the nightly reindex into a 500. Settled by knowing the real request adapter.
- **S3. Whether a private path exists for the scheduler:** whether the scheduler can reach `docs-app:8000` without going through the proxy, and whether port 8000 is otherwise closed. This determines how F1 should be fixed.

## REFUTED

- **Candidate: a user can delete another user's document.** Refuted. `store.delete_doc` checks the owner (`store.py:18`), and `test_cannot_delete_other_users_doc` covers it.

## WHAT HOLDS UP

- Authentication is enforced before every `/api/*` route.
- Listing is filtered by owner.
- Deletion checks the owner and returns 404 instead of leaking whether a document exists.
- `rebuild_index` itself is harmless.

## UNVERIFIED CLAIMS

- **"4 tests pass":** not run here. Confirm with `python -m unittest test_app`.
- **"Called only by the scheduler on the private network" (the code comment):** contradicted by `proxy.conf:7`. Confirm the actual network path.

## QUESTIONS FOR THE AUTHOR

1. Why was `purge` added, and who asked for it?
2. Can the scheduler call the app directly on the private network?
3. Is `auth.py` the production auth module?

## DECISION-MAKER SUMMARY

Do not release. The reindex endpoint is open to the internet with no authentication, and one request can delete every customer document. Before release:
- Remove the public `/internal/` proxy route.
- Require a scheduler credential on the endpoint.
- Remove `purge`.
- Add tests that reject unauthenticated calls.

## OWNER SUMMARY

The new nightly maintenance feature can be triggered by anyone on the internet without logging in, and one variant of it erases all customer documents. It needs to be locked down so only the scheduler can call it, and the erase option should be removed before release. The rest of the documents service looks sound.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "deploy/proxy.conf", "status": "seen", "matters": true},
    {"item": "previous app.py (API baseline)", "status": "not_seen", "matters": true},
    {"item": "scheduler config and network ACLs", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code and fixture tokens only; no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "app.py:internal", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "deploy/proxy.conf", "kind": "config"}
    ],
    "not_checked": [
      {"unit": "runtime behaviour", "reason": "no tools; code not executed"},
      {"unit": "scheduler config", "reason": "not supplied"},
      {"unit": "previous app.py", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:8-9, app.py:24-28, deploy/proxy.conf:7",
     "scenario": "Anonymous internet client sends POST https://docs.example.test/internal/reindex?purge=1; the public proxy forwards it, internal() checks no token, and store.delete_all() erases every customer's documents.",
     "fix": "Remove location /internal/ from the public proxy, route the scheduler over the private network, and require a scheduler credential in internal().",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/internal/reindex','POST',query={'purge':'1'}) with no token returns 200 and empties store.DOCS; expected 401."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:26-27",
     "scenario": "A purge option the request never asked for wipes all documents on one query flag; a scheduler misconfiguration or a typo destroys in-memory data with no recovery.",
     "fix": "Remove purge; if it is needed, make it a separate, separately authorised operation with a backup.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "Call /internal/reindex with purge=1 using a valid credential; DOCS becomes empty."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:20-21",
     "scenario": "test_reindex asserts 200 for an unauthenticated call, so an open endpoint passes CI; there is no auth or purge test.",
     "fix": "Add tests that no token or a user token gets 401/403 on /internal/reindex and that purge is not reachable.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "The current suite passes with the endpoint fully open."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:3",
     "scenario": "If this module ships, anyone with repo access can authenticate as ann or bo using the hardcoded tokens.",
     "fix": "Load tokens from a secret store; confirm whether the file is a fixture.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "req('/api/docs', token='tok-ann') returns ann's documents."},
    {"id": "S1", "status": "needs_validation", "track": "A", "location": "app.py:handle",
     "suspicion": "The /api/* behaviour may have changed, contrary to 'keep the document API as it is'.",
     "unresolved_fact": "A diff against the pre-change app.py, which was not supplied."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:26",
     "suspicion": "request.get('query', {}).get raises if query is None, which would turn the nightly reindex into a 500.",
     "unresolved_fact": "How the real HTTP adapter populates request['query']."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "deploy/proxy.conf:7",
     "suspicion": "There may be no private network path for the scheduler, which affects how F1 is fixed.",
     "unresolved_fact": "Scheduler network path and firewall rules for docs-app:8000."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A user can delete another user's document.",
     "evidence": "store.delete_doc checks the owner at store.py:18; test_cannot_delete_other_users_doc covers it."}
  ]
}
```