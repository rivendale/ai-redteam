# pr-review report: notes service request handlers

## Before the findings: what this review can and cannot claim

- **Target not frozen (Step 1).** No PR number, head SHA or merge base was supplied. The change was pasted in, so I could not check out a worktree. I have no tools, so nothing was run. This report covers **only the four files shown above**. If they differ from the PR head, this is not a review of that head.
- **Tier: High (Step 2).** The change implements authentication, admin authorization and access to private customer notes. The context says production with "no rollback window for data exposure". High tier needs **two rounds, ideally on two vendors**. This is **round 1 of 2**. The PR is not reviewed until round 2 runs.
- **Data (Step 3).** No approved endpoints were named. I sent nothing outside this session. The owner must choose an approved endpoint for round 2 before sending the code anywhere.
- **Independence (Step 4).** As far as this session shows, it did not write the change. Without the commits I cannot read the author from the trailers.
- **"test_app.py passes (5 tests)"** is a claim I could not verify. Even if true, no test touches `/admin/export`, the route that fails below.

---

**Review report**

REVIEWED: pasted change (app.py, auth.py, store.py, test_app.py). Head SHA: not provided. Merge base SHA: not provided.
TIER: High. Auth and permissions, plus private customer data in production.
REVIEWERS: round 1 by Claude Opus 5.5 (claude-opus-5-5), a session separate from the author, reading the code without running it. Round 2 is still required on an approved endpoint. Author: unknown, since no commit trailers were available.

FINDINGS:

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `app.py:26-27` | `/admin/export` never calls `auth.require_admin(user)`, unlike `/admin/users` (`app.py:24`). Alice sends `{"path": "/admin/export", "method": "GET", "token": "tok-alice"}`. `current_user` succeeds, the branch returns `store.export_all()` and she gets 200 with every user's notes, including `"root: rotate keys"`. Any valid token can leak all customer data. The request requires 403. Root cause: admin checks are opt-in per route, so each new `/admin` route is open by default. | `assertEqual(req("/admin/export", "tok-alice")["status"], 403)` fails today (returns 200). Add `assertEqual(req("/admin/export", "tok-root")["status"], 200)` and `assertEqual(req("/admin/export", "nope")["status"], 401)`. |
| 2 | P1 | `auth.py:4` | The token table, including the admin token `"tok-root"`, is hardcoded in source. If this module ships as is, anyone with repo access, or anyone who guesses the obvious string, has admin rights and can export all notes once #1 is fixed. Tokens never expire and cannot be rotated without a deploy. This is conditional: it is downgraded or rejected if production loads tokens from elsewhere, which this change does not show. | A test or deploy check that fails if `auth._TOKENS` contains a literal admin token, e.g. tokens must come from config or a secret store at startup. Assert `current_user("tok-root")` raises `AuthError` in a production configuration. |
| 3 | P2 | `auth.py:13` | `hmac.compare_digest` on two `str` values raises `TypeError` if either contains non-ASCII characters. It also raises if the token is a non-str truthy value such as an int. A request with token `"tök"` makes `current_user` raise `TypeError`, not `AuthError`. `handle` does not catch it at `app.py:12`, so an unauthenticated request crashes the handler (500) where the request requires 401. | `assertEqual(req("/notes", "tök")["status"], 401)` and `assertEqual(req("/notes", 123)["status"], 401)`. Both raise today. Fix: encode both sides to bytes, or reject non-ASCII and non-str tokens with `AuthError`. |
| 4 | P2 | `app.py:20` | `request["body"]` raises `KeyError` when a POST omits `body`, giving an unhandled exception and a 500. A `None` body (the test helper's default) is stored as `"alice: None"`, and non-string bodies are stored through the f-string. | `handle({"path": "/notes", "method": "POST", "token": "tok-bob"})` should return 400. A POST with `body=None` should return 400 and leave `list_notes` unchanged. |
| 5 | P3 | `store.py:17-18` | `list_users()` returns the keys of `_NOTES`, so it lists only users who have at least one note, not all users. Provision `tok-carol` with no notes and `/admin/users` omits carol. The request says "/admin/users lists users". | Add a user to the token table with no notes and assert they appear in `req("/admin/users", "tok-root")["body"]`. |

Structural note on #1: put one gate in `handle`, such as `if path.startswith("/admin"): auth.require_admin(user)` before routing. This closes the whole class of missed checks instead of only this instance. The test for #1 must still be added either way.

FILES NEEDED BUT NOT PROVIDED: PR identity and head/merge-base SHAs; the commit log (author trailers); how tokens are provisioned in production (decides #2); the server or framework that calls `handle` (how unhandled exceptions surface, relevant to #3 and #4); CI check results.

---

**Close-out**

The author adjudicates each finding, not this reviewer. Status:

ADJUDICATION: pending for #1 to #5. #1 (P0) and #2 (P1, if confirmed) cannot be deferred.
VERIFIED AFTER FIXES: nothing yet. A fix for #1 is verified by reading the correction diff and running the new `/admin/export` tests, not by another full review.
MERGE RECOMMENDATION: **do not merge.** Open items: P0 #1 lets any logged-in user export every customer's notes; High-tier round 2 has not run; the head SHA was never frozen; there are no CI check results.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by code reading (not executed; no tools)",
      "location": "app.py:26-27",
      "scenario": "GET /admin/export with non-admin token tok-alice passes current_user, never hits require_admin, returns 200 with every user's notes. Required: 403.",
      "fix": "Call auth.require_admin(user) for every /admin path, preferably once in handle() via path.startswith('/admin') before routing. Add tests: alice -> 403, root -> 200, bad token -> 401."
    },
    {
      "severity": "P1",
      "evidence_level": "code reading; conditional on production using this token table",
      "location": "auth.py:4",
      "scenario": "Admin token 'tok-root' and user tokens hardcoded in source; anyone with repo access or who guesses it gains admin and can export all notes; no rotation or expiry.",
      "fix": "Load tokens/credentials from a secret store or config at startup; remove literals from source; add a check that no literal admin token ships."
    },
    {
      "severity": "P2",
      "evidence_level": "code reading plus documented hmac.compare_digest behavior (not executed)",
      "location": "auth.py:13",
      "scenario": "Token with non-ASCII characters (e.g. 'tök') or a non-str value (e.g. 123) makes compare_digest raise TypeError, which handle() does not catch: 500 instead of 401.",
      "fix": "Reject non-str tokens and compare UTF-8 bytes (or reject non-ASCII) raising AuthError; test both cases return 401."
    },
    {
      "severity": "P2",
      "evidence_level": "code reading",
      "location": "app.py:20",
      "scenario": "POST /notes without a 'body' key raises KeyError (500); body=None is stored as 'alice: None'.",
      "fix": "Validate body is a non-empty string; return 400 otherwise; test missing and None bodies."
    },
    {
      "severity": "P3",
      "evidence_level": "code reading",
      "location": "store.py:17-18",
      "scenario": "list_users derives users from _NOTES keys, so a provisioned user with no notes is missing from /admin/users.",
      "fix": "List users from the user/token registry, not the notes store; test a user with zero notes appears."
    }
  ]
}
```