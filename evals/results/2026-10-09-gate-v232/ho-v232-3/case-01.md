VERDICT: **REWORK.** `/staff/trips.csv` has no staff check, so any rider token downloads every rider's name and email.

CONFIDENCE: **medium.** I had no tools. Every finding is traced by reading all four supplied files; nothing was executed. The work was not written in this conversation, but this is still a single-reviewer pass, so re-run it with tests in a fresh session before production.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `app.py`, `auth.py`, `trips.py`, `test_app.py`.
- **Not seen:**
  - The test run output behind "4 tests pass". It matters a little: the claim is unverified, but no finding depends on it.
  - How production tokens and rider records are provisioned. This matters for S1 and S2.

COVERAGE:
- **Scope:** the whole work, all four files.
- **Checked:**
  - `app.py:handle`, every branch
  - `auth.py:current` and `auth.py:require_staff`
  - `trips.py:for_rider`, `trips.py:all_rows` and `trips.py:as_csv`
  - All 4 tests in `test_app.py`
  - `request.md` and `context.md`
- **Not checked:**
  - Test execution and mutation testing (`no_tools`)
  - Deployment and the real token store (`not_supplied`)

SEATS AND GATE:
- **Reviewer:** one local reviewer. No subagent or cross-vendor seats, because this session has no tools.
- **Sensitivity gate:** passed. The data is fixtures on the reserved `example.test` domain, though in production it would be personal data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (traced) | B | `app.py` `/staff/trips.csv` branch (`return {"status": 200, "body": trips.as_csv()}`) | The CSV export never calls `auth.require_staff`. The JSON branch does. | A rider authenticates with their own token and requests `/staff/trips.csv`. `current` returns `("rita","rider")` and no check runs, so the rider gets a 200 response containing every rider's name and email (`tomas@example.test`). This breaks the requirement that a rider gets 403 and leaks personal data. | **Fix:** enforce staff once for every path starting with `/staff/`, before dispatch, so new staff routes cannot fail open. **Repro:** `get("/staff/trips.csv","tok-rita")` should return 403; trace shows it returns 200 with `tomas@example.test` in the body. | y/y/y/y |
| F2 | **High** | CONFIRMED | B | `test_app.py` (whole file) | No test touches `/staff/trips.csv` at all, so the 4/4 green result is silent on the route that leaks. | Any future regression on a staff route other than JSON also ships green. F1 shows this has already happened. | **Fix:** add `test_rider_cannot_export_csv` (expect 403), `test_no_token_staff_csv_is_401` and `test_staff_can_export_csv`. Mutation-check the JSON test by deleting `require_staff`: trace says it goes red; run it to confirm. **Repro:** add `assertEqual(get("/staff/trips.csv","tok-rita")["status"],403)`; it fails on the current code. | y/y/n/y |
| F3 | Medium | CONFIRMED (traced) | B | `trips.py:as_csv` f-string | Fields are written without quoting or escaping. | A rider name or email containing `,`, `"` or a newline shifts columns or splits rows in the staff export, misattributing trips. If riders control their names, a value like `=HYPERLINK(...)` becomes spreadsheet formula injection (see S3). | **Fix:** use `csv.writer` on an `io.StringIO`, and prefix cells starting with `=+-@` if the export is opened in spreadsheets. **Repro:** add `{"rider":"Ann, Jr","email":"a@example.test","bike":"B-1","km":1}` to `_TRIPS`; the CSV row has 5 fields under a 4-column header. | y/y/n/n |
| F4 | Low | CONFIRMED (traced) | B | `app.py` final `return 404` | An unknown `/staff/*` path returns 404 to riders and staff alike, and is not gated. | `/staff/anything` with a rider token returns 404, not the 403 the request specifies "on a /staff route". This is harmless today, but it is the same fail-open shape as F1 for the next route added. | **Fix:** apply the prefix gate from F1. **Repro:** `get("/staff/x","tok-rita")["status"]` should be 403; trace gives 404. | y/y/n/n |
| F5 | Low | CONFIRMED (traced) | B | `app.py` `path = request["path"]` | A request with no `"path"` key raises `KeyError` instead of returning a status. | A malformed request from an authenticated caller produces an unhandled exception (a 500 upstream) rather than a 400 or 404. | **Fix:** use `request.get("path")` and fall through to 404 or 400. **Repro:** `app.handle({"token":"tok-sam"})` raises `KeyError: 'path'`; expected a status dict. | y/y/n/n |

**Pass 3 records:**
- **F1:**
  - *Sibling search:* every `/staff` branch in `handle` (2 found; only JSON is guarded) and every caller of `trips.all_rows` and `trips.as_csv` (only `app.py`). The unguarded fall-through is F4.
  - *Boundary (security):* the principal is a rider with a valid token; the input is the path `/staff/trips.csv`; the failing control is the missing `require_staff`; the boundary crossed is rider to staff; the resource is all riders' names and emails.
  - *Confirm-or-refute:* I looked for any route-level middleware or a check inside `as_csv` that would defend this route and found none. It holds.
- **F2:**
  - *Sibling search:* every test, against every route and auth state. Untested: CSV for all roles, 401 on staff routes, and unknown paths.
  - *Security:* not a security finding in itself (no boundary is crossed by the test file).
  - *Confirm-or-refute:* holds.

## NEEDS VALIDATION
- **S1 (`auth.py` `_TOKENS`):** Static bearer tokens are hard-coded in source. Settle it by finding out whether this dict, or anything like it, is the production token store. If it is, anyone with repo read access can use `tok-sam` to dump all personal data. That would be a finding, and the tokens must be rotated, with git history checked for them.
- **S2 (`trips.for_rider(ident[0])`):** Trips are matched by display name, not a unique rider ID. Settle it by finding out whether rider names are guaranteed unique in production. If they are not, two riders named "rita" see each other's trips.
- **S3 (`as_csv`):** Formula injection depends on whether riders can set their own name or email.

## REFUTED
- **C1: "No token, or a non-string token, crashes `current` or matches."** `None` or a non-string becomes `b""`. `compare_digest` against every known token is False, so `AuthError` is raised and `handle` returns 401. That is correct.
- **C2: "The JSON route lets riders through."** `require_staff` raises on role `"rider"`, and `handle` returns 403. That is correct.
- **C3: "Timing leak in token comparison is material."** `compare_digest` is used. The leaks of length and loop position are negligible against random tokens and do not cross a boundary.

## WHAT HOLDS UP
- The 401 path for missing, empty and garbage tokens is correct.
- Riders get only their own rows on `/trips` (subject to S2).
- The JSON export is correctly gated.
- `trips` returns copies, so callers cannot mutate the in-memory store.

## UNVERIFIED CLAIMS
- **"4 tests pass":** run `python3 -m unittest test_app` in an isolated copy.
- **"`test_rider_cannot_export_json` guards the check":** delete the `require_staff` call in a scratch copy and confirm the test goes red.

## QUESTIONS FOR THE AUTHOR
1. Is `_TOKENS` the production auth mechanism or a placeholder?
2. Are rider names unique, or is there a rider ID that should key trips?

## DECISION-MAKER SUMMARY
Do not ship: the CSV staff export is open to any rider, which exposes every rider's name and email. Fix it with a single staff gate on all `/staff/` paths, plus CSV tests, then re-run the review. Proceeding as is means a personal-data breach the moment a rider tries the URL.

## OWNER SUMMARY
One of the two staff-only download links has no access check, so any rider who logs in can download every rider's name and email address. The automated tests never tried that link, which is why they all passed. This needs a small code fix and new tests before going live.

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
    {"item": "test run output for '4 tests pass'", "status": "not_seen", "matters": false},
    {"item": "production token store / rider identity model", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer-no-tools", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Fixture data on example.test; no real personal data supplied."},
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
      {"unit": "trips.py:for_rider", "kind": "function"},
      {"unit": "trips.py:all_rows", "kind": "function"},
      {"unit": "trips.py:as_csv", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation of test_app.py", "reason": "no_tools"},
      {"unit": "production token store and deployment", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: /staff/trips.csv branch",
     "scenario": "A rider token on GET /staff/trips.csv passes current(), no require_staff runs, and the rider receives 200 with every rider's name and email.",
     "fix": "Enforce require_staff once for every path starting with /staff/ before dispatch.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "get('/staff/trips.csv','tok-rita'): expected status 403; traced result is 200 with tomas@example.test in the body.",
     "security": true,
     "boundary": {"principal": "a rider with a valid token", "input": "the path /staff/trips.csv",
                  "control": "require_staff is never called on this branch", "crossed": "rider to staff",
                  "resource": "all riders' names and emails"},
     "siblings_searched": {"searched": "every /staff branch in handle and every caller of trips.all_rows and trips.as_csv",
                           "found": "JSON branch guarded; unknown /staff/* falls through ungated (F4)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py (whole file)",
     "scenario": "No test exercises /staff/trips.csv, so the F1 leak and any future staff-route regression pass CI green.",
     "fix": "Add tests: rider on CSV gets 403, no token on staff routes gets 401, staff on CSV gets 200; mutation-check the JSON test.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add assertEqual(get('/staff/trips.csv','tok-rita')['status'], 403); it fails on the current code (traced 200).",
     "security": false,
     "siblings_searched": {"searched": "all four tests against every route and auth state",
                           "found": "CSV untested for all roles; 401 on staff routes untested; unknown paths untested"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "trips.py:as_csv",
     "scenario": "A name or email containing a comma, quote or newline corrupts the staff CSV export and misattributes trips.",
     "fix": "Write rows with csv.writer and neutralise leading =+-@ characters.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a trip with rider 'Ann, Jr'; the CSV row has 5 fields under a 4-column header."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: final 404 return",
     "scenario": "A rider token on an unknown /staff/* path gets 404 rather than the 403 the request specifies; the same fail-open shape as F1 for future routes.",
     "fix": "Use the /staff/ prefix gate from F1.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "get('/staff/x','tok-rita')['status']: expected 403; traced result is 404."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py: path = request['path']",
     "scenario": "An authenticated request without a 'path' key raises KeyError instead of returning a status.",
     "fix": "Use request.get('path') and return 400 or 404.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "app.handle({'token':'tok-sam'}) raises KeyError: 'path'; expected a status dict."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:_TOKENS",
     "suspicion": "Static staff bearer tokens hard-coded in source would let anyone with repo access dump personal data.",
     "unresolved_fact": "Whether _TOKENS is the production token store or a placeholder."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py /trips branch; trips.py:for_rider",
     "suspicion": "Trips are keyed by display name, so riders with the same name would see each other's trips.",
     "unresolved_fact": "Whether rider names are unique in production or a rider ID exists."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "trips.py:as_csv",
     "suspicion": "Spreadsheet formula injection via rider-controlled names or emails.",
     "unresolved_fact": "Whether riders can set their own name or email."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A missing or non-string token crashes or matches in auth.current.",
     "evidence": "It becomes b'', compare_digest is False for every known token, AuthError is raised, and handle returns 401."},
    {"id": "C2", "candidate": "The JSON staff route admits riders.",
     "evidence": "require_staff raises for role 'rider' and handle returns 403."},
    {"id": "C3", "candidate": "The timing leak in token comparison is material.",
     "evidence": "compare_digest is used; the residual length and position leak crosses no boundary for random tokens."}
  ]
}
```