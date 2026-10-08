# pr-review: notes service request handlers

## Review report

**REVIEWED:** No PR number, head SHA or merge base was provided. I reviewed only the four files pasted in the inputs (`app.py`, `auth.py`, `store.py`, `test_app.py`). This report cannot be tied to a commit. Before anyone acts on it, record the PR and both SHAs and confirm the files match that head.

**TIER: High.** The change implements authentication and admin authorization over private customer notes, which is personal data in production with "no rollback window for data exposure." High tier needs two review rounds, ideally from two vendors. **This is round 1 of 2.** The PR is not reviewed until a second independent round has run on an endpoint approved for this data.

**REVIEWERS:** Round 1 is this session (Claude, claude-opus-5-5), which did not write the change. The author is unknown because no commit trailers were provided. The second reviewer has not been assigned.

**Limits:** I had no tools in this session. I ran nothing, including the "5 tests pass" claim. Every finding comes from reading and tracing the code.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `app.py:25-26` | `/admin/export` never calls `auth.require_admin(user)`. Any valid non-admin token, such as `tok-alice` sending `GET /admin/export`, gets **200 with every user's notes**, including `root: rotate keys`. This is a direct breach of the request ("a valid token without admin rights gets 403 on /admin routes") and exposes private customer data. | `self.assertEqual(req("/admin/export", "tok-alice")["status"], 403)` fails today (200). Also assert `req("/admin/export", "tok-root")["status"] == 200`. |
| 2 | **P1** | `auth.py:4` | Tokens are hard-coded in source, and the admin token is the guessable `tok-root`. If this table ships to production as written, anyone who reads the repo or guesses the token has full admin access, including the export. Severity is P0 if this is the real production token source and P1 if it is a stub. **The author must confirm which.** | Have a test or startup check that fails when `_TOKENS` contains literal source-defined tokens in a production config, for example by loading tokens from the environment or a secret store and asserting the module has no default admin token. |
| 3 | P2 | `auth.py:13` (called from `app.py:11`) | `hmac.compare_digest` raises `TypeError` for a `str` containing non-ASCII characters, or for a non-str/bytes token such as an int. A request with token `"tök"` or `123` escapes `except auth.AuthError` and `handle` raises instead of returning 401. A client can trigger this at will, causing a 500 and possibly a crash, depending on the server wrapper. | `self.assertEqual(req("/notes", "tök")["status"], 401)` and `req("/notes", 123)` → 401. Both raise `TypeError` today. |
| 4 | P3 | `app.py:22-28` | Admin routes are matched on path *and* method before the admin check. A non-admin sending `POST /admin/users`, or `GET /admin/anything`, gets 404, not the 403 the request specifies for "/admin routes". Admins and non-admins get the same answers, so the impact is low, but it breaks the spec as written. | `self.assertEqual(req("/admin/users", "tok-alice", "POST")["status"], 403)` fails today (404). |
| 5 | P3 | `app.py:19-20`, `store.py:11-12` | `POST /notes` does not validate the body. A missing or `None` body is stored as `"bob: None"`, and a dict or list body is stored as its repr. Notes get corrupted without any error. | `req("/notes", "tok-bob", "POST", None)["status"] == 400` and the note count is unchanged. Fails today (201). |
| 6 | P2 | `test_app.py` (whole file) | The test suite has no test for `/admin/export` and none for non-admin access to it. "5 tests pass" is consistent with finding #1 shipping. The claimed coverage does not cover the riskiest route. | Add the tests from #1 and #4. A suite that covers each `/admin` route must fail on today's code. |

**FILES NEEDED BUT NOT PROVIDED:**
- The PR and its diff against the merge base. Without it I can't tell what is new and what already existed.
- Commit trailers, to identify the author.
- The server or wrapper that calls `app.handle`, to see how uncaught exceptions are handled (#3).
- The production token and config source (#2).
- CI configuration, to see which checks are expected.

## Close-out

Not written. The author adjudicates these findings, and the reviewer must not.

**ADJUDICATION:** pending for #1–#6.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.**
- **Open blocker:** finding #1 (P0). Any authenticated user can export every user's private notes. P0 cannot be deferred.
- **Owner decision needed:** finding #2. Are the hard-coded tokens the production credentials?
- **Required round missing:** this is High tier, and the second review round has not run.
- **Unverified checks:** no SHAs or CI results were provided, and the tests were not run here.

The fix for #1 is one line (`auth.require_admin(user)` before `export_all()`). It needs a regression test that fails without the fix, as in #1. That fix should be verified by reading the correction diff and running the tests, not by another full round. The second High-tier round is still required separately.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code-read, traced (not executed)",
      "location": "app.py:25-26",
      "scenario": "GET /admin/export with non-admin token tok-alice returns 200 and every user's notes; require_admin is never called on this route.",
      "fix": "Call auth.require_admin(user) before store.export_all(); add tests asserting 403 for tok-alice and 200 for tok-root on /admin/export."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read; production impact unconfirmed (P0 if these are the production tokens)",
      "location": "auth.py:4",
      "scenario": "Tokens, including the guessable admin token 'tok-root', are hard-coded in source; anyone with repo access or a guess gains admin and can export all notes.",
      "fix": "Load tokens from a secret store or environment, with no source-defined admin token; add a check that fails if defaults are present in production config."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read, documented hmac.compare_digest behavior (not executed)",
      "location": "auth.py:13",
      "scenario": "A token that is a non-ASCII str (e.g. 'tök') or non-str/bytes (e.g. 123) makes hmac.compare_digest raise TypeError, which escapes 'except auth.AuthError' in app.py:12, so handle raises instead of returning 401.",
      "fix": "Reject tokens that are not ASCII str before comparing (or compare encoded bytes) and raise AuthError; add tests for 'tök' and 123 expecting 401."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read, traced",
      "location": "app.py:22-28",
      "scenario": "A non-admin sending POST /admin/users or GET /admin/<unknown> gets 404, not the 403 the spec requires for /admin routes.",
      "fix": "For any path starting with /admin, call require_admin before route and method matching; test that non-admin POST /admin/users returns 403."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read, traced",
      "location": "app.py:19-20; store.py:11-12",
      "scenario": "POST /notes with a missing, None or non-string body stores 'bob: None' or a repr and returns 201.",
      "fix": "Validate that body is a non-empty str and return 400 otherwise; add a test."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read of test file",
      "location": "test_app.py",
      "scenario": "No test covers /admin/export, so the 5 passing tests are consistent with the P0 data exposure shipping.",
      "fix": "Add authorization tests for every /admin route, for both non-admin (403) and admin (200)."
    }
  ]
}
```