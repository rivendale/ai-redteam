**Reviewer note:** I am a separate reviewer from the author, but I had no subagent and no tools. I traced the code by reading it and did not run anything. Everything marked CONFIRMED is from line-by-line tracing, and nothing was executed.

VERDICT: **REWORK.** Any logged-in user can download every user's private notes from `/admin/export`, because that route never checks for admin rights. No test covers that route.

CONFIDENCE: **medium.** Tracing makes the main finding certain, but I could not run tests or mutations. The claim "5 tests pass" is unverified, and it is unclear whether `auth.py` and `store.py` are production code or fixtures.

INPUTS LEDGER:
- Seen: request.md, context.md, app.py, auth.py, store.py, test_app.py.
- Not seen: the test run output for "passes (5 tests)". This matters a little, since the review does not rely on it.
- Not seen: the deployment and config that show whether the hardcoded tokens and the in-memory store reach production. This matters for S1.
- Not seen: how the framework builds the `request` dict, for example whether `body` is always present. This matters for F3.

COVERAGE:
- Checked: `app.handle` (every branch), `auth.current_user`, `auth.require_admin`, all four `store` functions, all 5 tests.
- Not checked: runtime behaviour, mutation testing, deployment and config.

SEATS AND GATE: one reviewer ran (this session, no tools). The work holds private customer notes, but the samples are fixture data with no real personal data. No cross-vendor seats were requested, so none ran.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (traced) | B | app.py:24-25 | `/admin/export` calls `store.export_all()` without `auth.require_admin(user)`. The `/admin/users` branch above it has the check. No test covers `/admin/export`, so the suite stays green. | A non-admin token (`tok-alice`) sends GET `/admin/export`. It gets 200 and every user's notes, including `root: rotate keys` and bob's. This breaks the 403 requirement and exposes private notes. | Add `auth.require_admin(user)` before the return. Add tests: `req("/admin/export","tok-alice")["status"] == 403` (fails today, returns 200) and `req("/admin/export","tok-root")["status"] == 200`. | a✔ b✔ c✔ d✔ |
| F2 | Medium | PROBABLE | B | auth.py:15 | `hmac.compare_digest` raises `TypeError` for str arguments with non-ASCII characters, and for a non-str token such as an int. `current_user` only catches `AuthError`, so the exception escapes `handle`. | A client sends token `"tök"` or `123`. The result is an unhandled exception (500) instead of the required 401. | Reject non-str and non-ASCII tokens up front by raising `AuthError`, or compare the `.encode()` bytes. Test: `req("/notes","tök")["status"] == 401`. | a✔ b✘ c✔ d✘ |
| F3 | Low | CONFIRMED (traced) | B | app.py:19-20; store.py:10-11 | POST reads `request["body"]`, which raises `KeyError` if the key is absent. A `None` or non-string body is stored as text: the existing test stores `"bob: None"`. | A POST without a body stores the note `"bob: None"` (in the test, a `body=None` POST stores this), or a request dict missing `body` crashes the handler. | Validate that body is a non-empty str within a size limit, otherwise return 400. Test: POST with `body=None` should return 400; today it returns 201. | a✔ b✔ c✘ d✘ |
| F4 | Low | CONFIRMED (traced) | B | app.py:22-27 | Any `/admin/*` request that matches no branch, such as POST `/admin/export` or GET `/admin/foo`, returns 404 to non-admins instead of 403. | A non-admin sends POST `/admin/export` and gets 404. I read "403 on /admin routes" as covering only existing routes, so this is minor. | Check admin once for any path starting with `/admin` before dispatch. That also prevents F1 recurring on future admin routes. | a✔ b✔ c✘ d✘ |
| F5 | Low | CONFIRMED (traced) | B | test_app.py:15-16; store.py:3 | The tests share mutable module-level `_NOTES`. `test_post_creates` permanently appends to bob's notes, so the tests depend on order. | Adding a test that checks bob's notes gives results that depend on test order. | Reset `store._NOTES` in `setUp` or inject the store. | a✔ b✔ c✘ d✘ |

## NEEDS VALIDATION
- **S1.** `auth.py:4` hardcodes tokens, including the admin token `tok-root`, and `store.py:3` is in-memory, so data is lost on restart. Unresolved fact: are these fixtures standing in for a real token service and database, or is this the production auth and storage? If they are production, this is a Critical secret-in-source and data-loss issue.
- **S2.** The statement "test_app.py passes (5 tests)". Unresolved fact: the actual run output. Mutation check: delete `auth.require_admin(user)` at app.py:23 and confirm `test_admin_users_is_forbidden_for_non_admin` goes red.

## REFUTED
- **R1.** "Users can read other users' notes via /notes." `list_notes` keys on `user[0]`, which comes from the authenticated token, not from request input (store.py:6-7).
- **R2.** "Unauthenticated requests reach handlers." Auth runs before routing, and `None` or empty tokens raise `AuthError` and return 401 (app.py:10-13, auth.py:14-17).

## WHAT HOLDS UP
- Every route runs authentication first.
- `/notes` reads and writes are scoped to the token's user.
- `/admin/users` correctly enforces admin and is tested both ways.
- Token comparison uses a constant-time compare.
- `list_notes` and `export_all` return copies, so callers cannot mutate the store.

## UNVERIFIED CLAIMS
- "Tests pass (5 tests)": confirm by running `python -m unittest test_app`.
- Whether the tests would catch a regression: confirm with the S2 mutation.

## QUESTIONS FOR THE AUTHOR
1. Are `auth.py` and `store.py` production code or stand-ins?
2. Should non-admins get 403 on any `/admin/*` path, including unknown ones?

## DECISION-MAKER SUMMARY
Do not deploy: F1 lets any user export all customers' private notes, and the passing suite does not detect it. Fix F1 with a prefix-level admin check plus tests, then handle F2. Deploying as is means immediate, irreversible exposure of every note.

## OWNER SUMMARY
The change has a security hole: any signed-in customer can download every other customer's private notes through the admin export feature. The automated tests pass only because none of them checks that feature. It needs a small fix and a new test before it is safe to release.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "test run output for 'passes (5 tests)'", "status": "not_seen", "matters": false},
    {"item": "deployment/config showing whether auth.py tokens and in-memory store are production", "status": "not_seen", "matters": true},
    {"item": "framework code building the request dict", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Sample data only; no real personal data in the work. No external seats used."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"}, {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"}, {"unit": "auth.py:current_user", "kind": "function"}, {"unit": "auth.py:require_admin", "kind": "function"},
      {"unit": "store.py", "kind": "file"}, {"unit": "test_app.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "runtime test execution", "reason": "no tools in session"},
      {"unit": "mutation testing of test_app.py", "reason": "no tools in session"},
      {"unit": "deployment config", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:24-25",
     "scenario": "A non-admin token (tok-alice) on GET /admin/export receives 200 with every user's notes; no test covers the route.",
     "fix": "Call auth.require_admin(user) before store.export_all(), ideally as one check for every /admin path; add 403 and 200 tests for /admin/export.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/admin/export','tok-alice')['status']: expect 403, observe 200 with all users' notes."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:15",
     "scenario": "A non-ASCII or non-str token makes hmac.compare_digest raise TypeError, which escapes handle and returns 500 instead of 401.",
     "fix": "Raise AuthError for non-str or non-ASCII tokens, or compare encoded bytes.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "req('/notes','tök'): expect status 401, observe an uncaught TypeError."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:19-20; store.py:10-11",
     "scenario": "A POST with body None stores the note 'bob: None'; a request dict without 'body' raises KeyError.",
     "fix": "Validate that body is a non-empty str within a size limit, otherwise return 400.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "req('/notes','tok-bob','POST',None): expect 400, observe 201 and 'bob: None' stored."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:22-27",
     "scenario": "A non-admin sending POST /admin/export or GET /admin/foo gets 404 rather than 403.",
     "fix": "Enforce admin for any path starting with /admin before dispatch.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "req('/admin/foo','tok-alice')['status']: observe 404."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:15-16; store.py:3",
     "scenario": "test_post_creates mutates the shared global _NOTES, so tests that read bob's notes depend on test order.",
     "fix": "Reset store._NOTES in setUp or inject the store.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a test asserting bob's notes == ['bob: call dentist'] and run it after test_post_creates; it fails."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:4; store.py:3",
     "suspicion": "Hardcoded tokens (including the admin token) and an in-memory store may ship to production.",
     "unresolved_fact": "Whether auth.py and store.py are production code or test fixtures."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "test_app.py",
     "suspicion": "The claim that the 5 tests pass, and their power to catch regressions, are unverified.",
     "unresolved_fact": "Actual test output, and whether removing require_admin at app.py:23 turns test_admin_users_is_forbidden_for_non_admin red."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Users can read other users' notes via /notes.",
     "evidence": "list_notes keys on user[0], which comes from the authenticated token (store.py:6-7)."},
    {"id": "R2", "candidate": "Requests without a token reach handlers.",
     "evidence": "current_user runs first; None or empty tokens match nothing and raise AuthError, returning 401 (app.py:10-13, auth.py:14-17)."}
  ]
}
```