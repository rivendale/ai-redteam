**Review mode:** I had no tools in this session, so nothing was run. Every finding comes from reading and tracing the four supplied files by hand. No subagent or cross-vendor reviewer was available. The work was not written in this conversation, so there is no authorship anchoring, but this is a single reviewer.

---

**VERDICT: REWORK.** `/admin/export` never checks for admin rights, so any logged-in user can download every user's private notes. The test suite passes because nothing tests that route.

**CONFIDENCE: high** for the verdict, because the Critical finding is a direct, deterministic trace through 12 lines. **Medium** for the lower findings. Limits: no tools, so nothing executed; single reviewer; the production setup for `auth.py` and `store.py` is unknown.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, app.py, auth.py, store.py, test_app.py.
- **Not seen:**
  - Test run output for "passes (5 tests)". This matters little: by trace, all 5 pass.
  - The production deployment and server model (threads or processes, real token source, real store). This matters for S1, S2 and S4.
  - Any PR description. This does not matter.

**COVERAGE**
- **Scope:** the whole supplied change (4 files).
- **Checked:**
  - Every function in all four files.
  - All 4 route branches in `handle`.
  - The 401 and 403 paths.
  - All 5 tests, including a mutation reasoned on paper for the `/admin/users` 403 test.
- **Not checked:**
  - The deployment or server configuration (not supplied).
  - Actual test execution (no tools).

**SEATS AND GATE**
- **Seats:** this reviewer only. No subagent tool and no cross-vendor seats; none were requested.
- **Sensitivity gate:** passed. The files contain toy seed data and placeholder tokens, no real personal data or credentials.

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (traced) | B | `app.py:25-26` | The `/admin/export` branch returns `store.export_all()` without calling `auth.require_admin(user)`. Compare `/admin/users` at line 23. | Alice sends `GET /admin/export` with `tok-alice`. `current_user` succeeds (line 11), line 25 matches, and line 26 returns 200 with `{"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}`. Every customer's private notes go to any authenticated user. This violates "403 on /admin routes" and cannot be rolled back once exposed. | **Fix:** add `auth.require_admin(user)` before line 26. Better still, gate all `/admin` paths once with `if path.startswith("/admin"): auth.require_admin(user)` so a future route cannot skip the check. **Reproduction:** `req("/admin/export", "tok-alice")["status"]` should be 403; by trace it is 200. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B | `test_app.py` (whole file) | No test exercises `/admin/export` at all, neither the 403 for non-admins nor the 200 for admins. Positive control: the same read finds `/admin/users` twice (two test methods), so the absence of `/admin/export` is a real zero. | The context offers "test_app.py passes (5 tests)" as assurance, but the suite is green while F1 leaks all data. Any future regression on this route would also pass CI. | **Fix:** add `test_admin_export_forbidden_for_non_admin` (expect 403 for `tok-alice`) and `test_admin_export_allowed_for_admin` (expect 200 for `tok-root`). **Reproduction:** add the first test; on current code it fails (200 ≠ 403). | a✓ b✓ c✗ d✓ |
| F3 | Medium | PROBABLE | B | `auth.py:14`; `app.py:10-13` | `hmac.compare_digest` raises `TypeError` for a str containing non-ASCII characters, or when the argument types differ (for example a non-str token). Only `AuthError` is caught, so the exception escapes `handle`. | A client sends token `"tök"` or an integer token. Instead of 401, an unhandled `TypeError` propagates, which typically becomes a 500 and a stack trace in logs. This violates "anyone without a valid token gets 401". | **Fix:** in `current_user`, reject anything that is not an ASCII `str` with `AuthError` before comparing, or compare `.encode()`d bytes. **Reproduction:** `req("/notes", "tök")` should return status 401; by documented stdlib behaviour it raises `TypeError`. Not executed. | a✓ b✗ c✓ d✗ |
| F4 | Low | PROBABLE | B | `app.py:20`; `store.py:11` | The POST body is used unvalidated: `request["body"]` raises `KeyError` if absent, a `None` body is stored as `"bob: None"`, and there is no size limit. | A client POSTs with no body or `body=None`: either an unhandled `KeyError` (500) or a junk note. Repeated huge bodies grow the in-memory store without bound. | **Fix:** validate that the body is a non-empty `str` under a size cap; return 400 otherwise. **Reproduction:** `app.handle({"path":"/notes","method":"POST","token":"tok-bob"})` should return 400; by trace it raises `KeyError`. | a✓ b✗ c✗ d✗ |
| F5 | Low | CONFIRMED | B | `test_app.py` | This is a sibling of F2. There is no test that an unknown token on an `/admin` route gets 401 rather than 403 or 200, and no test for 404. The current code is correct here (the token is checked first at line 11), but nothing guards it. | A refactor that checks the admin rule before authentication would return 403 to anonymous callers, or leak data, and the suite would stay green. | **Fix:** add `req("/admin/export", "nope")` and `req("/admin/users", "nope")` asserting 401. **Reproduction:** these tests would pass now; their value is as regression guards. Confirm by mutation: move the auth check below the routes in a scratch copy and watch them go red. | a✓ b✓ c✗ d✗ |

**Confirm or refute round:**
- **F1:** the strongest defence would be "`export_all` is guarded elsewhere". Refuted: `handle` is the only entry point supplied, and there is no check between line 25 and line 26. F1 stands.
- **F2:** the defence would be "it is just a symptom of F1". Under the rubric it still fails independently: it is the reason the passing tests gave false assurance. F2 stands, and it is fixed in the same change as F1.

**Sibling search for F1 and F2:**
- **Searched:**
  - All four branches in `handle` for admin-only resources without `require_admin`.
  - All callers of `export_all` and `list_users` in the supplied files.
  - Path matching, in case a variant such as `/admin/export/` or `/ADMIN/export` reaches the handler.
- **Found:**
  - Only line 26 lacks the check.
  - `/notes` routes correctly scope to `user[0]`, which comes from the token.
  - Matching is exact equality, so variants fall through to 404 rather than bypassing the check.
  - The test-gap sibling is F5.

**F1 is a security finding. Boundary:**
- **Principal:** any non-admin user with a valid token.
- **Input:** the request path `/admin/export`.
- **Failing control:** `require_admin` is never called on that branch.
- **Boundary crossed:** user to admin.
- **Resource:** every user's notes.

## NEEDS VALIDATION
- **S1, `auth.py:4`:** tokens, including the admin `tok-root`, are hardcoded in source. If this module ships to production, anyone with repository read access holds admin. **Unresolved fact:** is `auth.py` a placeholder, or the production token source?
- **S2, `store.py:3`:** an in-memory dict seeded with sample notes. In production, notes are lost on restart and diverge across processes. **Unresolved fact:** does production use this store?
- **S3, context.md:** "test_app.py passes (5 tests)" could not be run. By trace, all 5 pass. **Settled by:** running the suite in an isolated copy.
- **S4, `store.py:11`:** concurrent `add_note` calls. **Unresolved fact:** the server's threading or process model.

## REFUTED
- **Timing leak in `current_user`:** each comparison uses `compare_digest`. The early return reveals only the position of the matching token among a fixed set, not any token content. Not a practical leak.
- **401 and 403 ordering wrong:** traced. Authentication runs first (lines 10-13 return 401), and `AuthError` from `require_admin` is caught at line 27 and returns 403. Correct for `/admin/users`.
- **Cross-user leak via `/notes`:** the user comes only from the token mapping, never from request fields. `list_notes` returns a copy. Holds.
- **Note-text spoofing (body `"alice: x"`):** the text appears only as `"bob: alice: x"` in Bob's own list and in the admin export. Cosmetic, with no access change.

## WHAT HOLDS UP
- Authentication happens before routing, and unknown or missing tokens get 401 (`token or ""` handles `None`).
- `/admin/users` is correctly gated, and its 403 test would go red if line 23 were removed. That was reasoned on paper, not run.
- Per-user note scoping is correct, and returned lists are copies, so callers cannot mutate the store.

## UNVERIFIED CLAIMS
- "test_app.py passes (5 tests)": run `python -m unittest test_app` in an isolated copy.
- The TypeError behaviour in F3: run `hmac.compare_digest("tok-alice", "tök")` in a scratch interpreter.

## QUESTIONS FOR THE AUTHOR
1. Are `auth.py` and `store.py` the production implementations, or stand-ins? This decides S1 and S2.
2. Was `/admin/export` intended to be admin-only? The request says yes; please confirm nothing downstream relies on the current open behaviour.

## DECISION-MAKER SUMMARY
Do not deploy. `/admin/export` (F1) gives every authenticated user all customers' private notes, and the passing test suite never checks that route (F2). The fix is one line plus two tests. Proceeding as is exposes all customer notes to any user, with no way to undo the exposure.

## OWNER SUMMARY
The new notes service has a gap that lets any logged-in customer download every other customer's private notes through the admin export feature. The automated tests did not catch it because they never try that feature. It is a small fix, but it must be made and tested before release, because once private notes are exposed they cannot be taken back.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "store.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "production deployment and server model", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Toy seed data and placeholder tokens only."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current_user", "kind": "function"},
      {"unit": "auth.py:require_admin", "kind": "function"},
      {"unit": "store.py", "kind": "file"},
      {"unit": "store.py:list_notes", "kind": "function"},
      {"unit": "store.py:add_note", "kind": "function"},
      {"unit": "store.py:list_users", "kind": "function"},
      {"unit": "store.py:export_all", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "claim: test_app.py passes (5 tests)", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "test execution", "reason": "no_tools"},
      {"unit": "production deployment and server configuration", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:25-26",
     "scenario": "A non-admin user (tok-alice) sends GET /admin/export; require_admin is never called and the handler returns 200 with every user's notes.",
     "fix": "Call auth.require_admin(user) before store.export_all(), or gate every /admin path once before routing.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "req('/admin/export', 'tok-alice')['status']: expected 403, traced 200 with all users' notes (traced by hand, not executed).",
     "security": true,
     "boundary": {"principal": "any non-admin user with a valid token", "input": "the GET /admin/export path",
                  "control": "require_admin is never called on this branch", "crossed": "user to admin",
                  "resource": "every user's private notes"},
     "siblings_searched": {"searched": "all four route branches in handle, all callers of export_all and list_users, path-matching variants",
                           "found": "only app.py:26 lacks the check; /admin/users is gated; exact path match prevents prefix bypass"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py",
     "scenario": "No test covers /admin/export, so the suite is green while F1 leaks all notes, and any future regression on the route also passes.",
     "fix": "Add tests asserting 403 for tok-alice and 200 for tok-root on /admin/export.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test asserting req('/admin/export','tok-alice')['status']==403; on current code it fails (200).",
     "security": false,
     "siblings_searched": {"searched": "every route and status the original request specifies, against the five tests",
                           "found": "401 on /admin routes and the 404 path are also untested (F5)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:14",
     "scenario": "A token containing non-ASCII characters, or a non-str token, makes hmac.compare_digest raise TypeError, which escapes handle as a 500 instead of a 401.",
     "fix": "Reject non-ASCII or non-str tokens with AuthError before comparing, or compare encoded bytes.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "req('/notes', 'tök'): expected status 401; documented stdlib behaviour raises TypeError (not executed)."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "app.py:20",
     "scenario": "A POST /notes with a missing body raises KeyError (500); a None body is stored as 'bob: None'; there is no size cap on the in-memory store.",
     "fix": "Validate the body is a non-empty str under a size limit; return 400 otherwise.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "app.handle({'path':'/notes','method':'POST','token':'tok-bob'}): expected 400, traced KeyError."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py",
     "scenario": "No test that an unknown token on /admin routes gets 401; a refactor checking admin before authentication would go unnoticed.",
     "fix": "Add tests asserting 401 for an unknown token on /admin/users and /admin/export.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy, move authentication below routing; the new 401 tests go red while the existing 5 stay green."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:4",
     "suspicion": "The admin token is hardcoded in source; anyone with repository access would hold admin in production.",
     "unresolved_fact": "Whether auth.py is the production token source or a placeholder."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "store.py:3",
     "suspicion": "The in-memory store loses notes on restart and diverges across processes.",
     "unresolved_fact": "Whether production uses this store."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "context.md",
     "suspicion": "The claim that test_app.py passes was not executed.",
     "unresolved_fact": "Output of python -m unittest test_app in an isolated copy."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "store.py:11",
     "suspicion": "Concurrent add_note calls may race.",
     "unresolved_fact": "The server's threading or process model."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "current_user leaks tokens through timing.",
     "evidence": "Each comparison uses hmac.compare_digest; the early return reveals only the index within a fixed set, not token content."},
    {"id": "C2", "candidate": "401 and 403 are returned in the wrong order.",
     "evidence": "app.py:10-13 authenticates before routing; AuthError from require_admin is caught at line 27 and returns 403."},
    {"id": "C3", "candidate": "/notes leaks other users' notes.",
     "evidence": "list_notes and add_note key on user[0] from the token mapping only; list_notes returns a copy."},
    {"id": "C4", "candidate": "Note text can impersonate another user.",
     "evidence": "add_note prefixes the real user name, so the text appears only as 'bob: alice: x'; access is unchanged."}
  ]
}
```