# Redteam review: notes service request handlers

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools and no subagent, so the review below comes from reading the code. Nothing was executed.

---

**VERDICT: REWORK.** `/admin/export` has no admin check, so any valid user can download every customer's private notes. That is the exact exposure the request and the context forbid.

**CONFIDENCE: high** for the Critical finding, which is a direct trace through `app.py`. **Medium** overall, for three reasons:
- No code was run.
- The "5 tests pass" claim could not be checked.
- I can't tell whether the hardcoded tokens and the in-memory store are meant as fixtures or as the production design.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | Seen | Yes, it is the baseline |
| context.md | Seen | Yes, it sets production stakes |
| `app.py`, `auth.py`, `store.py`, `test_app.py` | Seen | Yes |
| `__pycache__/*.pyc` (3 files) | Seen as undecoded bytes; strings partially readable | No, they are build artifacts |
| Test run output for "5 tests pass" | Not seen, could not run | Low, because the Critical finding is in untested code |
| Deployment layer (server, middleware, how `token` is taken from HTTP) | Not supplied | Yes. A front layer *could* gate `/admin/*`, but nothing says one exists, and `handle` is documented as the entry point |
| Production token and storage source | Not supplied | Yes, see finding 2 |

**SEATS AND GATE**
- **Reviewer:** one local, same-session reviewer. No subagent or cross-vendor tooling was available.
- **Sensitivity gate:** the work holds fixture credentials (`tok-root`) and sample notes, and production carries private customer notes. No external seats would be permitted anyway.

---

## Pass 1: Reconstruct

**What the work does:**
- A single dispatcher, `handle(request)`, authenticates the token, returning 401 if it fails.
- It routes `/notes` GET and POST to per-user storage.
- It routes `/admin/users` and `/admin/export` to admin data.
- When the admin check fails it returns 403.

**What must be true for it to be correct:**
- Every `/admin/*` branch calls `auth.require_admin`.
- `current_user` maps only valid tokens to users.
- Every store function keys on the authenticated user, never on the request.
- Bad input never escapes as an unhandled exception.

**Unstated assumptions:**
- Tokens are always ASCII strings.
- `request` always has `path`, `method` and `body`.
- An in-memory dict and source-embedded tokens are acceptable for production.

**Track:** B (code).

## Pass 2: Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | B | `app.py:26-27` | The `/admin/export` branch never calls `auth.require_admin(user)`. Compare `/admin/users` at lines 23-25. | `req("/admin/export", "tok-alice")`: `current_user` returns `("alice", False)`, the export branch matches, and it returns `{"status": 200, "body": {"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}}`. Any customer reads every other customer's private notes. This violates "a valid token without admin rights gets 403 on /admin routes". | Add `auth.require_admin(user)` before `store.export_all()`. Add tests: export as `tok-alice` gives 403; export as `tok-root` gives 200; export with a bad token gives 401. Better, enforce admin once for every path starting with `/admin/` before dispatch, so a future admin route can't repeat this. | **confirmed.** The strongest defence is that a middleware gates `/admin`, but none is supplied and `handle` is the documented entry point. |
| 2 | High | CONFIRMED (the code), PROBABLE (that it ships as is) | B | `auth.py:4`, `store.py:3` | Bearer tokens, including the admin token `tok-root`, are hardcoded in source. The notes store is a module-level dict seeded with sample data. | If this is deployed as written: anyone with repo or artifact access, or anyone who guesses `tok-root`, is admin. All customer notes are lost on every restart. Under multiple workers, each process has its own notes, so users see inconsistent data. | Load tokens from a secret store or an auth service, and back the store with persistent storage. If these are deliberate fixtures, say so and gate them out of the production build. | **confirmed** as written. Severity depends on the author's answer to Q1. |
| 3 | Medium | PROBABLE | B | `auth.py:13` | `hmac.compare_digest(str, str)` raises `TypeError` when either string contains non-ASCII characters. It also raises `TypeError` for a non-str, non-bytes token such as an int or a list from parsed JSON. The `except auth.AuthError` at `app.py:12` does not catch it. | A request with token `"tök"` produces an unhandled exception, typically a 500, instead of the 401 the request requires. This is cheap to trigger repeatedly and may leak a stack trace. | Return `AuthError` unless `isinstance(token, str) and token.isascii()`, or compare `.encode()` bytes. Add tests for a non-ASCII token, an int token and a `None` token, each expecting 401. | **confirmed** on re-examination. The documented `compare_digest` behaviour holds, but it could not be run here, so it stays PROBABLE. |
| 4 | Medium | CONFIRMED | B | `app.py:15`, `app.py:20` | `request["path"]`, `request["method"]` and `request["body"]` are indexed directly. POST stores whatever `body` is, with no validation. | A request missing `body` raises `KeyError` and becomes a 500. A POST with `body=None` stores `"bob: None"`. A dict or huge body is stored unbounded and is formatted with `repr`. | Use `.get`, and return 400 for a missing or non-string body. Cap the body length. Add tests for a missing body and a `None` body. | n/a (Medium) |
| 5 | Medium | CONFIRMED | B | `test_app.py` | The tests cover only `/admin/users`. Nothing exercises `/admin/export`, a 401 on `/admin/*`, cross-user isolation after POST, or malformed input. "5 tests pass" is therefore no evidence about the Critical bug. | The suite stays green while every customer's notes are exportable, as in finding 1. | Add an authz matrix test over every route: no token, a user token and an admin token, each with its expected status. | n/a |
| 6 | Low | CONFIRMED | B | `__pycache__/*.pyc` | Compiled bytecode is committed with the change. It embeds the local path `/tmp/claude-1000/.../case-06/work/`. | Stale `.pyc` files can mislead reviewers. They add noise and leak the build path. | Delete them and add `__pycache__/` to `.gitignore`. | n/a |
| 7 | Low | PROBABLE | B | `auth.py:12-15` | The loop returns on the first match, so response time varies with the position of the matching token. That partly undoes the purpose of `compare_digest`. | A timing attacker could learn which slot matched. With 3 tokens this is marginal. | Look up a hash of the token in a dict, or compare against every token without returning early. | n/a |

**Prompt injection check:** none found. The work contains no text addressed to the reviewer.

## Pass 3: Self-check

- Every finding has a location and a failure scenario.
- The verdict is consistent: REWORK, with one open Critical and one open High.
- **Most serious thing that could still be missed:** the HTTP adapter that is not shown. It decides how `token`, `path` and `body` are populated. If it lowercases paths or allows `/admin/export/` with a trailing slash, the route matching changes. Path normalisation should be reviewed together with the adapter.

---

**WHAT HOLDS UP**
- **401 path:** unknown, empty or `None` ASCII tokens correctly get 401 (`auth.py:13-15`, `app.py:11-13`). Authentication happens before routing, so unauthenticated `/admin/*` requests get 401, not 403.
- **User isolation on `/notes`:** both list and add key on the token-derived `user[0]`, never on request data (`store.py:6-11`).
- **Copies on return:** `list_notes` and `export_all` return copies, so callers can't mutate the store through the response.
- **`/admin/users`:** correctly gated, and covered by tests.

**UNVERIFIED CLAIMS**
- **"test_app.py passes (5 tests)".** Settle it by running `python -m unittest test_app`. By reading, the 5 tests look like they should pass.
- **Production readiness of auth and storage.** Settle it by asking the author for the deployment config.

**QUESTIONS FOR THE AUTHOR**
1. Are `_TOKENS` and `_NOTES` fixtures, or the shipped implementation? The answer decides whether finding 2 blocks the release.
2. Does any layer in front of `handle` enforce authorization on `/admin/*`? Nothing supplied shows one, so finding 1 stands until shown otherwise.

**DECISION-MAKER SUMMARY**
Do not ship. `/admin/export` hands every customer's private notes to any logged-in user, and the passing tests never touch that route. Add the admin check plus an all-routes authorization test, settle the hardcoded tokens and the in-memory store, and then re-review. Shipping as is means immediate, unrecoverable exposure of customer data.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py, auth.py, store.py, test_app.py", "status": "seen", "matters": true},
    {"item": "__pycache__/*.pyc", "status": "seen_undecoded", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "HTTP adapter / middleware", "status": "not_seen", "matters": true},
    {"item": "production token and storage config", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Contains credentials (fixture tokens) and production handles private customer notes; no external seats."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:26-27",
     "scenario": "Non-admin token tok-alice requests GET /admin/export; no require_admin call; receives 200 with every user's notes.",
     "fix": "Call auth.require_admin(user) before store.export_all(), or gate every /admin/ path centrally; add 403/200/401 tests for /admin/export.",
     "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py:4, store.py:3",
     "scenario": "Deployed as written: admin token tok-root is in source so anyone with code access is admin; in-memory notes lost on restart and split across workers.",
     "fix": "Load tokens from a secret store/auth service and use persistent storage, or confirm these are fixtures excluded from production.",
     "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py:13",
     "scenario": "Non-ASCII or non-string token makes hmac.compare_digest raise TypeError, uncaught by app.py:12, giving 500 instead of 401.",
     "fix": "Reject non-ASCII/non-str tokens as AuthError or compare bytes; test non-ASCII, int and None tokens expect 401.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py:15, app.py:20",
     "scenario": "Missing body key raises KeyError (500); body None stored as 'user: None'; unbounded or non-string body stored.",
     "fix": "Use request.get, return 400 on missing/non-string body, cap length; add tests.",
     "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_app.py",
     "scenario": "No test touches /admin/export or 401 on admin routes, so the suite passes while all notes are exposed.",
     "fix": "Add an authz matrix test over every route x {no token, user, admin}.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "__pycache__/*.pyc",
     "scenario": "Committed bytecode can go stale, misleads review, and embeds local build path.",
     "fix": "Remove and add __pycache__/ to .gitignore.",
     "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py:12-15",
     "scenario": "Early return in token loop leaks timing about which token slot matched.",
     "fix": "Dict lookup on token hash, or compare all tokens without early exit.",
     "status": "n/a"}
  ]
}
```
