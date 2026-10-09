VERDICT: **REJECT.** Production exposes the new reindex endpoint to the internet with no authentication, and `?purge=1` deletes every customer document.

CONFIDENCE: **medium.** I traced the defects line by line, but I had no tools, so nothing was executed. The reproductions below are derived, not observed. The scheduler config, network topology and pre-change version of the service were not supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, app.py, auth.py, store.py, test_app.py, deploy/proxy.conf.
- **Not seen: pre-change app.py (diff or prior commit).** This matters. The request says "keep the document API as it is", and I cannot diff the `/api/` routes against what was there before.
- **Not seen: scheduler job definition.** This matters. It would show whether the scheduler ever sends `purge=1` and which hostname it calls.
- **Not seen: network/firewall rules in front of the proxy.** This matters, but only to confirm the proxy listens on a public interface. The `server_name` and `listen 443 ssl` strongly suggest it does.
- **Not seen: output of the "4 tests pass" run.** This matters little, since the tests do not cover the defects anyway.

COVERAGE:
- **Checked:** app.py (`handle`, `internal`), store.py (`delete_all`, `rebuild_index`, `delete_doc`), auth.py (`authenticate`), test_app.py (all 4 tests), deploy/proxy.conf (both `location` blocks). I also checked the request's three requirements: admin, nightly scheduler, API unchanged.
- **Not checked:** the `/api/` behaviour against its previous version (not supplied), and runtime behaviour (no tools).

SEATS AND GATE:
- Single reviewer: this instance, with no tools and no subagent available.
- The work was not written in this conversation, but this is still one unchecked read. Re-run with tools before relying on it.
- The data is synthetic fixtures (`ann`/`bo`, example tokens), so the sensitivity gate passed. No cross-vendor seats were requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B, R | app.py:8-9, 23-29; deploy/proxy.conf:7 | Any path under `/internal/` is dispatched before `auth.authenticate`. `internal()` has no credential or admin check, and relies on the comment's claim that only the private network can reach it (line 24). The production proxy forwards `/internal/` from public port 443 with no `allow`/`deny`, and its own comment says the scheduler uses that same public path. The request asked for an *admin* reindex; nothing checks admin. | Anyone on the internet sends `POST https://docs.example.test/internal/reindex?purge=1`. Request reaches `internal()` → `store.delete_all()` → every customer's documents are erased. No token, no log entry. Without `purge`, anyone can trigger reindexes at will. | **Fix:** (1) Require a scheduler/admin credential inside `internal()`, and do not bypass auth by path prefix. (2) Remove the `location /internal/` block from proxy.conf, or restrict it with `allow <scheduler IP>; deny all;`. Point the scheduler at `docs-app:8000` on the private network, because removing the block alone breaks the nightly job. **Repro:** `req("/internal/reindex","POST",query={"purge":"1"})` with no token, then `req("/api/docs",token="tok-ann")`. Expected 401/403 and `["plan"]`; derived result is 200 and `[]`. Add this as a test asserting 401. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED | B, D | app.py:26-27; store.py:24-25 | The `purge` parameter was not requested. The request asked for a reindex only. `purge` adds an irreversible delete-everything mode with no confirmation, no backup and no audit record. It is the reason F1 means data loss rather than nuisance. | Even after F1 is fixed, one scheduler or operator misconfiguration that adds `purge=1` wipes all customer documents nightly with no trace. | **Fix:** Remove `purge` (lines 26-27) and `store.delete_all`. If a purge is truly needed, make it a separate, audited, admin-only operation. **Repro:** the call in F1 with a valid scheduler credential still clears `DOCS`. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED | B | test_app.py:19-20 | `test_reindex` calls the endpoint with **no token** and asserts 200. It encodes the F1 hole as expected behaviour. No test covers `purge`, admin authorization, or that `/api/` routes still reject missing tokens after the new prefix branch. "4 tests pass" therefore says nothing about the risky change. | A fix that adds auth to `internal()` turns this test red, which invites someone to "fix" the test back. The purge path is never exercised. | **Fix:** Replace it with: no token → 401; non-admin token → 403; scheduler credential → 200 with the index version incremented and the docs untouched. Mutation check: delete the auth check and confirm the new test fails. | a✓ b✓ c✗ d✓ |

**Answers to the a/b/c/d questions for F1:** (a) the scenario is concrete; (b) it is traced through exact lines; (c) it loses customer data and is a security breach; (d) public endpoints are routinely scanned. That makes it **Critical**.

## NEEDS VALIDATION

- **S1.** Is the `/api/docs` behaviour (lines 13-20) unchanged from before? Settled by the pre-change app.py or the diff.
- **S2.** Is auth.py's hardcoded `TOKENS` dict the production auth, or a stand-in? Settled by the deploy manifest or real auth module. If it is production, static tokens in source are a separate High.
- **S3.** Does the proxy listen on a publicly reachable interface? Settled by the firewall/LB config. The `server_name` and port 443 strongly suggest yes, and nothing in the supplied config suggests otherwise.
- **S4.** Does the scheduler currently send `purge=1`? Settled by the scheduler job definition. If it does, F2 becomes nightly loss of all data.

## REFUTED

- **R1.** "`request.get("query", {}).get(...)` crashes when query is absent." The default `{}` handles a missing key. A `None` value would crash, but the test harness always supplies a dict. This is unverified for the real server adapter, but it is not a finding.
- **R2.** "`test_reindex` mutates shared state and breaks other tests." It does not purge. `rebuild_index` only bumps `INDEX`, so the `DOCS` fixtures used by the other tests are unaffected.

## WHAT HOLDS UP

- `/api/` routes all sit behind `auth.authenticate` (app.py:10-12).
- `delete_doc` checks ownership before deleting, and a missing doc returns 404 without leaking existence (store.py:18-19).
- `list_docs` filters by owner.
- `rebuild_index` itself is harmless and idempotent in effect.

## UNVERIFIED CLAIMS

- **"4 tests pass."** I could not run them. Reading the code, all four would pass. Confirm with `python -m unittest test_app`.
- **"Called only by the scheduler on the private network"** (app.py:24). This is contradicted by proxy.conf:7, including its own comment.
- **The proxy file "runs in production."** Taken from context.md. Confirm against the deployed config by checksum.

## QUESTIONS FOR THE AUTHOR

1. Why was `purge` added, and does the scheduler use it?
2. How should the scheduler authenticate? Is there an admin role or a service credential available?
3. Can the scheduler reach `docs-app:8000` directly, so `/internal/` can be dropped from the public proxy?

## DECISION-MAKER SUMMARY

Do not release. Anyone on the internet can call the new reindex endpoint without logging in, and one URL parameter erases every customer document. Before release, require a credential on the endpoint, stop the public proxy forwarding `/internal/`, remove the purge option, and replace the test that currently asserts the unauthenticated call succeeds.

## OWNER SUMMARY

The new nightly maintenance feature can be triggered by anyone on the internet without signing in. One version of the call deletes every customer's documents permanently. It needs a login check, must be hidden from the public, and the delete-everything option should be removed before this goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "deploy/proxy.conf", "status": "seen", "matters": true},
    {"item": "pre-change app.py or diff", "status": "not_seen", "matters": true},
    {"item": "scheduler job definition", "status": "not_seen", "matters": true},
    {"item": "network/firewall config in front of proxy", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-instance-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Synthetic fixture data only; no real personal data or credentials."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "app.py:internal", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "store.py:delete_all", "kind": "function"},
      {"unit": "store.py:rebuild_index", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "deploy/proxy.conf", "kind": "config"},
      {"unit": "request: admin-only reindex", "kind": "claim"},
      {"unit": "comment: private-network-only caller", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "/api/ behaviour vs previous version", "reason": "pre-change code not supplied"},
      {"unit": "runtime behaviour and test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:8-9,23-29; deploy/proxy.conf:7",
     "scenario": "Anyone on the internet sends POST https://docs.example.test/internal/reindex?purge=1 with no token; the proxy forwards it, internal() skips auth and calls store.delete_all(), erasing every customer's documents.",
     "fix": "Require a scheduler/admin credential in internal() and stop bypassing auth by path prefix; remove or IP-restrict the /internal/ location in proxy.conf and route the scheduler to docs-app:8000 privately.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/internal/reindex','POST',query={'purge':'1'}) with no token, then req('/api/docs',token='tok-ann'): expected 401 and ['plan'], derived 200 and []."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "app.py:26-27; store.py:24-25",
     "scenario": "Unrequested purge parameter: any scheduler or operator call with purge=1, even after auth is added, irreversibly deletes all documents with no confirmation, backup or audit record.",
     "fix": "Remove the purge branch and store.delete_all; if needed, build a separate audited admin-only purge.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Call /internal/reindex with purge=1 using any accepted credential; store.DOCS becomes empty."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:19-20",
     "scenario": "test_reindex asserts an unauthenticated reindex returns 200, encoding the F1 hole; no test covers purge or admin authorization, so the passing suite gives false assurance and resists the fix.",
     "fix": "Replace with tests: no token -> 401, non-admin -> 403, scheduler credential -> 200 with index bumped and DOCS unchanged; confirm the new test fails when the auth check is removed.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the auth check from F1's fix; test_reindex goes red, showing it asserts the vulnerable behaviour."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "app.py:13-20",
     "suspicion": "The /api/docs behaviour may have changed despite 'keep the document API as it is'.",
     "unresolved_fact": "The pre-change app.py or diff (not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:3",
     "suspicion": "Static tokens hardcoded in source may be the production auth.",
     "unresolved_fact": "Whether auth.py is the deployed auth module or a test stand-in."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "deploy/proxy.conf:3",
     "suspicion": "The proxy is publicly reachable, which makes F1 exploitable from the internet.",
     "unresolved_fact": "Firewall/load-balancer rules in front of the proxy."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "app.py:26",
     "suspicion": "The scheduler may already send purge=1 nightly.",
     "unresolved_fact": "The scheduler job definition (not supplied)."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Missing query key crashes internal().",
     "evidence": "request.get('query', {}) defaults to an empty dict; the harness always supplies a dict."},
    {"id": "R2", "candidate": "test_reindex mutates DOCS and breaks other tests.",
     "evidence": "It does not pass purge; rebuild_index only increments INDEX['version']."}
  ]
}
```