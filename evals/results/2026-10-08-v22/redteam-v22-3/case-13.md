# Redteam report: `import_customers.py` and `fixtures/customers.csv`

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so I could not run anything or create a subagent. Every behavior below comes from reading the code against standard Python `csv` and `open()` semantics.

**VERDICT: REWORK.** Every invalid row writes the customer's full national ID number, email, phone and name to the error log, and that has to be fixed before this runs nightly in production.

**CONFIDENCE: medium.** Three things limit it: this is a same-context review, nothing was executed, and the billing `sink`, the caller and the log configuration were not supplied.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, `import_customers.py` (27 lines), `fixtures/customers.csv` (5 rows).
- **Not seen, and it matters:**
  - The `sink` implementation (whether it is idempotent, which fields it needs, which errors it raises).
  - The caller that reports `(ok, failed)`.
  - The logging handler and where logs are retained.
- **Not seen, and it matters for test coverage:** any tests. None were supplied.
- **Not seen, low impact:** the production CSV's exporter (encoding, BOM).

**COVERAGE**
- **Checked:**
  - `import_customers.py:parse_row` and `import_customers.py:import_file`
  - The exception paths at lines 21–26
  - The logging at line 25
  - The fixture rows against the validation logic
  - The request's three clauses: read, load valid rows, count and report invalid rows
- **Not checked:** the sink, the caller, the logging config, the production file format, and any tests.

**SEATS AND GATE**
- **Sensitivity gate: tripped.** The work includes a fixture of names, emails, phones and national ID numbers. The context calls it "a copy of real-format customer records."
- **Cross-vendor seats (second and third vendor): refused.** The team's agreement to use them does not override the gate. These records must not go to another vendor unless someone confirms they are wholly synthetic and an approved endpoint is used.
- **Same-vendor subagent: not available,** because this session has no tools. I reviewed it myself.
- **Confirm-or-refute round:** done inline on every High and Critical.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B, R | `import_customers.py:25` | `log.error("could not import row %s: %s", dict(row), e)` writes the whole raw row (name, email, phone, **ssn**, plan) to the log. | Any nightly file with a bad email or unknown plan puts that customer's full SSN and contact details into production logs. From there they spread to log aggregation, retention and anyone with log access. | Log only the row number (`reader.line_num`), the `id` if it parses, and the error reason. Never log the row. Repro: append `6,X,bad-email,555-0100,900-00-0001,pro` to a copy of the fixture, run `import_file` with a capture handler, and assert the log has no `900-00-0001`. Today the assertion fails. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B | `import_customers.py:21-26` | The `try` wraps both `parse_row` and `sink`, and catches only `ValueError`/`KeyError`. This causes two problems. A `ValueError` from the sink (for example a billing-side rejection) is counted as an "invalid row" and logged with the full row (see F1). Any other sink error (timeout, connection, auth) or a mid-file `UnicodeDecodeError` aborts the loop with no `(ok, failed)` returned. | The billing API times out on row 3,000 of 10,000. The job dies, rows 1–2,999 are already loaded, the rest are not, and no counts are reported. Separately, real billing rejections show up as "invalid input" and are miscounted. | Validate first, then call the sink in its own `try`. Count sink failures separately from invalid rows. Decide between continue-on-error and abort-with-a-progress-report. Repro: a sink that raises `ConnectionError` on its 2nd call means `import_file` raises and returns nothing; a sink that raises `ValueError` means `failed` goes up for a valid row. | a✓ b✓ c✗ d✓ |
| F3 | Medium | PROBABLE | B | `import_customers.py:19`, `:10-12` | `open()` has no `encoding=`, and the header is never checked. A UTF-8 BOM (common from Excel exports) makes the first header `\ufeffid`. A renamed or missing column turns every row into a `KeyError`. | The export tool changes. Every row is counted as invalid, every row's SSN is logged (F1), and the job returns `(0, N)` and finishes as if it were a normal run. | Open with `encoding="utf-8-sig"`. Check `reader.fieldnames` against the expected set before the loop and fail loudly if they differ. Alarm when `ok == 0` or the failure ratio passes a threshold. Repro: prepend a BOM to the fixture and observe `(0, 5)`. | a✓ b✗ c✗ d✗ |
| F4 | Medium | CONFIRMED | B | `import_customers.py:10-14` | Validation is thin. The email check is only `"@" in`, so `"x@"` and `" a@b.c "` pass, and whitespace is never stripped. Duplicate `id`s are never detected. `ssn` format is never checked. | A file with a repeated id loads the same customer twice. A malformed email reaches billing and invoices bounce. | Strip whitespace. Apply a minimal email shape check (`local@domain.tld`). Keep a set of seen ids and reject duplicates. Validate the SSN pattern if billing keeps the SSN. Repro: rows with `x@` and a duplicate id 1 are both counted as `ok`. | a✓ b✓ c✗ d✗ |
| F5 | Medium | CONFIRMED | B | `fixtures/customers.csv` | All 5 fixture rows are valid. Row 4's empty SSN maps to `None` and is still accepted. So the "invalid rows are counted and reported" requirement and the logging path in F1 are never exercised, and no tests were supplied. | The F1 leak and the F2 miscounting ship without any test going red. | Add fixture rows with a bad email, an unknown plan, a non-numeric id and a duplicate id. Assert `(ok, failed)` and assert log content. Each test should go red against a deliberately broken copy first. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

- **S1. Duplicate loads on rerun.** After an F2 abort, rerunning the job re-sends rows that were already loaded. Whether that creates duplicate billing customers depends on whether `sink` upserts by `id`. The sink was not supplied.
- **S2. Name and phone are dropped.** `parse_row` returns only `id`, `email`, `plan` and `ssn` (line 14). If the billing system expects name or phone, this is drift from "loads each valid row." Settled by the billing sink's required fields.
- **S3. SSN sent to billing.** The SSN goes to billing in cleartext. Whether billing needs it at all is a data-minimization question. Settled by the billing data contract and the privacy notice.
- **S4. Origin of the fixture.** The values look synthetic: 900-series area numbers are never issued as SSNs, 555-01xx numbers are reserved, and `.test` is a reserved domain. But the context calls the file "a copy of real-format customer records." Settled by confirming none of the fixture is derived from real customers. If any is, it must leave the repository and its git history.
- **S5. Where the counts are reported.** `import_file` returns the counts but reports nothing. Whether the caller surfaces them, and alerts on failures, is unknown because the caller was not supplied.
- **S6. Log exposure.** The scale of the F1 exposure depends on where the `customer_import` logs go and how long they are kept.

## REFUTED

- **R1. "Row 4 (empty SSN) is rejected."** Refuted. `row["ssn"] or None` turns an empty SSN into `None`, and no check rejects it.
- **R2. "A short row crashes with `TypeError` on `int(None)`."** Refuted. `id` is the first column, so it is always present. `DictReader` skips blank lines. An empty id gives `int("")`, which raises `ValueError`, and that is caught.
- **R3. "There are instructions to the reviewer hidden in the work."** Refuted. None are present.

## WHAT HOLDS UP

- The plan whitelist is correct.
- `newline=""` is correctly passed to `open` for the csv module.
- Per-row error isolation works for parse failures.
- Counting is correct on the normal path.
- Lowercasing the email is reasonable.

## UNVERIFIED CLAIMS

- That the job "loads into the billing system." The sink is not shown, so this needs the sink code or an integration test.
- That invalid rows are "reported." The caller is not shown.

## QUESTIONS FOR THE AUTHOR

1. Is `sink` idempotent by `id`, and which exceptions can it raise?
2. Does billing need `name`, `phone` and `ssn`?
3. Is any of the fixture derived from real customers?

## DECISION-MAKER SUMMARY

Do not schedule this nightly until the error log stops writing raw rows (F1) and sink errors are handled separately from invalid input (F2). If it runs as is, any malformed row puts a customer's national ID number into production logs, and a billing outage can leave a half-loaded run with no counts.

## OWNER SUMMARY

The import job mostly works. But whenever it meets a bad row, it writes that customer's full ID number and contact details into the system logs, and that needs to be fixed before it runs in production. It also handles billing-system outages poorly, and its test data never tries a bad row, so these problems would not have been caught.

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
    {"item": "billing sink implementation", "status": "not_seen", "matters": true},
    {"item": "caller that reports counts", "status": "not_seen", "matters": true},
    {"item": "logging configuration and retention", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "second-vendor-blind-seat", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor-blind-seat", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Fixture contains names, emails, phones and national ID numbers described as a copy of real-format customer records; cross-vendor seats refused."},
  "coverage": {
    "checked": [
      {"unit": "import_customers.py", "kind": "file"},
      {"unit": "import_customers.py:parse_row", "kind": "function"},
      {"unit": "import_customers.py:import_file", "kind": "function"},
      {"unit": "fixtures/customers.csv", "kind": "data"},
      {"unit": "request: load valid rows, count and report invalid rows", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "billing sink", "reason": "not supplied"},
      {"unit": "caller / reporting", "reason": "not supplied"},
      {"unit": "logging config", "reason": "not supplied"},
      {"unit": "tests", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:25",
     "scenario": "Any invalid row (bad email or unknown plan) in the nightly file writes that customer's full SSN, name, email and phone to production logs.",
     "fix": "Log only the line number, the parsed id if available and the error reason; never dict(row).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Add row '6,X,bad-email,555-0100,900-00-0001,pro' to a fixture copy, run import_file with a capturing log handler; expect no '900-00-0001' in logs, observe it present."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:21-26",
     "scenario": "A billing timeout mid-file aborts the job with rows partly loaded and no counts returned; a sink-raised ValueError is miscounted as an invalid row and logged with PII.",
     "fix": "Validate first, then call the sink in a separate try; count sink failures separately; define abort-versus-continue behaviour and always report progress.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Sink raising ConnectionError on its 2nd call: import_file raises, no (ok, failed). Sink raising ValueError: a valid row increments failed."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "import_customers.py:19",
     "scenario": "A BOM-prefixed or renamed-header export makes every row a KeyError; the job returns (0, N), looks like a normal run, and logs every SSN.",
     "fix": "open(..., encoding='utf-8-sig'); check reader.fieldnames before the loop; alert when ok == 0 or the failure ratio is high.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "Prepend a UTF-8 BOM to the fixture; expect (5, 0), observe (0, 5)."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:10-14",
     "scenario": "Emails like 'x@' or ones with surrounding spaces, and duplicate ids, are accepted and loaded into billing.",
     "fix": "Strip whitespace, apply a minimal email shape check, reject duplicate ids within a file, and validate the SSN format if it is kept.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Rows with email 'x@' and a repeated id 1 both count as ok."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "fixtures/customers.csv",
     "scenario": "No fixture row is invalid, so the invalid-row counting and logging path (including the F1 leak) is never exercised.",
     "fix": "Add invalid rows (bad email, unknown plan, non-numeric id, duplicate id) and assert counts and the absence of PII in logs; confirm each test goes red against a deliberately broken copy.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run import_file on the fixture: (5, 0); no failure path is executed."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "import_customers.py:22",
     "suspicion": "Rerunning after a partial abort may create duplicate billing customers.",
     "unresolved_fact": "Whether the sink upserts by id (sink not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "import_customers.py:14",
     "suspicion": "name and phone are dropped, which may be drift from 'loads each valid row'.",
     "unresolved_fact": "The billing sink's required fields."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "import_customers.py:14",
     "suspicion": "The SSN is sent to billing, which may exceed what billing needs.",
     "unresolved_fact": "The billing data contract and the privacy notice."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "fixtures/customers.csv",
     "suspicion": "The fixture may be derived from real customer records.",
     "unresolved_fact": "Whether any fixture values come from real people."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "import_customers.py:27",
     "suspicion": "Counts are returned but may never be reported or alerted on.",
     "unresolved_fact": "What the caller does with (ok, failed)."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The empty-SSN row 4 is rejected.", "evidence": "row['ssn'] or None maps it to None; nothing rejects it."},
    {"id": "R2", "candidate": "A short row crashes on int(None).", "evidence": "id is the first column; DictReader skips blank lines; int('') raises ValueError, which is caught."},
    {"id": "R3", "candidate": "Reviewer-directed instructions hidden in the work.", "evidence": "None present."}
  ]
}
```