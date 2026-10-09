# Redteam report: admin reindex for the documents service

> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available. Nothing was executed. Every CONFIRMED finding below rests on tracing the supplied code line by line, and each comes with an exact test you can run to confirm it.

**VERDICT: REWORK.** Anyone on the internet can call the new reindex endpoint without a token, through the production proxy, and add `purge=1` to permanently delete every customer's documents.

**CONFIDENCE: medium.** The main defect is plain from the code and the config. Confidence is limited because this is a same-context review, nothing was run, and the pre-change version and the scheduler/network config were not supplied.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | yes |
| app.py, auth.py, store.py, test_app.py, deploy/proxy.conf | seen (full text) | yes |
| Diff or pre-change version | **not supplied** | yes. I cannot tell which lines are new, so I cannot fully check "keep the document API as it is". |
| Scheduler config (how it calls reindex, whether it sends `purge`) | not supplied | yes, for the purge finding |
| Network/firewall config for `docs-app:8000` | not supplied | yes, for who can reach the app directly |
| Test run output ("4 tests pass") | not seen; assertion only | low. The tests would pass on the vulnerable code anyway. |

## COVERAGE

- **Scope:** the whole supplied work. All five files and both documents were read.
- **Checked:**
  - `app.py:handle`, `app.py:internal`
  - `auth.authenticate`
  - every function in `store.py`
  - all 4 tests
  - both `location` blocks in `proxy.conf`
  - the claim in the code comment at `app.py:24`
- **Not checked:**
  - scheduler config (not_supplied)
  - network/firewall config (not_supplied)
  - the prior version (not_supplied)
  - runtime behavior (no_tools)

## SEATS AND GATE

- **Seats:** local same-context reviewer only. No subagent is available. No cross-vendor seats were requested.
- **Sensitivity gate:** the supplied material is code and config only, with no customer data. It would not have blocked a second seat.
- **Note:** `auth.py` contains literal tokens, possibly real ones. See S1.

## Pass 1: Reconstruct

**What the work does.** The work adds `POST /internal/reindex`, which rebuilds the index. With `?purge=1` it first deletes every document. The handler takes no token, on the premise stated at `app.py:24`: "Called only by the scheduler on the private network". The existing `/api/docs` routes are unchanged.

**What must be true for it to be correct:**
- `/internal/` is unreachable from untrusted networks.
- Nothing untrusted can reach `docs-app:8000` directly.
- The purge mode is wanted and safe.

The first assumption is contradicted by `proxy.conf:7`.

**Tracks:** B (code), with D (scope of purge).

**Trust boundaries:**

| Principal | Route | Check |
|---|---|---|
| Internet client | `proxy:443` → `/api/*` | token check |
| Internet client | `proxy:443` → `/internal/*` | **none** |
| Private-network host | `docs-app:8000` → `/internal/*` | **none** |
| Scheduler | either route | none |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `deploy/proxy.conf:7` | The production edge proxy forwards `/internal/` from the public `listen 443` server to the app, with no `allow`/`deny`, no auth and no IP restriction. The comment on the same line says the scheduler uses this public route. This contradicts the "private network" premise at `app.py:24`. | An internet user sends `POST https://docs.example.test/internal/reindex?purge=1` with no token. The proxy forwards it, `store.delete_all()` runs, and every customer's documents are gone. The store is in memory, so there is no recovery. | Remove the `/internal/` location from the public server, or restrict it (`allow <scheduler IP>; deny all;` or mTLS), and also do F2. **Repro:** `curl -X POST 'https://docs.example.test/internal/reindex?purge=1'` against staging. Expected 403/404; the trace predicts 200 "reindexed" followed by an empty `GET /api/docs` for every user. | T/T/T/T |
| F2 | Critical | CONFIRMED (traced) | B | `app.py:8-9`, `app.py:23-29` | `/internal/` is dispatched *before* `auth.authenticate` (line 8). `internal()` has no credential check at all. Network placement is the only control, and it is not real. | Even after F1 is fixed, any process that can reach `docs-app:8000` (another service, a compromised pod, an SSRF in a neighbour) can call `POST /internal/reindex?purge=1` and wipe all documents. | Require a dedicated scheduler credential (an admin token or a shared secret compared in constant time) inside `internal()`. Return 401/403 otherwise. **Repro test:** `r = req("/internal/reindex","POST", query={"purge":"1"}); assert r["status"] in (401,403); assert store.DOCS`. On the current code the trace gives status 200 and `store.DOCS == {}`, so this test goes red. | T/T/T/T |
| F3 | High | CONFIRMED (traced) | B/D | `app.py:25-26`, `store.py:27-28` | Drift: the request asks for a nightly *reindex*. The work adds an unrequested destructive `purge` mode that deletes **all users'** documents. It has no confirmation, no backup, no audit record and no test. | A scheduler job or an operator adds `purge=1` (copied from a runbook, or while debugging). Every customer document is deleted irreversibly, and nothing records who did it. | Remove `purge` from the reindex endpoint. If a purge is genuinely needed, make it a separate, authenticated, audited operation with an explicit confirmation step. **Repro:** `req("/internal/reindex","POST", query={"purge":"1"})` then `req("/api/docs", token="tok-bo")["body"]`. Expected: bo's "budget" is still present (the request was only for reindex). Traced result: `[]`. | T/T/F/F. Rule 8 sets drift at High minimum. |
| F4 | Medium | CONFIRMED (traced) | B | `test_app.py:20-21` | `test_reindex` asserts that an **unauthenticated** call succeeds, so the test encodes the F2 bug as intended behavior. No test covers `purge`, auth on `/internal/`, or that the index version changed. "4 tests pass" therefore says nothing about safety. | A fix for F2 makes this test fail, which pushes the next author to weaken the fix. A regression that re-opens the endpoint stays green. | Replace it with three tests: no token → 401/403; scheduler credential → 200 and `store.INDEX["version"]` incremented; purge rejected or absent. **Repro:** the test passes on the current code with `token=None`, which shows it cannot detect F2. | T/T/F/T |
| F5 | Low | CONFIRMED (traced) | B | `app.py:25` | `request.get("query", {}).get(...)` crashes with `AttributeError` when the key is present but `None`. The tests always pass `{}`, which hides this. | A scheduler or framework sends `query: None`. The request crashes with a 500 and the nightly reindex silently fails. | Use `(request.get("query") or {}).get("purge")`. **Repro:** `app.handle({"path":"/internal/reindex","method":"POST","query":None})`. Expected 200; the trace predicts `AttributeError`. | T/T/F/F |

### Sibling search for F1, F2 and F3

**F1** (root cause: route exposed at the proxy).
- **Searched:** both `location` blocks in `proxy.conf`.
- **Found:** `/api/` is also public, but it is gated by tokens in the app. F2 is the app-side sibling and is recorded separately.
- **Security finding:** yes.
- **Boundary:**
  - principal: unauthenticated internet client
  - input: request path and query string
  - failed control: none at the proxy
  - boundary crossed: internet → admin/destructive action
  - resource: all customer documents

**F2** (root cause: missing check before a destructive sink).
- **Searched:** every route dispatched before `authenticate` (only the `/internal/` prefix) and every caller of `store.delete_all` and `store.rebuild_index` (only `internal()`).
- **Found:** no other unauthenticated sink.
- **Security finding:** yes.
- **Boundary:**
  - principal: any host that can reach `docs-app:8000`
  - input: path and query
  - failed control: the code comment's "private network" premise, with no real check
  - boundary crossed: network peer → admin
  - resource: all documents

**F3** (root cause: unrequested destructive mode).
- **Searched:** other unrequested additions across `app.py` and `store.py`.
- **Found:** `delete_all` is the only one.
- **Security finding:** no. It is a data-loss and scope finding, and it is exploitable only through F1/F2.

## NEEDS VALIDATION

- **S1** (`auth.py:3`). The tokens are hardcoded in source (`tok-ann`, `tok-bo`). If these are real production credentials, anyone with read access to the repository or its history can act as these users. **Fact that would settle it:** whether production loads tokens from elsewhere, and whether this file predates the change.
- **S2** (`store.py:1`, `store.py:31-32`). The store is "in-memory" and `rebuild_index` only bumps a counter. **Fact that would settle it:** whether this is a stand-in for a real store and index. If it is the production implementation, the reindex does no real work and every restart loses data.
- **S3** (`app.py:17-18`, `app.py:15-16`). A non-integer id on DELETE (`int()` raises `ValueError`) or a missing body on POST (`TypeError`) produces an unhandled exception. **Fact that would settle it:** the prior version. If it is pre-existing, it is out of scope under "keep the API as it is".

## REFUTED

- **Candidate:** the reindex change altered `/api/docs` behavior. **Evidence:** the `/api/` branches only call `list_docs`, `add_doc` and `delete_doc`, which do not touch `INDEX` or `delete_all`. Ownership checks still hold (`store.py:19`). There is a caveat: without the prior version this cannot be fully confirmed, and a purge (F3) does change what the API returns.

## WHAT HOLDS UP

- Token authentication gates every `/api/` route (`app.py:10-12`).
- `delete_doc` enforces ownership (`store.py:19`), and a test covers this.
- `list_docs` filters by owner.
- `rebuild_index` itself is harmless and idempotent in effect.

## UNVERIFIED CLAIMS

- **"4 tests pass".** Not run. Confirm with `python -m unittest test_app`. Note that passing does not address F2 (see F4).
- **"Called only by the scheduler on the private network"** (`app.py:24`). Contradicted by `proxy.conf:7`. Confirm the actual network path with the infrastructure owner.
- **"The file that runs in production"** (`proxy.conf:1`). Confirm against the deployed proxy config by checksum, not by the repository.

## QUESTIONS FOR THE AUTHOR

1. Is `purge` required by anyone? If not, can it be removed?
2. What credential can the scheduler present, and can it reach the app without going through the public proxy?
3. Are the tokens in `auth.py` real production credentials?

## DECISION-MAKER SUMMARY

Do not release. The new reindex endpoint is publicly reachable without any login, and one parameter on it deletes every customer document. If shipped as is, the first person who finds `/internal/reindex?purge=1` can irreversibly wipe all customer data. Fix this by:
- blocking the route at the proxy,
- requiring a scheduler credential in the app,
- removing the purge option,
- replacing the test that currently certifies the hole.

## OWNER SUMMARY

The new nightly maintenance feature can be triggered by anyone on the internet without logging in. One option on it deletes every customer's documents permanently. It needs to be locked down and the delete option removed before release.

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
    {"item": "pre-change version / diff", "status": "not_seen", "matters": true},
    {"item": "scheduler config", "status": "not_seen", "matters": true},
    {"item": "network/firewall config for docs-app:8000", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "code and config only; auth.py holds literal tokens of unknown status (S1)"},
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
      {"unit": "app.py:24 'private network' premise", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "pre-change version / diff", "reason": "not_supplied"},
      {"unit": "scheduler config", "reason": "not_supplied"},
      {"unit": "network/firewall config", "reason": "not_supplied"},
      {"unit": "runtime execution of tests and reproductions", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "deploy/proxy.conf:7",
     "scenario": "An unauthenticated internet client sends POST https://docs.example.test/internal/reindex?purge=1; the public proxy forwards it and all customer documents are deleted irreversibly.",
     "fix": "Remove /internal/ from the public server block or restrict it to the scheduler (allow/deny or mTLS), in addition to F2.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "curl -X POST 'https://docs.example.test/internal/reindex?purge=1' against staging with no token; expected 403/404, traced result 200 'reindexed' and empty GET /api/docs for every user. Not executed in this review.",
     "security": true,
     "boundary": {"principal": "unauthenticated internet client", "input": "request path and query string", "control": "no access restriction on location /internal/", "crossed": "internet to admin/destructive action", "resource": "all customer documents"},
     "siblings_searched": {"searched": "all location blocks in deploy/proxy.conf", "found": "/api/ also public but token-gated in app; app-side sibling recorded as F2"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:8-9, app.py:23-29",
     "scenario": "Any host that can reach docs-app:8000 calls POST /internal/reindex?purge=1 with no credential; internal() runs store.delete_all() and all documents are lost.",
     "fix": "Require a dedicated scheduler credential inside internal() (constant-time compare) and return 401/403 otherwise.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "r = req('/internal/reindex','POST', query={'purge':'1'}); assert r['status'] in (401,403); assert store.DOCS. Traced on current code: status 200 and store.DOCS == {} (test goes red). Not executed in this review.",
     "security": true,
     "boundary": {"principal": "any network peer able to reach docs-app:8000", "input": "path and query", "control": "no credential check; reliance on a 'private network' comment", "crossed": "network peer to admin", "resource": "all customer documents"},
     "siblings_searched": {"searched": "routes dispatched before auth.authenticate; callers of store.delete_all and store.rebuild_index", "found": "only /internal/ prefix and internal(); no other unauthenticated sink"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:25-26, store.py:27-28",
     "scenario": "A scheduler job or operator passes purge=1; every user's documents are deleted with no confirmation, backup or audit record. The request asked only for a reindex.",
     "fix": "Remove purge from the reindex endpoint; if needed, make it a separate authenticated, audited, confirmed operation.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "req('/internal/reindex','POST', query={'purge':'1'}); then req('/api/docs', token='tok-bo')['body']; expected bo's 'budget' present, traced result []. Not executed in this review.",
     "security": false,
     "siblings_searched": {"searched": "other unrequested additions across app.py and store.py", "found": "delete_all is the only one"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:20-21",
     "scenario": "test_reindex asserts an unauthenticated call returns 200, encoding the F2 bug; a fix makes it fail and a regression reopening the endpoint stays green. No test covers purge or index change.",
     "fix": "Replace with tests: no token -> 401/403; scheduler credential -> 200 and INDEX version incremented; purge absent or rejected.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "The test passes with token=None on current code, showing it cannot detect F2."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:25",
     "scenario": "A caller sends query=None; request.get('query', {}) returns None and .get raises AttributeError, so the nightly reindex fails with a 500.",
     "fix": "Use (request.get('query') or {}).get('purge').",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "app.handle({'path':'/internal/reindex','method':'POST','query':None}); expected 200, traced AttributeError. Not executed in this review."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:3",
     "suspicion": "Hardcoded user tokens in source may be real production credentials.",
     "unresolved_fact": "Whether production loads tokens from elsewhere and whether this file predates the change."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "store.py:1, store.py:31-32",
     "suspicion": "In-memory store and counter-only rebuild_index may be a stub presented as production code.",
     "unresolved_fact": "Whether this is the production store/index implementation."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "app.py:15-18",
     "suspicion": "Non-integer DELETE id or missing POST body raises an unhandled exception.",
     "unresolved_fact": "Whether this behavior predates the change (prior version not supplied)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The reindex change altered /api/docs behavior.",
     "evidence": "The /api/ branches call only list_docs, add_doc and delete_doc, none of which touch INDEX or delete_all; ownership check at store.py:19 intact. Caveat: prior version not supplied."}
  ]
}
```

I could not run `tools/validate_findings.py` against this block in this session.