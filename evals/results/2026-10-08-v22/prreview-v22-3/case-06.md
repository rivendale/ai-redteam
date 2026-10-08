# pr-review: notes service request handlers

**Review report**

**REVIEWED:** The change as attached (app.py, auth.py, store.py, test_app.py). No PR number, head SHA or merge base was provided, so this review is tied to the file contents shown here and not to any commit. If the branch differs from these contents, the differences were not reviewed.

**TIER:** **High.** The change implements authentication and the admin permission boundary, and it handles private customer notes (personal data). The context says there is no rollback window for data exposure. High tier requires two rounds, ideally on two vendors. **This is round 1 of 2.** The PR is not reviewed until a second independent round has run.

**REVIEWERS:**
- Reviewer: one fresh instance (claude-opus-5-5) with no part in writing the change. It had no tools, so it could not run code.
- Author: unknown. No commit trailers were provided.
- Data approval (Step 3): the code was supplied directly to this session. Whether this endpoint is approved for code that carries customer notes was not stated. The owner should confirm that before round 2 is sent anywhere.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `app.py:25-26` | `/admin/export` never calls `auth.require_admin(user)`, unlike `/admin/users` at `app.py:23`. Any valid non-admin token gets every user's notes. For example, `{"path": "/admin/export", "method": "GET", "token": "tok-alice"}` returns 200 with bob's and root's notes (`"root: rotate keys"`). This breaks the request ("non-admin gets 403 on /admin routes") and is exactly the data exposure the context says cannot be rolled back. No test covers `/admin/export` at all. | `self.assertEqual(req("/admin/export", "tok-alice")["status"], 403)` and assert `"bob"` is not in the body. Also `req("/admin/export", "tok-root")` → 200. The first fails today. |
| 2 | P2 | `auth.py:14` | `hmac.compare_digest` raises `TypeError` instead of returning False in two cases: a str token containing non-ASCII characters (for example `"tök"`), or a non-str/bytes token such as `123` or a list from a JSON body. `handle` only catches `AuthError` (`app.py:12`), so the exception escapes. An unauthenticated caller gets a 500 or a crash instead of the 401 the request requires. | `req("/notes", "tök")["status"] == 401` and `req("/notes", 123)["status"] == 401`. Both raise today. |
| 3 | P3 | `app.py:22, 25, 29` | Admin checks are keyed to exact path and method pairs. A non-admin calling `POST /admin/users` or `GET /admin/anything` gets 404, not the 403 the request specifies for "/admin routes". Today this only produces the wrong status. But any new `/admin/...` route added the same way is open by default, which is how finding #1 happened. | `req("/admin/users", "tok-alice", "POST")["status"] == 403`. Also, for an unknown `/admin/x` with a non-admin token, assert 403. |
| 4 | P3 | `store.py:10-11`, `app.py:20` | `POST /notes` with no body (or `body: None`) stores the note `"alice: None"`. A non-string body such as a dict is stored as its repr. Nothing validates the input. | `req("/notes", "tok-alice", "POST", None)["status"] == 400`, and the note list is unchanged. |

**Not findings (checked):**
- `list_notes` and `export_all` return copies, so callers cannot mutate the store.
- A missing or `None` token is handled by `token or ""` and returns 401.
- `test_user_sees_only_own_notes` assumes the store has not been mutated, and `test_post_creates` mutates bob's notes, not alice's. There is no test-order hazard today.

**On the claim "test_app.py passes (5 tests)":** I could not run it. From reading the tests, the claim is plausible. None of the five touches `/admin/export`, a 401 on an admin route, or a malformed token, so a passing suite says nothing about finding #1.

**FILES NEEDED BUT NOT PROVIDED:**
- The PR and its commit SHAs, with commit trailers.
- CI check configuration and results.
- Whatever framework calls `handle` (to know how an uncaught exception from #2 surfaces).

---

**Close-out**

Pending. A reviewer does not adjudicate its own findings. The author must record a decision for each finding: #1 cannot be deferred (P0); #2–#4 may be deferred with a linked issue.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | — | — |
| 2 | — | — |
| 3 | — | — |
| 4 | — | — |

**VERIFIED AFTER FIXES:** Nothing yet. The fix for #1 should be a one-line `auth.require_admin(user)` before `export_all()`, or better, a single admin gate for every path starting with `/admin`, which also resolves #3. It should then be verified by reading that diff and running the regression test from #1. Another full round is not needed for that.

**MERGE RECOMMENDATION:** **Do not merge.**
- Finding #1 (P0) is open: any authenticated user can export every customer's private notes.
- The second High-tier round has not run.
- No SHAs or CI checks were provided, so check status is unknown, and a missing check is not green.
- The data-approval question in Step 3 is open for round 2.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed by reading code (not executed)",
      "location": "app.py:25-26",
      "scenario": "GET /admin/export with non-admin token tok-alice returns 200 and every user's notes; require_admin is never called on this route, unlike /admin/users at app.py:23. No test covers /admin/export.",
      "fix": "Call auth.require_admin(user) before store.export_all(), preferably via one admin gate for all /admin paths; add tests asserting 403 for tok-alice and 200 for tok-root on /admin/export."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred from documented hmac.compare_digest behavior (not executed)",
      "location": "auth.py:14",
      "scenario": "A non-ASCII str token (e.g. 'tök') or non-str token (e.g. 123) makes hmac.compare_digest raise TypeError; handle only catches AuthError, so the caller gets an unhandled exception/500 instead of 401.",
      "fix": "Reject non-str tokens and encode to bytes (token.encode('utf-8')) before compare_digest, or catch TypeError and raise AuthError; add tests for 'tök' and 123 returning 401."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading code (not executed)",
      "location": "app.py:22, 25, 29",
      "scenario": "Non-admin POST /admin/users or GET /admin/<unknown> returns 404 rather than the 403 the request specifies for /admin routes; admin checks are per-route, so new admin routes are open by default (the cause of the P0).",
      "fix": "Gate on path.startswith('/admin') with require_admin before route dispatch; test 403 for non-admin on any /admin path and method."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed by reading code (not executed)",
      "location": "store.py:10-11 (called from app.py:20)",
      "scenario": "POST /notes with body None stores 'alice: None'; non-string bodies are stored as their repr. No input validation.",
      "fix": "Return 400 unless body is a non-empty str; test that POST with None returns 400 and leaves the notes unchanged."
    }
  ]
}
```