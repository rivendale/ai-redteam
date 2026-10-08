**Review mode:** I had no tools, so nothing was run. Every finding comes from tracing the code by hand. The work was not written in this conversation, so the risk of anchoring on the author's reasoning is low. Still, because of the stakes, re-run this review in a fresh session with execution.

---

**VERDICT: REWORK.** `/admin/export` has no admin check, so any authenticated user can download every customer's private notes. The tests don't cover it. The per-route opt-in pattern that caused it will cause it again.

**CONFIDENCE IN VERDICT: high.** The critical finding is a direct trace of four lines of code. Confidence is limited only because nothing was executed.

## Pass 1: Reconstruct

The change adds a single `handle()` dispatcher. It authenticates every request (401 on failure), serves per-user `/notes` GET and POST, and serves two admin routes that should return 403 to non-admins. Correctness depends on these assumptions:
- every `/admin` branch calls `auth.require_admin`;
- `current_user` raises only `AuthError` for bad tokens;
- the hardcoded token table is a stand-in, not the production credential store;
- the in-memory store is acceptable for production;
- the 5 passing tests cover the access-control requirements.

The first assumption is false.

## FINDINGS

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `app.py`, `if path == "/admin/export" and method == "GET": return {"status": 200, "body": store.export_all()}` | No `auth.require_admin(user)` call, unlike the `/admin/users` branch above it. | `req("/admin/export", "tok-alice")` returns 200 with `{"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}`. Any valid user can dump all private notes, which is irreversible exposure. | Add `auth.require_admin(user)` before `export_all()`. Better, enforce it structurally: `if path.startswith("/admin/"): auth.require_admin(user)` before route dispatch, so a new admin route cannot forget it. Add tests: export returns 403 for alice and 200 for root. |
| 2 | High | CONFIRMED | `test_app.py` (whole file) | The suite never requests `/admin/export`, which is the most sensitive route in the spec. "Tests pass (5 tests)" therefore says nothing about the requirement that failed. | Finding 1 passes CI. Any future regression on admin routes also passes. | Write one table-driven test over every `/admin/*` route × {no token → 401, user token → 403, admin token → 200}. Also add a cross-user test: bob's notes are never visible to alice, including after bob POSTs. |
| 3 | High | PROBABLE (depends on whether `auth.py` is a placeholder) | `auth.py`, `_TOKENS = {"tok-alice": ..., "tok-root": ("root", True)}` | Credentials, including an admin token, are hardcoded in source with guessable values. | If this ships as-is, anyone who reads the repo or guesses `tok-root` has full admin access, including `/admin/export`. | Load tokens from a real credential store or secret manager. Confirm with the author that this file is not the production version. |
| 4 | Medium | PROBABLE (based on documented `hmac.compare_digest` behavior; not run) | `auth.py`, `hmac.compare_digest(known, token or "")` | `compare_digest` raises `TypeError` if the types differ (str vs bytes or int) or if a str contains non-ASCII characters. `handle()` catches only `AuthError`. | A token like `"tök"`, `b"x"`, or `123` raises an uncaught `TypeError`. The caller gets a 500 or a crash instead of the required 401. | In `current_user`, reject non-`str` or non-ASCII tokens with `AuthError`, or compare encoded bytes. Add tests for those tokens expecting 401. |
| 5 | Medium | PROBABLE (depends on server threading model) | `store.py`, `export_all` and `list_users` iterate `_NOTES`; `add_note` calls `setdefault` | A global dict is mutated without a lock. Also, the process memory is the only storage. | Under a threaded server, a first POST by a new user during an export raises `RuntimeError: dictionary changed size during iteration`. Separately, a restart loses all customer notes. | Add a lock around store access, or use a real database. Confirm the production deployment model. |
| 6 | Low | CONFIRMED | `app.py`, `store.add_note(user, request["body"])` | The body is not validated. A missing key raises `KeyError`, which is an uncaught 500. | POST with body `None` stores `"alice: None"`. POST without a `"body"` key crashes the handler. | Validate that the body is a non-empty `str` and return 400 otherwise. |
| 7 | Low | CONFIRMED | `app.py`, final `return {"status": 404, ...}` | For a non-admin, unknown `/admin/*` paths and non-GET methods return 404, not 403. The spec says non-admins get 403 on /admin routes. | `req("/admin/anything", "tok-alice")` returns 404. This is minor, and it also stops leaking which admin routes exist. | The prefix-based check in finding 1 resolves this too. |
| 8 | Low | PROBABLE | `store.py`, `list_users(): return sorted(_NOTES)` | Users are derived from note ownership, not from the user registry. | A user who has a valid token but has never posted is missing from `/admin/users`. | Build the list from the auth or user source, or confirm that this behavior is intended. |

## WHAT HOLDS UP

- **401 handling:** authentication runs before any routing. A `None` token is handled with `token or ""`.
- **Per-user isolation on `/notes`:** `list_notes` is keyed on the authenticated user, not on request input, and it returns a copy. There is no path for alice to read bob's notes there.
- **`/admin/users`:** correctly gated, with `AuthError` mapped to 403.
- **Token comparison:** uses a constant-time compare. Early return leaks only the table position, which is negligible here.

## UNVERIFIED CLAIMS

- **"test_app.py passes (5 tests)":** a trace says it would pass, but it was not run. Confirm with `python -m unittest test_app`. Note that `test_post_creates` mutates global state, so test order can matter.
- **That `auth.py` and `store.py` are the production implementations:** confirm with the author.
- **The `TypeError` behavior in finding 4:** confirm by calling `auth.current_user("tök")` and `auth.current_user(b"x")`.

## QUESTIONS FOR THE AUTHOR

1. Are `_TOKENS` and the in-memory `_NOTES` what ship to production, or stubs for real auth and DB modules?
2. What server and threading model will call `handle()`?

## DECISION-MAKER SUMMARY

Do not ship. Any logged-in customer can download every other customer's notes via `/admin/export`, and the test suite would not catch it. Before release, enforce admin checks for all `/admin/*` routes in one place, add authorization tests for every admin route, and confirm that hardcoded tokens and in-memory storage are not production.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "app.py: /admin/export branch, `return {\"status\": 200, \"body\": store.export_all()}`", "scenario": "req('/admin/export', 'tok-alice') returns 200 with every user's notes; any authenticated non-admin can exfiltrate all private notes", "fix": "Call auth.require_admin(user) before export_all; better, enforce require_admin for every path starting with /admin/ before dispatch; add 403/200 tests for export"},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "test_app.py: no test touches /admin/export", "scenario": "The missing admin check on export passes CI; future admin-route regressions also pass", "fix": "Table-driven test over all /admin routes x {no token 401, user 403, admin 200}, plus cross-user isolation tests"},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "auth.py: _TOKENS hardcoded, including admin 'tok-root'", "scenario": "If shipped, anyone with repo access or who guesses 'tok-root' gets full admin access including export", "fix": "Load credentials from a secret store / real auth backend; confirm this is a stub"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "auth.py: hmac.compare_digest(known, token or \"\")", "scenario": "Non-ASCII str, bytes, or int token raises TypeError, uncaught by handle(), yielding 500/crash instead of 401", "fix": "Reject non-str/non-ASCII tokens with AuthError or compare encoded bytes; add tests expecting 401"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "store.py: global _NOTES mutated by add_note, iterated by export_all/list_users", "scenario": "Concurrent first POST during export raises 'dictionary changed size during iteration'; restart loses all notes", "fix": "Lock store access or use a persistent DB; confirm deployment model"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py: store.add_note(user, request[\"body\"])", "scenario": "Missing body key raises KeyError (500); body None is stored as 'alice: None'", "fix": "Validate body is a non-empty str; return 400 otherwise"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py: fall-through 404 return", "scenario": "Non-admin requesting unknown /admin/* path or method gets 404 rather than the spec's 403", "fix": "Prefix-based require_admin before dispatch"},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "store.py: list_users returns sorted(_NOTES)", "scenario": "Users with valid tokens but no notes are omitted from /admin/users", "fix": "Derive user list from the user/auth registry or confirm intended"}
  ]
}
```