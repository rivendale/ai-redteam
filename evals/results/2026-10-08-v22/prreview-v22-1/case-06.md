# pr-review: notes service handlers

**Review report**

**REVIEWED:** PR number not provided. Head SHA not provided. Merge base SHA not provided. The change came inline as four files (`app.py`, `auth.py`, `store.py`, `test_app.py`). I could not freeze it to a commit or check it out in a worktree. This report covers exactly the text supplied. Any commit that differs from it is unreviewed.

**TIER:** High. The change implements authentication and admin authorization (401/403 gating). It hard-codes credentials. It serves customer notes, which the context calls private, with "no rollback window for data exposure." High tier requires two rounds, ideally on two different vendors.

**ROUNDS:** This is round 1 of 2. **The PR is not reviewed until round 2 runs.** Round 2 should go to a second vendor that is approved for code handling customer personal data, for example a zero-retention endpoint. The owner decides which endpoint that is. I cannot confirm one exists from here, and if none does, round 2 cannot run.

**REVIEWERS:**
- Reviewer: this instance, Claude Opus 5.5 (`claude-opus-5-5`). It has no part in authoring the change.
- Author: unknown. No commits or `Co-Authored-By` trailers were provided.

**Evidence level:** I had no tools, so every finding below comes from reading the code. None was executed. The claim "test_app.py passes (5 tests)" is also unverified, and none of those 5 tests touches `/admin/export`.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `app.py:26-27` (`/admin/export` branch) | The export branch never calls `auth.require_admin(user)`. Any valid non-admin token gets every user's notes. Example: `{"path": "/admin/export", "method": "GET", "token": "tok-alice"}` returns 200 with `{"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}`. The request requires 403 here. This is a full cross-tenant leak of private notes. | `self.assertEqual(req("/admin/export", "tok-alice")["status"], 403)` and `assertNotIn("bob", str(req("/admin/export", "tok-alice")["body"]))`. Also add the admin-allowed case: `req("/admin/export", "tok-root")["status"] == 200`. |
| 2 | **P1** | `auth.py:4` (`_TOKENS`) | Bearer tokens, including the admin token `tok-root`, are hard-coded in source. They are short and guessable. Anyone with read access to the repo, a build artifact, or a log of the source has admin access in production. Rotating a token requires a code deploy. | Test that `auth` loads tokens from configuration or a secret store and that no literal token appears in source. For example, assert that `current_user("tok-root")` raises `AuthError` when no secret is configured. |
| 3 | P2 | `auth.py:13` (`hmac.compare_digest(known, token or "")`) | `hmac.compare_digest` raises `TypeError` for a str containing non-ASCII characters, or when given mismatched types such as an int or bytes token. An unauthenticated request with token `"é"` or `123` escapes the `except auth.AuthError` in `app.py:11`. The caller gets an unhandled exception (likely a 500) instead of 401. Any anonymous client can trigger it repeatedly. | `self.assertEqual(req("/notes", "é")["status"], 401)` and `self.assertEqual(req("/notes", 123)["status"], 401)`. |
| 4 | P3 | `app.py:20-27, 30` | The request says a non-admin token "gets 403 on /admin routes." A non-admin calling `POST /admin/users` or `GET /admin/anything` gets 404 instead, because the admin check runs only inside matched routes. This is a spec mismatch, and it also lets callers enumerate which admin routes exist. | `self.assertEqual(req("/admin/nope", "tok-alice")["status"], 403)`. Fix by checking `path.startswith("/admin/")` before route dispatch. |
| 5 | P3 | `app.py:19-20`, `store.py:11-12` | `POST /notes` with no or `None` body stores the literal note `"alice: None"`. A request dict missing the `"body"` key raises an uncaught `KeyError`. The body is never validated for type or length. | `req("/notes", "tok-bob", "POST", None)` returns 400 and leaves `bob`'s notes unchanged. A request without a `body` key returns 400, not an exception. |

**Test gap behind #1:** the suite covers the admin check only on `/admin/users`. The unguarded route has no test at all. That is why "5 tests pass" did not catch it.

**FILES NEEDED BUT NOT PROVIDED:**
- PR metadata: number, head SHA, merge base, commit trailers.
- The server or framework that calls `app.handle`, which determines what an unhandled exception becomes (for #3).
- The production token and secret configuration, if `_TOKENS` is a placeholder (for #2).
- CI check results.

**Close-out**

The author adjudicates and whoever closes the PR writes the close-out. As the reviewer, I do not adjudicate my own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending* (P0, cannot be deferred) | |
| 2 | *pending* (P1, cannot be deferred) | |
| 3 | *pending* | |
| 4 | *pending* | |
| 5 | *pending* | |

**VERIFIED AFTER FIXES:** None yet. Verify the fix for #1 with a targeted read of its diff plus the new export tests, run red before the fix and green after.

**MERGE RECOMMENDATION: do not merge.**
- **Open blocker:** P0 #1, a non-admin can export every customer's private notes.
- **Open P1:** #2, hard-coded admin credential.
- **Required rounds:** High-tier round 2 has not run.
- **Checks:** CI status was not shown, and a missing check is not green.
- **Owner decision pending:** which approved endpoint runs round 2.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "code-read (not executed)",
      "location": "app.py:26-27",
      "scenario": "GET /admin/export with a valid non-admin token (tok-alice) returns 200 and every user's notes; require_admin is never called on this route.",
      "fix": "Call auth.require_admin(user) before store.export_all(); add tests that non-admin gets 403 and admin gets 200 on /admin/export."
    },
    {
      "severity": "P1",
      "evidence_level": "code-read (not executed)",
      "location": "auth.py:4",
      "scenario": "Static, guessable tokens including the admin token 'tok-root' are committed in source; anyone with repo or artifact access gains admin in production, and rotation needs a deploy.",
      "fix": "Load tokens/credentials from a secret store or configuration; remove literals from source; fail closed when unconfigured."
    },
    {
      "severity": "P2",
      "evidence_level": "code-read (not executed)",
      "location": "auth.py:13",
      "scenario": "hmac.compare_digest raises TypeError for non-ASCII str or non-str tokens (e.g. 'é', 123); the exception escapes the AuthError handler and yields an unhandled error instead of 401.",
      "fix": "Reject non-str tokens and encode to bytes (token.encode('utf-8')) before compare_digest, or catch TypeError and raise AuthError; test both inputs return 401."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "app.py:20-30",
      "scenario": "Non-admin calling an unmatched /admin path or method (POST /admin/users, GET /admin/nope) gets 404 rather than the specified 403, and can enumerate admin routes.",
      "fix": "Enforce require_admin for any path starting with /admin/ before route dispatch; test non-admin gets 403 on an unknown /admin path."
    },
    {
      "severity": "P3",
      "evidence_level": "code-read (not executed)",
      "location": "app.py:19-20, store.py:11-12",
      "scenario": "POST /notes with body None stores 'alice: None'; a request missing the 'body' key raises an uncaught KeyError; body type/length not validated.",
      "fix": "Validate body is a non-empty str within a length limit; return 400 otherwise; test None and missing body."
    }
  ]
}
```