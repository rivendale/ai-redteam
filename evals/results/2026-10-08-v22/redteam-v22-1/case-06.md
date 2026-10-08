# Redteam report: notes service request handlers

**Same-context review, no tools: anchoring risk. Re-run in a fresh session with tools for anything high-stakes.** No subagent or code execution was available in this session. Every result below comes from reading and hand-tracing the supplied source. Nothing was run.

**VERDICT: REWORK.** `/admin/export` returns every user's private notes to any valid token, including non-admins, which breaks the core access rule in the request.

**CONFIDENCE: medium.** The headline finding comes from a direct trace of a short code path. Confidence is limited by no execution, a single reviewer, and not knowing whether `_TOKENS` and the in-memory `_NOTES` are the real production backends.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, app.py, auth.py, store.py, test_app.py.
- **Not seen:**
  - The test run output behind "passes (5 tests)". This matters little: 5 test methods exist, and passing is consistent with the trace.
  - The deployment and framework that call `handle()`. This matters for how uncaught exceptions surface (F3, F4).
  - The production token and storage backends. This matters for S1 and S2.
- **Embedded instructions aimed at the reviewer:** none found.

**COVERAGE**
- **Checked:**
  - app.py:handle, every route branch and both exception paths.
  - auth.py:current_user and require_admin.
  - store.py, all four functions.
  - test_app.py, all 5 tests.
  - The request's four access rules: own notes, admin users, admin export, 401/403.
- **Not checked:** the runtime and framework, the production config, and concurrency under a real server.

**SEATS AND GATE:** One local same-context reviewer ran. No cross-vendor seats ran, because the user did not ask for them and none are available. Sensitivity gate: the code contains only fixture data, no real personal data, so it is not sensitive.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | app.py:25-26 | `/admin/export` never calls `auth.require_admin(user)`. Only `/admin/users` (line 23) does. | Alice sends `GET /admin/export` with `tok-alice`. `current_user` succeeds and nothing raises `AuthError`, so she gets 200 with `{"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}`. Every customer's private notes leak to any logged-in user. | Add `auth.require_admin(user)` before `store.export_all()`. Repro test: `self.assertEqual(req("/admin/export","tok-alice")["status"], 403)`. Expected 403; the current code returns 200 with all notes. | y/y/y/y |
| F2 | High | CONFIRMED | B | test_app.py (no export tests) | No test covers `/admin/export`, for either the 403 or the 200 case. The admin check is tested on one route only, so F1 passed CI. "5 tests pass" says nothing about export. | Any later refactor that drops or misplaces an admin check on a route without a test ships silently. That already happened here. | Add `test_admin_export_is_forbidden_for_non_admin` (fails today) and `test_admin_export_allowed_for_admin`. Better: one table-driven test asserting 403 for a non-admin on every `/admin/*` route. | y/y/n/y |
| F3 | Medium | PROBABLE | B | auth.py:14 | With `str` arguments, `hmac.compare_digest` raises `TypeError` unless both are ASCII-only. A non-`str`, non-bytes token (an int, for example) also raises `TypeError`. Only `AuthError` is caught (app.py:12). | A client sends token `"tök"` or `123`. `TypeError` propagates out of `handle()`, giving a 500 or crash instead of the required 401. | In `current_user`, reject tokens that are not ASCII `str` by raising `AuthError`, or compare `.encode()` bytes. Repro: `req("/notes","tök")`. Expected 401; observed `TypeError` (to be confirmed by running). | y/n/y/n |
| F4 | Low | CONFIRMED | B | app.py:15, 20 | `request["path"]`, `request["method"]` and `request["body"]` use indexing, so a missing key raises `KeyError`, which is uncaught. | A POST without `"body"` produces `KeyError` and a 500 instead of a 4xx. | Use `.get()` and return 400 for a missing or invalid body. Repro: `handle({"path":"/notes","method":"POST","token":"tok-bob"})` raises `KeyError`. | y/y/n/n |
| F5 | Low | CONFIRMED | B | store.py:10-11 | `add_note` stores any body unvalidated. `None` becomes `"bob: None"`, and lists or dicts are stringified. | A POST with an empty or JSON-object body stores junk notes. | Validate that the body is a non-empty `str` in the handler and return 400 otherwise. Repro: `req("/notes","tok-bob","POST",None)`, then GET shows `"bob: None"`. | y/y/n/n |

## NEEDS VALIDATION
- **S1, auth.py:4:** The admin token `tok-root` and the user tokens are hardcoded in source. *Unresolved fact:* is `_TOKENS` the production token source or a fixture? If it ships as-is, anyone who can read the repo is admin, and that would be Critical.
- **S2, store.py:3:** Notes live only in process memory. *Unresolved fact:* is this the production store? If so, every restart loses all notes, and multi-worker deploys show different data per worker.
- **S3, test_app.py:15:** `test_post_creates` mutates the shared module-level `_NOTES` (it appends to bob's notes). *Unresolved fact:* does the test runner order or parallelize tests in a way that affects other assertions? It does not affect the current 5 tests.

## REFUTED
- **R1:** "A non-admin hitting an unknown `/admin/foo` gets 404, not 403." The request defines 403 for the `/admin` routes it lists, and returning 404 for nonexistent routes does not expose data. Not a defect.
- **R2:** "The token loop leaks timing." Each comparison is constant-time. The early return reveals at most which table slot matched, not token bytes, and with three fixed tokens this is not exploitable in a realistic way.
- **R3:** "Users can read other users' notes via `/notes`." `list_notes` keys strictly on `user[0]` from the authenticated token (store.py:7), and `test_user_sees_only_own_notes` covers it. This holds.

## WHAT HOLDS UP
- Missing or unknown tokens return 401: `token or ""` handles `None`, and `AuthError` is caught at app.py:12.
- `/notes` GET and POST are scoped to the caller's own notes.
- `/admin/users` correctly returns 403 for non-admins and 200 for admins. Removing line 23 would turn `test_admin_users_is_forbidden_for_non_admin` red, by trace; this was not executed.
- `export_all` and `list_notes` return copies, so callers cannot mutate the store.

## UNVERIFIED CLAIMS
- "test_app.py passes (5 tests)." Confirm by running `python -m unittest test_app -v`. Even if true, it does not cover F1.
- F3's `TypeError` behavior. Confirm by running `hmac.compare_digest("tok-alice", "tök")`.

## QUESTIONS FOR THE AUTHOR
1. Are `_TOKENS` and `_NOTES` the production backends, or placeholders to be replaced before deploy? (S1, S2)
2. What does the hosting layer do with an exception escaping `handle()`? Does it return a 500 or crash the worker? (F3, F4)

## DECISION-MAKER SUMMARY
Do not deploy. `/admin/export` hands every customer's notes to any logged-in user (F1), and the test suite cannot catch it (F2). The fix is one line plus two tests. If this ships as-is, private data is exposed immediately, with no way to recall it.

## OWNER SUMMARY
The new notes service has a missing permission check: any ordinary user can download every customer's private notes through the admin export page. The fix is small, but it must go in, together with a test that proves it works, before the service reaches production. A few smaller issues cause errors on unusual input and should be tidied up at the same time.

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
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "production token and storage backends", "status": "not_seen", "matters": true},
    {"item": "hosting framework calling handle()", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code contains only fixture data; no real personal data supplied."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current_user", "kind": "function"},
      {"unit": "auth.py:require_admin", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md access rules (401/403, own notes, admin routes)", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "hosting runtime / framework", "reason": "not supplied"},
      {"unit": "production config (tokens, storage)", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:25-26",
     "scenario": "A non-admin (tok-alice) sends GET /admin/export; no require_admin call exists on that branch, so the handler returns 200 with every user's notes.",
     "fix": "Call auth.require_admin(user) before store.export_all().",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/admin/export', 'tok-alice'): expect status 403, observe 200 with alice, bob and root notes."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py (no /admin/export tests)",
     "scenario": "The admin check is tested only on /admin/users; a missing check on /admin/export (F1) passes all 5 tests and ships.",
     "fix": "Add 403-for-non-admin and 200-for-admin tests for /admin/export, ideally table-driven over all /admin routes.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add assertEqual(req('/admin/export','tok-alice')['status'], 403); it fails on the current code."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:14",
     "scenario": "A non-ASCII str or non-str token makes hmac.compare_digest raise TypeError, which is not caught, so the client gets a 500 or crash instead of 401.",
     "fix": "Raise AuthError for tokens that are not ASCII str, or compare encoded bytes.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "req('/notes', 'tök'): expect 401, expect TypeError (unexecuted)."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:15,20",
     "scenario": "A request missing 'path', 'method' or (on POST) 'body' raises an uncaught KeyError instead of returning 4xx.",
     "fix": "Use request.get() and return 400 for a missing or invalid field.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "handle({'path':'/notes','method':'POST','token':'tok-bob'}) raises KeyError."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:10-11",
     "scenario": "A POST with body None or a non-string stores a junk note such as 'bob: None'.",
     "fix": "Validate that the body is a non-empty str in the handler; return 400 otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "req('/notes','tok-bob','POST',None), then GET /notes shows 'bob: None'."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:4",
     "suspicion": "Admin and user tokens are hardcoded in source.",
     "unresolved_fact": "Whether _TOKENS is the production token source or a test fixture."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "store.py:3",
     "suspicion": "Notes are held only in process memory and are lost on restart.",
     "unresolved_fact": "Whether the in-memory _NOTES is the production store."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "test_app.py:15",
     "suspicion": "test_post_creates mutates shared module state, which may couple tests.",
     "unresolved_fact": "Whether the test runner reorders or parallelizes tests in a way that makes other assertions depend on it."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Unknown /admin/* paths should return 403, not 404.",
     "evidence": "The request specifies 403 for the defined /admin routes; a 404 for a nonexistent route exposes no data."},
    {"id": "R2", "candidate": "The token comparison loop leaks token contents via timing.",
     "evidence": "Each comparison uses hmac.compare_digest; the early return reveals at most which slot matched, not token bytes."},
    {"id": "R3", "candidate": "Users can read other users' notes via /notes.",
     "evidence": "list_notes keys on user[0] from the authenticated token (store.py:7); covered by test_user_sees_only_own_notes."}
  ]
}
```