# Adversarial Diagnostic Review: Pedalo ops API handlers

**VERDICT: SHIP WITH FIXES.** The access control the request asks for holds on every path I traced. The staff CSV export, though, does no escaping on personal data, and the tests leave one stated requirement and the export contents unchecked.

**CONFIDENCE IN VERDICT: medium.** I had no tools, so nothing was run. Every behavioural claim below comes from reading the code and from known Python semantics. "7 tests pass" is unverified, and no test has been seen to fail.

## Pass 1: Reconstruct

The work implements `handle(request)`:
- Any request without a valid token gets 401.
- `/trips` returns the caller's own trips.
- Anything under `/staff/` returns 403 unless the caller's role is staff.
- Staff get a JSON dump and a CSV dump of all trips, including names and emails.

For this to be correct, these must hold:
1. Authentication runs before any routing.
2. Every data-returning `/staff` route sits inside the role check.
3. `auth.current` never raises anything other than `AuthError`.
4. Rider name is a unique identity key. This is unstated.
5. CSV field values never contain `,`, `"`, newlines or formula prefixes. This is unstated.
6. The hardcoded token table and in-memory trips are stand-ins for a real store. This is unstated.

## COVERAGE

| Unit | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| app.py | checked: every branch traced |
| auth.py | checked |
| trips.py | checked |
| test_app.py | checked by reading. Not run (no tools), and no mutation testing was possible. |

## FINDINGS, ordered by severity

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (code) | `trips.py` `as_csv`, the f-string row builder | Fields are joined with `,` and no quoting, escaping or formula neutralisation. | **Comma:** a rider named `Smith, Jr.` produces 5 columns, so `email` holds ` Jr.` and every later column shifts.<br>**Newline:** a name containing `\n` injects a forged row into the staff export.<br>**Formula:** a name starting with `=`, `+`, `-` or `@` (e.g. `=HYPERLINK(...)`) runs as a formula when staff open the PII export in a spreadsheet. | Write with `csv.writer` (QUOTE_MINIMAL or QUOTE_ALL). Prefix any cell starting with `= + - @ \t \r` with `'`.<br>**Repro:** add `{"rider":"a,b","email":"x@y","bike":"B","km":1}` to `_TRIPS`, then `next(csv.reader(io.StringIO(as_csv()).readlines()[-1:]))` has 5 fields, not 4. | a yes, b yes, c no (harm needs special-character names; whether riders set their own names is not in the material), d no |
| 2 | Low | CONFIRMED (code + Python semantics) | `auth.py` `current`, `token.encode("utf-8")` | A `str` token with a lone surrogate raises `UnicodeEncodeError`, which is not an `AuthError`. `handle` lets it escape as a crash or 500 instead of 401. That contradicts the intent of `test_an_odd_token_is_401_not_an_error`. A JSON body `{"token":"\ud800"}` decoded by `json.loads` produces exactly this. | Client sends a token with a lone surrogate. The handler raises instead of returning 401. | Wrap the encode: `except UnicodeError: raise AuthError`. Or use `errors="surrogatepass"`.<br>**Repro:** `app.handle({"path":"/trips","token":"\ud800"})` raises. | a yes, b yes, c no, d no |
| 3 | Low | CONFIRMED (code) | `test_app.py` | Gaps in what the tests check, listed below this table. | See list below. | Add `assertEqual(get("/staff/trips.json", None)["status"], 401)` and the same for `.csv`. Assert the JSON body contains `tomas` and that every row has `email`. Add a test that a CSV with a comma in a name round-trips through `csv.reader`. | a yes, b yes, c no, d no |

Test gaps behind finding 3:
- The request's "no token gives 401" rule is never tested on a `/staff` route. A refactor that runs the role check before authentication, returning 403 for a missing token, stays green.
- `test_staff_can_export_json` asserts status only. A mutant `all_rows: return []` passes the whole suite.
- No test feeds the CSV to a real CSV parser.

## NEEDS VALIDATION

- **Hardcoded, guessable credentials (`auth.py` `_TOKENS`).** If this table, or anything like it, ships to production, anyone with repo read access holds `tok-sam` and can pull the full PII export. To settle it: what is the production token source, and are these fixtures excluded from the deployed build?
- **Identity keyed on display name (`app.py` `trips.for_rider(ident[0])`, matched against `t["rider"]`).** If two accounts can share a name, each sees the other's trips and email. To settle it: is `name` a unique, immutable account ID in the real identity store?
- **Source of rider names.** This decides whether finding 1 is attacker-reachable, which would raise it to High or Critical as a security issue. The lower-trust principal would be the rider, the input their name, and the failing control the absent CSV escaping. The boundary crossed is rider data reaching a staff workstation, and the resource is the staff export. To settle it: can riders set or edit their own display name?
- **Audit trail on PII exports.** `/staff/*.csv` and `.json` log nothing about who exported. Not requested, but likely expected for personal data. To settle it: does an org policy require export logging?

## REFUTED

- **Prefix or traversal bypass of `/staff`.** Data is served only on exact-match paths nested inside the `startswith("/staff/")` role check. `/staff`, `//staff/...`, `/STAFF/...` and `/staff/../x` all reach 404 or 403 and never data.
- **Unauthenticated access.** `auth.current` runs before any routing. `None`, an int, bytes and `""` all map to `b""`, which matches no token, so the result is 401.
- **Non-ASCII token crash.** `"tök"` encodes to bytes, and `compare_digest` on bytes of unequal length simply returns False.
- **Staff reading another rider's trips via `/trips`.** `for_rider("sam")` returns `[]`, with no leak.
- **Shared mutable state.** Both `for_rider` and `all_rows` return `dict` copies.
- **Token timing leak.** The early return reveals only which entry matched, after a constant-time comparison. Not exploitable.
- **Prompt injection in the work.** None found.

## WHAT HOLDS UP

- The 401 and 403 split matches the request on every route.
- The role check covers every staff data path.
- Token comparison is constant-time and type-safe for non-strings.
- The rider-scoping test would catch a leak of other riders' rows, because `all()` over a body that includes `tomas` fails.

## UNVERIFIED CLAIMS

- "7 tests pass." There are 7 test methods. Confirm by running `python -m unittest test_app`.
- No test has been shown to fail. Mutate `require_staff` to a no-op, and separately make `all_rows` return `[]`, in a scratch copy. The first should go red; the second, as finding 3 shows, will not.

## QUESTIONS FOR THE AUTHOR

1. Can riders set their own display name?
2. Is `name` unique per account?
3. What replaces `_TOKENS` in production?

## DECISION-MAKER SUMMARY

The access control is sound and the request is met. Before production, fix the CSV export to quote fields and neutralise formulas, catch encoding errors in token parsing, and add the missing staff-401 and export-content tests. The risk if you ship as is: a rider name containing commas, newlines or a formula corrupts or weaponises the staff PII export. That risk becomes serious if riders choose their own names or if the hardcoded tokens reach production.

## OWNER SUMMARY

The new service correctly keeps riders out of staff-only data and makes sure riders only see their own trips. The spreadsheet export of rider names and emails needs a small fix so that unusual names cannot break it or run hidden spreadsheet commands when staff open it. A few extra tests should be added, and the sample login tokens in the code must not be used for the live system.

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
      {"unit": "app.py handle", "kind": "function"},
      {"unit": "auth.py current/require_staff", "kind": "function"},
      {"unit": "trips.py for_rider/all_rows/as_csv", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation testing", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "trips.py as_csv row f-string",
      "scenario": "A rider name containing a comma, quote or newline misaligns columns or injects rows in the staff PII export; a name starting with = + - @ executes as a spreadsheet formula when staff open the file.",
      "fix": "Use csv.writer with quoting; prefix cells starting with = + - @ \\t \\r with a single quote; add a round-trip test via csv.reader.",
      "reproduction": "Append {'rider':'a,b','email':'x@y','bike':'B','km':1} to _TRIPS; parse the last line of as_csv() with csv.reader -> 5 fields instead of 4.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "auth.py current, token.encode('utf-8')",
      "scenario": "A token string with a lone surrogate (e.g. from a JSON body with \\ud800) raises UnicodeEncodeError, which escapes handle as a crash instead of 401.",
      "fix": "Catch UnicodeError and raise AuthError, or encode with errors='surrogatepass'.",
      "reproduction": "app.handle({'path':'/trips','token':'\\ud800'}) raises UnicodeEncodeError.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_app.py",
      "scenario": "No test checks no-token on /staff routes returns 401, and the JSON export test asserts status only; reordering the role check before authentication, or all_rows returning [], keeps the suite green.",
      "fix": "Add no-token 401 tests for /staff/trips.json and /staff/trips.csv; assert JSON body contents including other riders and email fields.",
      "reproduction": "In a scratch copy change all_rows to return []; run python -m unittest test_app; all 7 tests still pass.",
      "answers": {"a": true, "b": true, "c": false, "d": false}
    },
    {
      "id": "NV1", "status": "needs_validation", "location": "auth.py _TOKENS",
      "suspicion": "Hardcoded guessable staff tokens would allow any repo reader to export all rider PII if shipped.",
      "unresolved_fact": "What is the production token source, and are these fixtures excluded from deployment?"
    },
    {
      "id": "NV2", "status": "needs_validation", "location": "app.py trips.for_rider(ident[0]); trips.py for_rider",
      "suspicion": "Identity keyed on display name; duplicate names would expose another rider's trips and email.",
      "unresolved_fact": "Is name a unique, immutable account identifier?"
    },
    {
      "id": "NV3", "status": "needs_validation", "location": "trips.py as_csv (source of rider field)",
      "suspicion": "If riders control their names, F1 becomes a rider-to-staff CSV formula injection on a PII export.",
      "unresolved_fact": "Can riders set or edit their own display name?"
    },
    {
      "id": "NV4", "status": "needs_validation", "location": "app.py /staff branch",
      "suspicion": "PII exports leave no audit record of who exported.",
      "unresolved_fact": "Does policy require logging of personal-data exports?"
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Path prefix/traversal bypass of /staff role check", "evidence": "Data returned only on exact-match paths nested inside the startswith('/staff/') role check; variants hit 403/404."},
    {"id": "R2", "candidate": "Unauthenticated access", "evidence": "auth.current runs before routing; None/int/bytes/'' map to b'' and match no token, giving 401."},
    {"id": "R3", "candidate": "Non-ASCII token crashes compare_digest", "evidence": "Token is encoded to bytes first; compare_digest on unequal-length bytes returns False."},
    {"id": "R4", "candidate": "Staff or rider sees others' trips via /trips", "evidence": "for_rider filters on the caller's own name; staff get []."},
    {"id": "R5", "candidate": "Token timing leak", "evidence": "Per-entry comparison is constant-time; the early return reveals only the match position."}
  ]
}
```