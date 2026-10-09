# Adversarial Diagnostic Review: Pedalo ops API handlers

**VERDICT: REWORK.** `/staff/trips.csv` has no staff check, so any rider token downloads every rider's name and email. That breaks the request's 403 rule and leaks personal data. The four passing tests never touch that route.

**CONFIDENCE IN VERDICT: high.** The main finding comes from reading `app.py` directly. No tools were available, so nothing was run. Test results and mutation behaviour are inferred from reading the code.

## Pass 1: Reconstruct

The work implements `handle(request)` with three routes:
- `/trips` returns the caller's own trips.
- `/staff/trips.json` returns all trips.
- `/staff/trips.csv` returns all trips as CSV.

It authenticates with a static token table: an unknown or missing token gives 401. The request's invariants are that riders see only their own trips, every `/staff` route returns 403 to non-staff, and no token returns 401.

Load-bearing assumptions:
1. Every `/staff` route calls `auth.require_staff`.
2. `auth.current` rejects every invalid token type.
3. The rider name in the token table matches the `rider` key in the trip data.
4. The four tests cover the stated requirements (unstated).

Assumption 1 is false.

## COVERAGE

| Unit | Status |
|---|---|
| request.md | checked |
| context.md | checked |
| app.py | checked, every branch |
| auth.py | checked |
| trips.py | checked |
| test_app.py | checked |
| Test execution and mutation runs | not checked: no tools |

## FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | `app.py`, branch `if path == "/staff/trips.csv": return {"status": 200, "body": trips.as_csv()}` | The CSV export never calls `auth.require_staff(ident)`. The JSON branch directly above it does. | A rider calls `handle({"path": "/staff/trips.csv", "token": "tok-rita"})`. They get status 200 and a body containing `tomas,tomas@example.test,...`, which is another rider's name and email. The request requires 403. | Wrap the branch in the same `require_staff` try/except that returns 403. Better: guard once with `if path.startswith("/staff/")` before dispatch. Reproduce: `assert get("/staff/trips.csv","tok-rita")["status"] == 403`. This fails today. | y/y/y/y |
| 2 | Medium | CONFIRMED | `test_app.py`, the whole file | No test exercises `/staff/trips.csv`. Nothing checks rider→403, no-token→401 or staff→200 on that route, or that its body is scoped. The claim "4 tests pass" is true-but-irrelevant evidence. It is what let finding 1 through. | Any regression on the CSV route, or any new `/staff` route, ships green. | Add three tests: CSV with a rider token gives 403, CSV with no token gives 401, CSV with a staff token gives 200. Add a parametrized test asserting every `/staff/*` route returns 403 for `tok-rita`. | y/y/n/y |
| 3 | Medium | PROBABLE | `trips.py`, `as_csv` f-string | Fields are joined with `,` without quoting or escaping, and the `csv` module is not used. | A rider named `Smith, Jo` shifts every later column. A name or email starting with `=`, `+`, `-` or `@` runs as a formula when staff open the export in a spreadsheet (CSV injection). The current data is static, so this only bites once names come from riders. | Use `csv.writer`. Prefix cells that start with `= + - @ \t \r` with `'`. Reproduce: add a trip with rider `=HYPERLINK("http://x","a")` and inspect the output. | y/n/n/n |
| 4 | Medium | CONFIRMED | `auth.py`, `_TOKENS = {"tok-rita": ..., "tok-sam": ..., "tok-ola": ...}` | Bearer tokens, including two staff tokens, are hardcoded in source. | Anyone with read access to the repo or a build artifact can use `tok-sam` to pull the full personal-data export. Rotation requires a code deploy. | Load tokens from a secret store or env, store hashes only, and rotate the committed values. | y/y/n/n |
| 5 | Low | CONFIRMED | `app.py`, `path = request["path"]` | A missing `path` key raises `KeyError`. It is not handled. | A malformed request produces an uncaught exception (a 500 upstream) instead of 400 or 404. Data does not leak, because auth runs first. | Use `request.get("path")` and return 400 when it is absent. | y/y/n/n |

**Root-cause sibling search (finding 1):** I checked every branch of `handle`.
- `/trips` is scoped by `ident[0]`. Correct.
- `/staff/trips.json` enforces staff. Correct.
- `/staff/trips.csv` does not enforce staff. Bug.
- The 404 fallthrough is reached only after authentication.

The root cause is per-route opt-in authorization with no `/staff` prefix guard. Every future `/staff` route inherits the same risk. No other instance exists today.

**Security boundary (finding 1):**
- Principal: any authenticated non-staff rider.
- Input: path `/staff/trips.csv`.
- Failing control: the missing `auth.require_staff` call.
- Boundary crossed: rider → staff authorization.
- Resource: names and emails of all riders.

**Strongest defence of finding 1:** the CSV is "just a format" of data staff already see. This fails. The caller here is a rider, not staff, and the request explicitly names this route as staff-only. The finding stands.

## NEEDS VALIDATION

- **Unknown `/staff/*` paths return 404 to riders, not 403.** Settled by asking whether "a rider token on a /staff route gives 403" covers non-existent paths. A prefix guard (the fix for finding 1) resolves it either way.
- **Test mutation.** If `require_staff` is removed from the JSON branch, `test_rider_cannot_export_json` should go red. By reading it would, since rita would get 200. Settled by running that mutation in a scratch copy.

## REFUTED

- **Timing leak in `auth.current`:** it uses `hmac.compare_digest` per entry. The early return reveals at most the table position of a *valid* token, which the caller already holds. Not exploitable.
- **Non-string or empty token bypass:** `None`, bytes, ints and `""` all map to `b""`. That matches no key, so the call raises `AuthError` and returns 401. Holds.
- **Staff hitting `/trips` leaks data:** `for_rider("sam")` returns `[]`. No leak.
- **Shared mutable state:** each handler returns `dict(t)` copies, so callers cannot mutate `_TRIPS` through the JSON or rider responses.

## WHAT HOLDS UP

- Authentication runs before any routing, so every route needs a valid token and no-token returns 401 everywhere, including the CSV route.
- Rider scoping on `/trips` is correct.
- The JSON staff export enforces 403 correctly.
- Token comparison is constant-time.

## UNVERIFIED CLAIMS

- **"4 tests in test_app.py pass."** By reading, they should pass. Confirm by running `python -m unittest test_app`.

## QUESTIONS FOR THE AUTHOR

1. Should unknown `/staff/*` paths return 403 or 404 to riders?
2. Where will tokens and rider names come from in production, and can rider names contain commas or start with `=`?

## DECISION-MAKER SUMMARY

Do not deploy. The CSV staff export is open to any logged-in rider and exposes every rider's name and email. Add a single `/staff` prefix authorization guard plus CSV route tests, move tokens out of source, then re-review. If you ship as is, any rider can download the full personal-data export.

## OWNER SUMMARY

One of the two staff-only download links, the spreadsheet version, does not check whether the person is staff. Any logged-in rider can download every rider's name and email address. This must be fixed and tested before launch, and the passwords currently written into the code should be moved out and changed.

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
    {"item": "trips.py", "status": "seen", "matters": true},
    {"item": "test_app.py", "status": "seen", "matters": true}
  ],
  "coverage": {
    "checked": [
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py:current", "kind": "function"},
      {"unit": "auth.py:require_staff", "kind": "function"},
      {"unit": "trips.py", "kind": "file"},
      {"unit": "test_app.py", "kind": "file"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"}
    ],
    "not_checked": [
      {"unit": "test execution and mutation runs", "reason": "no_tools"}
    ]
  },
  "findings": [
    {
      "id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
      "location": "app.py handle(), branch path == \"/staff/trips.csv\"",
      "scenario": "handle({'path':'/staff/trips.csv','token':'tok-rita'}) returns 200 with all riders' names and emails; request requires 403",
      "fix": "Call auth.require_staff (return 403 on AuthError) before as_csv(); preferably a single path.startswith('/staff/') guard before dispatch; add CSV authz tests",
      "answers": {"a": true, "b": true, "c": true, "d": true},
      "reproduction": "assert app.handle({'path':'/staff/trips.csv','token':'tok-rita'})['status'] == 403  # fails today with 200",
      "security": true,
      "siblings_searched": {"searched": "every branch of app.handle (/trips, /staff/trips.json, /staff/trips.csv, 404 fallthrough)", "found": "only /staff/trips.csv lacks the check; root cause is per-route opt-in authz with no /staff prefix guard"},
      "boundary": {"principal": "authenticated non-staff rider", "input": "path /staff/trips.csv", "control": "auth.require_staff (missing)", "crossed": "rider -> staff authorization", "resource": "all riders' names and emails"}
    },
    {
      "id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "test_app.py (whole file)",
      "scenario": "No test touches /staff/trips.csv, so the F1 leak and future /staff regressions pass CI",
      "fix": "Add CSV tests for rider 403, no-token 401, staff 200, plus a parametrized test that every /staff route returns 403 to a rider",
      "answers": {"a": true, "b": true, "c": false, "d": true},
      "reproduction": "grep test_app.py for 'trips.csv': zero hits; positive control: 'trips.json' hits twice"
    },
    {
      "id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
      "location": "trips.py as_csv() f-string join",
      "scenario": "A rider name containing a comma corrupts columns; a name starting with '=' runs as a formula when staff open the CSV",
      "fix": "Use csv.writer and neutralize leading = + - @ tab CR",
      "answers": {"a": true, "b": false, "c": false, "d": false},
      "reproduction": "Add trip rider '=HYPERLINK(\"http://x\",\"a\")' or 'Smith, Jo' and inspect as_csv() output"
    },
    {
      "id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
      "location": "auth.py _TOKENS literal",
      "scenario": "Anyone with repo or artifact read access uses tok-sam to pull the full personal-data export",
      "fix": "Load hashed tokens from a secret store or env; rotate the committed tokens",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "handle({'path':'/staff/trips.json','token':'tok-sam'}) returns 200 using only values visible in source"
    },
    {
      "id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
      "location": "app.py: path = request[\"path\"]",
      "scenario": "A request with a valid token and no 'path' key raises an uncaught KeyError",
      "fix": "Use request.get('path') and return 400 when it is missing",
      "answers": {"a": true, "b": true, "c": false, "d": false},
      "reproduction": "app.handle({'token':'tok-rita'}) raises KeyError"
    },
    {
      "id": "NV1", "status": "needs_validation", "location": "app.py 404 fallthrough",
      "suspicion": "Riders get 404, not 403, on unknown /staff/* paths",
      "unresolved_fact": "Whether 'a /staff route' includes non-existent paths under /staff"
    },
    {
      "id": "NV2", "status": "needs_validation", "location": "test_app.py test_rider_cannot_export_json",
      "suspicion": "Test has not been shown to fail when the guard is removed",
      "unresolved_fact": "Result of deleting require_staff from the JSON branch in a scratch copy and running the tests"
    }
  ],
  "refuted": [
    {"id": "R1", "candidate": "Timing side channel in token check", "evidence": "hmac.compare_digest per entry; the early return reveals only the position of a token the caller already holds"},
    {"id": "R2", "candidate": "Non-string or empty token bypasses auth", "evidence": "Non-str and '' map to b'', which matches no key, so AuthError gives 401"},
    {"id": "R3", "candidate": "Staff calling /trips leaks data", "evidence": "for_rider('sam') returns []"},
    {"id": "R4", "candidate": "Callers can mutate _TRIPS via responses", "evidence": "for_rider and all_rows return dict copies"}
  ]
}
```