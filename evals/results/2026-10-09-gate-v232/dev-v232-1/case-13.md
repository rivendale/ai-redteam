# Redteam review: `import_customers.py` and `fixtures/customers.csv`

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools and no subagent, so I reviewed the work myself. I traced every finding by reading the code; I ran nothing.

VERDICT: **REWORK.** The job writes every invalid row's full record, including the national ID number, into the error log. It also aborts partway through a production nightly run on errors it should count or survive.

CONFIDENCE: **medium.** Three things limit it:
- This is a same-context review with no tools, so I traced the code but executed nothing.
- I did not have the billing `sink`, the logging configuration or the caller.
- The cross-vendor seats were refused, so there is no second or third opinion.

INPUTS LEDGER:

| Item | Status | Matters |
|---|---|---|
| `request.md` (original request) | seen | — |
| `context.md` | seen | — |
| `import_customers.py` | seen | — |
| `fixtures/customers.csv` | seen | — |
| The billing `sink` implementation (error types, retries, idempotency) | not supplied | **yes**: decides the severity of F2 and F5 and whether reruns double-bill |
| Logging config and destination (who can read `customer_import` logs, retention) | not supplied | **yes**: decides how far F1 spreads |
| The caller or scheduler (how `(ok, failed)` is reported, exit code, alerting) | not supplied | **yes**: the request requires invalid rows to be "reported" |
| Tests | none exist | yes (F8) |
| Billing schema (which fields billing needs) | not supplied | yes (S2) |
| Git history (secrets or PII in earlier commits) | not openable (no tools) | yes, if the fixture holds real data (S1) |

COVERAGE:
- **Scope:** the whole work (2 files).
- **Checked:**
  - `request.md`, `context.md`, `import_customers.py`, `fixtures/customers.csv`
  - the functions `parse_row` and `import_file`
  - the requirement "invalid rows counted and reported"
  - the requirement "loads each valid row"
  - the assumption that the fixture is synthetic
- **Not checked:**
  - sink, logging config, caller: not supplied
  - git history: no tools
  - a byte-level scan for zero-width, bidi or look-alike characters: no tools; I read the text visually and found nothing
  - executing any reproduction: no tools

SEATS AND GATE:
- **Sensitivity gate: sensitive.** The context describes `fixtures/customers.csv` as "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)", and the code handles SSNs.
- **Both cross-vendor seats were REFUSED,** even though the team agreement calls for them. A second opinion is not a reason to send national ID data to another vendor. If the team confirms the fixture is fully synthetic (S1), the seats could be re-run on a version with the fixture removed.
- **Ran:** the same-context self-review only. No subagent was available.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (trace) | B | `import_customers.py` `import_file`, `log.error("could not import row %s: %s", dict(row), e)` | The full raw row is logged for every rejected row: name, email, phone, **SSN** and plan. | Any row fails validation (for example plan `gold`, or a missing email). The nightly job writes that customer's SSN in plaintext to the error log, where anyone with log access can read it, along with any log shipper or aggregator and its retention. F4 makes this happen for every row in the file. | **Fix:** log only the line number (`reader.line_num`) and the id, plus the reason. Never log `ssn`, `email`, `phone` or `name`. Add a test asserting that no SSN pattern appears in the captured logs. **Repro:** create a CSV with header `id,name,email,phone,ssn,plan` and one row `9,A B,a@x.test,555-0100,900-11-2222,gold`. Run `import_file(path, rows.append)` under pytest's `caplog`. Expected: the log has no `900-11-2222`. Observed: the log message contains `'ssn': '900-11-2222'`. | a✔ b✔ c✔ d✔ |
| F2 | High | CONFIRMED (trace) | B | `import_customers.py` `import_file`, `except (ValueError, KeyError)` around `sink(...)` | Any exception from the sink other than ValueError or KeyError escapes. That includes timeouts, connection errors and HTTP errors. The run aborts mid-file, nothing is returned, the remaining valid rows are never loaded, and the rows before the failure are already committed. | Billing has a transient outage at row 2,000 of 10,000. The job dies with a traceback, 8,000 valid customers are never loaded that night, and no invalid count is reported. If the operator reruns the job, rows 1 to 2,000 are sent again. | **Fix:** catch sink failures separately from validation failures and count them as `sink_failed`. Retry with a bounded backoff, continue with the rest of the file, and return all three counts. Make loads idempotent on `id` before allowing reruns. **Repro:** use a sink that raises `ConnectionError` on its 2nd call and run it against the fixture. Expected: rows 3 to 5 are attempted and counts are returned. Observed: `ConnectionError` propagates out of `import_file`, rows 3 to 5 are never offered, and there is no return value. | a✔ b✔ c✔ d✔ (see note) |
| F3 | High | CONFIRMED (trace) | B | `import_customers.py` `import_file`, `for row in csv.DictReader(f)` with `open(path, newline="")` | Decoding and CSV parse errors are raised by the iterator, which sits **outside** the `try`. `open` has no `encoding=`, so the encoding depends on the locale. One bad line aborts the whole job instead of being counted as invalid. | Someone exports the file from a spreadsheet in Windows-1252, and a name contains `é`. On a UTF-8 host, `UnicodeDecodeError` kills the run at that line. A field over the csv field size limit raises `csv.Error` with the same result. | **Fix:** pass `encoding="utf-8-sig"` explicitly (or the agreed encoding). Count undecodable or unparseable lines as invalid, or fail fast before loading anything. Do not fail halfway. **Repro:** write the header, then the bytes `b"6,Jos\xe9 R,j@x.test,555-0101,,pro\n"`, then a valid row. Expected: `failed==1` and the valid row is loaded. Observed: `UnicodeDecodeError` escapes and the trailing valid row is not loaded. | a✔ b✔ c✔ d✔ (see note) |
| F4 | High | CONFIRMED (trace) | B | `import_customers.py` `parse_row` `int(row["id"])` together with `except (ValueError, KeyError)` | A header mismatch turns every row into an "invalid row" instead of failing the job. A UTF-8 BOM makes the first key `"\ufeffid"`, and `newline=""` with default encoding does not strip it. A renamed column (`Email`) has the same effect. Each row is also logged with full PII (F1). | Someone re-saves the file with "CSV UTF-8" in a spreadsheet, which adds a BOM. The email and plan checks pass, then `row["id"]` raises KeyError, which is caught. The result is `(0, N)`: no customer is loaded, and N SSNs go into the log. | **Fix:** open with `utf-8-sig`. Before the loop, compare `reader.fieldnames` to the expected header and abort the job with no load if they differ. Do not catch KeyError per row. **Repro:** encode the fixture as `utf-8-sig` and run the import. Expected: the job is rejected for a bad header, or `(5, 0)`. Observed: `(0, 5)` and 5 log lines, each containing an SSN. | a✔ b✔ c✔ d✔ |
| F5 | Medium | CONFIRMED (trace) | B | `import_customers.py` `import_file`, where `sink(parse_row(row))` shares one `try` | Billing rejections that raise ValueError or KeyError are counted as invalid **input** rows, and they are logged with PII. | Billing rejects a valid customer with `ValueError("duplicate")`. The report says the CSV had a bad row, so someone investigates the data instead of the billing system. | **Fix:** call `parse_row` in its own `try`, and the sink in another with separate counters. **Repro:** use a sink that raises `ValueError("rejected")` for id 2. Expected: a separate sink-failure count. Observed: `(4, 1)`, with row 2 reported as invalid input. | a✔ b✔ c✘ d✘ |
| F6 | Medium | CONFIRMED (trace) | B | `import_customers.py` `import_file`, no duplicate handling | Duplicate `id`s are both passed to the sink and both counted as loaded. | The source file contains id 7 twice with different plans. Billing receives two records, or the later one overwrites the first, depending on the sink. The report shows two successes. | **Fix:** track the ids already seen and count repeats as invalid (or follow a defined policy). **Repro:** create a CSV with two `id=1` rows and run `import_file` with a list sink. Expected: a duplicate is flagged. Observed: `ok==2` and the sink receives two records. | a✔ b✔ c✘ d✘ |
| F7 | Medium | CONFIRMED | B | Repository (no test file); `fixtures/customers.csv` | There are no tests. The fixture has **no invalid row**, so the invalid-row path, the main requirement of "counted and reported", has never run. Row 4's empty SSN is accepted. | Every defect above ships to production unnoticed. Any future test that only uses this fixture passes with `(5, 0)` and proves nothing about counting failures. | **Fix:** add tests with invalid rows (bad email, unknown plan, non-integer id), a duplicate, a BOM file and a failing sink. Assert the counts and that the logs are free of PII. Confirm each test goes red against the current code. **Repro:** add the F1 test. It fails today, which shows the test suite has a gap. | a✔ b✔ c✘ d✔ |
| F8 | Low | CONFIRMED (trace) | B | `import_customers.py` `parse_row` email check | The email is not stripped. `"@"` alone and `" a@b "` both pass. The name and phone are not validated at all. | A value with a stray space or a junk value like `@` reaches billing as a "valid" email. | **Fix:** strip the value and require a non-empty local part and a domain containing a dot. **Repro:** a row with email `"@"` and plan `pro`. Expected: counted invalid. Observed: `ok` increments and the sink gets `email="@"`. | a✔ b✔ c✘ d✘ |

**Severity note for F2 and F3.** I treated "Critical needs a, b and c" as a necessary condition, not a sufficient one. Both F2 and F3 fail loudly with a visible traceback; they do not silently corrupt data. They rise to Critical only if reruns double-bill, which depends on whether the sink is idempotent (S3).

**F1 sibling search.**
- **Security finding:** yes.
- **Boundary:**
  - Principal: anyone with read access to the application logs or the log pipeline.
  - Input: none needed; the data is pushed to them.
  - Failed control: no masking or minimization before logging.
  - Boundary crossed: from the customer data import into the operational log stream.
  - Resource: SSNs, emails, phones and names.
- **What I searched:** every `log` call, which turned out to be the only one, and every exception message that reaches the log.
  - `int()`'s ValueError echoes only the id.
  - KeyError echoes only the column name.
  - Sink exception messages could echo the payload, which is S4.
  - Uncaught tracebacks from F2 and F3 could carry `row` in their locals if an error tracker captures locals, which is S5.

**F2, F3 and F4 sibling search.** These are separate locations that share one root cause: errors are not classified as "row invalid", "sink failed" or "file unusable". I searched every exception source in `import_file`: the `open` call, the iterator, `parse_row` and the sink. All of them are listed above. None is a security finding.

## NEEDS VALIDATION

- **S1. Is the fixture derived from real people?** The context says "a copy of real-format customer records". The values look synthetic: `example.test` addresses, phone numbers in the reserved 555-01xx range, and SSNs in the 900 range. One of them (`900-88-4521`) is in a valid ITIN range, though. **What would settle it:** the fixture's origin. If it is real, it is a Critical breach that is now in git history, and the fix needs a history rewrite and an incident process, not just a file deletion.
- **S2. Field minimization.** `name` and `phone` are dropped silently, while `ssn` is forwarded to billing. **What would settle it:** the billing schema. If billing needs name and phone, this is drift from "loads each valid row". If billing does not need the SSN, it should not be sent.
- **S3. Rerun safety.** **What would settle it:** whether the sink upserts on `id` or inserts blindly. This decides whether F2 or F3 followed by a rerun creates duplicate billing records.
- **S4. Sink exception messages.** **What would settle it:** whether the sink's ValueError or KeyError messages include the payload. If they do, F1 also covers the `%s` of `e`.
- **S5. Error tracker.** **What would settle it:** whether production uses Sentry or a similar tool that captures frame locals. If it does, the `row` in an uncaught traceback carries the SSN.
- **S6. "Reported."** **What would settle it:** what the caller does with `(ok, failed)`. Right now the only "report" is the PII-laden error log. If the caller ignores the return value, nobody is told about invalid rows.
- **S7. Empty SSN accepted.** Row 4 loads with `ssn=None`. **What would settle it:** whether a missing SSN makes a row invalid under the business rules.

## REFUTED

- **R1.** Candidate: a short row makes `int(None)` raise TypeError, which escapes. Refuted because `id` is the first column, so a non-blank short row always has it, and DictReader skips blank lines. The missing email or plan is caught as ValueError first.
- **R2.** Candidate: text inside the work addresses the reviewer. Refuted: none was found in either file on a visual read. A byte-level scan was not possible.

## WHAT HOLDS UP

- The plan allow-list is strict and correct for the values given.
- The id is coerced to `int`, so a non-numeric id is counted as invalid.
- The email is lowercased.
- `newline=""` is correct for the csv module.
- The per-row `try` does keep one bad *validated* row from stopping the run.
- The code is small and readable, and the fix scope is contained to `import_file`.

## UNVERIFIED CLAIMS

- The docstring says the job imports "into the billing system". The sink is not supplied; confirm it by reading the sink's code.
- The fixture is "real-format". Confirm its origin (S1).

## QUESTIONS FOR THE AUTHOR

1. Is the fixture synthetic or copied from real customers?
2. Does the sink upsert on `id`, and what exceptions does it raise?
3. Where do `customer_import` logs go, and who can read them?
4. Does billing need name, phone and SSN?

## DECISION-MAKER SUMMARY

Do not schedule this job yet. As written, every rejected row puts a customer's SSN into the logs, and a byte-order mark alone would do that for the entire file. A billing hiccup or one oddly encoded line also stops the nightly load partway through. Fix F1 to F4 and add tests with invalid rows before production; proceeding now risks a reportable personal-data exposure and partial loads that may double-bill on rerun.

## OWNER SUMMARY

The customer import is not safe to run in production yet. When it finds a bad record, it copies that customer's full details, including their social security number, into the system logs. It can also stop halfway through the night's import if the billing system briefly fails or the file is saved in a slightly different format.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "import_customers.py", "status": "seen", "matters": true},
    {"item": "fixtures/customers.csv", "status": "seen", "matters": true},
    {"item": "billing sink implementation", "status": "not_seen", "matters": true},
    {"item": "logging configuration and destination", "status": "not_seen", "matters": true},
    {"item": "caller/scheduler handling of (ok, failed)", "status": "not_seen", "matters": true},
    {"item": "billing schema", "status": "not_seen", "matters": true},
    {"item": "git history", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor-seat-2", "status": "refused", "cross_vendor": true},
    {"vendor": "cross-vendor-seat-3", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Fixture is described as a copy of real-format customer records including national ID numbers, and the code handles SSNs; no cross-vendor reviewer may receive it."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "import_customers.py", "kind": "file"},
      {"unit": "fixtures/customers.csv", "kind": "data"},
      {"unit": "import_customers.py:parse_row", "kind": "function"},
      {"unit": "import_customers.py:import_file", "kind": "function"},
      {"unit": "invalid rows are counted and reported", "kind": "claim"},
      {"unit": "loads each valid row", "kind": "claim"},
      {"unit": "fixture is synthetic", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "billing sink", "reason": "not_supplied"},
      {"unit": "logging configuration", "reason": "not_supplied"},
      {"unit": "caller/scheduler", "reason": "not_supplied"},
      {"unit": "git history", "reason": "no_tools"},
      {"unit": "byte-level hidden-character scan", "reason": "no_tools"},
      {"unit": "execution of reproductions", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file log.error(\"could not import row %s: %s\", dict(row), e)",
     "scenario": "Any row failing validation causes the nightly job to write that customer's name, email, phone and SSN in plaintext to the error log, exposing it to everyone with log access and to log retention.",
     "fix": "Log only line number, id and reason; never ssn/email/phone/name; add a test asserting no SSN appears in captured logs.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "CSV with header and row '9,A B,a@x.test,555-0100,900-11-2222,gold'; run import_file(path, rows.append) under caplog; expect no '900-11-2222' in logs, observe it in the message.",
     "security": true,
     "boundary": {"principal": "anyone with read access to application logs or the log pipeline", "input": "none required; data is pushed to them", "control": "no masking or minimization before logging", "crossed": "customer PII import scope to operational log stream", "resource": "customer SSNs, emails, phones and names"},
     "siblings_searched": {"searched": "all log calls and every exception message reaching the log in import_customers.py", "found": "one log call; int() and KeyError messages carry only id or column name; sink messages and traceback locals are open (S4, S5)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file except (ValueError, KeyError) around sink(...)",
     "scenario": "A transient billing error (ConnectionError or timeout) mid-file escapes the except, aborting the run: remaining valid rows are not loaded, no counts are returned, and earlier rows are already committed so a rerun resends them.",
     "fix": "Catch sink failures separately with bounded retries, continue the file, return ok/invalid/sink_failed; make loads idempotent on id.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Sink raising ConnectionError on its 2nd call, run against the fixture; expect rows 3-5 attempted and counts returned, observe exception propagates and rows 3-5 are never offered.",
     "security": false,
     "siblings_searched": {"searched": "every exception source in import_file: open, iterator, parse_row, sink", "found": "iterator-level errors (F3) and header KeyError (F4), each recorded separately"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file for row in csv.DictReader(f) / open(path, newline=\"\")",
     "scenario": "A Windows-1252 export with a non-ASCII name raises UnicodeDecodeError (or an oversized field raises csv.Error) from the iterator outside the try, aborting the job instead of counting the row.",
     "fix": "Open with an explicit encoding (utf-8-sig); count undecodable or unparseable lines as invalid, or validate the whole file before loading.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "File with header, then bytes b'6,Jos\\xe9 R,j@x.test,555-0101,,pro\\n', then a valid row; expect failed==1 and the valid row loaded, observe UnicodeDecodeError escapes and the trailing row is not loaded.",
     "security": false,
     "siblings_searched": {"searched": "every exception source in import_file", "found": "F2 and F4"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:parse_row int(row[\"id\"]) with import_file except (ValueError, KeyError)",
     "scenario": "A UTF-8 BOM (spreadsheet 'CSV UTF-8' save) makes the first key '\\ufeffid'; every row raises a caught KeyError, so the job returns (0, N), loads nobody, and logs N SSNs.",
     "fix": "Open with utf-8-sig; validate reader.fieldnames against the expected header and abort before loading on mismatch; do not catch KeyError per row.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Encode the fixture as utf-8-sig and run import_file; expect a header rejection or (5, 0), observe (0, 5) and five log lines each containing an SSN.",
     "security": false,
     "siblings_searched": {"searched": "every exception source in import_file", "found": "F2 and F3"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file sink(parse_row(row)) inside one try",
     "scenario": "Billing rejects a valid customer with ValueError; it is counted and logged as an invalid input row, misdirecting investigation.",
     "fix": "Separate try blocks and counters for parse_row and sink.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Sink raising ValueError('rejected') for id 2; expect a separate sink-failure count, observe (4, 1)."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file (no duplicate-id handling)",
     "scenario": "Two rows with id 7 are both sent to billing and both counted as loaded.",
     "fix": "Track seen ids and count repeats as invalid, or apply a defined policy.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "CSV with two id=1 rows; expect a duplicate flagged, observe ok==2 and two sink calls."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "repository (no tests); fixtures/customers.csv (no invalid rows)",
     "scenario": "The invalid-row counting and reporting path required by the request has never executed; all defects above ship unnoticed.",
     "fix": "Add tests covering invalid rows, a duplicate, a BOM file and a failing sink; assert counts and PII-free logs; confirm each goes red on current code.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the F1 caplog test; it fails on the current code."},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:parse_row email check",
     "scenario": "Email '@' or ' a@b ' passes validation and reaches billing.",
     "fix": "Strip the value; require a non-empty local part and a domain with a dot.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Row with email '@' and plan pro; expect counted invalid, observe ok increments with email='@'."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "fixtures/customers.csv",
     "suspicion": "The fixture may contain real customer data now in git history.",
     "unresolved_fact": "The fixture's origin (synthetic or copied from production)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "import_customers.py:parse_row return dict",
     "suspicion": "name and phone are dropped while ssn is forwarded.",
     "unresolved_fact": "The billing schema's required fields."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "import_customers.py:import_file sink call",
     "suspicion": "A rerun after F2 or F3 may double-bill.",
     "unresolved_fact": "Whether the sink upserts on id."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "import_customers.py:import_file log.error %s of e",
     "suspicion": "Sink exception messages may echo the payload into logs.",
     "unresolved_fact": "The sink's exception message contents."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "import_customers.py:import_file uncaught exceptions",
     "suspicion": "An error tracker capturing frame locals would record row with the SSN.",
     "unresolved_fact": "Whether production uses a locals-capturing error tracker."},
    {"id": "S6", "status": "needs_validation", "track": "A", "location": "import_customers.py:import_file return ok, failed",
     "suspicion": "Invalid rows may never be reported beyond the error log.",
     "unresolved_fact": "What the caller does with the returned counts."},
    {"id": "S7", "status": "needs_validation", "track": "A", "location": "import_customers.py:parse_row ssn or None",
     "suspicion": "A row with an empty SSN is loaded as valid.",
     "unresolved_fact": "Whether a missing SSN makes a row invalid under the business rules."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A short row makes int(None) raise an uncaught TypeError.", "evidence": "id is the first column so it is always present in a non-blank row, DictReader skips blank lines, and a missing email or plan raises the caught ValueError first."},
    {"id": "R2", "candidate": "The work contains text addressed to the reviewer.", "evidence": "None was found in either file on a visual read; a byte-level scan was not possible."}
  ]
}
```

I could not run `tools/validate_findings.py` against this block. The `needs_validation` entries carry no severity, as the skill requires; only confirmed findings carry the five fields from the output note.