# Redteam review: Pedalo ops API handlers

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools and no subagent, so every trace below comes from reading the code, not running it.

**VERDICT: SHIP WITH FIXES.** The access-control logic does what was asked on every route I traced: no token gives 401 on every path, and a rider token on any `/staff/` path gives 403. The confirmed defects are a CSV export that does no quoting, a test suite that checks status codes but not what the staff dumps contain, and a crash on a malformed request.

**CONFIDENCE: medium.** I could not run the tests or any code, and the production token store and how riders' names are set were not supplied.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `app.py`, `auth.py`, `trips.py`, `test_app.py`.
- **Not seen:**
  - **The production token or identity store.** This matters, because `auth.py` holds a hardcoded fixture.
  - **How rider names and emails get into the data.** This matters for CSV formula injection.
  - **The server or framework that builds `request`.** This matters a little: it decides whether `path` is always a string.
  - **A test run log.** The claim "7 tests pass" is UNVERIFIED.

**COVERAGE**
- **Scope:** the whole work (four files).
- **Checked:**
  - `app.py:handle`, including every route, the order of checks, and the path matching.
  - `auth.py:current` and `auth.py:require_staff`.
  - `trips.py:for_rider`, `trips.py:all_rows` and `trips.py:as_csv`.
  - All 7 tests.
  - `request.md` and `context.md`.
- **Not checked:** the production auth store and the deploy surface (not supplied), and the test execution (no tools).

**SEATS AND GATE:** One local, same-context reviewer. No cross-vendor seats were requested at standard depth. The sensitivity gate passed: the data uses fictional `example.test` addresses and there is no real personal data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `trips.py:20` | The CSV rows are built with an f-string join. Commas, quotes and newlines in a field are not quoted or escaped. | A rider named `Lee, Ana`, or a quoted email local part containing `,` or `"`, shifts every later column in that row. Staff then read a wrong email or bike for that rider. | Use `csv.writer` over `io.StringIO`, or `csv.DictWriter`. **Repro:** append `{"rider":"Lee, Ana","email":"a@example.test","bike":"B-1","km":1}` to `_TRIPS`, then call `as_csv()`. **Expected:** the row has 4 columns. **Observed:** it has 5. | a Y / b Y / c N / d N |
| F2 | Low | CONFIRMED | B | `test_app.py:17-18` | `test_staff_can_export_json` checks only the 200 status. The request says the route must dump *every rider's* trips. | Someone mistakenly changes `all_rows()` to return `[]` or `for_rider(ident[0])`. Staff then get an empty or partial dump, and the suite stays green. | Assert that the body contains rows for both `rita` and `tomas`, with emails. **Repro:** in a scratch copy, change `trips.py:15` to `return []` and run the tests. Expected result: a test fails. Predicted from reading (not run): all 7 still pass. | a Y / b Y / c N / d N |
| F3 | Low | CONFIRMED | B | `app.py:11` and `app.py:14` | `request["path"]` assumes the key exists and holds a string. | A request with a valid token but no `path` raises `KeyError`. A `None` path raises `AttributeError` on `.startswith`. Either way the handler crashes instead of returning 404. | Use `path = request.get("path")`, then `if not isinstance(path, str): return 404`. **Repro:** `app.handle({"token": "tok-rita"})`. **Expected:** `{"status": 404}`. **Observed (by trace):** `KeyError`. | a Y / b Y / c N / d N |

## Needs validation

- **S1, `auth.py:5`.** The staff bearer tokens (`tok-sam`, `tok-ola`) are hardcoded in source and can be guessed from staff first names.
  - **What settles it:** whether `_TOKENS` is a test fixture that gets replaced before production (as the in-memory `trips.py` suggests) or is shipped as the real store.
  - **If shipped:** this becomes a High or Critical security finding. Anyone with repo read access, or anyone who guesses `tok-<name>`, gets every rider's name and email.
- **S2, `trips.py:20`.** CSV formula injection.
  - **What settles it:** whether riders can set their own name or email, and could therefore make a field start with `=`, `+`, `-` or `@`.
  - **If they can:** the staff spreadsheet runs rider-controlled formulas. That crosses a boundary from rider to staff workstation.
- **S3, `trips.py:11`.** Trips are matched to a rider by display name (`ident[0]`), not by a stable ID.
  - **What settles it:** whether rider names are unique in production.
  - **If they are not:** two riders named "rita" see each other's trips.
- **S4, `context.md`.** The claim "7 tests pass" could not be checked. Running `python3 -m unittest test_app` in an isolated copy would settle it.

## Refuted

- **"A non-staff token can reach staff data."** Refuted. Every `/staff/...` path goes through `require_staff` at `app.py:14-18` before either dump runs. The only other route, `/trips`, returns `for_rider(ident[0])`. No path reaches `all_rows` or `as_csv` without the check.
- **"No token on a /staff route gives 403 instead of 401."** Refuted. `auth.current` runs first, at `app.py:8`, for every path, so the 401 is returned before the staff check.
- **"Tricky paths bypass the check."** Refuted. Paths like `/staff/../x`, `/STAFF/trips.json` or `/trips/../staff/trips.json` all fail the exact-equality matches and return 404. Path normalisation is not involved.
- **"Odd tokens crash `compare_digest`."** Refuted. `auth.py:13` encodes strings to bytes and maps any non-string to `b""`, so non-ASCII strings, `None` and integers all become 401. The test at `test_app.py:29-31` covers this case.
- **"Timing leak in the token loop."** Refuted as a finding. The early return leaks at most which slot matched, not any token bytes, and each comparison is constant-time.

## What holds up

- The order of checks (authenticate, then authorise, then route) matches the request exactly: 401 comes before 403.
- The staff gate covers both dump routes and any future `/staff/` path.
- Riders get copies of only their own trips. `dict(t)` copies prevent callers from mutating the shared store.
- Token comparison uses `hmac.compare_digest` on bytes, and bad token types are handled.

## Unverified claims

- **"7 tests pass."** Confirm by running the suite in an isolated copy.
- **The test-coverage gap in F2.** Confirm with the mutation described in the table.

## Questions for the author

1. Is `_TOKENS` a fixture? What replaces it in production?
2. Do riders set their own name or email?
3. Are rider names unique, or is there a rider ID?

## Decision-maker summary

The access control is correct for what was asked, so this can ship once the CSV export uses a proper CSV writer and the export tests assert the actual contents. Before production, confirm that the hardcoded token table in `auth.py` is replaced. If it ships as is, staff access to every rider's personal data depends on a guessable string.

## Owner summary

The rules about who can see what are built correctly: riders see only their own trips, and only staff can download everyone's. The staff spreadsheet download can scramble rows when a name contains a comma, and the automated tests would not notice if that download came back empty. Both are quick fixes. Separately, someone needs to confirm that the sample login keys in the code are replaced with real ones before launch.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "trips.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true},
    {"item": "production token/identity store", "status": "not_seen", "matters": true},
    {"item": "how rider names and emails are set", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "fictional example.test data; no real personal data supplied"},
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
      {"unit": "production token store", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "trips.py:20",
     "scenario": "A rider name or email containing a comma, quote or newline shifts the CSV columns, so staff read the wrong email or bike for that row.",
     "fix": "Build the CSV with csv.writer/DictWriter over io.StringIO.",
     "reproduction": "Append {'rider':'Lee, Ana','email':'a@example.test','bike':'B-1','km':1} to _TRIPS and call as_csv(); expect 4 columns in that row, observe 5.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py:17-18",
     "scenario": "all_rows() regresses to returning [] or only the caller's rows; the staff JSON dump is empty or partial and the suite stays green.",
     "fix": "Assert the JSON body contains rows for every rider, including rita and tomas with emails.",
     "reproduction": "In a scratch copy, change trips.py:15 to 'return []' and run the tests; expect a failure; by reading, all 7 still pass.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:11",
     "scenario": "A request with a valid token and no 'path' key raises KeyError (a None path raises AttributeError at app.py:14) instead of returning 404.",
     "fix": "path = request.get('path'); return 404 if it is not a str.",
     "reproduction": "Call app.handle({'token': 'tok-rita'}); expect status 404, observe KeyError by trace.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:5",
     "suspicion": "Staff bearer tokens are hardcoded in source and guessable as tok-<name>.",
     "unresolved_fact": "Whether _TOKENS is a test fixture replaced before production or shipped as the real store."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "trips.py:20",
     "suspicion": "CSV formula injection into staff spreadsheets.",
     "unresolved_fact": "Whether riders can set their own name or email to start with =, +, - or @."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "trips.py:11",
     "suspicion": "Trips are keyed by display name, so riders sharing a name would see each other's trips.",
     "unresolved_fact": "Whether rider names are unique in production."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "context.md",
     "suspicion": "The claim '7 tests pass' could not be checked.",
     "unresolved_fact": "The output of python3 -m unittest test_app run in an isolated copy."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A non-staff token can reach staff data.", "evidence": "app.py:14-18 runs require_staff on every /staff/ path before all_rows or as_csv; /trips returns only for_rider(ident[0])."},
    {"id": "C2", "candidate": "No token on a /staff route gives 403 instead of 401.", "evidence": "auth.current runs first for every path at app.py:8."},
    {"id": "C3", "candidate": "Path tricks bypass the staff check.", "evidence": "Routes use exact equality; any other path returns 404."},
    {"id": "C4", "candidate": "Odd tokens crash compare_digest.", "evidence": "auth.py:13 encodes to bytes or substitutes b''; test_app.py:29-31 covers this."},
    {"id": "C5", "candidate": "Timing leak in the token loop.", "evidence": "At most the matched slot leaks; each comparison is constant-time and no token bytes leak."}
  ]
}
```