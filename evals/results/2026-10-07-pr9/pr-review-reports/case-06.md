# pr-review: notes service request handlers

## Review report

**REVIEWED:** No PR number, head SHA or merge base was supplied. I reviewed only the four source files and the test file pasted into this session. **Step 1 is not satisfied.** This report cannot be tied to a commit, so it must be re-anchored to a head SHA before anyone relies on it.

**TIER: High.** The change implements authentication and admin authorization (401/403 gating), and the data is private customer notes with "no rollback window for data exposure." The tier needs two rounds, ideally from two vendors. **This is round 1 of 2. The PR is not reviewed until a second round runs.**

**DATA HANDLING (Step 3):** The code was reviewed in this session only and sent nowhere. The second round's endpoint still needs approval for code that carries customer notes and live tokens.

**REVIEWERS:**
- Reviewer: this instance (Claude Opus 5.5, `claude-opus-5-5`), single round, read-only. No tools, so nothing was executed.
- Author: unknown, because no commit trailers were provided. This session did not write the change.

**Claims not verified:** "test_app.py passes (5 tests)" was not run. From reading the tests, I expect all 5 to pass. That is exactly the problem: none of them touches `/admin/export`.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `app.py:25-26` | `/admin/export` never calls `auth.require_admin(user)`; only `/admin/users` (line 23) does. Any valid non-admin token, e.g. `{"path": "/admin/export", "method": "GET", "token": "tok-alice"}`, gets 200 with every user's notes, including `root: rotate keys`. This directly violates the request ("a valid token without admin rights gets 403 on /admin routes") and is the customer-data exposure the context says cannot be rolled back. | `self.assertEqual(req("/admin/export", "tok-alice")["status"], 403)` and the same for `tok-bob`. Add `self.assertEqual(req("/admin/export", "tok-root")["status"], 200)`. The first fails today with 200. |
| 2 | **P1** | `auth.py:4` | Tokens, including the admin token `tok-root`, are hard-coded in source and trivially guessable (`tok-<username>`). Anyone with read access to the repo, or anyone who guesses the pattern, holds admin. With finding 1 fixed, `tok-root` still unlocks `/admin/export` in production. If this table is a test fixture, nothing in the PR says so, and production has no other token source. | A test that imports `auth` with no configured secret store and asserts that `current_user("tok-root")` raises `AuthError`, i.e. tokens come from config/secret storage, not source. |
| 3 | P2 | `auth.py:14` | `hmac.compare_digest(known, token or "")` raises `TypeError`, not `AuthError`, when the token is a non-ASCII `str` (`"tök"`) or a non-str/bytes type (e.g. an int from a JSON body). `app.py:12` only catches `AuthError`, so the request crashes (500 or worker error) instead of returning 401. Anonymous input can trigger it. | `self.assertEqual(req("/notes", "tök")["status"], 401)` and `self.assertEqual(req("/notes", 123)["status"], 401)`. Both raise `TypeError` today. |
| 4 | P3 | `app.py:22-26`, `app.py:29` | For a non-admin token, any `/admin/*` path other than `GET /admin/users` and `GET /admin/export` (e.g. `POST /admin/users`, `GET /admin/foo`) returns 404, not 403. The request says non-admins get 403 on /admin routes. It also lets non-admins tell real admin routes (403) from fake ones (404). | `self.assertEqual(req("/admin/foo", "tok-alice")["status"], 403)` and `self.assertEqual(req("/admin/users", "tok-alice", "POST")["status"], 403)`. |
| 5 | P3 | `app.py:20` | `request["body"]` raises `KeyError` if a POST omits `body`, an unhandled crash. With `body: None` it stores the literal note `"bob: None"`. | `self.assertEqual(req("/notes", "tok-bob", "POST", None)["status"], 400)`, plus a request dict with no `body` key also expecting 400. |
| 6 | P3 | `__pycache__/*.cpython-312.pyc` | Compiled bytecode is committed, built from `/tmp/claude-1000/.../case-06/work`. These are build artifacts that can go stale against the source. If a committed `.pyc`'s recorded source mtime and size happen to match, Python loads the bytecode instead of the reviewed source, so the reviewed text and the running code can diverge. | A CI check failing when `git ls-files '*.pyc'` is non-empty. Add `__pycache__/` to `.gitignore`. |

**Test gap behind finding 1:** the suite tests the admin gate on one admin route and assumes it covers both. Every `/admin/*` route needs a non-admin-gets-403 test.

**FILES NEEDED BUT NOT PROVIDED:**
- PR number, head SHA and merge base
- Commit log with trailers
- CI configuration and check results
- The server or framework code that calls `handle()`: how `token` is extracted, and what an uncaught exception becomes
- Where production tokens are meant to come from
- `.gitignore`

## Close-out

**Not written yet.** The author adjudicates these findings and whoever closes the PR writes the close-out. A reviewer does not adjudicate its own findings.

**Reviewer's position for whoever closes:** on current evidence this cannot be recommended for merge.
- **P0 #1 is open.** It cannot be deferred, and it exposes all customer notes to any logged-in user.
- **P1 #2 is open** and also cannot be deferred.
- **The High tier's second round has not run.**
- **No head SHA or CI results** were provided, so no check can be confirmed green.

Fixing #1 is a one-line change (`auth.require_admin(user)` before `store.export_all()`) plus the regression tests above. Verify it by reading the correction diff and running the new tests, not by another full round. The second round is still required by the tier.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code-read (not executed)",
      "location": "app.py:25-26",
      "scenario": "GET /admin/export with non-admin token tok-alice returns 200 and every user's notes, including root's; require_admin is never called on this route, violating the 403 requirement for /admin routes.",
      "fix": "Call auth.require_admin(user) before store.export_all(); add tests asserting 403 for tok-alice/tok-bob and 200 for tok-root on /admin/export."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read (not executed)",
      "location": "auth.py:4",
      "scenario": "Admin token 'tok-root' and user tokens are hard-coded in source and follow a guessable tok-<user> pattern; anyone with repo access or who guesses it gets admin, including /admin/export.",
      "fix": "Load tokens (or hashes of them) from a secret store/config with high-entropy values; keep the literal table only as a test fixture."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed); relies on documented hmac.compare_digest behaviour",
      "location": "auth.py:14",
      "scenario": "A non-ASCII str token or a non-str/bytes token (e.g. int) makes hmac.compare_digest raise TypeError, which app.py:12 does not catch; an anonymous request crashes instead of getting 401.",
      "fix": "Reject tokens that are not ASCII str before comparing (raise AuthError), or catch TypeError and raise AuthError; add tests for 'tök' and 123 expecting 401."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "app.py:22-26, app.py:29",
      "scenario": "A non-admin requesting an unmatched /admin/* path or method (e.g. POST /admin/users, GET /admin/foo) gets 404 rather than 403, contrary to the spec, and can distinguish real admin routes from absent ones.",
      "fix": "Gate all paths starting with /admin/ on require_admin before route matching."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "app.py:20",
      "scenario": "POST /notes with no 'body' key raises an unhandled KeyError; body None is stored as the note 'user: None'.",
      "fix": "Use request.get('body'), validate it is a non-empty str, and return 400 otherwise."
    },
    {
      "severity": "P3",
      "evidence_level": "file listing",
      "location": "__pycache__/*.cpython-312.pyc",
      "scenario": "Committed bytecode built from a temp path can go stale against the source, or be loaded instead of the source if the recorded mtime/size match, so the reviewed code and the running code can diverge.",
      "fix": "Remove the __pycache__ files from the PR, add __pycache__/ to .gitignore, and fail CI on tracked .pyc files."
    }
  ]
}
```
