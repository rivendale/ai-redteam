# Review report

**REVIEWED:** PR number, head SHA and merge base SHA were **not provided**. This review covers only the four files pasted inline (`app.py`, `auth.py`, `store.py`, `test_app.py`). It does not cover any commit. Before posting, record the PR and both SHAs. If the head differs from this content, this review does not cover it.

**TIER: High.** The change implements authentication and authorization (401/403 and admin gating) and handles private customer notes, which is personal data with no rollback window for exposure.

**REVIEWERS:**
- **Reviewer:** this session (claude-opus-5-5), round 1 of the 2 rounds the tier requires. **The second round has not run, so this PR is not yet reviewed.** It should run on a second vendor approved for customer-note data.
- **Author:** unknown. No commit trailers were provided. This session did not write the change.
- **Data handling (Step 3):** the code was reviewed only inside this session and was not sent anywhere else.
- **Limits:** I had no tools, so nothing was run. The claim "test_app.py passes (5 tests)" is unverified. Even if true, none of the 5 tests exercise `/admin/export`.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `app.py:25-26` | The `/admin/export` branch never calls `auth.require_admin(user)`. Any valid non-admin token gets every user's notes. For example, `{"path": "/admin/export", "method": "GET", "token": "tok-alice"}` returns 200 with `{"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}`. The request requires 403. This exposes private customer data across users. | `assertEqual(req("/admin/export", "tok-alice")["status"], 403)` and `assertNotIn("bob: call dentist", str(req("/admin/export", "tok-alice")["body"]))`. Both fail today. Also add the admin-allowed case (`tok-root` gets 200) and the no-token case (gets 401). |
| 2 | **P1** | `auth.py:4` | Bearer tokens, including the admin token `tok-root`, are string literals in source. Anyone with read access to the repo, a build artifact or a log of the source can call `/admin/export` as admin. The tokens cannot be rotated without a code deploy. In production this is admin access for anyone who can read the code. | A test or CI check that `auth._TOKENS` is loaded from configuration or a secret store and that no `tok-` literal exists in `auth.py`. Or test that `current_user("tok-root")` raises `AuthError` when the secret store has no such token. |
| 3 | P2 | `auth.py:13` (`hmac.compare_digest(known, token or "")`) | `hmac.compare_digest` raises `TypeError` when given a `str` containing non-ASCII characters, or a non-str/bytes value. A request with `token = "tök"` or `token = 123` raises `TypeError`. `app.handle` catches only `AuthError`, so the error escapes as an unhandled exception (a 500 or a crash) instead of 401. Any unauthenticated client can trigger this. | `assertEqual(req("/notes", "tök")["status"], 401)` and `assertEqual(req("/notes", 123)["status"], 401)`. Both raise today. |
| 4 | P3 | `app.py:19-20`, `store.py:10-11` | `POST /notes` with no body or `body=None` stores the literal note `"bob: None"`. A request dict missing the `"body"` key raises `KeyError` and escapes as a 500. No input validation exists. | `assertEqual(req("/notes", "tok-bob", "POST", None)["status"], 400)`, and the note list is unchanged afterwards. |
| 5 | P3 | `store.py:14-15` | `list_users()` derives users from `_NOTES` keys. A user who holds a valid token but has never posted a note is missing from `/admin/users`. This cannot happen with today's fixture data. It happens as soon as a token is added without a seeded note. | Add a token-holder `carol` with no notes and assert that `"carol"` appears in `req("/admin/users", "tok-root")["body"]`. |

**FILES NEEDED BUT NOT PROVIDED:**
- PR metadata: number, head and merge-base SHAs, commit trailers.
- CI check results.
- The deployment code that would replace the in-memory `auth`/`store` in production. If real token and storage modules exist, findings 2 and 5 must be re-checked against them.

**Signal:** The P0 is not a subtle bug. One of the two admin routes has no admin check, and the test suite tests only the route that does. Before merge, add a structural guard so that every `/admin/*` path is gated in one place (for example, `if path.startswith("/admin/"): auth.require_admin(user)` before dispatch). Per-route checks let the next admin route repeat this mistake.

# Close-out

The reviewer does not adjudicate its own findings. The author must give each finding a written decision. Findings 1 and 2 cannot be deferred.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (P0, must be fixed) | n/a |
| 2 | Pending (P1, fix or reject with evidence) | n/a |
| 3 | Pending | n/a |
| 4 | Pending | n/a |
| 5 | Pending | n/a |

**VERIFIED AFTER FIXES:** None yet. Verify each fix with a targeted read of its diff plus the regression test above, which must fail before the fix and pass after it.

**MERGE RECOMMENDATION: do not merge.**
- **Open P0:** any authenticated user can export every customer's notes.
- **Open P1:** the admin token is hardcoded in source.
- **Second review round not run:** the High tier requires two rounds.
- **CI checks not seen:** a missing check is not green.
- **SHAs not recorded.**

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by code read (app.py:25-26 has no require_admin call; contrast app.py:23)",
      "location": "app.py:25-26",
      "scenario": "GET /admin/export with non-admin token tok-alice returns 200 and every user's notes (bob, root) instead of 403.",
      "fix": "Call auth.require_admin(user) before store.export_all(), preferably via a single guard for all /admin/ paths before dispatch; add tests for 403 (non-admin), 200 (admin), 401 (no token) on /admin/export."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed by code read",
      "location": "auth.py:4",
      "scenario": "Admin token 'tok-root' and user tokens are literals in source; anyone with repo or artifact read access can call /admin/export as admin, and tokens cannot be rotated without a deploy.",
      "fix": "Load tokens or verify them against a secret store or identity provider; remove literals from source; rotate any token that has been committed."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from documented hmac.compare_digest behavior; not executed",
      "location": "auth.py:13",
      "scenario": "A non-ASCII str token (e.g. 'tök') or non-string token (e.g. 123) makes hmac.compare_digest raise TypeError, which app.handle does not catch, giving a 500 or crash instead of 401.",
      "fix": "Reject non-str tokens and encode to bytes (token.encode('utf-8')) before compare_digest, or catch TypeError/ValueError and raise AuthError; add tests for both inputs returning 401."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by code read",
      "location": "app.py:19-20; store.py:10-11",
      "scenario": "POST /notes with body None stores 'bob: None'; a request missing the 'body' key raises KeyError and escapes as a 500.",
      "fix": "Validate that body is a non-empty string and return 400 otherwise; add a test that the note list is unchanged."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by code read; not reachable with current fixture data",
      "location": "store.py:14-15",
      "scenario": "list_users derives users from note owners, so a valid token holder with no notes is omitted from /admin/users.",
      "fix": "List users from the user or token registry, not from _NOTES keys."
    }
  ]
}
```