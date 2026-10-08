**Review mode:** This is an independent review. The work came as supplied inputs, not from this conversation. No tools were available, so every finding below comes from reading and tracing the code by hand. Nothing was executed.

---

VERDICT: **REWORK.** `/admin/export` hands every customer's private notes to any authenticated user, and the token store is hardcoded in source. Both problems block production.

CONFIDENCE IN VERDICT: **High.** The critical finding follows directly from the code, with no branch or condition in the way. Two things limit confidence: I could not run the tests or the code, and the deployment model (how `handle` is called, where tokens should really come from) is not stated.

## Pass 1: Reconstruct

The change adds a single `handle(request)` dispatcher:
- It authenticates the token and returns 401 if the token is unknown.
- It serves `/notes` GET and POST for the caller's own notes.
- It gates `/admin/*` routes behind `auth.require_admin`, which raises `AuthError`; the dispatcher maps that to 403.

For this to be correct, three things must hold:
1. Every `/admin` branch calls `require_admin` before touching data.
2. `current_user` turns every bad token into `AuthError`, never some other exception.
3. The in-memory token and notes stores are acceptable for production.

The context also claims 5 passing tests stand in for verification, which is a load-bearing assumption. None of the tests touches `/admin/export`.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | `app.py`, the `/admin/export` branch: `return {"status": 200, "body": store.export_all()}` | It has no `auth.require_admin(user)` call, unlike the `/admin/users` branch above it. | `req("/admin/export", "tok-alice")` returns 200 with `{"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}`. Any customer can read every other customer's notes. The spec requires 403 here. | Add `auth.require_admin(user)` before `export_all()`. Better, check admin once for any path starting with `/admin` before dispatching, so a new admin route can't forget the check. Add tests: export as `tok-alice` returns 403, and export as `tok-root` returns 200. |
| 2 | High | CONFIRMED | `auth.py`, `_TOKENS = {"tok-alice": ..., "tok-root": ("root", True)}` | Credentials, including the only admin token, are hardcoded in source. They are low-entropy, guessable, and cannot be rotated without a code change. | Anyone with repo access, or anyone who guesses the `tok-<name>` pattern, gets admin. Rotating the key needs a redeploy. | Load hashed tokens from a secret store or config. Generate tokens with `secrets.token_urlsafe`. Compare against hashes. Keep fixture tokens in tests only. |
| 3 | Medium | CONFIRMED (documented `hmac.compare_digest` behavior) | `auth.py`, `hmac.compare_digest(known, token or "")` | `compare_digest` raises `TypeError` when given str and non-str arguments, or a str containing non-ASCII characters. Only `AuthError` is caught. | A token like `"tök"`, or a non-string token such as an int or list from a JSON body, raises an unhandled `TypeError`. The caller gets a 500 or crash instead of 401. That gives a cheap way to fault the service and may leak a stack trace. | Return `AuthError` early if `not isinstance(token, str)`. Compare on `token.encode()` bytes. Add tests for a non-ASCII token, a `None` token, and an int token, each expecting 401. |
| 4 | Medium | CONFIRMED | `app.py`, `request["path"], request["method"]` and `request["body"]` | Indexing raises `KeyError` on a missing key, and nothing catches it. `body=None` is accepted and stored as the literal text `"alice: None"`. Any non-string body gets stringified. | A POST without `body` crashes with a 500. A POST with `body: null` creates a garbage note. An unbounded body grows memory without limit. | Use `.get`. Validate that the body is a non-empty string under a size cap, and return 400 otherwise. Add tests for each case. |
| 5 | Medium | PROBABLE (depends on intended scope) | `store.py`, module-level `_NOTES` dict | Notes live only in process memory. | After a restart or redeploy, every customer note is lost. With multiple workers, each process has its own divergent store, so a user's POST may not show up on their next GET. | Confirm with the author whether persistence is in scope. If production means real customers, back the store with a database. |
| 6 | Low | CONFIRMED | `app.py`, the fall-through `return {"status": 404, ...}` | A non-admin hitting an unknown `/admin/*` path, or a wrong method on an admin path (e.g. `POST /admin/users`), gets 404. The spec says such callers get 403 on `/admin` routes. | `req("/admin/anything", "tok-alice")` returns 404. This deviates from the spec and lets non-admins enumerate which admin routes exist. | Enforce admin on the `/admin` prefix before routing (the same fix as #1). |
| 7 | Low | CONFIRMED | `store.py`, `list_users` returning `sorted(_NOTES)` | The user list is derived from note owners, not from the user registry. | A user who has never posted a note does not appear in `/admin/users`. Today all three seeded users have notes, so this is latent. | List users from the auth registry, or a real users table. |
| 8 | Medium | CONFIRMED | `test_app.py` | The tests never touch `/admin/export`. They don't test admin access to export, a missing or `None` token, malformed tokens, or POST validation. They also share mutable module state, since `test_post_creates` appends to `_NOTES` permanently. | The critical bug in #1 ships with a green suite. "5 tests pass" is not evidence that the authz requirements are met. | Add a parametrized matrix covering every route × {no token, bad token, user, admin} with expected status codes. Reset the store in `setUp`. |

## What holds up

- The 401 path is correct for unknown and empty tokens. `token or ""` handles `None`.
- `/notes` GET and POST correctly scope data to `user[0]`. There is no way to pass a target username, so users cannot reach each other's notes through `/notes`.
- `/admin/users` is correctly gated, and `AuthError` from `require_admin` maps to 403.
- `list_notes` and `export_all` return copies, so callers cannot mutate the store through the response.
- The 5 stated tests would pass according to the trace. Bob's POST does not disturb Alice's assertion.

## Unverified claims

- **"test_app.py passes (5 tests)":** By trace this is plausible, but it was not executed. Confirm by running `python -m unittest test_app -v`.
- **Production deployment model:** It is unknown whether there is a single process, what calls `handle`, and how exceptions surface to clients (whether there's a 500 handler, and whether stack traces leak). Confirm by inspecting the server wrapper.

## Questions for the author

1. Is the in-memory store and hardcoded token table meant for production, or is it a placeholder for a real auth system and DB? The answer decides whether #2 and #5 are blockers or out of scope.
2. What framework or server calls `handle`, and what does it do with an uncaught exception? This sets the real severity of #3 and #4.

## Decision-maker summary

Do not ship. Any logged-in customer can call `/admin/export` and download every user's private notes, and the tests miss it because they never exercise that route. Fix by gating the whole `/admin` prefix and adding a route × role test matrix. Replace the hardcoded tokens before production as well. If this ships anyway, assume all customer notes are exposed to every account holder from day one.

```json
{
  "verdict": "REWORK",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "app.py: /admin/export branch `return {\"status\": 200, \"body\": store.export_all()}`",
      "scenario": "Non-admin token tok-alice requests GET /admin/export and receives 200 with every user's notes (bob, root), exposing private customer data; spec requires 403.",
      "fix": "Call auth.require_admin(user) before export_all, preferably enforce admin once for any path starting with /admin; add tests: export as tok-alice -> 403, as tok-root -> 200."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "location": "auth.py: _TOKENS hardcoded dict including (\"root\", True)",
      "scenario": "Admin and user tokens are low-entropy, guessable (tok-<name>), committed in source, and unrotatable without redeploy; repo access or guessing yields admin.",
      "fix": "Load hashed, randomly generated tokens (secrets.token_urlsafe) from a secret store/config; keep fixture tokens in tests only."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "auth.py: hmac.compare_digest(known, token or \"\")",
      "scenario": "Non-ASCII str token or non-str token (int/list) makes compare_digest raise TypeError, which is not caught; request crashes with 500 instead of 401.",
      "fix": "Reject non-str tokens with AuthError, compare encoded bytes; add tests for non-ASCII, None and int tokens expecting 401."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "app.py: request[\"path\"], request[\"method\"], request[\"body\"]",
      "scenario": "Missing keys raise unhandled KeyError (500); body=None stores the note 'alice: None'; unbounded or non-string bodies are accepted.",
      "fix": "Use .get, validate body is a non-empty bounded string and return 400 otherwise; add tests."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "store.py: module-level _NOTES",
      "scenario": "Restart or redeploy loses all customer notes; multiple worker processes hold divergent stores so a POST may not appear on the next GET.",
      "fix": "Confirm scope; back the store with persistent shared storage for production."
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "location": "test_app.py",
      "scenario": "No test touches /admin/export, missing/malformed tokens or POST validation, so the critical authz bug ships with a green suite; tests share mutable global state.",
      "fix": "Add a parametrized route x {no token, bad token, user, admin} status matrix and reset the store in setUp."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "app.py: fall-through 404 return",
      "scenario": "Non-admin requesting an unknown /admin/* path or the wrong method on an admin route gets 404 instead of the specified 403, enabling admin route enumeration.",
      "fix": "Enforce admin on the /admin prefix before routing."
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "location": "store.py: list_users returns sorted(_NOTES)",
      "scenario": "Users with no notes are omitted from /admin/users.",
      "fix": "Derive the user list from the auth/user registry."
    }
  ]
}
```