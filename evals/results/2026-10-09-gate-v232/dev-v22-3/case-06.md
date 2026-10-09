# Redteam review: notes service request handlers

**VERDICT: REWORK.** `/admin/export` returns every user's private notes to any valid token, admin or not. This breaks the core access rule in the request, and nothing in the tests checks for it.

**CONFIDENCE: medium.** I had no tools, so all findings come from reading and tracing the code by hand. Nothing was executed. No fresh subagent was available, so this is a single-reviewer read; I did not write the work, which reduces anchoring. It is still unclear whether `auth.py` and `store.py` are what will run in production.

**INPUTS LEDGER:**
- Seen:
  - The original request (verbatim)
  - `context.md`
  - `app.py`, `auth.py`, `store.py` and `test_app.py` (full text)
- Not seen:
  - Any test run output. The claim that "5 tests pass" is unverified.
  - The production deployment config.
  - Whether `auth.py` and `store.py` are production modules or scaffolding. This matters for S1.

**COVERAGE:**
- Checked:
  - Every branch of `app.py:handle`
  - `auth.current_user` and `auth.require_admin`
  - All four functions in `store.py`
  - All five tests
- Not checked:
  - Runtime behaviour, since nothing was executed
  - Mutation testing, since there was no scratch copy to break

**SEATS AND GATE:**
- One local reviewer ran, from the same vendor.
- Cross-vendor seats were refused: the work contains customer notes and access tokens, so the sensitivity gate applies.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (traced) | B | `app.py`, `/admin/export` branch | The export branch never calls `auth.require_admin(user)`. Compare the `/admin/users` branch, which does. | Alice sends `GET /admin/export` with `tok-alice`. `current_user` returns `("alice", False)` and the branch returns `200` with `export_all()`. That response includes `bob: call dentist` and `root: rotate keys`. Any customer can read every customer's notes. | Add `auth.require_admin(user)` before `store.export_all()`. Repro test: `self.assertEqual(req("/admin/export","tok-alice")["status"], 403)` fails today (it returns 200). | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED | B | `test_app.py` (whole file) | No test touches `/admin/export`, for admins or non-admins. The suite passing is how F1 got through. | Someone later removes or reorders the admin check (once F1 is fixed). The suite stays green and exposure returns. | Add tests for `/admin/export` returning 403 for a non-admin and 200 for an admin. Confirm the 403 test goes red when the guard is removed, in a scratch copy. | a✓ b✓ c✗ d✓ |
| F3 | Low | CONFIRMED (traced) | B | `auth.py`, `current_user`; `app.py`, `request["path"]`, `request["method"]`, `request["body"]` | Malformed requests raise uncaught exceptions instead of returning a status. A non-string token (int, bytes) makes `hmac.compare_digest` raise `TypeError`. A missing `path`, `method` or `body` key raises `KeyError`. | A client sends a JSON number as the token. `handle` raises, and the caller turns that into a 500 with a possible stack trace. | Treat a non-`str` token as unauthenticated (401). Use `.get()` and return 400 for a missing path, method or body. Repro: `app.handle({"path":"/notes","method":"GET","token":123,"body":None})` raises instead of returning 401. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1. Hardcoded, guessable tokens and in-memory storage.** `auth.py` hardcodes `"tok-root"` as the admin token in source. `store.py` keeps notes only in memory, so they are lost on every restart.
  - If these modules ship to production, the token is a Critical (anyone who reads the repo or guesses the token gets admin) and the storage is data loss.
  - Unresolved fact: are `auth.py` and `store.py` the production modules, or test scaffolding standing in for real ones?
- **S2. 404 versus 403 for non-admins on other `/admin` routes.** A non-admin sending `GET /admin/foo` or `POST /admin/users` gets 404, not 403.
  - The request says a valid token without admin rights "gets 403 on /admin routes".
  - Unresolved fact: does the spec mean any `/admin/*` path, or only the two defined routes? If it means any path, the fix is to check the `/admin` prefix with `require_admin` before dispatching.

## REFUTED

- **"A missing or None token crashes."** Refuted. `current_user` uses `token or ""`, so `compare_digest` gets a string, no token matches, and the result is `AuthError` → 401.
- **"A user can see another user's notes via `/notes`."** Refuted. `list_notes` and `add_note` key on `user[0]`, which comes only from the token lookup. Nothing in the request body can choose the user.
- **"Returned lists alias the store."** Refuted. `list_notes` and `export_all` return copies (`list(...)`).

## WHAT HOLDS UP

- 401 handling is correct for unknown and empty tokens.
- `/admin/users` correctly returns 403 to non-admins.
- Each user's notes are isolated from other users on `/notes`.
- Token comparison uses `hmac.compare_digest`.
- My hand trace says the five existing tests would pass, though I did not run them. The `test_post_creates` mutation only touches bob's notes, so it does not interfere with the alice assertion.

## UNVERIFIED CLAIMS

- **"test_app.py passes (5 tests)."** Run `python3 -m unittest test_app -v` to confirm.
- **The existing 403 test catches a removed guard.** Delete `require_admin` from `/admin/users` in a scratch copy and confirm `test_admin_users_is_forbidden_for_non_admin` goes red.

## QUESTIONS FOR THE AUTHOR

1. Are `auth.py` and `store.py` what runs in production? (Settles S1.)
2. Should a non-admin get 403 on every `/admin/*` path, including undefined ones? (Settles S2.)

## DECISION-MAKER SUMMARY

Do not deploy. Any logged-in user can download every customer's notes through the admin export route. The code fix is one line plus two tests. Deploying as is causes an immediate, irreversible exposure of private data.

## OWNER SUMMARY

The new code lets any ordinary user download everyone's private notes through a feature meant only for administrators. The fix is small, and tests should be added so it cannot quietly happen again. Until then, this should not go live.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "test run output for test_app.py", "status": "not_seen", "matters": false},
    {"item": "whether auth.py/store.py are production modules", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-local", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Customer notes and access tokens in the work; no cross-vendor seats."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current_user", "kind": "function"},
      {"unit": "auth.py:require_admin", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "runtime execution of test_app.py", "reason": "no tools in this session"},
      {"unit": "mutation testing of existing tests", "reason": "no scratch copy available"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: /admin/export branch in handle()",
     "scenario": "A non-admin token (tok-alice) on GET /admin/export receives 200 with every user's notes, because require_admin is never called on this branch.",
     "fix": "Call auth.require_admin(user) before store.export_all(); add tests for 403 (non-admin) and 200 (admin) on /admin/export.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/admin/export', 'tok-alice') -> expect status 403, observe 200 with all users' notes."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py (no /admin/export test)",
     "scenario": "The admin check on export can be missing or later removed while the suite stays green, as it is today.",
     "fix": "Add tests for 403 for a non-admin and 200 for an admin on /admin/export; confirm the 403 test fails when the guard is removed (in a scratch copy).",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run the suite against the current app.py: all tests pass despite F1."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:current_user (hmac.compare_digest); app.py:handle request['path'|'method'|'body']",
     "scenario": "A non-str token raises TypeError, and a missing path, method or body key raises KeyError; handle() throws instead of returning 401 or 400.",
     "fix": "Treat a non-str token as unauthenticated (401); use .get() and return 400 for missing fields.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "app.handle({'path':'/notes','method':'GET','token':123,'body':None}) raises TypeError; expected 401."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:_TOKENS; store.py:_NOTES",
     "suspicion": "A hardcoded guessable admin token ('tok-root') and in-memory storage would be critical exposure and data loss if shipped to production.",
     "unresolved_fact": "Whether auth.py and store.py are the production modules or test scaffolding."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:handle final 404 return",
     "suspicion": "A non-admin on undefined /admin paths or methods gets 404, not the 403 the request specifies for /admin routes.",
     "unresolved_fact": "Whether the spec's '403 on /admin routes' covers any /admin/* path or only the two defined routes."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A None or missing token crashes current_user.",
     "evidence": "current_user uses `token or \"\"`, so no token matches and AuthError gives 401."},
    {"id": "R2", "candidate": "A user can read another user's notes via /notes.",
     "evidence": "list_notes and add_note key on user[0], which comes only from the token lookup."},
    {"id": "R3", "candidate": "Returned lists alias internal store state.",
     "evidence": "list_notes and export_all return list(...) copies."}
  ]
}
```