**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session had no tools and no subagent. Nothing below was run; every result comes from reading and tracing the code.

VERDICT: **SHIP WITH FIXES**. The access control the request asks for traces correctly on every path, but the CSV export does not quote fields, and one malformed token crashes the handler instead of returning 401.

CONFIDENCE: **medium**. It is limited by the same-context review, by having no tools (so the "7 tests pass" claim is unverified), and by not having the HTTP layer or the production token store.

INPUTS LEDGER:
- Seen: request.md, context.md, `app.py`, `auth.py`, `trips.py`, `test_app.py`.
- Not seen: the test run output. This matters a little: the "7 pass" claim is unverified.
- Not seen: the HTTP layer that builds `{"path","token"}`. This matters: query strings, path normalisation and how the token is extracted all happen there.
- Not seen: the production token and trip stores. This matters: `auth.py` and `trips.py` look like fixtures (see S1).

COVERAGE:
- Checked: `app.py:handle` (every branch), `auth.py:current`, `auth.py:require_staff`, `trips.py` (all three functions), all 7 tests.
- Hostile inputs traced: token `None`, `""`, int, non-ASCII, lone surrogate. Paths `/staff`, `/STAFF/...`, `/trips/../staff/trips.json`, `/staff/other`, and a missing `path` key.
- Not checked: the HTTP adapter, the deployment config, and the real data sources.

SEATS AND GATE: Only the local same-context reviewer ran. The work contains rider names and emails, which are personal data, although here they are fixture data on `example.test`. Cross-vendor seats would be refused for real data and were not requested.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `trips.py:20-21` | CSV rows are built with an f-string, so no field is quoted or escaped. | A rider named `Smith, Jo` or `Jo "JJ" Smith`, or one whose name contains a newline, shifts the columns or splits the row, so the staff export misattributes emails. A name starting with `=`, `+`, `-` or `@` runs as a formula when staff open the file in a spreadsheet. | Write rows with `csv.writer` (QUOTE_MINIMAL) into an `io.StringIO`, and prefix formula-leading cells with `'`. **Test:** add a trip with rider `"a,b"` and assert that `csv.reader(io.StringIO(as_csv()))` yields rows of exactly 4 fields. This fails on the current code. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (traced) | B | `auth.py:15` | `token.encode("utf-8")` raises `UnicodeEncodeError` on a lone surrogate. That is not an `AuthError`, so `app.py:9` does not catch it. | A JSON body with `"token": "\ud800"` is accepted by `json.loads`. It produces an unhandled exception (a 500) instead of 401, which contradicts the intent of `test_an_odd_token_is_401_not_an_error`. | Use `encode("utf-8", "surrogatepass")`, or catch `UnicodeError` and treat the token as `b""`. **Repro:** `get("/trips", "\ud800")` should give 401; it raises instead. | a✓ b✓ c✗ d✗ |

## Needs validation

- **S1** (`auth.py:4`): The tokens are hardcoded and guessable (`tok-sam` and `tok-ola` grant staff access to every rider's PII). The unresolved fact is whether `auth.py` ships to production or is a test fixture. If it ships, this becomes Critical.
- **S2** (`app.py:13`, `trips.py:12`): Riders are matched to trips by display name (`ident[0]` == `t["rider"]`). The unresolved fact is whether rider names are unique in the real store. If two riders share a name, each sees the other's trips and email.
- **S3** (`app.py:11`): The handler assumes the adapter passes a normalised path without a query string. For example, `/staff/trips.json?x=1` returns 404, which is safe. The unresolved fact is the adapter's path handling.
- **S4** (tests): The tests were never seen failing. The mutations that would settle it are: delete the `auth.require_staff(ident)` call, and both `test_rider_cannot_export_*` should go red; delete the `except auth.AuthError` around `current`, and `test_no_token_is_401` should go red. By trace both would fail, but this was not run.

## Refuted

- **R1**: "A missing token on a /staff route might return 403 or leak data." Refuted: `auth.current` runs before path dispatch (`app.py:8-10`), so it returns 401.
- **R2**: "Path tricks bypass the staff check." Refuted: the export branches use exact `==` matches inside the `startswith("/staff/")` block. `/STAFF/...`, `/trips/../staff/...` and `/staff` all fall through to 404 with no data.
- **R3**: "A non-string token crashes the handler." Refuted: `auth.py:15` maps any non-string to `b""`, which matches no token, so it returns 401.
- **R4**: "Riders can mutate shared trip records through the returned rows." Refuted: `for_rider` and `all_rows` return `dict(t)` copies.

## Summary

WHAT HOLDS UP:
- 401 is returned before any routing.
- 403 is returned for any non-staff identity under `/staff/`.
- Riders only ever get rows filtered by their own identity.
- Token comparison uses `hmac.compare_digest`.
- The tests cover each 401 and 403 rule in the request, and the rider-isolation test asserts real behaviour (a non-empty result, and every row is Rita's).

UNVERIFIED CLAIMS:
- "7 tests in test_app.py pass": run `python3 -m unittest test_app`.
- The tests guard what they claim to: apply the S4 mutations in a scratch copy.

QUESTIONS FOR THE AUTHOR:
1. Is `auth.py`'s token table what production uses?
2. Is the rider name the unique account key?
3. Can riders choose their own display name, which affects F1's formula-injection risk?

DECISION-MAKER SUMMARY: The required access rules are implemented correctly. Fix the CSV quoting (F1) and the token-encoding crash (F2) before release, and confirm that the hardcoded tokens are not the production store (S1). If the tokens do ship as written, anyone who guesses `tok-sam` can download every rider's name and email.

OWNER SUMMARY: The rules for who may see which trips work as asked. The staff spreadsheet export can become garbled, or unsafe to open, if a rider's name contains certain characters, and one kind of malformed login crashes the request instead of rejecting it; both are small fixes. Before launch, someone should confirm that the built-in sample passwords are not what production actually uses.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "app.py, auth.py, trips.py, test_app.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true},
    {"item": "HTTP adapter building the request dict", "status": "not_seen", "matters": true},
    {"item": "production token and trip stores", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": true, "reason": "Rider names and emails are personal data (fixture values here); no external seats used."},
  "coverage": {
    "checked": [
      {"unit": "app.py", "kind": "file"}, {"unit": "app.py:handle", "kind": "function"},
      {"unit": "auth.py", "kind": "file"}, {"unit": "auth.py:current", "kind": "function"},
      {"unit": "auth.py:require_staff", "kind": "function"},
      {"unit": "trips.py", "kind": "file"}, {"unit": "trips.py:as_csv", "kind": "function"},
      {"unit": "test_app.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "HTTP adapter", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "trips.py:20-21",
     "scenario": "A rider name containing a comma, quote or newline corrupts the staff CSV columns; a name starting with = + - @ executes as a formula when staff open the export in a spreadsheet.",
     "fix": "Build the CSV with csv.writer and neutralise formula-leading cells with a leading apostrophe.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a trip with rider 'a,b'; parse as_csv() with csv.reader; expect 4 fields per row, observe 5."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:15",
     "scenario": "A token containing a lone surrogate (e.g. from JSON '\\ud800') raises UnicodeEncodeError, uncaught by app.py, giving a 500 instead of 401.",
     "fix": "Encode with errors='surrogatepass' or catch UnicodeError and treat the token as unknown.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "get('/trips', '\\ud800'); expect status 401, observe UnicodeEncodeError."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:4",
     "suspicion": "Hardcoded, guessable staff tokens grant access to all rider PII.",
     "unresolved_fact": "Whether auth.py's token table is used in production."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "app.py:13; trips.py:12",
     "suspicion": "Trips are matched by display name; duplicate names would expose another rider's trips and email.",
     "unresolved_fact": "Whether rider names are unique keys in the real store."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "app.py:11",
     "suspicion": "Routing depends on the adapter supplying a normalised, query-free path.",
     "unresolved_fact": "How the HTTP adapter builds request['path']."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "test_app.py",
     "suspicion": "Tests were never seen failing.",
     "unresolved_fact": "Whether removing auth.require_staff(ident) turns both test_rider_cannot_export_* red in a scratch copy."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "No token on a /staff route returns 403 or data.", "evidence": "auth.current runs before routing (app.py:8-10), so it returns 401."},
    {"id": "R2", "candidate": "Path variants bypass the staff check.", "evidence": "Exports use exact == matches inside the startswith('/staff/') guard; other variants fall to 404."},
    {"id": "R3", "candidate": "Non-string tokens crash the handler.", "evidence": "auth.py:15 maps non-str to b'', which matches no token, so it returns 401."},
    {"id": "R4", "candidate": "Returned rows alias the shared store.", "evidence": "for_rider and all_rows return dict(t) copies."}
  ]
}
```