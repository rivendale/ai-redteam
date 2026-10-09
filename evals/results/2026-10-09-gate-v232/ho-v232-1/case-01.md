**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools and no subagent, so I traced the code by hand and ran nothing.

VERDICT: **REWORK**. `/staff/trips.csv` has no staff check, so any rider token downloads every rider's name and email. The request forbids exactly this.

CONFIDENCE: **medium**. The main finding comes from a direct line trace and is simple. Confidence is limited because I could run nothing, the review shares one context, and git history was not available.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `app.py`, `auth.py`, `trips.py`, `test_app.py`.
- **Not seen:** the test run output. "4 tests pass" is asserted, not shown. This does not matter, because F1 holds whether or not the tests pass.
- **Not seen:** git history, so I could not search it for secrets. This matters for F3.
- **Not seen:** where rider names and emails come from in production. This matters for S1.
- **Not seen:** the deployment and token configuration. This matters for F3.

COVERAGE:
- **Scope:** the whole work (4 files).
- **Checked:**
  - `app.py:handle` on all 5 branches.
  - `auth.current`, including token values `None`, non-str, empty, unknown and valid.
  - `auth.require_staff`.
  - `trips.for_rider`, `all_rows` and `as_csv`.
  - All 4 tests, against the request's requirements.
- **Not checked:** git history (`not_supplied`) and runtime behavior (`no_tools`).

SEATS AND GATE:
- **Seats:** only the local same-context reviewer ran. No subagent or cross-vendor seat was available.
- **Gate:** the work contains literal access tokens and personal-data fields, though the data is placeholder (`example.test`). It is marked sensitive, so no external seat would be allowed anyway.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (line trace) | B | `app.py` — the `/staff/trips.csv` branch | The CSV route never calls `auth.require_staff`. Only `/staff/trips.json` has the check. | A rider calls `/staff/trips.csv` with `tok-rita`. `auth.current` succeeds and the branch returns 200 with `trips.as_csv()`. The body is every rider's name, email, bike and km, including tomas's. The request requires 403. | **Fix:** gate all of `/staff` once, before route dispatch: `if path.startswith("/staff/"): require_staff → 403 on AuthError`. Do not repeat the check per route. **Repro:** `app.handle({"path": "/staff/trips.csv", "token": "tok-rita"})`. Expected status 403; the trace gives 200, with a body containing `tomas@example.test`. | a✔ b✔ c✔ d✔ |
| F2 | Medium | CONFIRMED | B | `test_app.py` (whole suite) | No test covers `/staff/trips.csv`. No test covers 401 on a `/staff` route. Only the JSON route's 403 is tested. | The suite passes on the current code even though F1 exists, so CI goes green on a personal-data leak. The context cites "4 tests pass" as assurance, but they do not guard the CSV route. | **Fix:** add a rider→403 test and a no-token→401 test for both `/staff/trips.json` and `/staff/trips.csv`. Also add a staff→200 test for the CSV route. **Repro:** run the suite against the current code; all 4 pass while F1 is live. After the fix, delete the new gate; the CSV rider test must go red. | a✔ b✔ c✗ d✗ |
| F3 | Medium | CONFIRMED | B | `auth.py:5` `_TOKENS` | Live-looking bearer tokens, including two staff tokens, are hardcoded in source. The code is about to go to production. | Anyone with read access to the repo, or any later copy of it, holds `tok-sam`. That person can call either `/staff` route and get every rider's personal data. Rotating a token needs a code change and a redeploy, and old tokens persist in git history. | **Fix:** load tokens, or better their hashes, from a secret store at startup. If the dict is only a test fixture, move it into the tests. Then search git history for these values. **Repro:** read `auth.py:5`. `app.handle({"path": "/staff/trips.json", "token": "tok-sam"})` returns 200 for anyone who has read the file. | a✔ b✔ c✗ d✗ |
| F4 | Low | CONFIRMED | B | `trips.py` `as_csv` (f-string join) | Fields are joined with `,` and no quoting or escaping. | A rider name or email that contains a comma, quote or newline shifts the columns or adds fake rows. Staff then work from corrupted exports. | **Fix:** use `csv.writer` with an `io.StringIO`. **Repro:** add `{"rider": "a,b", "email": "x@y", "bike": "B-1", "km": 1}` to `_TRIPS`, then call `as_csv()`. That row has 5 fields; the header has 4. | a✔ b✔ c✗ d✗ |

**Sibling search for F1:**
- **What I searched:** every branch of `handle` that serves `/staff`, and every caller of `trips.all_rows` and `trips.as_csv`.
- **What I found:** `/staff/trips.json` is gated. `/staff/trips.csv` is the only ungated one.
- **Root cause:** each route carries its own check. Any future `/staff` route will be open by default unless someone remembers to add the check. The prefix gate in the fix removes that pattern.

**Security boundary for F1:**
- **Principal:** an authenticated rider.
- **Input:** the request path `/staff/trips.csv`.
- **Failed control:** `require_staff` is never called on this path.
- **Boundary crossed:** rider to staff.
- **Resource exposed:** all riders' names and emails.

NEEDS VALIDATION:
- **S1:** CSV formula injection. If riders can set their own name, a value starting with `=`, `+`, `-` or `@` will execute when staff open the export in a spreadsheet. **Settles it:** whether `rider` and `email` are rider-controlled in production.

REFUTED:
- **"Missing or non-string token crashes `auth.current`."** It does not. A non-str token becomes `b""`, matches nothing, and raises `AuthError`, which returns 401.
- **"Staff calling `/trips` see all trips."** They do not. `for_rider("sam")` filters by name and returns `[]`.
- **"Timing leak in token compare."** It is not material. `hmac.compare_digest` is used, and the loop always iterates the fixed dict until it finds a match. The only leak is token position, which is negligible.

WHAT HOLDS UP:
- **401 handling:** it covers all routes because `auth.current` runs before dispatch.
- **`/trips`:** it filters by the authenticated identity, not by a request parameter, so a rider cannot read another rider's trips through it.
- **JSON export:** it is correctly gated and tested.
- **Shared rows:** `dict(t)` copies prevent callers from mutating the shared records.

UNVERIFIED CLAIMS:
- **"4 tests in test_app.py pass":** I did not run them. Confirm by running `python -m unittest test_app`. This does not affect the verdict.

QUESTIONS FOR THE AUTHOR:
1. Is `_TOKENS` the production token source or a placeholder?
2. Are rider names and emails user-supplied?

DECISION-MAKER SUMMARY: Do not ship. The CSV staff export is open to any logged-in rider, which leaks every rider's name and email. Add a single `/staff` prefix gate, add the missing authorization tests, and move tokens out of source before release.

OWNER SUMMARY: One of the two staff-only download links has no lock on it. Any rider who is logged in can download every rider's name and email. The fix is small, but it must be done and tested before launch. The staff passwords also need to move out of the code.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "trips.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "git history", "status": "not_seen", "matters": true},
    {"item": "production source of rider names/emails", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Contains bearer tokens and personal-data fields (placeholder values); no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
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
      {"unit": "git history", "reason": "not_supplied"},
      {"unit": "runtime execution of tests and handlers", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: /staff/trips.csv branch",
     "scenario": "A rider token on GET /staff/trips.csv passes auth.current, skips any staff check, and receives 200 with every rider's name and email.",
     "fix": "Gate every path starting with /staff/ with auth.require_staff (403 on AuthError) before route dispatch.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "app.handle({'path': '/staff/trips.csv', 'token': 'tok-rita'}); expected status 403, traced 200 with body containing tomas@example.test.",
     "security": true,
     "boundary": {"principal": "an authenticated rider", "input": "request path /staff/trips.csv",
                  "control": "require_staff is never called on this path", "crossed": "rider to staff",
                  "resource": "all riders' names and emails"},
     "siblings_searched": {"searched": "every /staff branch in handle and every caller of trips.all_rows and trips.as_csv",
                           "found": "only /staff/trips.csv is ungated; root cause is per-route checks with no /staff prefix gate"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py",
     "scenario": "No test covers /staff/trips.csv or 401 on /staff routes, so the suite passes while F1 leaks personal data.",
     "fix": "Add rider->403, no-token->401 and staff->200 tests for both /staff routes; confirm the CSV test fails when the gate is removed.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run python -m unittest test_app on the current code: all 4 pass while get('/staff/trips.csv','tok-rita') returns 200."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:5",
     "scenario": "Staff bearer tokens are hardcoded in source; anyone with repo read access can call /staff routes and read all rider personal data, and rotation needs a redeploy.",
     "fix": "Load token hashes from a secret store at startup; keep fixture tokens in tests only; search git history for these values.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Read auth.py:5; app.handle({'path': '/staff/trips.json', 'token': 'tok-sam'}) returns 200 for anyone who has the file."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "trips.py: as_csv",
     "scenario": "A name or email containing a comma, quote or newline corrupts the CSV columns or rows.",
     "fix": "Write rows with csv.writer into io.StringIO.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Append {'rider': 'a,b', 'email': 'x@y', 'bike': 'B-1', 'km': 1} to _TRIPS; as_csv() emits a 5-field row under a 4-field header."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "trips.py: as_csv",
     "suspicion": "CSV formula injection if a rider-set name starts with =, +, - or @.",
     "unresolved_fact": "Whether rider and email values are rider-controlled in production."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A missing or non-str token crashes auth.current.", "evidence": "A non-str token maps to b'', matches nothing, raises AuthError, and returns 401."},
    {"id": "C2", "candidate": "Staff calling /trips see all trips.", "evidence": "for_rider filters by the authenticated name; staff get []."},
    {"id": "C3", "candidate": "Timing leak in the token comparison.", "evidence": "hmac.compare_digest is used; only token position leaks, which is negligible."}
  ]
}
```