VERDICT: **SHIP WITH FIXES.** The authorization logic meets the request on every path I traced, but the CSV export does no escaping, the token store is hard-coded in source, and the test suite never checks two of the stated requirements.

CONFIDENCE: **medium.** I had no tools in this session, so nothing was run. Every finding comes from reading the code and tracing it by hand. I was a single reviewer and did not author the work, so there is no anchoring risk, but there was also no second seat.

**INPUTS LEDGER**
- Seen: request.md, context.md, app.py, auth.py, trips.py, test_app.py.
- Not seen:
  - The claim that "7 tests pass", which I could not run. It matters only a little, because the tests are simple to trace by hand.
  - The production token store and identity provider. This matters, because auth.py may or may not be what ships (see S1).
  - The source of rider names. This matters for F1 and S2.
  - The server or framework that builds `request["path"]`. This matters a little for S3.

**COVERAGE**
- Checked:
  - `app.py:handle`: every branch, plus these inputs: a None token, a non-str token, an empty string, a non-ASCII token, `/staff`, `/staff/`, `/STAFF/...`, `/staff/../`, unknown `/staff/x`, and a missing `path`.
  - `auth.py:current` and `auth.py:require_staff`.
  - All three functions in trips.py.
  - All 7 tests, each mapped to a requirement.
- Not checked: runtime behavior, the deployment and token provisioning, and the HTTP layer.

**SEATS AND GATE:** One local reviewer. No subagent or cross-vendor seats were available. The sensitivity gate is technically tripped because the work contains personal data (rider names and emails), but the records are `example.test` fixtures. External seats would have been refused anyway.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | PROBABLE | B | trips.py:19-21 (`as_csv`) | CSV fields are joined with commas and are never quoted or escaped. | If a rider name or email contains `,`, `"` or a newline, the staff export's columns shift. If a name starts with `=`, `+`, `-` or `@`, it runs as a spreadsheet formula when staff open the file (CSV/formula injection against staff, on a file full of personal data). | Use `csv.writer` with `QUOTE_MINIMAL`, and prefix any formula-leading cell with `'`. Repro: add the trip `{"rider": "=HYPERLINK(\"http://x\")", "email": "a,b@x", ...}`, call `as_csv()`, and observe that the row has 5 fields and the first cell is a live formula. Expected: 4 fields and an inert cell. | a✔ b✘ c✔ d✘ |
| F2 | Medium | PROBABLE | B | auth.py:4 (`_TOKENS`) | Static bearer tokens for both staff accounts are committed in source. They have no expiry, no rotation and no revocation. Nothing marks them as fixtures or a stub. | If this module ships as written before production, anyone with read access to the repo can send `tok-sam` to `/staff/trips.csv` and download every rider's name and email. | Load tokens from a secret store or an identity provider, keep fixtures only in the tests, and label the stub. Repro: `handle({"path": "/staff/trips.csv", "token": "tok-sam"})` returns 200 with every email. | a✔ b✘ c✔ d✘ |
| F3 | Low | CONFIRMED | B | test_app.py (whole file) | Two stated requirements have no test: "no token gives 401" on a `/staff` route (only `/trips` is tested), and the JSON export containing names and emails (`test_staff_can_export_json` checks the status code only). The code is correct on both today. I traced `app.py:8-10`, which authenticates before any routing, and `all_rows()`, which returns every field. | Someone later moves the staff branch above the `auth.current` call, or trims fields from `all_rows`. All 7 tests still pass while the API returns 403 instead of 401, or drops the emails from the export. | Add `get("/staff/trips.csv", None)` with an expected status of 401. Assert that `tomas@example.test` appears in the JSON body. Mutation check: swap the order of the auth and routing steps in a scratch copy and confirm that the new test goes red. | a✔ b✔ c✘ d✘ |
| F4 | Low | CONFIRMED | B | app.py:11 | `request["path"]` raises `KeyError` when the path is missing. Every other malformed input is turned into a status code; this one is not. | A malformed request with a valid token raises an uncaught exception instead of returning 400 or 404. | Use `request.get("path", "")`. Repro: `handle({"token": "tok-sam"})` raises `KeyError: 'path'`. | a✔ b✔ c✘ d✘ |

**NEEDS VALIDATION**
- **S1:** Is auth.py the token store that goes to production, or a stand-in? If it ships, F2 becomes High or Critical.
- **S2:** Is `rider` a unique account ID or a display name? `for_rider` matches on `t["rider"] == name`. If two riders can share a name, each sees the other's trips, which breaks "list their own trips".
- **S3:** Does the server strip query strings and trailing slashes before calling `handle`? If not, `/staff/trips.csv?x=1` returns 404 for staff. That is safe, but it breaks the export.

**REFUTED**
- *A rider reaches staff data through path tricks.* Refuted: the staff check guards the whole `/staff/` prefix, so `/staff/../trips.json` and similar paths are checked before the exact-match routes. `/STAFF/...` and `/staff` (no trailing slash) fall through to 404 and never touch data.
- *The staff check is skipped on one export path.* Refuted: both exports sit after `require_staff` in the same branch (app.py:14-21).
- *A None or non-str token crashes the handler.* Refuted: auth.py:13 maps a non-str token to `b""`, which matches no token and raises `AuthError`, giving 401. The odd-token test also covers this.
- *An empty-string token matches something.* Refuted: no known token is empty.
- *Timing leak in token comparison.* Not material: `compare_digest` is used, and the early return only reveals which entry in a 3-token table matched.

**WHAT HOLDS UP**
- 401 versus 403 ordering is correct. Authentication happens before any routing, so an unauthenticated caller can never get a 403 or 404 that reveals the route structure.
- A rider token on any `/staff/*` path, including unknown ones, gets 403.
- `/trips` is scoped to the caller's identity. A token cannot request another rider's data.
- Both exports include names and emails, as required. The handlers return copies, so callers cannot mutate the stored records.

**UNVERIFIED CLAIMS**
- "7 tests in test_app.py pass." Not run. Confirm with `python -m unittest test_app -v`. Tracing by hand, I expect all 7 to pass.

**QUESTIONS FOR THE AUTHOR**
1. Does auth.py ship to production as written? (S1 and F2)
2. Is the `rider` field a unique ID? (S2)

**DECISION-MAKER SUMMARY:** The access control matches the request and I found no way for a rider to reach staff exports. Before launch:
- Replace the hard-coded tokens.
- Escape the CSV.
- Add the two missing tests.

If you ship as is, the main risk is that anyone holding a copy of the code can use the committed staff token to download every rider's personal data.

**OWNER SUMMARY:** Riders can only see their own trips, and only staff can download the full list, as intended. Three things need fixing before launch. The staff passwords are written into the code itself, the spreadsheet download can be corrupted or misused by unusual names, and two of the rules have no automatic check. All three are small fixes.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "trips.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "test run output (7 passing)", "status": "not_seen", "matters": false},
    {"item": "production token store / identity provider", "status": "not_seen", "matters": true},
    {"item": "HTTP layer that builds request path", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Work handles rider names and emails (personal data); fixtures use example.test. External seats refused."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current", "kind": "function"},
      {"unit": "auth.py:require_staff", "kind": "function"},
      {"unit": "trips.py", "kind": "file"},
      {"unit": "trips.py:as_csv", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "runtime test execution", "reason": "no tools in session"},
      {"unit": "production token provisioning", "reason": "not supplied"},
      {"unit": "HTTP/path normalization layer", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "trips.py:19-21",
     "scenario": "A rider name or email containing a comma, quote or newline shifts the CSV columns; a name starting with = runs as a formula when staff open the export.",
     "fix": "Build the CSV with csv.writer and neutralize cells that start with a formula character.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Add a trip with rider '=HYPERLINK(\"http://x\")' and email 'a,b@x'; as_csv() yields a 5-field row with a live formula; expected 4 fields and an inert cell."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:4",
     "scenario": "If auth.py ships as written, anyone with repo access can send tok-sam to /staff/trips.csv and download all rider names and emails.",
     "fix": "Load tokens from a secret store or identity provider with expiry and revocation; keep literal tokens only as test fixtures.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "handle({'path': '/staff/trips.csv', 'token': 'tok-sam'}) returns 200 with every email."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py",
     "scenario": "No test covers no-token on a /staff route or the JSON export's contents; a refactor that returns 403 instead of 401, or drops emails from the export, passes all 7 tests.",
     "fix": "Add a test that /staff/trips.csv with a None token returns 401, and assert the JSON export body contains tomas@example.test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy, move the staff branch above auth.current; all 7 existing tests stay green."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:11",
     "scenario": "A request with no path raises KeyError instead of returning a status code.",
     "fix": "Use request.get('path', '').",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "handle({'token': 'tok-sam'}) raises KeyError: 'path'; expected 404."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:4",
     "suspicion": "The hard-coded token table may be the production credential store.",
     "unresolved_fact": "Whether auth.py ships to production unchanged."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "trips.py:11-12",
     "suspicion": "Trips are matched to a rider by name; two riders sharing a name would see each other's trips.",
     "unresolved_fact": "Whether the rider field is a unique account ID."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "app.py:11-21",
     "suspicion": "Exact path matching returns 404 for staff export URLs that carry a query string or a trailing slash.",
     "unresolved_fact": "Whether the HTTP layer normalizes the path before calling handle."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A rider reaches staff data through path variants.", "evidence": "require_staff guards the whole /staff/ prefix before the exact-match routes; /STAFF/ and /staff fall through to 404 without touching data."},
    {"id": "C2", "candidate": "One export path skips the staff check.", "evidence": "Both exports sit after require_staff in the same branch (app.py:14-21)."},
    {"id": "C3", "candidate": "A None or non-str token crashes the handler.", "evidence": "auth.py:13 maps a non-str token to b'', which matches nothing and raises AuthError, giving 401."},
    {"id": "C4", "candidate": "The token comparison leaks timing.", "evidence": "hmac.compare_digest is used; the early return only reveals which entry in a 3-token table matched."}
  ]
}
```