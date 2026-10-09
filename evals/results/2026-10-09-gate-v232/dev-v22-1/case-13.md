VERDICT: **REWORK**. On every invalid row the job writes the customer's full record, national ID number included, to the application log. It also drops name and phone from what it loads, and a billing outage stops the job partway through the file.

CONFIDENCE: **medium**. This was a single-reviewer, same-context review with no tools, so nothing was run. The requested cross-vendor seats were refused (see below). The billing `sink`, the logging config, the scheduler and the tests were not supplied. Re-run in a fresh session for anything high-stakes.

INPUTS LEDGER:
- **Seen:** `request.md` (verbatim), `context.md`, `import_customers.py`, `fixtures/customers.csv`.
- **Not seen:**
  - The `sink` implementation (billing client). This matters: it decides retries, idempotency and which exceptions it raises.
  - The logging configuration and log destination or retention. This matters for F1's blast radius, not for whether F1 is real.
  - The nightly runner or entry point. This matters: who reads `(ok, failed)`, and whether anything is "reported".
  - Any tests. This matters: no evidence the invalid-row path was ever exercised.
  - The billing schema. This matters for F3 (whether name and phone are required).
- **Missing-input finding:** none of these gaps clears the Critical. F1 rests only on code that was supplied.

COVERAGE:
- **Checked:**
  - `import_customers.py:parse_row` (every branch, plus hostile inputs: empty, missing column, BOM header, case and whitespace variants, non-integer id).
  - `import_customers.py:import_file` (exception paths, counting, logging).
  - `fixtures/customers.csv` (all 5 rows traced through `parse_row`).
  - The request versus the delivered behaviour.
  - The sensitivity of the fixture.
- **Not checked:** `sink`, logging config, runner, billing schema, runtime locale. None was supplied, and nothing was executed.

SEATS AND GATE:
- **Sensitivity gate: tripped.** The work includes a fixture described as "a copy of real-format customer records" containing names, emails, phones and national ID numbers. The code's purpose is also to handle SSNs.
- **Cross-vendor seats (2nd and 3rd vendor): refused.** The team's standing agreement and the DEEP request do not override the gate, because a second opinion is not a reason to send ID numbers to another vendor. They could be run on a version with the fixture stripped or replaced by clearly synthetic data, via approved zero-retention endpoints.
- **Fresh same-vendor subagent:** not available, because there are no tools in this session.
- **Ran:** this reviewer only, same context.
- No reviewer-directed instructions were found inside the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B, R | `import_customers.py` line `log.error("could not import row %s: %s", dict(row), e)` | Every rejected row is logged in full: name, email, phone and SSN in clear text. The exception text `e` from `sink` may add more personal data. | A nightly file contains one row with an unknown plan or a malformed email. That customer's SSN is written to the production log, then shipped to whatever aggregator and retention the logs have. This happens every night there is any invalid row. | Log only the row number (`reader.line_num`), the `id` if parseable, and the reason. Never log `row`. Purge or rotate any logs already written. **Repro:** add a fixture row `6,X,x@example.test,555-0000,900-00-0000,gold`. Run `import_file` with caplog. Expect no `900-00-0000` in the captured log; observe it present. | a✓ b✓ c✓ d✓ |
| F2 | **High** | CONFIRMED (from code; `sink` behaviour unseen) | B | `import_file`, `except (ValueError, KeyError)` | Only `ValueError` and `KeyError` are caught. Any other exception from `sink` (connection error, timeout, HTTP error) escapes the loop. The job aborts mid-file, returns no counts, and the rows already sent stay loaded. Conversely, a `ValueError` raised by billing is counted as an "invalid row", which mixes billing rejections into validation failures. | Billing has a 30-second outage at row 4,000 of 10,000. The job crashes, 3,999 customers are loaded, 6,000 are not, and there is no summary. Tomorrow's re-run reloads the first 3,999 (see S2). | Validate and send in separate steps. Catch sink errors separately with retry and backoff. Count `invalid` and `load_failed` distinctly. Always emit counts (use `finally`). Decide whether to abort or continue on sink failure. **Repro:** use a `sink` that raises `ConnectionError` on the 2nd call. Expect a returned `(1, 0, 1)`-style summary; observe an uncaught exception. | a✓ b✓ c✗ d✓ |
| F3 | **High** | CONFIRMED | B (drift) | `parse_row` return dict | The request says to load "each valid row" with columns id, name, email, phone, ssn, plan. The record sent to billing omits `name` and `phone`, yet it does send `ssn`. | Every customer is created in billing with no name and no phone. Invoices and dunning cannot address the customer. Nothing errors, so it goes unnoticed. | Include `name` and `phone`, or document the billing schema that excludes them. Confirm whether billing actually needs `ssn` (S1). **Repro:** feed fixture row 1. Expect `name` in the sink payload; observe it is absent. | a✓ b✓ c✗ (billing schema unseen) d✓ |
| F4 | Medium | PROBABLE | B | `open(path, newline="")`, `row["id"]` | There is no `encoding=` argument and no header check. A UTF-8 BOM (common in Excel exports) turns the first header into `\ufeffid`. `int(row["id"])` then raises `KeyError` on every row, so the whole file is "invalid", and through F1 every customer's SSN is logged. A non-UTF-8 default locale with accented names raises an uncaught `UnicodeDecodeError`. | The export tool changes to add a BOM. The job reports 0 ok and N failed, and logs all N full records. | Use `encoding="utf-8-sig"`. Check `reader.fieldnames` against the expected set and fail fast if it differs. **Repro:** prepend `\ufeff` to the fixture. Expect a header error; observe 0 ok and 5 failed. | a✓ b✗ c✗ d✓ |
| F5 | Medium | CONFIRMED | B | `parse_row` | Validation is thin. Email only needs to contain `"@"` (`"@"` alone passes), and surrounding whitespace is kept. `plan` is case- and whitespace-sensitive (`"Pro"` and `" pro"` are rejected). `ssn` format is never checked. Duplicate `id`s within a file are not detected. `name` is never checked. | A file containing `Pro` capitalised is rejected wholesale. A row with email `@` is loaded into billing. | Strip fields. Normalise the plan. Use a minimal email pattern. Validate SSN format when present. Detect duplicate ids. **Repro:** `parse_row({...,"email":"@","plan":"pro"})` should raise but returns. | a✓ b✓ c✗ d✗ |
| F6 | Medium | CONFIRMED | B | `fixtures/customers.csv` | All 5 fixture rows are valid (row 4 has an empty SSN, which the code allows). The invalid-row path, which is the path that leaks data in F1, is never exercised by this fixture. No tests were supplied. | A regression in counting or logging ships unnoticed. | Add invalid rows (bad email, unknown plan, non-integer id, wrong header) and assert counts and log content. Use a mutation check: remove `failed += 1` and confirm the test goes red. | a✓ b✓ c✗ d✗ |

**Confirm-or-refute round:**
- **F1** (strongest defence: "logs are access-controlled"): **holds.** Clear-text national IDs in application logs breach data minimisation whatever the access controls, and they spread to aggregators and backups.
- **F2** (defence: "the sink may retry internally"): **holds.** Even with retries, a final failure escapes uncaught, and the counting conflation is in the supplied code.
- **F3** (defence: "billing may not want name or phone"): **holds as drift against the request as written.** Severity is kept at High rather than Critical because the billing schema is unseen.

## NEEDS VALIDATION
- **S1:** Does billing need the SSN at all? If not, sending it is unnecessary transfer of sensitive data. *Settled by:* the billing API schema or a data-processing agreement.
- **S2:** Is `sink` idempotent (an upsert by `id`)? If not, every re-run or partial-failure recovery duplicates customers. *Settled by:* the `sink` source.
- **S3:** Is the fixture real customer data? The ID numbers use the 900 prefix, which is never issued as an SSN, and the domains and phone numbers are reserved test ranges, which points to synthetic data. The context, however, says "a copy of real-format customer records". If any value is real, it is committed personal data and needs purging from git history. *Settled by:* the fixture's provenance.
- **S4:** What does "reported" mean in the request? Currently the only report is `log.error` per row plus a returned tuple that nothing shown consumes. Logging is unconfigured here, so it relies on Python's last-resort stderr handler. *Settled by:* the runner and alerting setup.

## REFUTED
- **R1:** "`int(None)` on a short row raises an uncaught `TypeError`." `id` is the first column, so it is only `None` on a fully blank line, and `DictReader` skips blank lines. A blank `id` gives `int("")`, which raises `ValueError` and is caught.
- **R2:** "Row 4's empty SSN crashes or is rejected." `row["ssn"] or None` handles it, and the row is loaded with `ssn=None`. Whether that is acceptable for billing is a business question, not a defect.

## WHAT HOLDS UP
- The plan allow-list is enforced.
- Email is lower-cased.
- A non-integer `id` is caught and counted.
- `newline=""` is correct for `csv`.
- `ok` is incremented only after `sink` succeeds.
- Missing optional SSN maps cleanly to `None`.
- The code is small and readable.

## UNVERIFIED CLAIMS
- That the job "loads into the billing system" correctly. `sink` was not supplied; read it and run it against staging.
- That invalid rows are "reported". Confirm a consumer of the counts and an alert exist.

## QUESTIONS FOR THE AUTHOR
1. Is dropping name and phone intentional, and does billing actually require SSN?
2. Is `sink` an idempotent upsert, and what does it raise on failure?
3. Where do this logger's records go, and how long are they kept? Have any invalid rows been logged in production already?
4. Is the fixture fully synthetic?

## DECISION-MAKER SUMMARY
Do not ship. The job writes national ID numbers to production logs whenever a row fails validation, and it silently drops customer names and phones. A billing hiccup leaves a half-loaded night with no summary. If it runs as is, expect sensitive data in logs within days, which would need a purge and possibly incident handling.

## OWNER SUMMARY
The nightly customer import is not ready. When a record has a problem, the job copies that customer's full details, including their government ID number, into the system logs. It also leaves out names and phone numbers when loading customers, and it can stop halfway through without saying how far it got. These need fixing and testing before it runs in production.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "import_customers.py", "status": "seen", "matters": true},
    {"item": "fixtures/customers.csv", "status": "seen", "matters": true},
    {"item": "billing sink implementation", "status": "not_seen", "matters": true},
    {"item": "logging configuration / log destination", "status": "not_seen", "matters": true},
    {"item": "nightly runner / entry point", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "billing schema", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "second-vendor", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Fixture holds names, emails, phones and national ID numbers described as a copy of real-format customer records; code processes SSNs. No cross-vendor transfer."},
  "coverage": {
    "checked": [
      {"unit": "import_customers.py", "kind": "file"},
      {"unit": "import_customers.py:parse_row", "kind": "function"},
      {"unit": "import_customers.py:import_file", "kind": "function"},
      {"unit": "fixtures/customers.csv", "kind": "data"},
      {"unit": "request: load each valid row; count and report invalid rows", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "billing sink", "reason": "not supplied"},
      {"unit": "logging config", "reason": "not supplied"},
      {"unit": "nightly runner", "reason": "not supplied"},
      {"unit": "runtime execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file log.error(... dict(row) ...)",
     "scenario": "Any row failing validation (bad email, unknown plan, non-integer id) causes the full record including the SSN to be written to production logs nightly.",
     "fix": "Log only line number, parsed id if available, and the reason; never the row. Purge existing logs.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Add row '6,X,x@example.test,555-0000,900-00-0000,gold'; run import_file under caplog; expect no '900-00-0000' in logs, observe it present."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file except (ValueError, KeyError)",
     "scenario": "A ConnectionError or timeout from sink mid-file aborts the job uncaught, leaving a partial load and no counts; sink ValueErrors are miscounted as invalid rows.",
     "fix": "Separate validation from loading; catch and retry sink errors; count invalid and load_failed separately; always emit a summary.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Use a sink that raises ConnectionError on its 2nd call; expect a returned summary, observe an uncaught exception."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:parse_row return dict",
     "scenario": "Every customer is loaded into billing without name or phone, contrary to the request to load each valid row.",
     "fix": "Include name and phone, or document why billing excludes them; confirm whether ssn is needed.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Feed fixture row 1; expect 'name' in sink payload, observe absent."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "import_customers.py:import_file open(path, newline=\"\")",
     "scenario": "A UTF-8 BOM makes the header '\\ufeffid', so every row raises KeyError, is counted invalid and is fully logged; a non-UTF-8 locale raises an uncaught UnicodeDecodeError.",
     "fix": "Open with encoding='utf-8-sig' and validate reader.fieldnames before processing.",
     "answers": {"a": true, "b": false, "c": false, "d": true},
     "reproduction": "Prepend \\ufeff to the fixture; expect a header error, observe 0 ok and 5 failed."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:parse_row",
     "scenario": "Email '@' passes; 'Pro' or ' pro' plans are rejected; SSN format is unchecked; duplicate ids are loaded twice.",
     "fix": "Strip and normalise fields, use a minimal email pattern, validate SSN format when present, detect duplicate ids.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "parse_row with email '@' and plan 'pro' returns instead of raising."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "fixtures/customers.csv",
     "scenario": "All fixture rows are valid, so the invalid-row path (where F1 leaks) is never exercised; regressions ship unnoticed.",
     "fix": "Add invalid fixture rows and tests asserting counts and log content; mutation-check by removing 'failed += 1'.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Trace all 5 fixture rows through parse_row: none raises."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "import_customers.py:parse_row",
     "suspicion": "SSN may be sent to billing without need.",
     "unresolved_fact": "Whether the billing schema or contract requires the SSN."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "sink (not supplied)",
     "suspicion": "Re-runs may duplicate customers.",
     "unresolved_fact": "Whether sink upserts by id."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "fixtures/customers.csv",
     "suspicion": "Fixture may contain real personal data committed to the repo.",
     "unresolved_fact": "Provenance of the fixture values (900-prefix IDs and reserved domains and phones suggest synthetic)."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "import_customers.py:import_file return",
     "suspicion": "Invalid rows are counted but not reported to anyone.",
     "unresolved_fact": "What consumes the (ok, failed) tuple and whether an alert or report exists."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "int(None) on a short row raises an uncaught TypeError.",
     "evidence": "id is the first column; DictReader skips blank lines; an empty id gives int('') which raises ValueError and is caught."},
    {"id": "R2", "candidate": "An empty SSN (fixture row 4) crashes or is rejected.",
     "evidence": "row['ssn'] or None maps it to None and the row loads."}
  ]
}
```