**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session, so I reviewed the work myself and could not run any code.

**VERDICT: REWORK.** `/admin/export` has no admin check, so any logged-in user can download every customer's private notes. The tests never touch that route, so they do not catch it.

**CONFIDENCE: medium.** The main finding comes from reading the code line by line and needs no execution. Confidence is limited because I had no tools: the test suite, the "5 tests pass" claim and the mutation checks were not run, and this was a same-context review.

**INPUTS LEDGER:**
- Seen: the original request, the context, and the full text of `app.py`, `auth.py`, `store.py` and `test_app.py`.
- Not seen, and it matters: output of the test run. The "5 passing" claim is unverified.
- Not seen, and it matters: where production tokens come from (config, secret store, identity provider), and how the service is deployed and persisted.
- Not seen, and it does not matter: the diff against any prior version. The full files were supplied.

**SEATS AND GATE:**
- Local same-context reviewer: ran.
- Fresh subagent: not available (no tool).
- Cross-vendor seats: not requested. They would be refused anyway. The work contains hardcoded credentials (`auth.py` `_TOKENS`) and sample customer notes, so it must not go to outside reviewers.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | `app.py`, `/admin/export` branch (`return {"status": 200, "body": store.export_all()}`) | `auth.require_admin(user)` is never called on this route. Only `/admin/users` calls it. The request says a valid non-admin token must get 403 on all /admin routes. | Alice sends `GET /admin/export` with `tok-alice`. `current_user` succeeds, the branch runs, and she gets 200 with `{"alice": [...], "bob": ["bob: call dentist"], "root": ["root: rotate keys"]}`. Every user's private notes are exposed, and the context says there is no rollback for exposure. | Add `auth.require_admin(user)` before `export_all()`. Better: enforce admin centrally with `if path.startswith("/admin"): auth.require_admin(user)` before routing, so a new admin route cannot skip it. Add tests: export with `tok-alice` gives 403, `tok-root` gives 200, `nope` gives 401. | confirmed. As its defender I looked for any check elsewhere: `handle` has no middleware, and `export_all` does no check. Nothing guards the route. |
| 2 | High | CONFIRMED (gap) / UNVERIFIED (pass claim) | B | `test_app.py` (whole file) | No test calls `/admin/export`. Admin coverage is only `/admin/users`. "5 tests pass" is offered as assurance, but the suite cannot detect Finding 1. None of the tests is shown to fail when the guard it covers is removed. | The suite stays green while the most sensitive route is open, and CI reports success for a data-exposure bug. | Add the three export tests above. Mutation check in a scratch copy: delete `require_admin` from `/admin/users` and confirm `test_admin_users_is_forbidden_for_non_admin` goes red. Then add the guard to export and confirm the new test goes from red to green. | confirmed. No test references `/admin/export`; I checked by reading all 5 tests. |
| 3 | High | PROBABLE | B | `auth.py` `_TOKENS = {"tok-alice": ..., "tok-root": ("root", True)}` | Tokens are static, guessable strings committed to source, including the admin token `tok-root`. The work does not say whether this is a placeholder. | If this ships as written, anyone with repo access, or anyone who guesses `tok-root`, has full admin rights, including export. | Load tokens from a secret store or identity provider, hash them at rest, and remove them from the repo. If this is a stub, say so and block the deploy until it is replaced. | confirmed as written. It is refuted only if the author shows these are replaced before production (see Questions). |
| 4 | Medium | CONFIRMED (by reading) | B | `app.py` `request["path"], request["method"]`, `request["body"]`; `auth.py` `hmac.compare_digest(known, token or "")` | Malformed input causes uncaught exceptions or junk data. A missing `path`, `method` or `body` key raises `KeyError`. A non-str token such as an int raises `TypeError` in `compare_digest`. A POST with `body=None` stores `"bob: None"`. | Malformed requests crash the handler, giving a 500 or a stack trace, depending on the server around it. Empty or None notes are stored silently. | Use `.get()` with validation. Return 400 for a missing or non-string body. Reject non-str tokens with 401. Add a test for each. | n/a (Medium) |
| 5 | Medium | PROBABLE | B | `store.py` `_NOTES` module-level dict | The store is in memory: there is no persistence and no lock. In production, notes are lost on every restart. Concurrent `add_note` calls under a multi-threaded server are not coordinated. | A deploy or crash erases all customer notes. | Confirm whether this is a stub. If not, back it with a real datastore. | n/a |
| 6 | Medium | CONFIRMED | B | `store.py` `list_users(): return sorted(_NOTES)` | The user list is built from the users who have notes, not from the user registry. | A user with a token but no notes is missing from `/admin/users`, so admins get an incomplete list. | Build the list from the auth or user source. Add a test with a user who has no notes. | n/a |
| 7 | Low | PROBABLE | B | `auth.py` `current_user` loop | Comparison is constant-time per token, but the loop returns early, so response time reveals which token in the list matched. `compare_digest` also leaks length. | Theoretical timing side channel. It is minor next to Finding 3. | Look up by a hashed token in a dict, or compare against all tokens without returning early. | n/a |

### WHAT HOLDS UP
- **401 before routing.** Authentication runs before any route logic, so an unknown or missing token gets 401 on every path, including unknown paths. Unknown paths fail closed: a trailing slash or a wrong method gets 404, not 200.
- **Own notes only.** `/notes` GET and POST are scoped to `user[0]` taken from the token, not from the request. A user cannot read or write another user's notes through these routes. `list_notes` returns a copy, so callers cannot change the store through it.
- **403 mapping.** `/admin/users` correctly returns 403 for a non-admin and 200 for an admin.

### UNVERIFIED CLAIMS
- **"test_app.py passes (5 tests)."** Settle it by running `python -m unittest test_app -v` and attaching the output.
- **That the tests guard anything.** Settle it with the mutation checks in Finding 2.

### QUESTIONS FOR THE AUTHOR
1. Are `_TOKENS` and `_NOTES` placeholders that will be replaced before production? If so, by what, and is there a ticket or check that blocks the deploy until then?
2. Was leaving out the export guard deliberate, for example because it is enforced by a gateway in front of the service? If so, where is that configured and tested?

### DECISION-MAKER SUMMARY
Do not deploy. `/admin/export` lets any logged-in user download every customer's notes. The fix is one line plus three tests. Separately confirm that the hardcoded tokens and in-memory store are not what ships. Proceeding as is means an immediate, irreversible exposure of private customer data.

### OWNER SUMMARY
The change has a gap: any ordinary user can download every customer's private notes through the admin export page, and the existing tests do not check for this. The fix is small, but it must be made and tested before release. The login keys are also written directly into the code, and the notes are kept only in memory, so both need confirming as temporary.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "app.py, auth.py, store.py, test_app.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true},
    {"item": "production token source and deployment config", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "hardcoded credentials and customer notes in the work"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py /admin/export branch",
      "scenario": "Non-admin token (tok-alice) GET /admin/export returns 200 with every user's notes; require_admin is never called.",
      "fix": "Call auth.require_admin(user) before export_all(), or enforce admin for all /admin* paths centrally; add 403/200/401 tests for export.",
      "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_app.py",
      "scenario": "No test covers /admin/export, so the suite stays green with the route unguarded; pass claim unverified and no test shown to fail when its guard is removed.",
      "fix": "Add export authz tests; mutation-check require_admin removal in a scratch copy.",
      "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py _TOKENS",
      "scenario": "Static guessable tokens incl. admin tok-root committed to source; if shipped, anyone with repo access or a guess gets admin and export.",
      "fix": "Load hashed tokens from a secret store/IdP; block deploy until replaced.",
      "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "app.py request[...] indexing; auth.py compare_digest",
      "scenario": "Missing keys raise KeyError, non-str token raises TypeError (500); body=None stored as 'user: None'.",
      "fix": "Validate input; 400 on bad body, 401 on non-str token; add tests.",
      "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "store.py _NOTES",
      "scenario": "In-memory, unlocked store loses all notes on restart and is unsafe under concurrent writes.",
      "fix": "Back with a persistent datastore or confirm stub status.",
      "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "store.py list_users",
      "scenario": "Users with no notes are omitted from /admin/users.",
      "fix": "Derive the list from the user registry; add a test.",
      "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py current_user loop",
      "scenario": "Early return and length leak give a minor timing side channel.",
      "fix": "Lookup by hashed token in a dict.",
      "status": "n/a"}
  ]
}
```