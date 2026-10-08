**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available. Nothing was executed, so every finding below comes from reading and tracing the supplied code.

VERDICT: **REWORK**. `/admin/export` has no admin check, so any user with a valid token can download every user's private notes.

CONFIDENCE: **medium**. The main finding is an exact, traceable line and I am confident in it. Confidence is limited because this is a same-context review, nothing was run (including the "5 tests pass" claim), and it is unknown whether the hardcoded tokens and in-memory store are what will actually ship.

INPUTS LEDGER:
- **Seen:** request.md, context.md, `app.py`, `auth.py`, `store.py`, `test_app.py`.
- **Not seen:** the test run output behind "test_app.py passes (5 tests)". This matters a little: the 5 tests don't cover the broken route either way.
- **Not seen:** the deployment or runtime that builds the request dict (how `token`, `path` and `body` are populated). This matters for F2 and S2.
- **Not seen:** any production auth or storage that might replace `auth._TOKENS` and `store._NOTES`. This matters for S1.

COVERAGE:
- **Checked:**
  - `app.py:handle`, all four routes plus the 401, 403 and 404 paths
  - `auth.py:current_user` and `auth.py:require_admin`
  - `store.py`, all four functions
  - `test_app.py`, all five tests
  - every requirement sentence in request.md
- **Not checked:**
  - the test execution and mutation check (no tools)
  - the production request adapter
  - the deployment config

SEATS AND GATE: Only the local same-context reviewer ran. No subagent tool was available and no cross-vendor seats were requested. The sensitivity gate passed: the notes and tokens are sample fixtures, not real personal data or credentials.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (traced) | B | `app.py`, the `/admin/export` branch: `return {"status": 200, "body": store.export_all()}` with no `auth.require_admin(user)` | The admin-only export route never checks admin rights. Unlike `/admin/users`, nothing on this path can raise `AuthError`, so the 403 handler is unreachable here. No test covers `/admin/export` at all, which is how this passed the suite. | Alice sends `GET /admin/export` with `tok-alice`. `current_user` succeeds, the branch returns 200, and the body contains bob's and root's notes. Customer notes leak with no rollback, and this violates "a valid token without admin rights gets 403 on /admin routes". | **Fix:** add `auth.require_admin(user)` before `store.export_all()`. Better, enforce it once for every `path.startswith("/admin")` before dispatch, so a future admin route can't miss it. **Test:** `assertEqual(req("/admin/export","tok-alice")["status"], 403)` fails today (observed 200, expected 403). Also add an admin-allowed test and a 401 test for the same route. | a Y / b Y / c Y / d Y |
| F2 | Medium | PROBABLE | B | `auth.py:current_user`, `hmac.compare_digest(known, token or "")` | `hmac.compare_digest` raises `TypeError` for a `str` containing non-ASCII characters, and for a non-str, non-bytes value. `handle` only catches `AuthError`, so the exception escapes instead of returning 401. | A client sends the token `"tök"` (or an integer if the adapter passes parsed JSON). This raises `TypeError` and gives a 500 or an unhandled crash instead of the required 401. | **Fix:** in `current_user`, reject a non-str or non-ASCII token with `AuthError` before comparing, or catch `TypeError` and raise `AuthError`. **Repro:** `req("/notes","tök")`; expected `status` 401, observed `TypeError` raised (not run; based on documented `compare_digest` behaviour). | a Y / b N / c Y / d N |
| F3 | Low | CONFIRMED (traced) | B | `store.py:list_users`, `return sorted(_NOTES)` | The user list is derived from note owners, not from known users. A user with a valid token but no notes is omitted from `/admin/users`. | A new user is added to the token table and has not yet posted. `/admin/users` doesn't show them, so the admin's view of accounts is incomplete. With the current fixtures, every user has a note, so this does not trigger yet. | **Fix:** list users from the user or token source. **Repro:** add `"tok-carol": ("carol", False)` to `_TOKENS`, then `req("/admin/users","tok-root")`; expected to include `"carol"`, it does not. | a Y / b Y / c N / d N |

## Needs validation

- **S1:** `auth._TOKENS` hardcodes bearer tokens, including the admin token `tok-root`, in source. `store._NOTES` is in-memory, so every note is lost on restart.
  - If these ship to production as written, anyone with repo access holds root, and customer notes are lost on every deploy.
  - **Unresolved fact:** are `auth.py` and `store.py` the production implementations, or fixtures to be replaced before deploy?
- **S2:** `handle` reads `request["path"]`, `request["method"]` and, on POST, `request["body"]` with `[]`. A missing key raises `KeyError`, and a `None` body is stored as the note `"<user>: None"`.
  - **Unresolved fact:** does the production adapter always populate all four keys, and does it reject an empty body?
- **S3:** "test_app.py passes (5 tests)" was not observed. Rule 5 (break the guarded code and confirm the test goes red) was also not done.
  - **Unresolved fact:** delete `auth.require_admin(user)` from the `/admin/users` branch in a scratch copy and confirm `test_admin_users_is_forbidden_for_non_admin` fails.

## Refuted

- **R1:** "A missing token (`None`) crashes `current_user`." Refuted: `token or ""` makes the comparison `compare_digest(known, "")`, which returns False. The loop ends with `AuthError`, which gives 401.
- **R2:** "`/notes` can leak another user's notes." Refuted: `list_notes` and `add_note` key strictly on `user[0]`, which comes from the authenticated token, never from the request.
- **R3:** "Callers can mutate the store through returned lists." Refuted: `list_notes` returns `list(...)` and `export_all` copies each list.
- **R4:** "The token comparison leaks timing that enables token guessing." Refuted as a practical issue: the early return only reveals which fixture slot matched, after a full constant-time compare.

## What holds up

- 401 handling for unknown and missing tokens.
- Per-user isolation on `GET /notes` and `POST /notes`.
- The 403 on `/admin/users` for non-admins.
- The defensive copies in `store.py`.
- 404 for unknown paths and methods.
- The existing five tests assert real status codes and bodies; none is vacuous.

## Unverified claims

- **"test_app.py passes (5 tests)":** run `python -m unittest test_app` and capture the output.
- **That the tests guard what they name:** do the mutation check described in S3.

## Questions for the author

1. Are `_TOKENS` and `_NOTES` the production auth and store, or placeholders? (This decides S1.)
2. Was `/admin/export` meant to be admin-only by a check somewhere else, such as a gateway? Nothing in the supplied code does it.

## Decision-maker summary

Do not ship. Any logged-in customer can download every other customer's notes through `/admin/export`, and the test suite never exercises that route. The fix is one line plus three tests; shipping as is risks an irreversible exposure of private notes.

## Owner summary

The change lets any signed-in user download every other user's private notes through the admin export page, because that page never checks whether the user is an administrator. The existing tests pass only because none of them try that page. Add the administrator check and a test for it before this goes live, and confirm whether the built-in sample logins and temporary storage are really meant for production.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "test_app.py run output (5 tests pass)", "status": "not_seen", "matters": false},
    {"item": "production request adapter", "status": "not_seen", "matters": true},
    {"item": "production auth and storage, if any", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Sample fixture notes and tokens only; no real personal data or credentials supplied."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current_user", "kind": "function"},
      {"unit": "auth.py:require_admin", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md requirements", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation check", "reason": "no tools in this session"},
      {"unit": "production request adapter", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: /admin/export branch (return store.export_all() with no require_admin)",
     "scenario": "A non-admin token (tok-alice) on GET /admin/export receives 200 with every user's notes, violating the required 403 and leaking private customer notes.",
     "fix": "Call auth.require_admin(user) before store.export_all(), ideally for every /admin path before dispatch; add tests for 403 (non-admin), 200 (admin) and 401 on /admin/export.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/admin/export', 'tok-alice'): expect status 403, observe 200 with alice, bob and root notes."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:current_user (hmac.compare_digest(known, token or \"\"))",
     "scenario": "A token containing non-ASCII characters (or a non-str value) makes compare_digest raise TypeError, which handle does not catch, so the request errors instead of returning 401.",
     "fix": "Reject a non-str or non-ASCII token with AuthError before comparing, or convert TypeError to AuthError.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "req('/notes', 't\u00f6k'): expect status 401, observe TypeError raised (not executed; documented compare_digest behaviour)."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "store.py:list_users (sorted(_NOTES))",
     "scenario": "A user with a valid token but no notes is missing from /admin/users.",
     "fix": "List users from the user/token source rather than from note owners.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add 'tok-carol': ('carol', False) to _TOKENS; req('/admin/users', 'tok-root') body lacks 'carol'."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:_TOKENS; store.py:_NOTES",
     "suspicion": "Hardcoded bearer tokens (including admin tok-root) and an in-memory store would expose root to anyone with repo access and lose all notes on restart if shipped as is.",
     "unresolved_fact": "Whether auth.py and store.py are the production implementations or fixtures to be replaced."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:handle (request['path'], request['method'], request['body'])",
     "suspicion": "Missing keys raise KeyError; a None body is stored as '<user>: None'.",
     "unresolved_fact": "Whether the production adapter always supplies all four keys and rejects empty bodies."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "test_app.py",
     "suspicion": "The claim that 5 tests pass, and that they go red when the guarded code is broken, is unverified.",
     "unresolved_fact": "Output of python -m unittest test_app, and its result after removing require_admin from /admin/users in a scratch copy."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A None token crashes current_user.", "evidence": "token or \"\" yields compare_digest(known, \"\"), which returns False; AuthError leads to 401."},
    {"id": "R2", "candidate": "GET /notes can return another user's notes.", "evidence": "list_notes and add_note key only on user[0] from the authenticated token."},
    {"id": "R3", "candidate": "Returned lists let callers mutate the store.", "evidence": "list_notes returns list(...) and export_all copies each list."},
    {"id": "R4", "candidate": "Token comparison leaks exploitable timing.", "evidence": "Each comparison is constant-time; the early return reveals only which fixture slot matched."}
  ]
}
```