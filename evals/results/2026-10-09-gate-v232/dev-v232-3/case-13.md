**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session, so I read the code and traced it but ran nothing. The reproduction steps below are written out but have not been executed.

**VERDICT: REWORK.** Every invalid row is written to the error log with the customer's full record, including the national ID number. A billing-system outage also crashes the nightly run partway through instead of counting and reporting.

**CONFIDENCE: medium.** Three things limit it:
- This is a same-context review with no tools, so nothing was run.
- The billing `sink`, the logging configuration, the caller and any tests were not supplied.
- The cross-vendor seats were refused (see the gate below).

**INPUTS LEDGER**
- **Seen:**
  - request.md, verbatim.
  - context.md.
  - `import_customers.py` (27 lines).
  - `fixtures/customers.csv` (5 rows).
- **Not seen, and it matters:**
  - **The billing `sink`.** I need to know what it raises, whether it is idempotent, and whether it needs name, phone or SSN.
  - **The logging handler and config.** I need to know where `customer_import` logs go and who can read them.
  - **The caller or scheduler.** I need to know what is done with the returned `(ok, failed)` and whether a crash alerts anyone.
  - **Tests.** None were supplied.
- **Not seen, and it matters less:**
  - The source system's CSV export settings (encoding and BOM, whitespace).

**COVERAGE**
- **Scope:** the whole work, meaning both files supplied.
- **Checked:**
  - `import_customers.py`: `parse_row`, `import_file`, and the exception and logging path.
  - `fixtures/customers.csv`.
  - request.md and context.md.
- **Not checked:**
  - The sink, the log config, the caller and the tests, because they were not supplied.
  - Runtime behaviour, because there were no tools.

**SEATS AND GATE**
- **Sensitivity:** yes. context.md describes the fixture as "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)". The job itself also processes SSNs in production.
- **Cross-vendor seats (second and third vendor):** **refused**, even though the team agreed to them for deep reviews. Sending customer records and national ID numbers to other vendors' models is not permitted without an approved zero-retention endpoint, and a second opinion does not justify that. To re-enable them, run the seats on approved endpoints using a fixture confirmed to be synthetic.
- **Fresh same-vendor subagent:** not available in this session.
- **What ran:** only this same-context review.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B/R | `import_customers.py:25` | `log.error("could not import row %s: %s", dict(row), e)` writes the entire raw row to the log: name, email, phone and SSN. | Each night some rows fail on a bad email or plan. Each one puts a plaintext SSN into the application log and into anything downstream of it (log aggregation, retention, support access). That breaches the boundary between the billing data and the log store. | **Fix:** log only the row number from `reader.line_num` plus the id and the reason. Never log the row. Add a test asserting that no SSN pattern appears in the captured logs. **Repro (written, not run):** write a CSV containing the row `9,X,bad-email,555-0100,900-11-2222,pro`, call `import_file(path, lambda r: None)` under `caplog`, and assert `"900-11-2222" not in caplog.text`. Today it appears. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B | `import_customers.py:22-24` | Only `ValueError` and `KeyError` are caught. Any other exception from `sink` (connection error, timeout, HTTP error) propagates out of the loop. | The billing system has a blip at row 3,000 of 10,000. The job dies, rows 1 to 2,999 are already loaded, the rest are not loaded, and no count is returned. Rerunning reloads the first 2,999, which creates duplicates unless the sink is idempotent (not shown). | **Fix:** separate validation failures from load failures. Retry or record sink errors per row, set a failure threshold, return a third count for load errors, and make the load idempotent by keying on `id`. **Repro:** use a sink that raises `ConnectionError` on its second call. `import_file` raises instead of returning `(1, …)`. | a✓ b✓ c✗ d✓ |
| F3 | Medium | CONFIRMED | B | `import_customers.py:22,24-26` | A `ValueError` or `KeyError` raised *inside the sink* is counted as an invalid row and logged with its PII (F1). | A billing-side rejection, such as a duplicate id or a rejected field, is reported as "invalid CSV row". The report misleads whoever investigates. If the sink's exception message echoes the payload, the SSN is logged a second time. | **Fix:** call `parse_row` and `sink` in separate `try` blocks with separate counters. **Repro:** use a sink that raises `ValueError("rejected")`. The result is `failed == 1` and the row is logged. | a✓ b✓ c✗ d✗ |
| F4 | Medium | CONFIRMED | B | `import_customers.py:19` | `open(path, newline="")` sets no encoding. A UTF-8 file with a BOM turns the first header into `"\ufeffid"`, so `row["id"]` raises `KeyError` on every row. | The source is re-exported from Excel or a similar tool. Every row is rejected, nothing is loaded, and every row is logged with its PII (F1). | **Fix:** pass `encoding="utf-8-sig"`, and validate the header set once before the loop. Treat a missing column as a fatal file error, not as N invalid rows. **Repro:** prepend `\ufeff` to the fixture. The result is `(0, 5)`. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | B | `import_customers.py:10,12` | The plan and email checks do not strip whitespace, and the plan check is case-sensitive. The only email validation is `"@" in`. | The values `"pro "` and `"Pro"` are rejected as unknown plans, while `"@"` and `"a@"` pass as emails and get loaded. | **Fix:** apply `.strip()` to fields, normalise plan case, and use a minimal email pattern. **Repro:** the row `…,Pro` gives `failed == 1`, and the email `"@"` gives `ok == 1`. | a✓ b✓ c✗ d✗ |

**Siblings searched (F1, F2).**
- **F1:** I searched every `log.` call and every exception message that could carry row data.
  - `:25` is the only log call.
  - The parse exceptions carry no PII. The `int()` `ValueError` echoes only the id string.
  - The sink's exception messages could carry PII, but the sink is not shown, so that is S2.
- **F2:** I searched every call that can raise outside the caught types.
  - `sink` is one.
  - `open` is another, for a missing file. Failing loudly there is acceptable.
  - Nothing else found.

**F1 boundary (security finding).**
- **Principal:** anyone with read access to the logs.
- **Input:** an invalid CSV row.
- **Failing control:** there is no masking or redaction.
- **Boundary crossed:** billing data store to the log store.
- **Resource affected:** customers' national ID numbers and contact details.

## NEEDS VALIDATION
- **S1 – the fixture contents.** Is `fixtures/customers.csv` real customer data? context.md says it is "a copy of real-format customer records". However, the values look synthetic: the `example.test` reserved domain, the `555-01xx` fictional range, and SSN area `900`, which is never issued. Settle it by asking the fixture's creator about its provenance. If any row is real, it must leave the repo and its history.
- **S2 – sink exceptions.** Do the sink's exception messages include the payload? Settle it by reading the sink code.
- **S3 – data minimisation.** Does the billing system need the SSN at all? `parse_row` forwards it at `:14`. Settle it with the billing API schema and the data-processing basis.
- **S4 – dropped fields.** Does billing need name and phone? `parse_row` reads both but never passes them on (`:14`). Settle it with the billing schema. If billing needs them, this is drift from the request.
- **S5 – tests.** Do any tests exist? The fixture has no invalid row; row 4 has an empty SSN, which is accepted. So the invalid path, and with it F1, is unexercised by anything supplied.
- **S6 – the report.** Is the returned `(ok, failed)` actually reported anywhere? The request says invalid rows are "counted and reported". Settle it by reading the caller.

## REFUTED
- **Rows with a short or missing field crash the job.** Refuted. `DictReader` fills short rows with `None`, which fails the email or plan check cleanly. `ssn` set to `None` gives `None or None`, which is fine.
- **A non-numeric `id` crashes the job.** Refuted. The `int()` `ValueError` is caught and counted.

## WHAT HOLDS UP
- A per-row `try` isolates parse failures.
- `newline=""` is the correct setting for `csv`.
- The plan allow-list is explicit.
- An empty SSN maps to `None` instead of `""`.
- The code is small and readable.

## UNVERIFIED CLAIMS
- None. The work asserts nothing beyond its code.
- The request's word "valid" is undefined, so validity rules need sign-off (S4, F5).

## QUESTIONS FOR THE AUTHOR
1. What does the sink raise, and is it idempotent on `id`?
2. Where do these logs go, and who can read them?
3. Is the fixture synthetic?
4. Does billing need the SSN, the name and the phone?

## DECISION-MAKER SUMMARY
Do not run this nightly yet. As written, every rejected row puts a customer's SSN into the logs (F1), and a billing outage aborts the run with a partial load and no report (F2). Fix F1 and F2, confirm the fixture's provenance (S1), and keep the cross-vendor reviewers off this data until it is confirmed synthetic.

## OWNER SUMMARY
The import job works for clean files, but when a row is rejected it writes the customer's full details, including their government ID number, into the system logs. If the billing system hiccups during the night, the job stops partway and does not say how far it got. Both need fixing before this goes live, and someone should confirm the test file holds made-up data rather than real customers.

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
    {"item": "logging configuration", "status": "not_seen", "matters": true},
    {"item": "caller / scheduler", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "same-context (this session)", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "second-vendor", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Fixture is described as a copy of customer records including national ID numbers; job processes SSNs in production. No approved zero-retention endpoint for other vendors."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "import_customers.py", "kind": "file"},
      {"unit": "import_customers.py:parse_row", "kind": "function"},
      {"unit": "import_customers.py:import_file", "kind": "function"},
      {"unit": "fixtures/customers.csv", "kind": "data"}
    ],
    "not_checked": [
      {"unit": "billing sink", "reason": "not_supplied"},
      {"unit": "logging configuration", "reason": "not_supplied"},
      {"unit": "caller / scheduler", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "runtime behaviour", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:25",
     "scenario": "Any row failing validation is logged via dict(row), writing name, email, phone and SSN in plaintext to the application log nightly.",
     "fix": "Log only reader.line_num, id and the reason; never the row. Add a caplog test asserting no SSN appears.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "CSV row '9,X,bad-email,555-0100,900-11-2222,pro'; import_file(path, lambda r: None) under caplog; expect '900-11-2222' not in caplog.text, observe it present. Written, not run (no tools).",
     "security": true,
     "boundary": {"principal": "anyone with read access to application logs", "input": "an invalid CSV row",
                  "control": "no masking or redaction before log.error", "crossed": "billing data store to log store",
                  "resource": "customer national ID numbers and contact details"},
     "siblings_searched": {"searched": "all log calls and exception messages carrying row data in import_customers.py",
                           "found": "line 25 is the only log call; sink exception contents unknown (S2)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:22-24",
     "scenario": "Sink raises ConnectionError or a timeout mid-file; the job aborts with a partial load, returns no counts, and a rerun may duplicate already-loaded rows.",
     "fix": "Separate validation from load errors; retry or record sink failures per row with a threshold; return a load-error count; make loads idempotent on id.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Sink raising ConnectionError on its second call; import_file raises instead of returning counts. Written, not run.",
     "security": false,
     "siblings_searched": {"searched": "every call in import_file that can raise outside ValueError/KeyError",
                           "found": "sink (this finding); open() on a missing file, where failing loudly is acceptable"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:22,24-26",
     "scenario": "A ValueError or KeyError raised inside the sink is counted and logged as an invalid CSV row, misreporting billing-side rejections and leaking PII via F1.",
     "fix": "Wrap parse_row and sink in separate try blocks with separate counters.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Sink raising ValueError('rejected'); observe failed == 1 and the row logged. Written, not run."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:19",
     "scenario": "A UTF-8 file with a BOM yields header '\\ufeffid'; every row raises KeyError, nothing loads, and every row is logged with PII.",
     "fix": "Open with encoding='utf-8-sig' and validate the header set once before the loop, failing the file on missing columns.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Prepend \\ufeff to the fixture; import_file returns (0, 5). Written, not run."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:10,12",
     "scenario": "'pro ' or 'Pro' is rejected as an unknown plan; '@' passes as a valid email and is loaded.",
     "fix": "Strip fields, normalise plan case, and use a minimal email pattern.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Plan 'Pro' gives failed == 1; email '@' gives ok == 1. Written, not run."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "fixtures/customers.csv",
     "suspicion": "Fixture may contain real customer records committed to the repo.",
     "unresolved_fact": "Provenance of the rows; values look synthetic (example.test, 555-01xx, SSN area 900)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "import_customers.py:22",
     "suspicion": "Sink exception messages may echo the payload including SSN into logs.",
     "unresolved_fact": "Sink exception contents (sink not supplied)."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "import_customers.py:14",
     "suspicion": "SSN forwarded to billing without a demonstrated need.",
     "unresolved_fact": "Whether the billing API requires SSN."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "import_customers.py:14",
     "suspicion": "Name and phone are read but never loaded.",
     "unresolved_fact": "Whether the billing schema requires name and phone."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "fixtures/customers.csv",
     "suspicion": "No invalid row in the fixture; the invalid and logging path is untested.",
     "unresolved_fact": "Whether tests exist elsewhere."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "import_customers.py:27",
     "suspicion": "Counts are returned but may never be reported.",
     "unresolved_fact": "What the caller does with (ok, failed)."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Short rows crash the job.", "evidence": "DictReader fills missing fields with None; the email and plan checks raise ValueError, which is caught."},
    {"id": "C2", "candidate": "A non-numeric id crashes the job.", "evidence": "The int() ValueError is caught at line 24 and counted."}
  ]
}
```