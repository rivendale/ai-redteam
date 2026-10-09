**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available. I traced every finding by reading the code and ran nothing.

VERDICT: **REWORK.** Any logged-in non-admin can call `/admin/export` and receive every user's private notes. The 5 passing tests never exercise that route.

CONFIDENCE: **medium.** The main finding is a direct, deterministic trace of the code and does not depend on running anything. Confidence is limited because I could not run anything, the review is same-context, and I don't know whether `auth.py`'s token table is what ships.

INPUTS LEDGER:
- Seen: request.md, context.md, app.py, auth.py, store.py, test_app.py.
- Not seen: the test run output. Context says "5 tests pass", which I could not confirm, but it does not matter because the defect sits on a route no test touches.
- Not seen: deployment and config, including the real token source. This matters for S1.

COVERAGE:
- Scope: the whole change (4 files).
- Checked:
  - Files: app.py, auth.py, store.py, test_app.py.
  - Documents: request.md, context.md.
  - Functions: `app.handle`, all 5 route branches, `auth.current_user`, `auth.require_admin`, and all 4 `store` functions.
  - Assumptions: the 401 and 403 requirements from the request.
- Not checked: runtime behaviour (no tools), concurrency of the in-memory store (out of scope for an in-memory demo store), and deployment config (not supplied).

SEATS AND GATE: Only a local same-context reviewer ran. The sensitivity gate is clear: the work contains only sample data and no real personal data. No cross-vendor seats were requested.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | app.py:25-26 | `/admin/export` never calls `auth.require_admin(user)`. `/admin/users` does (line 23). | Alice (`tok-alice`, `is_admin=False`) sends GET `/admin/export`. `current_user` succeeds, the branch returns `store.export_all()`, and she gets 200 with bob's and root's notes, e.g. "root: rotate keys". The request requires 403. | **Fix:** add `auth.require_admin(user)` before `export_all()`. Better, gate every path starting with `/admin` once, before dispatch. **Reproduction:** `req("/admin/export","tok-alice")["status"]` should be 403; the trace shows 200 with all users' notes. | y/y/y/y |
| F2 | High | CONFIRMED | B | test_app.py (whole file) | No test covers `/admin/export`, whether as admin or non-admin. The "5 tests pass" assurance in context.md is the evidence offered for production readiness. | F1 shipped with a fully green suite. Any future regression on export authorization would also pass. | **Fix:** add `test_admin_export_forbidden_for_non_admin` (expects 403) and `test_admin_export_allowed_for_admin` (expects 200). **Reproduction:** add the first test; on the current code it fails with 200 != 403. Removing line 23 also leaves all 5 current tests passing except `test_admin_users_is_forbidden_for_non_admin`, which shows that only one admin route is guarded by a test. | y/y/n/y |
| F3 | Medium | PROBABLE | B | auth.py:14; app.py:10-13 | `hmac.compare_digest` raises `TypeError` when given a non-ASCII `str`, or a `str` and a `bytes`. Only `AuthError` is caught, so the request errors out instead of returning 401. | A client sends token `"tök"` or a non-string token. `handle` raises an uncaught `TypeError`, giving a 500 or a crash rather than the required 401. | **Fix:** in `current_user`, reject any token that is not an ASCII `str` by raising `AuthError`, or encode both sides to bytes. **Reproduction:** `req("/notes","tök")` should be 401; per the Python docs, `TypeError` is expected. Unrun. | y/n/y/n |
| F4 | Low | CONFIRMED (traced) | B | app.py:22-29 | Admin authorization lives per branch, so unknown or other-method `/admin/*` paths return 404 to non-admins. The request says non-admins get 403 on `/admin` routes. | Alice sends POST `/admin/export` or GET `/admin/anything` and gets 404, not 403. No data leaks, but behaviour departs from the spec, and the per-branch pattern is the root cause of F1. | **Fix:** one prefix check, `if path.startswith("/admin"): auth.require_admin(user)`, before route dispatch. **Reproduction:** `req("/admin/x","tok-alice")["status"]` should be 403; the trace shows 404. | y/y/n/n |

Sibling search for F1 and F2:
- I checked every `/admin` branch in `handle` (lines 22-26) and every caller of `store.export_all` and `store.list_users`. The only callers are in app.py. Only line 25 lacks the check.
- The user-scoped functions `list_notes` and `add_note` key on `user[0]` from the authenticated token, so they have no cross-user path.
- F1 is a security finding:
  - Principal: any holder of a valid non-admin token.
  - Input: the GET `/admin/export` path.
  - Control that fails: `require_admin` is never called.
  - Boundary crossed: user to admin.
  - Resource affected: every user's notes.

NEEDS VALIDATION:
- **S1:** auth.py:4 hardcodes live-looking tokens, including the admin `tok-root`. If this table is the production token source, anyone with read access to the source has admin rights. The fact that settles it: whether `_TOKENS` is a fixture or what production uses.
- **S2:** In a POST to `/notes` with no body, `request["body"]` is `None`, so the stored note is `"bob: None"`. There is also no size or type limit on the body. The fact that settles it: whether an upstream layer validates request bodies.

REFUTED:
- *Users can read other users' notes via `/notes`.* `list_notes` keys on the token-derived `user[0]`, and the body is not used for the lookup.
- *Unauthenticated requests reach handlers.* `current_user` runs first for every path, and `None` is coerced to `""`, which matches no token and returns 401.
- *`export_all` or `list_notes` return live references callers could mutate.* Both return copies.

WHAT HOLDS UP:
- Authentication runs before any routing.
- Token comparison uses a constant-time compare.
- Per-user note isolation holds on `/notes`.
- `/admin/users` is correctly gated.
- The 401 and 403 mapping via `AuthError` is sound for the paths that call the check.

UNVERIFIED CLAIMS:
- "test_app.py passes (5 tests)." The suite looks plausible but needs to be run to confirm. Even if it passes, it does not cover F1.

QUESTIONS FOR THE AUTHOR:
1. Is `_TOKENS` the production token store or a fixture?
2. Was the missing `require_admin` on export intentional? I assume not.

DECISION-MAKER SUMMARY:
Do not deploy. Any logged-in user can download every customer's notes through `/admin/export` (F1), and the passing tests do not cover that route (F2). The fix is a one-line admin gate plus two tests, but shipping as-is means an irreversible exposure of private data.

OWNER SUMMARY:
The change has a gap that would let any ordinary user download every other user's private notes from the admin export page. The existing tests passed only because none of them check that page. A small fix and two added tests are needed before release.

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
    {"item": "production token source / deployment config", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "sample data only"},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"}, {"unit": "auth.py", "kind": "file"},
      {"unit": "store.py", "kind": "file"}, {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"}, {"unit": "context.md", "kind": "document"},
      {"unit": "app.py:handle", "kind": "function"}, {"unit": "auth.py:current_user", "kind": "function"},
      {"unit": "auth.py:require_admin", "kind": "function"}, {"unit": "store.py:export_all", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "runtime execution of tests", "reason": "no_tools"},
      {"unit": "deployment config / token source", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:25-26",
     "scenario": "A non-admin (tok-alice) sends GET /admin/export and receives 200 with every user's notes instead of 403.",
     "fix": "Call auth.require_admin(user) before store.export_all(), or gate all /admin paths once before dispatch.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/admin/export','tok-alice')['status'] -> expect 403; traced result 200 with all notes.",
     "security": true,
     "boundary": {"principal": "any holder of a valid non-admin token", "input": "GET /admin/export",
                  "control": "require_admin is never called on this branch", "crossed": "user to admin",
                  "resource": "every user's notes"},
     "siblings_searched": {"searched": "all /admin branches in app.handle; all callers of store.export_all and store.list_users",
                           "found": "only /admin/export lacks the check"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py (no /admin/export test)",
     "scenario": "The export authorization bypass ships with all 5 tests green; future regressions are equally invisible.",
     "fix": "Add tests asserting 403 for non-admin and 200 for admin on /admin/export.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test asserting req('/admin/export','tok-alice')['status']==403; it fails on current code (200).",
     "security": false,
     "siblings_searched": {"searched": "every route in app.handle against test_app.py",
                           "found": "/admin/export is the only route with no test; POST/GET /notes and /admin/users are covered"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:14",
     "scenario": "A non-ASCII str or bytes token makes hmac.compare_digest raise TypeError, uncaught, giving a 500 instead of 401.",
     "fix": "Reject non-ASCII-str tokens with AuthError before comparing, or compare encoded bytes.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "req('/notes','tök') -> expect 401; expected TypeError per Python docs (unrun)."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:22-29",
     "scenario": "A non-admin requesting an unknown or other-method /admin/* path gets 404, not the 403 the request specifies.",
     "fix": "Check path.startswith('/admin') and require_admin once before dispatch.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "req('/admin/x','tok-alice')['status'] -> expect 403; traced result 404."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:4",
     "suspicion": "Hardcoded tokens, including the admin token, would give admin access to anyone who can read the source.",
     "unresolved_fact": "Whether _TOKENS is the production token source or a test fixture."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:20; store.py:add_note",
     "suspicion": "POST /notes accepts a missing or arbitrary body (stores 'user: None') with no size or type limit.",
     "unresolved_fact": "Whether an upstream layer validates request bodies."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Users can read others' notes via /notes.",
     "evidence": "list_notes keys on token-derived user[0], not on request input."},
    {"id": "C2", "candidate": "Missing token bypasses auth.",
     "evidence": "token or '' matches no entry; AuthError gives 401 before routing."}
  ]
}
```