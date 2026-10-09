**Review mode:** independent review with no tools in this session. I did not run, import or execute any code. Every finding comes from reading the supplied source and from documented Python standard-library behavior.

VERDICT: **REWORK**. `/admin/export` has no admin check, so any valid user token can download every user's private notes. The request forbids exactly this, and the stakes are a data exposure that cannot be rolled back.

CONFIDENCE: **medium-high** for F1, which is a pure code trace with no external dependency. **Medium** overall, because:
- I had no tools, so nothing was run.
- The claim that "5 tests pass" is unverified.
- It is unknown whether `auth.py` and `store.py` are the production implementations or stand-ins.

INPUTS LEDGER:
- **Seen:** request.md, context.md, app.py, auth.py, store.py, test_app.py.
- **Not seen:** any test run output (matters only a little, since the verdict does not depend on it). Deployment and config showing whether `_TOKENS` and the in-memory store ship to production (matters for S1 and S2).

COVERAGE:
- **Scope:** the whole change (4 files).
- **Checked:**
  - app.py: `handle`, every route branch
  - auth.py: `current_user`, `require_admin`, `_TOKENS`
  - store.py: all 4 functions
  - test_app.py: all 5 tests
  - request.md, context.md
- **Not checked:** runtime behavior (no tools). The production wiring of auth and store was not supplied.

SEATS AND GATE:
- **Seats:** same-session reviewer only. There is no subagent tool here, and cross-vendor seats were neither requested nor available.
- **Gate:** the work contains only toy fixture data (sample notes and tokens). No real personal data, so the gate was not triggered.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B | app.py, `if path == "/admin/export" and method == "GET":` branch | The branch calls `store.export_all()` without calling `auth.require_admin(user)`. The sibling `/admin/users` branch does call it. | Any authenticated non-admin (e.g. `tok-alice`) sends GET /admin/export. The handler returns 200 with every user's notes, including bob's and root's. The request says this must be 403. | **Fix:** add `auth.require_admin(user)` before `export_all()`. Better still, enforce admin once for every path starting with `/admin` before dispatch, so a new admin route cannot forget the check. **Repro:** `req("/admin/export", "tok-alice")`. Expected status 403; traced result is status 200 with body `{"alice": [...], "bob": [...], "root": [...]}`. Add this as a regression test. | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED | B | test_app.py (whole file) | No test covers `/admin/export`, for either admin or non-admin. The "5 tests pass" signal therefore says nothing about the route that leaks. | F1 ships with a green suite. A later regression on either admin route could also slip through if only one of them is tested. | **Fix:** add `test_admin_export_forbidden_for_non_admin` (expects 403) and `test_admin_export_allowed_for_admin` (expects 200). Also add a 401 test on an /admin route. **Repro:** apply the F1 mutation in reverse (as the code is now). The suite stays green, which shows the gap. | a✓ b✓ c✗ d✓ |
| F3 | Medium | PROBABLE | B | auth.py `current_user`, `hmac.compare_digest(known, token or "")` | `hmac.compare_digest` raises `TypeError` in two cases: when the token is a `str` containing non-ASCII characters, and when the token is a non-str/bytes type such as an int, or bytes compared against a str. `handle` catches only `auth.AuthError`, so the exception escapes. | A client sends token `"tök"` or a numeric token. Instead of 401, the handler raises an uncaught `TypeError`, which becomes a 500 or a crash depending on the server. The request requires 401 for anyone without a valid token. | **Fix:** in `current_user`, reject anything that is not an ASCII `str` with `AuthError`, or wrap the comparison and raise `AuthError` on `TypeError`. **Repro:** `req("/notes", "tök")`. Expected status 401; the stdlib-documented result is `TypeError`. | a✓ b✗ c✓ d✗ |
| F4 | Low | CONFIRMED | B | app.py route dispatch, final `return {"status": 404, ...}` | Non-admins get 404 rather than 403 on `/admin` paths outside the two exact path and method pairs (e.g. `POST /admin/users`, `GET /admin/anything`). The request says non-admins get 403 "on /admin routes". | A non-admin probing `/admin/*` gets 404. This mostly matters for spec conformance and is slightly at odds with the intent of the request. | **Fix:** apply the prefix check suggested in F1. **Repro:** `req("/admin/x", "tok-alice")`. Expected 403 (per the request's wording); observed 404. | a✓ b✓ c✗ d✗ |

**Siblings for F1:**
- **Searched:** every `/admin` branch in `handle`, and every caller of `store.export_all` and `store.list_users`.
- **Found:** `/admin/users` is guarded and `/admin/export` is not. There are no other callers.

**Security boundary for F1:**
- **Principal:** an authenticated non-admin user.
- **Input:** the path `/admin/export`.
- **Control that fails:** `require_admin` is never called.
- **Boundary crossed:** user to admin.
- **Resource exposed:** every user's private notes.

## NEEDS VALIDATION
- **S1:** `auth.py` hardcodes bearer tokens in source, including the admin token `tok-root`. If this ships, anyone with read access to the repo or its history has admin access. To settle: is `_TOKENS` a fixture, or is it the production token source?
- **S2:** `store.py` is in-memory. If it is the production store, all notes are lost on restart and multiple processes see different data. To settle: is this the deployed store?
- **S3:** "test_app.py passes (5 tests)" is plausible by trace (each assertion matches the code path) but was not run. To settle: run the suite in a scratch copy. Also delete `auth.require_admin(user)` from `/admin/users` and confirm that `test_admin_users_is_forbidden_for_non_admin` goes red.

## REFUTED
- **Timing leak in the token loop.** The loop returns early, which reveals which entry matched, but each comparison is constant-time. With 3 tokens, this leaks nothing usable about the token contents.
- **Users can read each other's notes.** `list_notes` and `add_note` key only on `user[0]` from the authenticated token, never on request input. Per-user isolation holds on `/notes`.

## WHAT HOLDS UP
- 401 is checked before any routing, on every path.
- `/notes` GET and POST are correctly scoped to the caller.
- `/admin/users` correctly returns 403 to non-admins and 200 to admins.
- Token comparison uses `hmac.compare_digest`.

## UNVERIFIED CLAIMS
- **"Tests pass (5 tests)."** Confirm by running `python -m unittest test_app` in an isolated copy.

## QUESTIONS FOR THE AUTHOR
1. Are `auth._TOKENS` and the in-memory `store` the production implementations?
2. Should non-admins get 403 on every `/admin/*` path, including unknown ones?

## DECISION-MAKER SUMMARY
Do not ship. Any logged-in user can download every customer's notes through `/admin/export` (F1). The fix is one line plus two tests. If it ships as is, private notes leak to every user, and that exposure cannot be rolled back.

## OWNER SUMMARY
The new notes service has a hole: any ordinary user can download every other customer's private notes from an admin-only page. The repair is small, but it has to be made and tested before release. Until then, it should not go live.

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
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "production auth/store wiring", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only fixture data"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current_user", "kind": "function"},
      {"unit": "auth.py:require_admin", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "runtime test execution", "reason": "no_tools"},
      {"unit": "production auth/store wiring", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: /admin/export branch in handle",
     "scenario": "A non-admin token (tok-alice) on GET /admin/export receives 200 with every user's notes instead of 403.",
     "fix": "Call auth.require_admin(user) before store.export_all(), or enforce admin for every /admin path before dispatch; add a regression test.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/admin/export', 'tok-alice'): expect status 403, traced result 200 with all users' notes.",
     "security": true,
     "boundary": {"principal": "authenticated non-admin user", "input": "GET /admin/export path",
                  "control": "require_admin never called", "crossed": "user to admin",
                  "resource": "every user's private notes"},
     "siblings_searched": {"searched": "all /admin branches in handle; callers of export_all and list_users",
                           "found": "/admin/users is guarded; no other unguarded caller"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py",
     "scenario": "No test covers /admin/export, so F1 ships with a green suite.",
     "fix": "Add 403-for-non-admin and 200-for-admin tests for /admin/export, and a 401 test on an /admin route.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run the suite against the current code: all green while /admin/export leaks."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:current_user hmac.compare_digest(known, token or '')",
     "scenario": "A non-ASCII or non-string token makes compare_digest raise TypeError, which handle does not catch: crash/500 instead of 401.",
     "fix": "Reject non-ASCII-str tokens with AuthError before comparing, or convert TypeError to AuthError.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "req('/notes', 't\u00f6k'): expect 401; stdlib-documented behavior is TypeError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: final 404 return in handle",
     "scenario": "A non-admin on POST /admin/users or GET /admin/x gets 404, not the 403 the request specifies for /admin routes.",
     "fix": "Check admin for any path starting with /admin before route matching.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "req('/admin/x', 'tok-alice'): expect 403, observe 404."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:_TOKENS",
     "suspicion": "Hardcoded bearer tokens, including admin tok-root, in source.",
     "unresolved_fact": "Whether _TOKENS is a fixture or the production token source."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "store.py:_NOTES",
     "suspicion": "In-memory store loses all notes on restart and is not shared across processes.",
     "unresolved_fact": "Whether store.py is the deployed store."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Timing leak in the token lookup loop.",
     "evidence": "Each comparison is constant-time; the early return reveals only which of 3 entries matched, not token content."},
    {"id": "C2", "candidate": "Users can read or write others' notes on /notes.",
     "evidence": "list_notes/add_note key only on user[0] from the authenticated token, never on request input."}
  ]
}
```