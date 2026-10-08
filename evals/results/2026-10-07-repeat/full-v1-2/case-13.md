# Redteam Report: `import_customers.py` + `fixtures/customers.csv`

**Review setup and limits**
- **Cross-vendor seats did not run.** The context asks for a deep review with a second and third vendor's model as blind seats. I have no tools in this session, so I could not dispatch them. This is a **single-model review**; treat it as one seat of the agreed process, not the whole thing.
- **Before you send this to other vendors, check what the fixture is.** The context calls `fixtures/customers.csv` "a copy of real-format customer records." The values look synthetic (`900-` SSN prefix, `555-01xx` phones, `example.test` domains). If any row came from real records, sending it to outside model vendors would publish PII. Confirm the fixture is synthetic, or redact it, before those seats run.
- **Nothing was executed.** All traces below are by reading. The work was not produced in this conversation, so there is no same-context anchoring risk.

---

**VERDICT: REWORK.** The job writes full PII, including SSNs, into production logs every night. It also cannot tell bad data apart from billing-system failures, and the invalid-row path has no tests.

**CONFIDENCE IN VERDICT: medium-high.** The core findings come from tracing exact lines. Confidence is limited because nothing was run, the sink's behavior is unknown, and the cross-vendor seats are missing.

## Pass 1: Reconstruct

The code streams the CSV with `csv.DictReader` and validates each row:
- email must be non-empty and contain `@`
- plan must be one of `basic`, `pro`, `team`
- `id` must parse as an integer

Each valid row becomes `{id, email, plan, ssn}` and is passed to `sink`. Rows that fail are logged and counted, and the function returns `(ok, failed)`.

Load-bearing assumptions:
1. `sink` only raises `ValueError` or `KeyError` for bad data and never for infrastructure problems.
2. Logs are safe for PII.
3. Billing needs the SSN but does not need name or phone.
4. Returning counts is enough to satisfy "reported."
5. The file arrives in the platform's default encoding with no BOM.
6. Re-running the job is safe.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `log.error("could not import row %s: %s", dict(row), e)` | The whole raw row is logged on failure: name, email, phone and SSN. | A row with a typo in `plan` fails. Its SSN lands in production logs, which get shipped, indexed and retained. If many rows fail (see #5), every customer's SSN is logged. | Log only the row number (`reader.line_num`), `id`, and the error class or message. Add a test that captures the log output and asserts no SSN, email or phone appears in it. |
| 2 | High | CONFIRMED | `except (ValueError, KeyError)` around `sink(...)` | Errors raised by `sink` are handled in two wrong ways. (a) If the sink raises `ValueError` or `KeyError`, for example a rejected duplicate id, the row is counted as "invalid" and the whole row is logged per #1. (b) Any other exception (network, timeout, `TypeError`) aborts the job partway through the file. | Billing has an outage at row 40,000. The job crashes, rows 1 to 39,999 are already loaded, no counts are reported, and the nightly run is half-applied. | Wrap `parse_row` and `sink` in separate handlers. Count validation failures and sink failures separately. Decide whether sink errors abort or retry, and make that explicit. Test with a sink that raises each exception type. |
| 3 | High | PROBABLE | `"ssn": row["ssn"] or None` in `parse_row` | The SSN is forwarded to billing. The request does not show that billing needs a national ID number. That adds an unneeded PII flow and makes a breach in the billing system worse. | Billing stores SSNs it never uses, which creates compliance exposure (data minimization). | Confirm with the billing owner whether the SSN is required. If it is not, drop it. If it is, validate its format and document the reason. |
| 4 | Medium | CONFIRMED | The return dict in `parse_row` | `name` and `phone` are silently dropped. The request says to load "each valid row" and lists six columns, but only four are sent. | Billing records are created with no customer name. | Pass `name` and `phone` through, or have the request owner confirm the cut in writing. |
| 5 | Medium | PROBABLE | `open(path, newline="")` | No `encoding` is given, so the platform default is used, and a BOM is not handled. With a UTF-8 BOM the header becomes `\ufeffid`, so `row["id"]` raises `KeyError` on every row. | An export tool adds a BOM. Every row is counted as failed and every row is logged with its PII. Non-ASCII names may also mis-decode under a non-UTF-8 locale. | Use `encoding="utf-8-sig"`. Before looping, check that the header matches the expected columns and fail fast if it does not. Add a BOM fixture test. |
| 6 | Medium | CONFIRMED | `import_file` return value | "Invalid rows are counted and reported" is only half done. The function returns a tuple and produces no report and no breakdown by failure reason. A file that is empty or has only a header returns `(0, 0)` and looks like success. | A truncated upstream file arrives. The nightly job loads nothing and nobody notices. | Emit a summary with total, ok, and failed by reason. Treat zero rows, or a failure rate above a threshold, as an alerting condition. |
| 7 | Medium | CONFIRMED | `fixtures/customers.csv` | The fixture contains no invalid rows. Row 4 has an empty SSN, which is valid under this code. The "invalid rows" requirement is never exercised, and no test file was provided. | A regression in validation or counting ships unnoticed. | Add fixture rows for a bad email, an unknown plan, a non-integer id, a short row, an extra column and a duplicate id. Assert the exact `(ok, failed)` values and the log content. |
| 8 | Medium | UNVERIFIED | Whole job | Idempotency on re-run is unknown. Combined with the partial load in #2, re-running after a crash may create duplicate billing records unless the sink upserts by `id`. Duplicate ids within one file are also not detected. | The job crashes and is re-run, and customers end up with two billing records. | Confirm the sink's semantics. Track the ids already seen in the file. Test a second run against the same sink. |
| 9 | Low | CONFIRMED | Validation in `parse_row` | Validation is shallow. Any string containing `@` passes as an email. The plan check is exact, so `" pro"` and `"Pro"` are rejected. The SSN format is not checked. | Whitespace or casing introduced by a spreadsheet export causes mass rejections. Garbage emails get loaded. | Strip whitespace and lowercase `plan`. Use a basic email pattern. Validate the SSN format if it is kept. |

## What holds up
- Reading is streamed, so memory stays flat on large files.
- `newline=""` is used correctly with the `csv` module.
- Short rows (fields come through as `None`) are rejected cleanly by the email check.
- A non-integer `id` raises `ValueError` and is counted as failed.
- An empty SSN normalizes to `None`.

## Unverified claims
- **Fixture is synthetic.** Confirm with the fixture's provenance or its generator script.
- **Billing needs the SSN.** Confirm with the billing API contract.
- **Sink exception and upsert behavior.** Confirm from the sink's code or docs, plus a test with a fake sink.
- **Log destination and retention.** Confirm in the logging configuration.

## Questions for the author
1. Does billing need the SSN, and should name and phone be loaded?
2. What does `sink` raise, and does it upsert by `id`?
3. Is the fixture synthetic or derived from real records?
4. What counts as a "report": a return value, an emitted summary, or an alert?

## Decision-maker summary
Do not run this nightly in production until the PII logging (#1) and the sink error handling (#2) are fixed and invalid-row tests exist. If it runs as is, SSNs will accumulate in logs, and any billing outage leaves a partial, unreported load. Confirm the fixture is synthetic before the cross-vendor seats are sent the code and data.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "import_customers.py: log.error(\"could not import row %s: %s\", dict(row), e)", "scenario": "Any failing row writes name, email, phone and SSN to production logs nightly; a header/BOM issue logs every customer's SSN.", "fix": "Log only line number, id and error; add a test asserting no PII appears in captured logs."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "import_customers.py: except (ValueError, KeyError) wrapping sink(parse_row(row))", "scenario": "Sink ValueError/KeyError is miscounted as invalid data and logged with PII; any other sink exception (network outage) aborts mid-file, leaving a partial load and no counts.", "fix": "Separate parse and sink error handling, count each separately, define abort/retry policy; test with a sink raising each exception type."},
    {"severity": "High", "evidence_level": "PROBABLE", "location": "import_customers.py: parse_row return, \"ssn\": row[\"ssn\"] or None", "scenario": "SSN is forwarded to billing without an established need, adding PII exposure in the billing system.", "fix": "Confirm billing needs SSN; drop it if not, validate format if so."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "import_customers.py: parse_row return dict", "scenario": "name and phone are silently dropped; billing records are created without a customer name.", "fix": "Pass name and phone through, or get explicit sign-off on the scope cut."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "location": "import_customers.py: open(path, newline=\"\")", "scenario": "A UTF-8 BOM makes the header key '\\ufeffid', so every row raises KeyError, fails and is logged with PII; the locale-default encoding mis-decodes names.", "fix": "Use encoding='utf-8-sig', validate the header up front and fail fast; add a BOM fixture test."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "import_customers.py: import_file return (ok, failed)", "scenario": "No report or failure-reason breakdown is produced; an empty or truncated file returns (0, 0) and looks like success.", "fix": "Emit a summary by reason; alert on zero rows or a high failure rate."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "fixtures/customers.csv", "scenario": "The fixture has no invalid rows, so the counting and reporting requirement is untested and regressions ship unnoticed.", "fix": "Add bad-email, unknown-plan, bad-id, short-row and duplicate-id rows; assert exact counts and log content."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "location": "import_customers.py: import_file (whole job)", "scenario": "Re-running after a partial failure may duplicate billing records if the sink does not upsert; duplicate ids within a file are not detected.", "fix": "Confirm sink upsert semantics, track seen ids, test a second run against the same sink."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "import_customers.py: parse_row validation", "scenario": "Plan values ' pro' or 'Pro' are rejected en masse; any string containing '@' passes as an email; SSN format is unchecked.", "fix": "Strip and lowercase plan, use a basic email pattern, validate SSN format if it is kept."}
  ]
}
```