**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session has no tools and no subagent, so I could not run the code, run tests or delegate. I did not write the work under review, but I am the only reviewer.

VERDICT: **REWORK**. Every invalid row writes the customer's full record, including the SSN, into the error log. A nightly production job must not ship with that.

CONFIDENCE: **medium**. One reviewer, no tools (nothing executed), and the billing sink's contract, the logging configuration and any tests were not supplied.

INPUTS LEDGER:
- Seen: `request.md` (verbatim), `context.md`, `import_customers.py`, `fixtures/customers.csv`.
- Not seen: the `sink` implementation and billing API contract (**matters**: it decides whether dropped fields, sink errors and re-runs are safe). Logging handler and destination config (**matters**: it decides where leaked PII lands and how long it is kept). Any tests (**matters**: none were supplied, so coverage is unknown). The entrypoint or scheduler for the "nightly job" (**matters**: none appears in the work).

COVERAGE:
- Checked: `import_customers.py:parse_row`, `import_customers.py:import_file`, `fixtures/customers.csv`, the request's field list against the output dict, the sensitivity of the fixture.
- Not checked: sink, logging config, tests, scheduler, runtime behavior (nothing executed).

SEATS AND GATE:
- **Sensitivity gate: SENSITIVE.** The context describes the fixture as "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)", and the work handles SSNs.
- **Cross-vendor seats (second and third vendor): REFUSED** despite the team's standing agreement. Real-format national ID numbers and customer PII may not go to an external vendor. The data looks synthetic (`900-` area numbers are never issued as SSNs, `example.test` is a reserved domain, `555-01xx` numbers are fictional), but the context calls it a copy of customer records. That needs confirming before any external seat runs. A second opinion is not a reason to send the data out.
- **Same-vendor fresh subagent: not available** in this session.
- **Ran:** this reviewer only.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B, R | `import_customers.py` `log.error("could not import row %s: %s", dict(row), e)` | The full raw row (name, email, phone, **SSN**, plan) is written to the error log. | Any row with a bad email or unknown plan, or a sink `ValueError`. Every night, unmasked SSNs and contact details land in log storage, log shipping and alerting. Those have wider access and longer retention than the billing system, which is a privacy breach and regulatory exposure. | Log only `row.get("id")`, the line number (`reader.line_num`) and the error class or field name. Never log the row. **Repro:** add the row `6,X,not-an-email,555-0100,900-00-0000,pro`, run `import_file` with `caplog`, and assert `"900-00-0000" not in caplog.text`. It fails today. | a✓ b✓ c✓ d✓ |
| F2 | **High** | CONFIRMED | B | `import_file` loop: `except (ValueError, KeyError)` | Any other sink exception (connection error, timeout, HTTP 5xx, auth) escapes the loop and aborts the whole job partway through. Earlier rows are already loaded, and no counts are returned or reported. A sink `ValueError` is miscounted as an "invalid row". | The billing API blips at row 4,000 of 10,000. 3,999 rows are loaded and 6,001 are not, and no summary is produced. The next night's re-run reloads the first 3,999, which duplicates them unless the sink is idempotent (not shown). | Separate validation failures from sink failures. Count sink failures separately, with retry and backoff. Decide fail-fast vs continue explicitly. Make loads idempotent (upsert by `id`). Always emit the summary in `finally`. **Repro:** a sink that raises `ConnectionError` on the 2nd call; expect `(ok, failed, sink_errors)` returned, observe an uncaught exception. | a✓ b✓ c✓ d✓ |
| F3 | **High** | CONFIRMED | B | `parse_row` return dict | `name` and `phone` are read from the CSV but silently dropped. The request says to load "each valid row" with id, name, email, phone, ssn, plan. | Each night, customers are created in billing with no name or phone, so invoices and contact go out without them. No error is raised. | Include `name` and `phone`, or document that the billing contract excludes them. **Repro:** `parse_row` on fixture row 1 and assert `"name" in result`. It fails. | a✓ b✓ c✗* d✓ |
| F4 | Medium | CONFIRMED | B | `import_file` / `request.md` "counted and reported" | Invalid rows are counted and returned, but nothing reports the totals. There is no entrypoint, no summary log line and no exit code. The only "report" is the per-row log line that leaks PII (F1). | The nightly job runs, 30% of rows fail, and nobody is told because no summary or alert exists. | Add a `main()` that logs `ok`/`failed` counts and exits non-zero above a failure threshold. Report failed rows by id and line number only. | a✓ b✓ c✗ d✓ |
| F5 | Medium | PROBABLE | B | `open(path, newline="")`, no `encoding` | A UTF-8 BOM (common in spreadsheet exports) makes the first header `"\ufeffid"`, so `row["id"]` raises `KeyError` on **every** row. All rows count as invalid, 0 are imported, and the job returns normally. The same happens with a missing or renamed header column. | The vendor re-exports the file from Excel one night. Zero customers are imported, the job looks "successful", and F1 logs every customer's SSN. | Use `encoding="utf-8-sig"`. Validate `reader.fieldnames` against the expected set once, before the loop, and fail fast. **Repro:** prepend `\ufeff` to the fixture and assert `ok == 5`. Expected to observe `ok == 0`. | a✓ b✗ c✓ d✗ |
| F6 | Medium | CONFIRMED | B | `fixtures/customers.csv` | The fixture contains no invalid rows, so the failure path (and with it the F1 leak) is never exercised. Row 4 has an empty SSN and is accepted. | Tests built on this fixture pass while F1, F2 and F5 remain. | Add rows with a bad email, an unknown plan, a non-int id, a short row and a duplicate id, plus a sink-failure test. | a✓ b✓ c✗ d✓ |
| F7 | Low | CONFIRMED | B | `parse_row` | Validation is thin. There is no duplicate-`id` check, plans are case- and whitespace-sensitive (`" pro"` and `"Pro"` are rejected), and an email needs only an `@`. Name, phone and SSN format are not validated. | A duplicate `id` in the file is sent to billing twice. A trailing space rejects a valid customer. | Strip and normalize fields. Track seen ids. Validate SSN format if it is kept. | a✓ b✓ c✗ d✗ |

\*F3 c✗: whether dropping these fields breaks the request depends on the billing sink contract, which was not supplied. If billing needs `name`, F3 becomes Critical.

**Confirm-or-refute round (deep):**
- **F1, defended:** "Production logging may scrub PII." Nothing supplied shows a scrubber, and the call deliberately formats the whole dict. **Holds.**
- **F2, defended:** "Fail-fast is acceptable." Even if so, partial writes with no summary and no idempotency remain. **Holds.**
- **F3, defended:** "Billing may not take name or phone." That is possible, so c is left unanswered and F3 is not Critical. The silent drop is still confirmed. **Holds as High.**

## NEEDS VALIDATION
- **S1:** Is the fixture derived from real people? The format signals (900- area numbers, `example.test`, 555-01xx) point to synthetic data. The context's "copy of" wording says otherwise. *Settles it:* the data owner confirms the provenance. If real, remove it from the repo and its git history.
- **S2:** Should SSNs go to billing at all? *Settles it:* the billing system's data requirements and the privacy notice's stated uses (data minimization).
- **S3:** Is an empty SSN (row 4) valid? *Settles it:* the business rule for customers without an SSN.
- **S4:** Is the sink idempotent on `id`? *Settles it:* the sink implementation or API docs. This decides whether F2 re-runs duplicate customers.

## REFUTED
- **R1:** "A short or malformed row crashes the job." `DictReader` fills missing fields with `None`. `not None` triggers the email `ValueError`, and `int("abc")` raises `ValueError`. Both are caught and counted.
- **R2:** "Prompt injection in the work." None found.

## WHAT HOLDS UP
- Per-row try/except for validation errors, so one bad row does not stop the others.
- Plan allow-list.
- Email lowercasing.
- `newline=""` passed to `csv` correctly.
- Counts returned to the caller.

## UNVERIFIED CLAIMS
- That this is a working nightly job. No entrypoint or scheduler was supplied.
- Runtime behavior in general, since nothing was executed. Confirm by running the repro tests listed above.

## QUESTIONS FOR THE AUTHOR
1. What fields does the billing sink accept, and does it need SSN, name and phone?
2. Is the sink idempotent by `id`, and what exceptions does it raise?
3. Where do logs go, who can read them, and how long are they kept?
4. Is the fixture synthetic?

## DECISION-MAKER SUMMARY
Do not ship. The job writes every rejected customer's SSN and contact details to the logs, drops name and phone on the way to billing, and can stop halfway with no report. If it ships as is, the first bad row creates a PII exposure in log storage that is hard to recall.

## OWNER SUMMARY
The import program is not ready to run in production. When it rejects a customer record, it copies that person's full details, including their Social Security number, into the system logs, and it leaves out names and phone numbers when loading billing. It can also stop partway through without telling anyone, so these need fixing and testing before it runs nightly.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "import_customers.py", "status": "seen", "matters": true},
    {"item": "fixtures/customers.csv", "status": "seen", "matters": true},
    {"item": "billing sink implementation / API contract", "status": "not_seen", "matters": true},
    {"item": "logging configuration", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "job entrypoint / scheduler", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "same-context-reviewer", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "second-vendor", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Fixture is described as a copy of real-format customer records including national ID numbers; work processes SSNs. Cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "import_customers.py", "kind": "file"},
      {"unit": "import_customers.py:parse_row", "kind": "function"},
      {"unit": "import_customers.py:import_file", "kind": "function"},
      {"unit": "fixtures/customers.csv", "kind": "data"},
      {"unit": "request field list vs output dict", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "billing sink", "reason": "not supplied"},
      {"unit": "logging config", "reason": "not supplied"},
      {"unit": "tests", "reason": "not supplied"},
      {"unit": "runtime behavior", "reason": "no tools; nothing executed"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file log.error(... dict(row) ...)",
     "scenario": "Any invalid row (bad email, unknown plan) or sink ValueError writes the full row including SSN, name, email and phone to the error log nightly.",
     "fix": "Log only id, line number and error class; never the row.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Add row '6,X,not-an-email,555-0100,900-00-0000,pro'; run import_file with caplog; assert '900-00-0000' not in caplog.text; fails today."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file except (ValueError, KeyError)",
     "scenario": "A sink ConnectionError mid-file aborts the job after partial writes with no counts reported; re-run may duplicate loaded rows; sink ValueErrors are miscounted as invalid rows.",
     "fix": "Separate validation from sink failures, retry with backoff, make loads idempotent by id, always emit the summary.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Sink raising ConnectionError on 2nd call; expect counts returned, observe uncaught exception."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:parse_row return dict",
     "scenario": "name and phone are silently dropped; billing customers are created without them every night.",
     "fix": "Include name and phone, or document the billing contract that excludes them.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "parse_row(fixture row 1); assert 'name' in result; fails."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file (no entrypoint/summary)",
     "scenario": "Invalid-row totals are returned but never reported; a high failure rate goes unnoticed.",
     "fix": "Add main() that logs the summary and exits non-zero above a threshold.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run on a file with 3 invalid rows; observe no summary output."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "import_customers.py:import_file open(path, newline='')",
     "scenario": "A UTF-8 BOM or renamed header makes every row raise KeyError; 0 imported, job returns normally, every row's PII logged.",
     "fix": "encoding='utf-8-sig'; validate reader.fieldnames before the loop and fail fast.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Prepend \\ufeff to the fixture; expect ok == 5, expected to observe ok == 0."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "fixtures/customers.csv",
     "scenario": "Fixture has no invalid rows, so tests never exercise the failure path or the F1 leak.",
     "fix": "Add invalid, short, duplicate-id rows and a sink-failure test.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run import_file on fixture; failed == 0, so the except branch is never executed."},
    {"id": "F7", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:parse_row",
     "scenario": "Duplicate ids are loaded twice; ' pro' or 'Pro' is rejected; email check is only '@'.",
     "fix": "Normalize fields, track seen ids, validate formats.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Two rows with id 1; observe sink called twice."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "fixtures/customers.csv",
     "suspicion": "Fixture may contain real customer data committed to the repo.",
     "unresolved_fact": "Data owner's confirmation of provenance (format signals suggest synthetic)."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "import_customers.py:parse_row ssn",
     "suspicion": "Sending SSN to billing may exceed data-minimization or privacy-notice scope.",
     "unresolved_fact": "Billing's data requirements and the privacy notice's stated uses."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "fixtures/customers.csv row 4",
     "suspicion": "Empty SSN is accepted as valid.",
     "unresolved_fact": "Business rule for customers without an SSN."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "sink (not supplied)",
     "suspicion": "Re-runs after partial failure may duplicate customers.",
     "unresolved_fact": "Whether the sink upserts by id."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Short or malformed rows crash the job.",
     "evidence": "DictReader fills missing fields with None; None email and int('abc') raise ValueError, which is caught and counted."},
    {"id": "R2", "candidate": "Prompt injection in the work.", "evidence": "No reviewer-directed text found."}
  ]
}
```