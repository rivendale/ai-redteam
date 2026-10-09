VERDICT: **REWORK.** The new reindex endpoint can be called by anyone on the internet without a token, and with `?purge=1` it deletes every customer document.

CONFIDENCE: **high** for the main finding, which comes from a direct static trace of the code and the production proxy config. Three things limit it:
- **No tools:** nothing was run, including the tests and the reproduction.
- **Not supplied:** the HTTP adapter that builds the `request` dict, the scheduler config, and the previous version of the API.
- **Who reviewed:** one reviewer, with no second instance. The work was not produced in this conversation, so the reviewer does not share the author's context.

INPUTS LEDGER:

| Item | Status | Matters? |
|---|---|---|
| Request, context, `app.py`, `auth.py`, `store.py`, `test_app.py`, `deploy/proxy.conf` | Seen and read in full | — |
| HTTP server/adapter that turns real requests into `{"path","method","token","query",...}` | Not supplied | Partly. It decides whether `?purge=1` reaches `request["query"]`. Plain unauthenticated reindex is reachable either way. |
| Scheduler job config (host it calls, credential, whether it sends `purge`) | Not supplied | Yes, for the fix: the scheduler currently calls through the public proxy. |
| Previous version of the code (diff) | Not supplied | Yes, for "keep the document API as it is". That cannot be confirmed without the baseline. |
| Network ACL / WAF in front of the proxy | Not supplied | Yes. The supplied conf has no `allow`/`deny` and listens publicly on 443. |
| Test run output ("4 tests pass") | Not seen | Low. See F2: the passing reindex test asserts the vulnerable behavior. |

COVERAGE:
- **Checked:**
  - `app.py`: `handle`, `internal`
  - `auth.py`: `authenticate`
  - `store.py`: all six functions
  - `test_app.py`: all four tests
  - `deploy/proxy.conf`: both `location` blocks
  - The assumption "/internal/ is only reachable from the private network"
- **Not checked:** HTTP adapter, scheduler config, prior API version, network layer.
- **Positive control:** my reading of the dispatch does find the auth call on the `/api/` path (`app.py:10`). The absence of any auth on the `/internal/` path is therefore a real absence, not a missed search.

SEATS AND GATE: One reviewer, local, with no tools. No cross-vendor seats were requested at standard depth.
- **Gate:** the supplied files contain sample data and sample tokens (`tok-ann`, `tok-bo`), not real customer records. The stakes are production customer documents, so if real data were attached no external seat should receive it. None were used.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (static trace) | B, A | `app.py:8-9`, `app.py:23-29`; `deploy/proxy.conf:7` | `/internal/*` is dispatched before authentication (`app.py:8-9`). The handler takes no token, based on the comment at `app.py:24`: "Called only by the scheduler on the private network". The production proxy forwards `/internal/` from public `listen 443` with no restriction (`proxy.conf:7`). Its own comment says the scheduler uses the same public proxy. The request asked for an *admin* reindex; the delivered one has no authorization at all. The unrequested `purge` flag (`app.py:26-27`) calls `store.delete_all()`. | Anyone on the internet sends `POST https://docs.example.test/internal/reindex?purge=1` with no token. The proxy forwards the request and the query string (`proxy_pass` with no URI keeps both). `internal()` runs `DOCS.clear()`, and every customer's documents are gone. The store is in memory, and `rebuild_index` only bumps a version number, so nothing restores them. Without `purge`, anyone can still trigger reindexes at will. | **Fix:**<br>1. Require an admin or scheduler credential inside `internal()`, or route `/internal/` through `auth` with an admin role check.<br>2. Remove `location /internal/` from the public proxy, or add `allow <scheduler-ip>; deny all;`, and have the scheduler call `docs-app:8000` on the private network.<br>3. Drop `purge`, which was not requested, or make it a separate, admin-only, audited operation.<br>4. Correct the comment at line 24.<br>**Repro (unit):** `req("/internal/reindex","POST",query={"purge":"1"})`. Expected 401/403; observed 200 and `store.DOCS == {}`.<br>**Repro (edge):** `curl -X POST 'https://docs.example.test/internal/reindex?purge=1'`, then `GET /api/docs` with `tok-ann` returns `[]`. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B | `test_app.py:19-20` | `test_reindex` calls the endpoint with **no token** and asserts 200. It encodes the vulnerability as required behavior. There is no test that an unauthenticated or non-admin caller is rejected, and no test of `purge`. "4 tests pass" therefore gives no assurance about the new endpoint. | A future fix that adds auth turns this test red. The likely "fix" is then to loosen the auth, not the test. Any regression back to an open endpoint stays green. | Replace it with these tests:<br>(i) no token → 401<br>(ii) non-admin user token → 403<br>(iii) admin/scheduler credential → 200, and `DOCS` is unchanged<br>(iv) if purge is kept: non-admin `purge=1` → rejected, and `DOCS` is unchanged<br>Before trusting (i), check that it fails on the current code (it will, at status 200). | a✓ b✓ c✗ d✓ |
| F3 | Low | CONFIRMED | B | `auth.py:3` | User tokens are hardcoded in source. | Anyone with read access to the repo or image can authenticate as `ann` or `bo`. It may predate this change (no diff was supplied). | Load tokens from a secret store or env, and rotate them. It also needs a real admin principal for F1's fix. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1.** Does the production HTTP adapter populate `request["query"]` from the URL query string? If so, the purge path in F1 is reachable exactly as written. If not, check which parameter reaches it. Unauthenticated reindex is reachable either way.
- **S2.** Was the document API (`/api/docs` GET/POST/DELETE) unchanged by this work? This settles "keep the document API as it is". It needs the previous version or diff.
- **S3.** Does the scheduler job send `purge=1`, and what credential could it present? This decides how the fix is rolled out without breaking the nightly job.
- **S4.** Is there any network-level control (security group, WAF, IP allowlist) in front of `docs.example.test` that blocks `/internal/`? The supplied production conf shows none.

## REFUTED
- **"DELETE lets a user delete another user's document."** Refuted. `store.delete_doc` checks the owner at `store.py:18-19`, and `test_cannot_delete_other_users_doc` covers it.
- **"`test_reindex` mutates shared state and breaks other tests."** Refuted. It sends no `purge`, so it only bumps `INDEX["version"]`. It also runs last in alphabetical order.

## WHAT HOLDS UP
- `/api/` routes authenticate before any store access (`app.py:10-12`).
- List and delete are owner-scoped (`store.py:7-8`, `17-21`).
- Unknown routes return 404.
- The non-purge reindex logic itself is trivial and correct.

## UNVERIFIED CLAIMS
- **"4 tests pass".** Not run here. Confirm by running `python3 -m unittest test_app`. Even if they pass, see F2.
- **"Called only by the scheduler on the private network" (`app.py:24`).** This is contradicted by `proxy.conf:7`, which is the basis of F1, not merely unverified.

## QUESTIONS FOR THE AUTHOR
1. Can the scheduler call `docs-app:8000` directly on the private network, and what credential can it carry?
2. Is `purge` actually needed for the nightly job? The request does not mention it.
3. Is there a network control outside `proxy.conf` that blocks `/internal/` today?

## DECISION-MAKER SUMMARY
Do not release. F1 lets any internet caller wipe all customer documents with one unauthenticated request, and the only reindex test (F2) asserts that open behavior. Fix the auth and proxy exposure, drop or lock down `purge`, and replace the test before release. Proceeding anyway risks total, unrecoverable loss of customer data.

## OWNER SUMMARY
The new nightly maintenance feature can be triggered by anyone on the internet without logging in. One option on it erases every customer's documents permanently. It needs to be locked to the scheduler only, and that dangerous option removed, before it goes live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "deploy/proxy.conf", "status": "seen", "matters": true},
    {"item": "HTTP adapter building the request dict", "status": "not_seen", "matters": true},
    {"item": "scheduler job config", "status": "not_seen", "matters": true},
    {"item": "previous version / diff of the document API", "status": "not_seen", "matters": true},
    {"item": "network ACL / WAF in front of proxy", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Supplied files hold sample data and sample tokens only; no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "app.py:internal", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "deploy/proxy.conf", "kind": "config"},
      {"unit": "/internal/ is reachable only from the private network", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "HTTP adapter", "reason": "not supplied"},
      {"unit": "scheduler config", "reason": "not supplied"},
      {"unit": "prior API version", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:8-9, app.py:23-29, deploy/proxy.conf:7",
     "scenario": "An unauthenticated internet caller sends POST https://docs.example.test/internal/reindex?purge=1; the public proxy forwards it, internal() skips auth and calls store.delete_all(), irrecoverably erasing every customer's documents.",
     "fix": "Require an admin/scheduler credential in internal(); remove /internal/ from the public proxy or restrict it to the scheduler IP; drop the unrequested purge flag or make it admin-only and audited; correct the comment at app.py:24.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/internal/reindex','POST',query={'purge':'1'}) with no token: expect 401/403, observe 200 and store.DOCS == {}."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:19-20",
     "scenario": "test_reindex asserts that an unauthenticated reindex returns 200, so the suite enshrines the vulnerability; a regression to an open endpoint stays green and an auth fix turns it red.",
     "fix": "Replace with tests: no token -> 401, non-admin -> 403, scheduler credential -> 200 with DOCS unchanged, non-admin purge rejected with DOCS unchanged.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test: req('/internal/reindex','POST')['status'] == 401; it fails on current code with 200."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:3",
     "scenario": "Anyone with read access to the repo or image can authenticate as ann or bo using the hardcoded tokens.",
     "fix": "Load tokens from a secret store or environment and rotate them.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Read auth.py:3; call /api/docs with token tok-ann; observe ann's documents."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "HTTP adapter (not supplied)",
     "suspicion": "The URL query string reaches request['query'], making purge reachable as written.",
     "unresolved_fact": "How the production adapter builds request['query']."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:13-19",
     "suspicion": "The document API may have changed despite the request to keep it as is.",
     "unresolved_fact": "The previous version or diff of app.py."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "scheduler config (not supplied)",
     "suspicion": "The nightly job may send purge=1 or depend on unauthenticated access.",
     "unresolved_fact": "The scheduler job's URL, parameters and available credential."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "deploy/proxy.conf:7",
     "suspicion": "No network control outside the proxy blocks /internal/.",
     "unresolved_fact": "Whether a security group, WAF or allowlist restricts /internal/ in production."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "DELETE lets a user delete another user's document.",
     "evidence": "store.py:18-19 checks the owner; test_cannot_delete_other_users_doc covers it."},
    {"id": "C2", "candidate": "test_reindex mutates shared state and breaks other tests.",
     "evidence": "It sends no purge, so it only bumps INDEX['version']; DOCS is untouched."}
  ]
}
```