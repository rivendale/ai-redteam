**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools, so no code was run. Every finding below comes from reading the supplied source line by line.

VERDICT: **REWORK**. `/staff/trips.csv` has no staff check, so any rider token downloads every rider's name and email, which the request explicitly forbids.

CONFIDENCE: **medium**. The main defect is certain from the code. Confidence is limited by the same-context review, no ability to run the tests or mutate code, and not knowing whether `_TOKENS` is the production token store.

INPUTS LEDGER:
- Seen: request.md, context.md, app.py, auth.py, trips.py, test_app.py.
- Not seen: test run output. The "4 tests pass" claim is unverified, but it doesn't change the verdict because no test touches the defective route.
- Not seen: how tokens are provisioned in production. This matters for S1.

COVERAGE:
- Checked: `app.py:handle` (every branch); `auth.py:current`, `auth.py:require_staff`, `auth.py:_TOKENS`; `trips.py:for_rider`, `all_rows`, `as_csv`; all 4 tests in test_app.py, each traced against the code.
- Not checked: runtime behaviour, deployment and routing layer, production token source.

SEATS AND GATE: Local same-context review only. The work contains personal data (names and emails in fixtures, and real ones in production) and credentials (`_TOKENS`), so the sensitivity gate is set and cross-vendor seats are refused. No subagent was available in this session.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B | `app.py:20-21` | The `/staff/trips.csv` branch never calls `auth.require_staff`. Only the JSON branch (lines 15-18) does. | Any authenticated rider sends `{"path": "/staff/trips.csv", "token": "tok-rita"}`. Instead of the 403 the request requires, they get 200 and a CSV of every rider's name, email, bike and km. That is a personal-data breach. | Enforce staff once for the whole prefix: `if path.startswith("/staff/"):` then `require_staff`, returning 403 on failure, placed before any staff route. Add the test `assertEqual(get("/staff/trips.csv", "tok-rita")["status"], 403)`. It fails on the current code (returns 200). | a✓ b✓ c✓ d✓ |
| F2 | Medium | CONFIRMED | B | `test_app.py` (whole file) | No test covers `/staff/trips.csv` at all, and no test sends a no-token request to a `/staff` route. The "4 tests pass" in context.md gives false assurance: the suite is green while the request's 403 rule is broken. | A future refactor removes a staff check on any route and CI stays green. That is exactly how F1 shipped. | Add rider→403 and staff→200 tests for both `.json` and `.csv`, plus a no-token→401 test on one `/staff` route. Then confirm the rider-CSV test goes red on the current code. | a✓ b✓ c✗ d✓ |
| F3 | Low | CONFIRMED | B | `trips.py:21-22` | `as_csv` joins fields with f-strings and no quoting or escaping. | A rider name or email containing a comma, quote or newline shifts or splits columns, and the export is silently corrupted. | Use `csv.writer` over an `io.StringIO`. Reproduce with a row whose rider is `"a,b"`: the output has 5 columns instead of 4. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED | B | `app.py:22` | Unknown `/staff/*` paths return 404 to riders. The request says a rider token on a /staff route gives 403. | A rider calling `/staff/anything` gets 404 instead of 403. This is minor spec drift and leaks nothing, but per-route checks are also the root cause of F1. | The prefix guard in F1's fix resolves this too. Test: rider on `/staff/x` → 403. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | B | `app.py:11` | `request["path"]` raises `KeyError` if `path` is missing. The 401 path is handled; this one is not. | A malformed request with a valid token and no path crashes the handler (an unhandled exception or 500, depending on the caller). | Use `request.get("path")` and return 400 or 404. Test: `app.handle({"token": "tok-sam"})` should not raise. | a✓ b✓ c✗ d✗ |

## Needs validation
- **S1** (`auth.py:5`): Bearer tokens, including two staff tokens, are hardcoded in source. If this is the production token store, anyone with read access to the repo can export all personal data. That would be Critical. Unresolved fact: whether `_TOKENS` is a test fixture or what production actually uses.
- **S2** (`trips.py:21`): CSV formula injection. If rider names can be set by riders (for example `=HYPERLINK(...)`), staff opening the export in a spreadsheet would execute the formula. Unresolved fact: whether `rider` and `email` values are rider-controlled in production.

## Refuted
- **"No token on /staff routes might bypass 401."** `auth.current` runs for every path at `app.py:8-10` before any routing, so a missing or unknown token always returns 401.
- **"`current(None)` or a non-str token could match."** Both map to `b""` (`auth.py:16`), and no known token is empty, so `AuthError` is raised.
- **"Riders could see others' trips via /trips."** `for_rider(ident[0])` filters on the identity derived from the token, not on request input.

## What holds up
- Authentication happens before routing, so unknown and missing tokens get 401 on every route.
- Token comparison uses `hmac.compare_digest`.
- `/trips` is correctly scoped to the caller.
- The JSON export's staff check is correct.
- `for_rider` and `all_rows` return copies, so callers can't mutate the store.
- `test_rider_sees_only_their_own_trips` would go red if the filter were removed, because tomas's row would appear (traced, not run).

## Unverified claims
- "4 tests in test_app.py pass." Confirm by running `python3 -m unittest test_app`. A pass does not change the verdict, since F1 is untested.

## Questions for the author
1. Is `_TOKENS` the production token store? (This settles S1.)
2. Was leaving `/staff/trips.csv` without a staff check intentional, for example because it is protected by an upstream gateway? If so, where is that enforced and tested?

## Decision-maker summary
Do not deploy. Any rider can download every rider's name and email through the CSV export, because that route skips the staff check and no test covers it. Fix it with a single `/staff` prefix guard plus tests for both export formats, then confirm the token store isn't hardcoded.

## Owner summary
The new system has a gap that would let any ordinary rider download the names and email addresses of all other riders. The automated tests passed only because none of them checked that download. The fix is small, but it must be made and tested before the system goes live.

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
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "production token provisioning", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Rider names and emails (personal data) and bearer tokens in source; no external seats."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"},
      {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:current", "kind": "function"},
      {"unit": "auth.py:require_staff", "kind": "function"},
      {"unit": "auth.py:_TOKENS", "kind": "config"},
      {"unit": "trips.py", "kind": "file"},
      {"unit": "trips.py:as_csv", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "runtime test execution", "reason": "no tools in this session"},
      {"unit": "production token source", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:20-21",
     "scenario": "A rider token on GET /staff/trips.csv returns 200 with every rider's name and email instead of 403.",
     "fix": "Guard every /staff/ path with auth.require_staff before routing; return 403 on AuthError.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "app.handle({'path': '/staff/trips.csv', 'token': 'tok-rita'}); expect status 403, observe 200 with all rows."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_app.py",
     "scenario": "No test exercises /staff/trips.csv or no-token on /staff, so the suite passes while the 403 rule is broken.",
     "fix": "Add rider->403 and staff->200 tests for .json and .csv, and a no-token->401 test on a /staff route.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add assertEqual(get('/staff/trips.csv', 'tok-rita')['status'], 403); it fails on current code."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "trips.py:21-22",
     "scenario": "A field containing a comma, quote or newline corrupts the CSV columns.",
     "fix": "Write rows with csv.writer into io.StringIO.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a trip with rider 'a,b'; the CSV line has 5 fields instead of 4."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:22",
     "scenario": "A rider token on an unknown /staff/ path gets 404, not the 403 the request specifies.",
     "fix": "Prefix guard from F1 returns 403 for any /staff/ path for non-staff.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "app.handle({'path': '/staff/x', 'token': 'tok-rita'}); expect 403, observe 404."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "app.py:11",
     "scenario": "A request with a valid token but no 'path' key raises KeyError.",
     "fix": "Use request.get('path') and return 400 or 404 when missing.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "app.handle({'token': 'tok-sam'}); expect a status dict, observe KeyError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:5",
     "suspicion": "Staff bearer tokens hardcoded in source would let anyone with repo access export all personal data.",
     "unresolved_fact": "Whether _TOKENS is the production token store or a test fixture."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "trips.py:21",
     "suspicion": "CSV formula injection if rider names or emails begin with =, +, - or @.",
     "unresolved_fact": "Whether rider and email values are rider-controlled in production."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "A missing token on /staff routes bypasses the 401.",
     "evidence": "auth.current runs for every path at app.py:8-10 before routing."},
    {"id": "C2", "candidate": "A None or non-str token could match a known token.",
     "evidence": "auth.py:16 maps it to b'', and no known token is empty, so AuthError is raised."},
    {"id": "C3", "candidate": "Riders could read other riders' trips via /trips.",
     "evidence": "for_rider(ident[0]) uses the token-derived identity, not request input."}
  ]
}
```