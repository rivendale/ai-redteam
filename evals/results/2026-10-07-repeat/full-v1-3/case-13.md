# Redteam Report: `import_customers.py` and `fixtures/customers.csv`

**Review setup:** This was a single-seat review. The cross-vendor blind seats named in the context were **not run**, because this session has no tools and no subagent. I did not produce this work, so author anchoring is limited, but nothing was executed. Every CONFIRMED finding below comes from reading the code and from documented Python `csv` and `open` behavior.

**Before anyone dispatches the cross-vendor seats:** the context calls the fixture "a copy of real-format customer records." Sending it to another vendor's model publishes it outside the org. The values look synthetic:
- `555-01xx` is the reserved fictional phone range.
- `900-xx-xxxx` is not a valid SSN area number.
- `.test` is a reserved domain.

The names, however, could be real people. Confirm the fixture is fully synthetic first, or send the seats only the code and a redacted fixture.

---

**VERDICT: REWORK.** The job writes full SSNs and contact details in plaintext to the logs on every failed row. It also silently drops `name` and `phone` from the loaded records, and any sink failure aborts the nightly run partway through.

**CONFIDENCE IN VERDICT: high.** The top findings can be read directly off the code. Confidence is limited by: no execution, no view of the `sink`/billing API contract, and no cross-vendor seats.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `import_file`: `log.error("could not import row %s: %s", dict(row), e)` | Logs the whole raw row on failure: name, email, phone, **SSN**. | Any row with a bad email or plan, e.g. `plan=Pro`, writes a full SSN into production logs every night. Logs usually have wider access and longer retention than the billing DB, and are often shipped to third-party aggregators. This is legal exposure (breach notification, GLBA/state SSN laws). | Log only the row number (`reader.line_num`) and `id` plus the reason. Never log raw rows. Add a test: a bad row's log output contains no `ssn`, `email`, or `phone` value. Purge the logs from any run that already happened. |
| 2 | High | CONFIRMED | `parse_row` return dict | `name` and `phone` are read but never passed to the sink. The request says to load "each valid row" with id, name, email, phone, ssn, plan. | Every customer reaches billing with no name or phone. The counts report full success, so the drop goes unnoticed. | Include `name` and `phone`, or get an explicit documented decision that billing must not receive them. Add a test that asserts the exact dict passed to the sink. |
| 3 | High | CONFIRMED | `except (ValueError, KeyError)` around `sink(...)` | Sink errors are mishandled in two ways. (a) Network errors, timeouts, and auth errors are not caught, so the job aborts partway through the file and never reports counts. (b) A `ValueError`/`KeyError` raised *by the sink* is counted as an "invalid row." | (a) Billing API times out on row 4,000 of 10,000. Rows 1 to 3,999 are loaded, the rest are not, and no report is produced. Tomorrow's rerun re-sends 1 to 3,999 (see #4). (b) A billing-side rejection is reported as a data problem. | Separate validation from loading. Validate first and count invalid rows. Wrap `sink` with its own handling (retry or timeout policy), record load failures separately, and always emit a final report (`try/finally`). |
| 4 | High | UNVERIFIED | `sink(parse_row(row))` | Nothing makes reruns idempotent, and duplicate `id`s within a file are not detected. | Partial run followed by nightly rerun, or two rows with the same id: if the sink inserts rather than upserts, customers are duplicated or double-billed. | Confirm the sink upserts by `id`. Reject duplicate ids within a file. Add a rerun test. |
| 5 | Medium | CONFIRMED | `open(path, newline="")` | No `encoding` is given, so the locale default applies. A UTF-8 BOM makes the first header `"\ufeffid"`. | A file exported from Excel with a BOM: every row raises `KeyError('id')`, so `ok=0, failed=N`. The job "completes" and loads nothing. Non-UTF-8 bytes raise an uncaught `UnicodeDecodeError` and abort the job. | Use `encoding="utf-8-sig"`. Validate the header set once before processing rows and fail the run if columns are missing. |
| 6 | Medium | CONFIRMED | `import_file` return value | "Reported" means only a returned tuple plus log lines. There is no failure threshold and no non-zero exit. | 100% of rows invalid (wrong header, wrong file) and the nightly scheduler still shows success. | Emit a summary (counts plus row numbers and reasons, no PII). Exit non-zero when the failure rate exceeds a threshold or `ok == 0`. |
| 7 | Medium | CONFIRMED | `parse_row` validation | Validation is minimal: `"@" in email` only; no whitespace stripping; `plan` is case-sensitive; `ssn` and `phone` are not validated at all; `name` is not checked. | `" pro"` or `"Pro"` is rejected as invalid. `"a@"` and `" x@y.com "` are accepted. `ssn="N/A"` or `"123"` is sent to billing as an SSN. | Strip fields. Normalize plan case. Validate SSN format (or omit SSN if billing does not need it; see Q2). Apply basic phone and email checks. Add a test for each rule. |
| 8 | Medium | CONFIRMED | `fixtures/customers.csv` | The fixture has no invalid rows. Row 4's empty SSN is valid by the code's rules. No tests are shown. | The "invalid rows are counted" path and the logging path (#1) are never exercised, which is why #1 and #2 would pass CI unnoticed. | Add fixture rows for: bad email, unknown plan, missing column, BOM, duplicate id, non-numeric id. Assert the counts, the sink payloads, and the log contents. |
| 9 | Low | PROBABLE | `fixtures/customers.csv` (whole file) | The context describes it as a "copy of real-format customer records" committed to the repo. | If any names are real (only the identifiers look synthetic), real PII sits in git history and would go to external vendors during the cross-vendor review. | Confirm it is fully synthetic and state so in a header or README. If it is not, remove it from history. |

## What holds up

- Using `csv.DictReader` with `newline=""` is the correct way to read the file. Quoted commas and embedded newlines are handled.
- Per-row `try/except` means one bad row does not kill the run for validation errors.
- `int(row["id"])` raising `ValueError` on a non-numeric id is correctly counted as invalid.
- Short rows (missing trailing fields become `None`) fall into the email or plan checks and are counted, not crashed on.
- Converting an empty SSN to `None` is reasonable.

## Unverified claims

- **Sink contract:** what exceptions it raises, whether it is idempotent or upserts, and whether it accepts SSN at all. Settle this by reading the billing client code or its API docs.
- **Fixture provenance:** synthetic or derived from real records. Settle this by asking the author or the data owner.
- **The behaviors described for findings 5 and 7** are standard Python behavior but were not executed here. Settle them by running the suggested tests.

## Questions for the author

1. Did the omission of `name` and `phone` from the sink payload happen on purpose?
2. Does the billing system actually need the SSN? If not, dropping it removes most of the exposure in #1 and #7.
3. Is the sink an upsert keyed on `id`, and what does it raise on failure?
4. Is every value in `fixtures/customers.csv`, names included, synthetic?

## Decision-maker summary

Do not ship as is. The job logs full SSNs on any bad row and silently loads customers without names or phones, and both would pass the current fixture unnoticed. Fix #1 through #3, add the negative-case fixture and tests, and confirm the fixture is synthetic before sending it to the cross-vendor seats. If it ships anyway, expect SSNs in production logs, partial loads on billing outages, and possible duplicates on rerun.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "import_file: log.error(\"could not import row %s: %s\", dict(row), e)", "scenario": "Any invalid row (e.g. plan='Pro') writes name, email, phone and full SSN to production logs nightly; logs have wider access/retention than billing DB.", "fix": "Log only line number, id and reason; test that failure logs contain no ssn/email/phone; purge existing logs."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "parse_row return dict", "scenario": "name and phone are never passed to the sink; every customer lands in billing without them while counts report success.", "fix": "Include name and phone (or document explicit exclusion); test exact sink payload."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "import_file: except (ValueError, KeyError) around sink(...)", "scenario": "Sink timeout/network error aborts the job partway with no report; sink-raised ValueError is miscounted as an invalid row.", "fix": "Validate separately from loading; handle sink errors with retry/timeout, count load failures separately, always emit final report."},
    {"severity": "High", "evidence_level": "UNVERIFIED", "location": "import_file: sink(parse_row(row))", "scenario": "Partial run then nightly rerun, or duplicate ids in file, duplicates customers if sink inserts rather than upserts.", "fix": "Confirm upsert-by-id; reject duplicate ids in-file; add rerun test."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "import_file: open(path, newline=\"\")", "scenario": "UTF-8 BOM makes header '\\ufeffid' so every row raises KeyError and nothing loads while job completes; non-UTF-8 bytes raise uncaught UnicodeDecodeError.", "fix": "encoding='utf-8-sig'; validate header once and fail the run on missing columns."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "import_file return (ok, failed)", "scenario": "100% invalid rows still looks like a successful nightly run; no report artifact or non-zero exit.", "fix": "Emit PII-free summary; exit non-zero above a failure threshold or when ok == 0."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "parse_row validation", "scenario": "' pro'/'Pro' rejected; 'a@' accepted; malformed ssn like 'N/A' sent to billing; phone/name unchecked.", "fix": "Strip and normalize fields; validate SSN/phone/email formats or drop SSN; per-rule tests."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "fixtures/customers.csv", "scenario": "No invalid rows in fixture, so the counting and logging paths are never exercised and findings 1-2 pass CI.", "fix": "Add rows for bad email, unknown plan, missing column, BOM, duplicate id, non-numeric id; assert counts, payloads, log contents."},
    {"severity": "Low", "evidence_level": "PROBABLE", "location": "fixtures/customers.csv (whole file)", "scenario": "Described as a copy of real-format records; if names are real, PII is in git history and would be sent to external vendors in the cross-vendor review.", "fix": "Confirm fully synthetic and document it; otherwise remove from history and redact before any external review."}
  ]
}
```