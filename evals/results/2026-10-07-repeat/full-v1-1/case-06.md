**Review mode:** I had no tools, so nothing below was executed. "CONFIRMED" means I traced it by hand to an exact line. The work was not produced in this conversation, so there is no anchoring to the author's reasoning.

VERDICT: **REWORK.** `/admin/export` has no admin check, so any valid user can dump every customer's private notes, and the passing tests do not cover that route.
CONFIDENCE IN VERDICT: **high** for the export flaw (a direct trace of a few lines); medium overall, because I could not run code, decompile the shipped `.pyc` files, or see the deployment's real token source.

## Pass 1: Reconstruct

The change adds `handle(request)`. It resolves a token to `(name, is_admin)`, returns 401 for unknown tokens, and serves per-user `/notes` GET and POST. `/admin/users` and `/admin/export` are meant to be admin-only, returning 403 for non-admins. The tests are offered as evidence that it works.

For this to be correct, all of the following must hold:
- Every `/admin` branch calls `require_admin`.
- `current_user` cannot be tricked or crashed.
- `store` scopes data by the authenticated name.
- The 5 tests cover the authorization matrix the request specifies.

There are also unstated assumptions:
- Hardcoded tokens and an in-memory store are acceptable in production.
- Requests always carry the keys `path`, `method` and `body`.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | `app.py`, the `if path == "/admin/export"` branch | `auth.require_admin(user)` is missing. Only `/admin/users` calls it. | `req("/admin/export", "tok-alice")` returns 200 with `{"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}`. Any valid user reads every customer's notes. That is the exact exposure the context says cannot be rolled back. | Add `auth.require_admin(user)` before `store.export_all()`. Better, gate all `path.startswith("/admin")` routes once, before dispatch, so a new admin route cannot forget the check. Add tests: export with `tok-alice` returns 403, export with `tok-root` returns 200. |
| 2 | High | CONFIRMED | `test_app.py` | The test suite has no case for `/admin/export`, which is the most sensitive route. "5 tests pass" is true but says nothing about the requirement that matters most. | Finding 1 shipped with a green suite. Any future regression in admin gating on other routes would also pass. | Add a table-driven test over every route × {no token, user token, admin token}, asserting 401/403/200 as the spec requires. |
| 3 | High | CONFIRMED | `auth.py`, `_TOKENS` | Bearer tokens are hardcoded in source, including the admin token `"tok-root"`, and are guessable. | Anyone with repo or artifact access, including the `__pycache__/auth.cpython-312.pyc` bundled in this change, has admin. The tokens cannot be rotated without a deploy. | Load token hashes from a secret store or config. Never commit them. Rotate anything that has already been committed. |
| 4 | Medium | CONFIRMED | `auth.py`, `hmac.compare_digest(known, token or "")` | `compare_digest` raises `TypeError` for a non-ASCII `str` or a non-str/bytes value. The error is not `AuthError`, so nothing catches it. | A token of `"tök"` or `123` raises an uncaught exception, which becomes a 500 or a crash instead of a 401. Attackers can trigger errors on demand. | Reject a token that is not an ASCII `str` (raise `AuthError`), or compare `.encode()` bytes. Add tests with a non-ASCII token and a non-string token. |
| 5 | Medium | CONFIRMED | `app.py`, `request["path"]`, `request["method"]`, `request["body"]` | There is no validation of request shape or body. | If `body` is missing, a `KeyError` produces a 500. If `body` is `None`, the note `"bob: None"` is stored. The existing `test_post_creates` passes `body=None` only by accident through the helper. Non-string bodies (dicts, huge payloads) are stored as is. | Use `.get`, require a non-empty `str` with a length cap, and return 400 otherwise. Add a test for each. |
| 6 | Low | CONFIRMED | `app.py`, fallthrough `return 404` | Non-admins hitting `/admin/<unknown>`, or a non-GET method on admin routes, get 404 rather than the 403 the spec states for "/admin routes". | `POST /admin/export` with `tok-alice` returns 404. This is a minor spec deviation and lets callers probe which routes exist. | Applying the prefix gate from Finding 1 fixes this. |
| 7 | Low | CONFIRMED | `__pycache__/*.pyc` | Compiled bytecode is included in the change. | The bytecode can diverge from the reviewed source, and it ships the hardcoded tokens a second time. Reviewers cannot audit it. | Remove the files and add `__pycache__/` to `.gitignore`. |
| 8 | Low | PROBABLE | `test_app.py`, `test_post_creates` | The test mutates the module-global `_NOTES` and never resets it. | Tests depend on run order. A future bob-notes assertion would break depending on order. | Reset the store in `setUp`. |

## What holds up

- The 401 path is sound. An unknown, empty or `None` token reaches `AuthError` and returns 401, since `token or ""` handles `None`.
- `/notes` scoping is correct. Both `list_notes` and `add_note` key on the authenticated `user[0]`, not on anything the client supplies, so a user cannot read or write another user's notes through `/notes`.
- `/admin/users` gating is correct. A non-admin gets `AuthError`, which returns 403.
- Using `compare_digest` is the right instinct. Early return in the loop leaks only which slot matched, which is negligible here.
- `list_notes` and `export_all` return copies, so callers cannot mutate the store.

## Unverified claims

- **"test_app.py passes (5 tests)."** I could not run it, though my trace agrees it should pass. Confirm with `python -m unittest test_app -v`.
- **Whether the `.pyc` files match the `.py` source.** The embedded strings look consistent, but I could not decompile them. Confirm by deleting them and regenerating.
- **Production deployment details.** I don't know what fronts `handle()`, whether request dicts are always well-formed, or whether real tokens replace `_TOKENS`. Confirm from the deployment config.

## Questions for the author

1. Is `_TOKENS` the real production credential source? If so, Finding 3 is a blocker on its own.
2. Is an in-memory store intended for production? All notes are lost on restart, and nothing persists the data.
3. Will future `/admin/*` routes be added? If so, will you accept a single prefix gate instead of per-route checks?

## Decision-maker summary

Do not deploy. Any logged-in customer can call `/admin/export` and download every other customer's private notes, and the test suite does not check it. Add the admin check, gate the whole `/admin` prefix, add authorization tests for every route, and move the tokens out of source. Proceeding as is guarantees an irreversible data exposure.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "app.py: /admin/export branch", "scenario": "GET /admin/export with non-admin token tok-alice returns 200 and every user's notes; require_admin is never called", "fix": "Call auth.require_admin(user) before store.export_all(), preferably as a single gate for all /admin paths; add tests asserting 403 for tok-alice and 200 for tok-root"},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "test_app.py", "scenario": "No test covers /admin/export; the critical authz bug ships with a green suite", "fix": "Table-driven tests over every route x {no token, user, admin} asserting 401/403/200"},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "auth.py: _TOKENS", "scenario": "Guessable bearer tokens, including the admin tok-root, hardcoded in source and in committed .pyc; anyone with repo or artifact access gains admin", "fix": "Load hashed tokens from a secret store or config, remove them from source, rotate"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "auth.py: hmac.compare_digest(known, token or \"\")", "scenario": "Non-ASCII str or non-str token raises TypeError, which is not caught, producing a 500 or crash instead of 401", "fix": "Validate the token is an ASCII str (else AuthError) or compare bytes; add tests"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "app.py: request[\"path\"], request[\"method\"], request[\"body\"]", "scenario": "A missing key raises KeyError and a 500; a None body stores 'user: None'; unbounded or non-string bodies are stored", "fix": "Validate request shape and body (non-empty str, length cap) and return 400; add tests"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py: final 404 fallthrough", "scenario": "Non-admin requesting /admin/unknown or POST /admin/export gets 404 instead of the 403 the spec requires", "fix": "Gate on path.startswith('/admin') before routing"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "__pycache__/*.pyc", "scenario": "Unauditable bytecode committed; may diverge from source and duplicates the hardcoded tokens", "fix": "Remove the files and add __pycache__/ to .gitignore"},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "test_app.py: test_post_creates", "scenario": "Mutates the global _NOTES without reset, making tests order-dependent", "fix": "Reset store state in setUp"}
  ]
}
```
