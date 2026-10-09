**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so nothing was executed. Every CONFIRMED finding below comes from reading and tracing the supplied source line by line.

---

**VERDICT: REWORK.** `/staff/trips.csv` has no staff check, so any rider token can download every rider's name and email. That is an open Critical, and an open Critical rules out SHIP WITH FIXES, even though the fix is a few lines.

**CONFIDENCE: medium.** The Critical is traced directly and does not depend on execution. Confidence is limited by:
- the same-context review,
- no ability to run the tests or a mutation,
- no deployment or config information.

**INPUTS LEDGER**
- Seen: request.md (verbatim), context.md, app.py, auth.py, trips.py, test_app.py.
- Not seen: the production token store or config, which matters for whether `_TOKENS` is a fixture or real (S1).
- Not seen: the deployment or router in front of `handle`. This matters only if something upstream adds auth, and the request treats these handlers as the boundary.
- Not seen: test run output. This matters little, because tracing shows all 4 tests would pass. That is exactly the problem: they pass with the Critical present.

**COVERAGE**
- Checked:
  - `app.py:handle`, all four branches plus the fallthrough.
  - `auth.py:current`, `auth.py:require_staff`, `auth.py:_TOKENS`.
  - `trips.py:for_rider`, `trips.py:all_rows`, `trips.py:as_csv`.
  - All four tests in `test_app.py`.
  - Each requirement sentence in request.md.
- Not checked:
  - Runtime behaviour, because nothing could be run.
  - Mutation testing of the suite.
  - Upstream routing.

**SEATS AND GATE**
- Sensitivity: the work handles rider PII by design, but the supplied data is fixture data (`@example.test`). Cross-vendor seats were not requested and none were available.
- Ran: the local same-context reviewer only. No subagent tool existed in this session.

---

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `app.py`, `/staff/trips.csv` branch (`if path == "/staff/trips.csv": return {"status": 200, "body": trips.as_csv()}`) | The CSV export never calls `auth.require_staff`. Only the JSON branch is guarded. The request says a rider token on a /staff route gives 403. | Rider `tok-rita` requests `/staff/trips.csv`. `auth.current` succeeds and the branch returns 200 with `tomas,tomas@example.test,...`, which is another rider's personal data. | **Fix:** check staff once for every path starting with `/staff/`, before dispatch, instead of per branch. **Reproduction:** add `self.assertEqual(get("/staff/trips.csv", "tok-rita")["status"], 403)`. Today it observes 200; the expected result is 403. | y/y/y/y |
| F2 | Medium | CONFIRMED | B | `test_app.py`, whole suite | No test touches `/staff/trips.csv`, for either the staff 200 case or the rider 403 case. The suite also has no 401 test on a /staff route. The suite claim "4 tests pass" is true and still does not cover the requirement. | Any future regression in the CSV branch, including the current one, ships green. | **Fix:** add rider→403, staff→200 and no-token→401 tests for both /staff routes. **Reproduction:** the F1 test, which fails on the current code. | y/y/n/y |
| F3 | Medium | CONFIRMED (code), PROBABLE (trigger) | B | `trips.py:as_csv`, the f-string row | Fields are joined with raw commas. Nothing is quoted or escaped, and nothing neutralises leading `=+-@`. | A rider name or email containing `,`, `"` or a newline produces shifted or broken rows in the staff export. A name like `=HYPERLINK(...)` executes as a formula when staff open the file in a spreadsheet. | **Fix:** write rows with `csv.writer` and prefix cells that start with `=+-@`. **Reproduction:** add a trip with rider `"Smith, J"`. The row then has 5 fields, where 4 are expected. | y/y/n/n |
| F4 | Low | CONFIRMED | B | `app.py`, `path = request["path"]` | A request without `"path"` raises `KeyError` after auth instead of returning a 4xx. | An authenticated malformed request gets an unhandled exception, which surfaces as a 500 depending on the host. | **Fix:** use `request.get("path")` and fall through to 404. **Reproduction:** `app.handle({"token": "tok-sam"})` raises `KeyError`; a 404 or 400 is expected. | y/y/n/n |

### NEEDS VALIDATION
- **S1, hard-coded, guessable tokens** (`auth.py:_TOKENS`). Staff tokens such as `tok-sam` and `tok-ola` sit in source and follow a guessable `tok-<name>` pattern. What would settle it: is `_TOKENS` a test fixture, or the store that ships to production? If it ships, this is at least High.
- **S2, identity by display name** (`app.py` `trips.for_rider(ident[0])`, `trips.py:for_rider`). Trips are matched on the rider's name. What would settle it: are rider names unique in production? If two riders share a name, each sees the other's trips.

### REFUTED
- **C1: a `None`, empty or non-string token bypasses auth.** Refuted: non-strings become `b""`, which never matches a known token, so `AuthError` is raised and the handler returns 401.
- **C2: timing leak in token comparison.** Refuted as a finding: `hmac.compare_digest` is used per token. The early return reveals only how far through the list a valid token sits, which has no practical impact here.
- **C3: unknown `/staff/*` paths return 404 instead of 403.** Refuted: the request specifies 403 for "a /staff route", and non-existent paths are not routes. There is also no data exposure.

### WHAT HOLDS UP
- Authentication runs before any routing, so a missing or unknown token gets 401 on every path, including both staff routes.
- The JSON export is correctly guarded.
- `/trips` filters by the caller's identity, never by a request parameter.
- `for_rider` and `all_rows` return copies, so callers cannot mutate the store.

### UNVERIFIED CLAIMS
- **"4 tests in test_app.py pass."** By trace they would pass. To confirm, run `python3 -m unittest test_app`.
- **That the tests guard what they claim.** No mutation run was possible. Settle it by deleting the `require_staff` call in the JSON branch in a scratch copy and confirming `test_rider_cannot_export_json` goes red.

### QUESTIONS FOR THE AUTHOR
1. Is `_TOKENS` the production token store (S1)?
2. Are rider names unique, or is there a stable rider ID that should be used instead (S2)?

### DECISION-MAKER SUMMARY
Do not deploy. Any rider can download every rider's name and email from the CSV export, and the test suite does not notice. Add one staff check covering all `/staff` routes, plus tests for both exports, then re-review. Proceeding as-is is a personal-data breach available to every rider account.

### OWNER SUMMARY
One of the two staff-only download links is not actually locked, so any rider who knows the address can download every rider's name and email. The existing tests check only the other link, which is why this went unnoticed. The fix is small, but it has to be made and tested before launch.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "trips.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "production token store / config", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Handles rider PII by design, but supplied data is fixture data (example.test); no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current", "kind": "function"},
      {"unit": "auth.py:require_staff", "kind": "function"},
      {"unit": "trips.py", "kind": "file"},
      {"unit": "trips.py:as_csv", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md: rider token on /staff route gives 403", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "runtime execution and mutation testing", "reason": "no tools in this session"},
      {"unit": "production token store / upstream routing", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: /staff/trips.csv branch",
     "scenario": "A rider token (tok-rita) on GET /staff/trips.csv receives 200 with every rider's name and email; require_staff is never called on this branch.",
     "fix": "Enforce auth.require_staff for every path starting with /staff/ before dispatch, returning 403 on AuthError.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "assertEqual(get('/staff/trips.csv', 'tok-rita')['status'], 403): expect 403, observe 200."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py (whole suite)",
     "scenario": "No test exercises /staff/trips.csv, so the F1 access-control gap and future regressions ship with a green suite.",
     "fix": "Add rider->403, staff->200 and no-token->401 tests for both /staff routes.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "The F1 test fails on the current code."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "trips.py:as_csv row f-string",
     "scenario": "A rider name or email containing a comma, quote or newline corrupts the staff CSV; a value starting with = is executed as a formula in a spreadsheet.",
     "fix": "Use csv.writer for quoting and neutralise cells starting with = + - @.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a trip with rider 'Smith, J'; the data row splits into 5 fields instead of 4."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: path = request['path']",
     "scenario": "An authenticated request without a 'path' key raises KeyError instead of returning a 4xx.",
     "fix": "Use request.get('path') and fall through to 404.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "app.handle({'token': 'tok-sam'}) raises KeyError; expect a 404 or 400 response."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:_TOKENS",
     "suspicion": "Staff tokens are hard-coded in source and follow a guessable tok-<name> pattern.",
     "unresolved_fact": "Whether _TOKENS is a test fixture or the store that ships to production."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py: trips.for_rider(ident[0]); trips.py:for_rider",
     "suspicion": "Trips are matched by display name, so riders sharing a name would see each other's trips.",
     "unresolved_fact": "Whether rider names are unique in production or a stable rider ID exists."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A None, empty or non-string token bypasses auth.",
     "evidence": "auth.current maps non-strings to b'', which matches no known token, so AuthError is raised and handle returns 401."},
    {"id": "C2", "candidate": "Timing leak in token comparison.",
     "evidence": "hmac.compare_digest is used per token; the early return reveals only list position, with no practical impact."},
    {"id": "C3", "candidate": "Unknown /staff/* paths should return 403, not 404.",
     "evidence": "The request requires 403 for /staff routes; non-existent paths are not routes and expose no data."}
  ]
}
```