**Same-context review, single reviewer, no tools.** I could not run the tests, mutate code or use a subagent. Every finding comes from reading the code; anything that needed execution is marked UNVERIFIED. Re-run in a fresh session with tools before relying on this for production.

---

**VERDICT: REWORK.** `/admin/export` has no admin check, so any valid user token can download every user's private notes. The tests do not cover that route, so they cannot catch it.

**CONFIDENCE: medium.** The main finding is certain from the code. Confidence is limited by having no tools (the tests, the TypeError path and test isolation were not run) and by a single same-context reviewer.

**INPUTS LEDGER**
- Seen: request.md, context.md, app.py, auth.py, store.py, test_app.py.
- Not seen: the test run output behind "test_app.py passes (5 tests)". This matters a little: the claim is plausible from the code, but passing tests are irrelevant to the main defect anyway.
- Not seen: any deployment or gateway config that might add authorization in front of `/admin`. It matters only if such a layer exists; nothing in the inputs says it does.
- Not seen: the production token and credential source. This matters because auth.py hardcodes the tokens.

**SEATS AND GATE**
- Single local reviewer (this session). No subagent or tools were available.
- Cross-vendor seats were not used. They were not requested, and customer notes are private, so the gate would refuse external seats for real data. The code under review contains only placeholder data.

**Pass 1, reconstruction.** The change implements one `handle()` dispatcher:
- An invalid token returns 401.
- `/notes` GET and POST are scoped to the token's user.
- `/admin/users` and `/admin/export` should require admin rights, otherwise 403.

For this to be correct, the user must come only from the token, and every `/admin` path must call `require_admin` before touching data. Unstated assumptions:
- Tokens are ASCII strings.
- The request always has `path`, `method` and `body`.
- Tokens and storage in this form are acceptable for production.

Tracks: B (code) and R (private customer data exposure).

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | app.py, `/admin/export` branch (`return {"status": 200, "body": store.export_all()}`) | `auth.require_admin(user)` is missing. `/admin/users` calls it; `/admin/export` does not. The request says non-admins get 403 on `/admin` routes. | `req("/admin/export", "tok-alice")` returns 200 with alice's, bob's and root's notes. Any customer can exfiltrate all private notes, and context says there is no rollback window for exposure. | Add `auth.require_admin(user)` before `export_all()`. Add tests that export gives 403 for `tok-alice` and 200 for `tok-root`. Better: enforce admin once for every path starting with `/admin` so a new route cannot skip it. | confirmed. The strongest defense is an upstream gateway enforcing admin. Nothing in the inputs shows one, and the request puts 403 in these handlers. |
| 2 | High | CONFIRMED | B | test_app.py (whole file) | No test touches `/admin/export`. The "5 tests pass" claim is the evidence offered for readiness, but the suite cannot detect finding 1. The admin tests have also never been shown to fail. | Finding 1 ships with green CI. A future regression on `/admin/users` would be caught only by the single 403 test, whose ability to fail is unproven (UNVERIFIED). | Add 401, 403 and 200 tests for every route, including export. Mutation check: remove `require_admin` from `/admin/users` in a scratch copy and confirm `test_admin_users_is_forbidden_for_non_admin` goes red. | confirmed. The coverage gap is directly visible. |
| 3 | High | CONFIRMED (presence in code); PROBABLE (that it would reach production) | B | auth.py `_TOKENS = {... "tok-root": ("root", True)}` | Credentials, including an admin token, are hardcoded in source. Anyone with repo access holds a production admin credential, and there is no rotation or revocation. | The repo is shared, leaked or forked, and `tok-root` grants full export in production. | Load tokens or verify them against a real identity provider or secret store. If this module is a stub, mark it as one and block deploy until it is replaced. | confirmed. Defense: "it's a stub." Context says this change goes to production and nothing labels auth.py a stub. |
| 4 | Medium | PROBABLE (documented `hmac.compare_digest` behavior, not run) | B | auth.py `hmac.compare_digest(known, token or "")` | `compare_digest` raises `TypeError` for str arguments with non-ASCII characters, and for a non-str token such as an int or list. `handle()` catches only `AuthError`. | A request with token `"tók"` or `123` raises an uncaught exception, giving a 500 or a crash instead of 401. This also lets anyone trigger errors and log noise without auth. | In `current_user`, reject non-str or non-ASCII tokens with `AuthError`, or compare bytes. Add tests for `token=None`, `123` and `"tók"` that expect 401. | — |
| 5 | Medium | CONFIRMED | B | app.py `request["path"], request["method"]`, `store.add_note(user, request["body"])`; store.py `add_note` | There is no validation of request shape or body. A missing key raises `KeyError` (500). A `None` or dict body is stored as `"bob: None"` or a stringified dict. Note size is unbounded. | POST without a body stores junk. A huge body grows memory without limit, since storage is in-memory. | Validate that `body` is a non-empty str within a size limit, otherwise return 400. Use `.get` with a 400 on malformed requests. | — |
| 6 | Low | CONFIRMED | B | app.py final `return {"status": 404 ...}` | A non-admin calling an unknown `/admin/*` path, or a wrong method on an admin route, gets 404 rather than the 403 the request specifies for "/admin routes". | `tok-alice` probing `/admin/foo` gets 404 and `/admin/users` gets 403. This mildly leaks which admin routes exist and deviates from the spec's wording. | Check admin for any `/admin` prefix before dispatch (this also fixes the class of bug in finding 1). | — |
| 7 | Low | PROBABLE | B | test_app.py `test_post_creates`; store.py module-global `_NOTES` | Tests mutate shared module state with no reset. The current assertions are unaffected, since bob posts and alice is read, but later tests will be order-dependent. | Someone adds a bob-listing test, and it passes or fails depending on run order. | Reset `_NOTES` in `setUp`, or inject the store. | — |
| 8 | Low | CONFIRMED | B | store.py in-memory `_NOTES` | Notes live only in process memory. A restart loses every customer note, and multiple workers each see different data. | A production deploy or restart wipes user data. | Confirm whether persistence is in scope (see questions). If so, back the store with durable storage. | — |

**WHAT HOLDS UP**
- **Per-user isolation on `/notes`.** The user comes only from the token. `list_notes` and `add_note` key on `user[0]`, and no request field can choose another user.
- **401 path.** `None`, empty and unknown ASCII tokens all raise `AuthError` and return 401.
- **`/admin/users`.** It correctly calls `require_admin` and maps `AuthError` to 403.
- **Token comparison.** It uses a constant-time compare.
- **Returned data.** `list_notes` and `export_all` return copies, so callers cannot mutate the store.

**UNVERIFIED CLAIMS**
- "test_app.py passes (5 tests)": run `python -m unittest test_app`.
- The TypeError on non-ASCII tokens: run `req("/notes", "tók")`.
- Whether the existing 403 test can fail: use the mutation check in finding 2.

**QUESTIONS FOR THE AUTHOR**
1. Is there any layer in front of this service that enforces admin on `/admin/*`? If not, finding 1 stands as Critical.
2. Are `auth.py` and `store.py` placeholders, and what replaces them in production?

**DECISION-MAKER SUMMARY:** Do not deploy. The export endpoint lets any logged-in customer download every customer's private notes, and the passing tests never check that route. Add the admin check and route-level tests, and replace the hardcoded admin token, before release; shipping as-is risks an irreversible data exposure.

**OWNER SUMMARY:** The new code lets any signed-in customer download everyone's private notes through the admin export feature, and the automated tests miss this. It also keeps an administrator password directly in the code. Both must be fixed and re-tested before this goes live.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "test run output for test_app.py", "status": "not_seen", "matters": false},
    {"item": "gateway/deployment authz config", "status": "not_seen", "matters": true},
    {"item": "production token source", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Code contains only placeholder notes; real customer notes would bar external seats."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py /admin/export branch",
     "scenario": "Any valid non-admin token (tok-alice) GETs /admin/export and receives every user's notes with 200.",
     "fix": "Call auth.require_admin(user) before store.export_all(), preferably enforce admin for every /admin prefix; add 403/200 tests.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_app.py",
     "scenario": "No test covers /admin/export, so the missing admin check ships with green tests.",
     "fix": "Add 401/403/200 tests per route; mutation-check the admin test in a scratch copy.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py _TOKENS",
     "scenario": "Hardcoded admin token tok-root in source; anyone with repo access can export all notes in production.",
     "fix": "Load or verify tokens from a secret store or identity provider; block deploy while stubbed.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py current_user hmac.compare_digest",
     "scenario": "Non-ASCII or non-str token raises TypeError, uncaught by handle(), giving a 500 or crash instead of 401.",
     "fix": "Reject non-str or non-ASCII tokens as AuthError or compare bytes; add tests."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py request[...] access; store.py add_note",
     "scenario": "Missing keys raise KeyError (500); None, dict or huge bodies are stored unvalidated.",
     "fix": "Validate request shape and body type/size; return 400."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py final 404",
     "scenario": "Non-admin on unknown /admin/* path or wrong method gets 404, not the specified 403.",
     "fix": "Check admin on any /admin prefix before dispatch."},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "test_app.py test_post_creates; store._NOTES",
     "scenario": "Tests mutate shared global state; future tests become order-dependent.",
     "fix": "Reset store in setUp or inject it."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "store.py _NOTES",
     "scenario": "In-memory store loses all notes on restart and diverges across workers.",
     "fix": "Confirm scope; use durable storage for production."}
  ]
}
```