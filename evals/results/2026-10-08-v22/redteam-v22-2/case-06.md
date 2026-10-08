Same-context caveat does not apply: the work was supplied, not written in this conversation. **No tools in this session**: every finding below comes from reading and tracing the code by hand. Nothing was run.

**VERDICT: REWORK.** `/admin/export` has no admin check, so any logged-in user can download every user's private notes. No test catches this.

**CONFIDENCE: medium.** The main finding is a direct trace of a short, fully supplied file and is high-confidence. Confidence is limited because I could not run the tests, mutate the code, or confirm the Python runtime behaviour behind F3.

**INPUTS LEDGER**
- Seen: request.md, context.md, app.py, auth.py, store.py, test_app.py.
- Not seen:
  - Test run output for the "5 tests pass" claim. It matters a little: by trace all 5 would pass, which is the problem.
  - The deployment wrapper or framework that calls `handle()`. It matters for F3 and S1.
  - Whether auth.py and store.py are the production modules or fixtures. It matters for S1.

**COVERAGE**
- Checked: every function in app.py, auth.py and store.py; all 5 tests; every requirement sentence in request.md.
- Not checked:
  - Test execution and mutation.
  - The caller and framework around `handle()`.
  - Production config.

**SEATS AND GATE**
- One local reviewer ran. No subagent or cross-vendor seats were available (no tools).
- Gate: the work contains only sample data. The service will hold private customer notes, but no sensitive data is in the work. Not sensitive.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | app.py, `/admin/export` branch (`if path == "/admin/export" ...: return {... store.export_all()}`) | No `auth.require_admin(user)` before `export_all()`. The `/admin/users` branch has the check; this branch skips it. | Alice sends GET `/admin/export` with `tok-alice`. `current_user` succeeds, no AuthError is raised, and she gets 200 with bob's and root's notes. This breaks "a valid token without admin rights gets 403" and exposes private notes, with no rollback window. | Add `auth.require_admin(user)` as the first line of the branch. Repro test: `self.assertEqual(req("/admin/export", "tok-alice")["status"], 403)`. On current code this returns 200, so the test fails; after the fix it passes. Also add an admin-allowed case for `tok-root` returning 200. | y/y/y/y |
| F2 | High | CONFIRMED | B | test_app.py (no test references `/admin/export`) | The suite never exercises `/admin/export`. "5 tests pass" is the evidence offered for production readiness, but it would pass with F1 present. | The suite goes green, the change ships, and F1 reaches production. Any later regression on admin routes other than `/admin/users` is also invisible. | Add 403 (non-admin), 200 (admin) and 401 (bad token) tests for `/admin/export`. Mutation check: remove `require_admin` from `/admin/users` in a scratch copy and confirm `test_admin_users_is_forbidden_for_non_admin` goes red. | y/y/n/y |
| F3 | Medium | PROBABLE | B | auth.py `current_user`: `hmac.compare_digest(known, token or "")` | `compare_digest` raises `TypeError` for a `str` with non-ASCII characters, and for a non-str, non-bytes token such as an int. Only `AuthError` is caught, so the request crashes instead of getting 401. | A client sends token `"tök"` or the integer `123`. An unhandled TypeError propagates out of `handle()` (500 or a crashed worker) instead of 401, which breaks "anyone without a valid token gets 401". | Reject non-str or non-ASCII tokens with `AuthError` before comparing, or compare `.encode()`d bytes. Repro: `req("/notes", "tök")` should return 401; per the Python docs it raises TypeError instead. | y/n/y/n |
| F4 | Medium | CONFIRMED | B | app.py `request["path"], request["method"]`, and `request["body"]` in POST | Required keys are read with `[]`. A missing key raises `KeyError`, which nothing catches. | A request dict without `"body"` on POST `/notes` (or without `"method"`) raises KeyError and returns no `{"status","body"}`. This contradicts the module docstring's "Every handler returns {status, body}". | Use `.get()` and return 400 on a missing path, method or body. Repro: `app.handle({"path": "/notes", "method": "POST", "token": "tok-bob"})` raises KeyError; expected 400. | y/y/n/n |

## NEEDS VALIDATION
- **S1:** auth.py hardcodes tokens, including the admin token `tok-root`, and store.py is in-memory, so notes are lost on restart.
  - Unresolved fact: are these the production modules or test fixtures?
  - If production, there are two problems. A committed admin secret gives admin to anyone with repo read. In-memory storage is data loss for customer notes.
- **S2:** POST `/notes` accepts `None` or non-string bodies and stores them as `"bob: None"`.
  - Unresolved fact: does the framework guarantee a string body?

## REFUTED
- **"Path tricks bypass the admin check"** (e.g. `/admin/users/`, `/ADMIN/export`). Refuted: routing uses exact `==`, so variants fall through to 404 and never reach an admin handler.
- **"No-token or empty-token requests reach handlers."** Refuted: `token or ""` compares against non-empty known tokens, nothing matches, and `AuthError` produces 401.
- **"A non-admin on `/admin/users` gets 401 instead of 403."** Refuted: `require_admin`'s `AuthError` is raised inside the second `try`, whose handler returns 403.
- **"Users can read other users' notes via `/notes`."** Refuted: `list_notes` keys on the authenticated `user[0]`. The request has no user parameter to tamper with.

## WHAT HOLDS UP
- 401 handling for unknown or missing ASCII tokens.
- Per-user isolation on `/notes` GET and POST.
- The `/admin/users` check and its 403 mapping.
- Constant-time token comparison.
- Exact-match routing.
- Copies are returned from the store (`list(...)`), so callers cannot mutate stored notes.

## UNVERIFIED CLAIMS
- **"test_app.py passes (5 tests)".** By trace all 5 would pass. Confirm by running `python -m unittest test_app`.
- **Coverage of the existing tests.** Unverified until the mutation in F2 has been run in a scratch copy.

## QUESTIONS FOR THE AUTHOR
1. Are auth.py and store.py what ships to production, or stand-ins? (Settles S1.)
2. Does the calling framework guarantee `path`, `method` and `body` keys, and string tokens? (Settles F3 and F4 severity.)

## DECISION-MAKER SUMMARY
Do not deploy. F1 lets any user download all customers' notes, and the passing test suite never checks that route (F2). The fix is a one-line admin check plus three tests. Proceeding anyway risks an irreversible privacy breach.

## OWNER SUMMARY
The export feature meant only for administrators can be used by any logged-in customer to download everyone's private notes. The automated tests did not catch this because they never try it. A small fix and a few added tests are needed before release.

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
    {"item": "framework/caller of handle()", "status": "not_seen", "matters": true},
    {"item": "production config for auth/store", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work contains only sample data; no personal data or credentials beyond test tokens."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current_user", "kind": "function"},
      {"unit": "auth.py:require_admin", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md: 401/403 requirements", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation", "reason": "no tools in this session"},
      {"unit": "caller/framework of handle()", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:handle /admin/export branch",
     "scenario": "A non-admin token (tok-alice) on GET /admin/export receives 200 with every user's notes instead of 403.",
     "fix": "Call auth.require_admin(user) before store.export_all().",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/admin/export', 'tok-alice')['status']: expect 403, observe 200."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py (no /admin/export test)",
     "scenario": "The suite passes with F1 present, so the exposure ships undetected.",
     "fix": "Add 401/403/200 tests for /admin/export; mutation-check the /admin/users test in a scratch copy.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add assertEqual(req('/admin/export','tok-alice')['status'], 403); it fails on current code."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:current_user hmac.compare_digest",
     "scenario": "A non-ASCII str or non-str token makes compare_digest raise TypeError, which escapes handle() instead of returning 401.",
     "fix": "Raise AuthError for non-str/non-ASCII tokens, or compare encoded bytes.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "req('/notes', 'tök'): expect 401, expect TypeError per Python docs."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:handle request['path'], request['method'], request['body']",
     "scenario": "A request dict missing body/method raises KeyError instead of returning a status.",
     "fix": "Use .get() and return 400 on missing fields.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "app.handle({'path':'/notes','method':'POST','token':'tok-bob'}): expect 400, observe KeyError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:_TOKENS; store.py:_NOTES",
     "suspicion": "Hardcoded admin token and in-memory note store would be a secret leak and data loss in production.",
     "unresolved_fact": "Whether auth.py and store.py are the production modules or fixtures."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "store.py:add_note",
     "suspicion": "None or non-string bodies are stored as text such as 'bob: None'.",
     "unresolved_fact": "Whether the framework guarantees a string body."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Path variants bypass the admin check.", "evidence": "Routing uses exact ==; variants fall through to 404."},
    {"id": "R2", "candidate": "Missing/empty token reaches handlers.", "evidence": "token or '' matches no known token; AuthError returns 401."},
    {"id": "R3", "candidate": "Non-admin on /admin/users gets 401.", "evidence": "require_admin's AuthError is caught by the inner try, which returns 403."},
    {"id": "R4", "candidate": "Users can read other users' notes via /notes.", "evidence": "list_notes keys on the authenticated user[0]; no user parameter exists."}
  ]
}
```