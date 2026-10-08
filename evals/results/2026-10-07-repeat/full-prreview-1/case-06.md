# pr-review: notes service request handlers

## Review report

**REVIEWED:** No PR number, head SHA or merge base was provided. The change came inline (`app.py`, `auth.py`, `store.py`, `test_app.py`), so this review covers exactly that text and cannot be tied to a commit. The author must record both SHAs before close-out.

**TIER:** High. The change implements authentication and admin authorisation, and it serves private customer notes in production with no rollback window for data exposure.

- High tier requires two rounds, ideally from two vendors. **This is round 1 of 2.** The PR is not reviewed until a second independent round runs on an endpoint approved for this code.
- Data handling: no code left this session and no subagent was used. The review ran in this session on the provided text.

**REVIEWERS:** Claude Opus 5.5 (`claude-opus-5-5`), a fresh instance with no part in writing the change. The author is unknown because no commit trailers were provided.

Limits of this round: I had no tools, so I ran nothing. Every finding comes from reading the code. The claim "5 tests pass" is unverified, and it would not matter much anyway, because no test covers the route in finding 1.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `app.py:25-26` | The `/admin/export` branch never calls `auth.require_admin(user)`. A request `{"path": "/admin/export", "method": "GET", "token": "tok-alice"}` passes `current_user` and gets back status 200 with `store.export_all()`. That response holds every user's notes, including `"root: rotate keys"`. Any customer can dump all private notes, and the spec requires 403 here. | `self.assertEqual(req("/admin/export", "tok-alice")["status"], 403)`, and also assert the body contains no notes. Add `req("/admin/export", "tok-root")` → 200 as the positive case. |
| 2 | P1 | `auth.py:5` (`_TOKENS`) | Bearer tokens are hard-coded literals in source. The admin token is `"tok-root"`. If this ships as written, anyone who can read the repo, or who guesses the obvious pattern, becomes admin. Combined with export, that exposes every user's notes. This may be a deliberate stub; the author must confirm. | A deployment or config test asserting that tokens load from a secret store or environment, and that no literal token appears in `auth.py`. Alternatively, a test that `current_user("tok-root")` raises `AuthError` in the production configuration. |
| 3 | P2 | `auth.py:14` | `hmac.compare_digest` raises `TypeError` instead of returning False in two cases: a `str` that contains non-ASCII characters, or a non-`str` token such as an int or a list from parsed JSON. `handle` catches only `AuthError` (`app.py:12`), so the token `"tök"` crashes the handler. The client gets a 500 or an unhandled exception instead of the 401 the spec requires, and an unauthenticated client can trigger this at will. | `self.assertEqual(req("/notes", "tök")["status"], 401)` and `self.assertEqual(req("/notes", 123)["status"], 401)` |
| 4 | P3 | `app.py:22-26` | The admin check is applied per route, not to the `/admin` prefix. That design is the root cause of finding 1, and any future `/admin/*` route will need someone to remember the check. A non-admin calling an unknown or wrong-method admin path, such as `GET /admin/foo` or `POST /admin/users`, gets 404 rather than 403. That tells a non-admin which admin routes exist, and the spec says non-admins get 403 on /admin routes. | `self.assertEqual(req("/admin/anything", "tok-alice")["status"], 403)` |
| 5 | P3 | `app.py:20` | `POST /notes` does no body validation. If `body` is missing, `request["body"]` raises `KeyError`, which becomes a 500. If `body` is `None`, the stored note is `"bob: None"`. A non-string body is formatted and stored as-is. | `req("/notes", "tok-bob", "POST", None)` → 400, and `list_notes` of bob is unchanged. |

**Structural note:** Findings 1 and 4 share one cause. Authorisation is opt-in per branch. The fix that removes the whole class of bug is a single gate placed before route dispatch: `if path.startswith("/admin"): auth.require_admin(user)`. A per-route test for each admin endpoint should back it up.

**FILES NEEDED BUT NOT PROVIDED:**
- The PR, head SHA and merge base.
- Commit trailers that identify the author.
- The CI results or test-run output behind the "5 tests pass" claim.
- The production token and secret configuration, if any, needed to settle finding 2.
- The HTTP layer that builds the `request` dict. It decides whether tokens can be non-`str` (finding 3) and how uncaught exceptions are rendered.

## Close-out

Not written by this reviewer. A reviewer never adjudicates its own findings.

**ADJUDICATION:** pending author. Each of findings 1–5 needs Accepted, Deferred or Rejected, with a fix commit or evidence. Finding 1 (P0) and finding 2 (P1) cannot be deferred.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.**
- Finding 1 is an open P0: any authenticated user can export all customers' private notes.
- Finding 2 (P1) is unresolved.
- The second High-tier review round has not run.
- The head and merge-base SHAs are not recorded.
- CI checks have not been seen.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by code reading (not executed)",
      "location": "app.py:25-26",
      "scenario": "GET /admin/export with non-admin token tok-alice returns 200 and store.export_all(): every user's private notes. require_admin is never called on this route; spec requires 403.",
      "fix": "Call auth.require_admin(user) before export_all, preferably via a single /admin prefix gate before dispatch; add tests for non-admin 403 and admin 200 on /admin/export."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by code reading; production intent unknown",
      "location": "auth.py:5",
      "scenario": "Bearer tokens, including admin token 'tok-root', are hard-coded guessable literals in source; if deployed as-is, anyone with repo access or a guess is admin.",
      "fix": "Load tokens/credentials from a secret store or environment; issue high-entropy tokens; confirm this is not shipped as a stub."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from documented hmac.compare_digest behaviour (not executed)",
      "location": "auth.py:14",
      "scenario": "Non-ASCII str token (e.g. 'tök') or non-str token makes hmac.compare_digest raise TypeError, which handle() does not catch: unauthenticated request crashes with 500 instead of 401.",
      "fix": "Reject tokens that are not ASCII str before comparing (or compare encoded bytes), raising AuthError; add 401 tests for 'tök' and 123."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by code reading (not executed)",
      "location": "app.py:22-26",
      "scenario": "Admin authorisation is opt-in per route (root cause of the P0); non-admin requests to unknown or wrong-method /admin paths get 404 instead of 403, revealing route existence.",
      "fix": "Gate all paths starting with /admin on require_admin before route matching."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by code reading (not executed)",
      "location": "app.py:20",
      "scenario": "POST /notes with missing body raises KeyError (500); body None stores 'user: None'; non-string bodies stored unvalidated.",
      "fix": "Validate body is a non-empty string, return 400 otherwise; add a test."
    }
  ]
}
```