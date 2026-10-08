**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools or subagent were available here, so nothing was executed. Every claim about Python behaviour is reasoned from the standard library's documented semantics.

**VERDICT: REWORK.** Every rejected row is written to the log in full, including the national ID number, on a production job that runs nightly. A billing outage also crashes the run partway through and leaves an import that cannot be safely re-run.

**CONFIDENCE: medium.** It is limited by:
- same-context review with no tools, so no code or tests were run;
- no billing sink or schema supplied;
- no tests supplied;
- cross-vendor seats refused (see below).

**INPUTS LEDGER**

| Item | Status | Matters |
|---|---|---|
| request.md (original request) | seen | — |
| context.md | seen | — |
| `import_customers.py` | seen | — |
| `fixtures/customers.csv` | seen | — |
| Billing sink implementation and schema (which fields it accepts, how it fails, whether it is idempotent) | not seen | yes: decides findings 2, 3 and 6 |
| Tests | not supplied | yes: no evidence the invalid-row path was ever exercised |
| Logging configuration and log destination or retention | not seen | yes: decides how far finding 1 spreads |
| Entry point or scheduler that runs the job nightly and "reports" the counts | not seen | yes: finding 7 |
| Provenance of the fixture data | not seen | yes: finding 4 |

**SEATS AND GATE**
- **Sensitivity gate: tripped.** The context says the fixture is "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)". The code also processes SSNs.
- **Cross-vendor seats (second and third vendor): refused.** The team's standing agreement to use cross-vendor seats does not override the gate. National ID numbers may not be sent to another vendor's model without confirmation that the data is synthetic, or an approved zero-retention endpoint. If the fixture is confirmed synthetic and the code is reviewed without it, the seats can be re-run.
- **Fresh same-vendor subagent: unavailable** (no tools in this session).
- **Ran:** this reviewer only.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B, R | `import_customers.py:25` | `log.error("could not import row %s: %s", dict(row), e)` logs the whole raw row: name, email, phone, **SSN**, plan. | Any invalid row, such as a typo in `plan`, writes a full SSN into production logs every night. Logs are typically shipped to aggregators and kept with broad access, which creates a reportable PII exposure. | Log only the row number (`reader.line_num`), the id if it parses, and the error reason. Never log `row`. Add a test asserting that log output contains no SSN pattern. | confirmed: the format string interpolates the whole dict and no masking happens anywhere. |
| 2 | High | CONFIRMED (omission) / PROBABLE (impact) | B | `import_customers.py:14` | `parse_row` drops `name` and `phone`. Only id, email, plan and ssn reach billing. | The request says to load "each valid row", but the billing system receives customers with no name or phone. The run reports success while records are incomplete. | Map every requested column, or document which fields billing takes. Add a test asserting the sink receives name and phone. | confirmed as drift unless the billing schema shows those fields are not accepted (Q1). |
| 3 | High | CONFIRMED | B | `import_customers.py:22-24` | Only `ValueError` and `KeyError` are caught, and the sink call sits inside the same `try`. | (a) The billing API times out or raises a connection or HTTP error, so the job aborts mid-file. Rows already sent stay loaded, later rows are never attempted or counted, and a re-run re-sends rows 1..k, which can mean duplicate customers or charges. (b) If the sink raises `ValueError`, a billing failure is counted as an "invalid row", so the report misstates data quality. | Separate validation from loading: count validation failures and sink failures in separate counters. Catch sink errors per row, with retry and timeout. Make loads idempotent (upsert by id). Report partial runs explicitly. | confirmed: the defender's reply "the sink never raises" is not supported by any provided code. |
| 4 | High | UNVERIFIED | R | `fixtures/customers.csv` and context.md | The context calls the fixture "a copy of real-format customer records" with national ID numbers, committed to the repository. | If any row is real, SSNs and contact data now sit in git history and in every clone and CI cache. That is Critical-level exposure and hard to purge. The values look synthetic (900-series SSNs, 555-01xx phones, `.test` domain), which conflicts with the context's wording. | Confirm provenance in writing. If any row is real, remove it from history and treat it as an incident. In either case, generate fixtures from a documented synthetic generator. | held as UNVERIFIED: the visible values support "synthetic", and the context's wording supports "copied". |
| 5 | High | CONFIRMED (stdlib behaviour) | B | `import_customers.py:19-20` | `open(path, newline="")` has no `encoding`, so the default is locale-dependent, and it does not handle a UTF-8 byte-order mark (BOM). | A spreadsheet export with a BOM makes the first header `'\ufeffid'`. Every `row["id"]` then raises `KeyError`, every row is counted invalid, and nothing loads, yet the job "succeeds" with ok=0. Non-UTF-8 input raises `UnicodeDecodeError` outside the `try` and crashes the run. | Use `encoding="utf-8-sig"`. Validate the header against the expected columns once and fail the run loudly if it does not match. Add a fixture with a BOM. | confirmed |
| 6 | Medium | PROBABLE | B | `import_customers.py:9-14` | Validation is minimal: email only needs to contain `@`; duplicate ids are not detected; `plan` is case- and whitespace-sensitive (`"Pro"` or `" pro"` is rejected); `ssn`, `phone` and `name` are not validated; empty `ssn` becomes `None` without checking whether billing requires it. | A duplicate id in the nightly file is loaded twice. A trailing space in `plan` rejects good customers. `a@` passes as a valid email. | Strip and normalise fields. Track seen ids. Agree the validity rules (Q2) and test each one. | — |
| 7 | Medium | CONFIRMED | A, B | `import_customers.py:27` | "Invalid rows are counted and reported", but the job only returns `(ok, failed)`. There is no summary, per-reason breakdown or alert, and no entry point. | The nightly run rejects 40% of rows and nobody notices, because only the per-row logs (which leak PII, see finding 1) record it. | Emit a summary (counts by reason) and alert above a threshold. Add a `main` that returns non-zero on partial failure. | — |
| 8 | Medium | CONFIRMED | B | `fixtures/customers.csv` | All five fixture rows are valid. No test exercises the invalid path, a sink failure, malformed CSV or a duplicate id. | Findings 1, 3 and 5 would ship unseen. A test can only be trusted once it has been seen to fail. | Add invalid, BOM, duplicate and sink-error fixtures. Confirm each test goes red against a deliberately broken copy. | — |
| 9 | Medium | CONFIRMED | B | `import_customers.py:20` | A `csv.Error` raised by the reader (oversized field, NUL byte) comes from the iterator, outside the `try`. | One corrupt line aborts the whole nightly import after a partial load. | Wrap the iteration, count the malformed line, and decide on continue-or-abort explicitly. | — |
| 10 | Low | PROBABLE | B, R | `import_customers.py:14` | The SSN is forwarded to billing, and email is lower-cased. | If billing does not need SSNs, this spreads PII without need (data minimisation, privacy notice scope). Lower-casing can also merge distinct mailbox identities in rare systems. | Confirm billing needs the SSN; drop it if not. | — |

## WHAT HOLDS UP
- Plan validation against a closed set.
- `newline=""` is correct for the `csv` module.
- Per-row `try` so that one bad row does not stop validation of the rest.
- Empty `ssn` is normalised to `None` rather than `""`.
- `int(row["id"])` failures are caught as `ValueError`.
- Short rows: `DictReader` fills missing trailing fields with `None`, and the email check `not None` rejects them cleanly.

## UNVERIFIED CLAIMS
- That the fixture is safe to commit. Settle it with a provenance statement or the name of the generator used (finding 4).
- That the sink's failure modes are limited to `ValueError` and `KeyError`. Settle it by reading the sink code.
- That the job "reports" invalid rows anywhere beyond the logs. Settle it by finding the caller or scheduler.

## QUESTIONS FOR THE AUTHOR
1. Which fields does the billing system accept? Are name and phone meant to be dropped, and is the SSN needed at all?
2. What counts as a valid row: is the SSN required, how strict is email, and what happens with duplicate ids?
3. Is the fixture synthetic? If so, generated by what?
4. Is the billing load idempotent by customer id?

## DECISION-MAKER SUMMARY
Do not deploy. As written, the job will put customers' SSNs into production logs on any bad row, and an outage of the billing API will leave a partial load that duplicates records if re-run. Fix findings 1, 3 and 5, confirm the fixture's provenance (finding 4), resolve the dropped name and phone (finding 2), then re-review with fresh, non-sensitive inputs.

## OWNER SUMMARY
The customer import is not ready for nightly production use. Whenever it rejects a record, it copies that customer's full details, including their national ID number, into system logs. If the billing system has a hiccup, it stops halfway in a way that can create duplicates when re-run. It also leaves out customer names and phone numbers, and the sample data may contain real personal information that needs to be checked and possibly removed.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "billing sink implementation/schema", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_supplied", "matters": true},
    {"item": "logging config and destination", "status": "not_seen", "matters": true},
    {"item": "job entry point / scheduler", "status": "not_seen", "matters": true},
    {"item": "fixture provenance", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "second-vendor", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Fixture described as a copy of real-format customer records including national ID numbers; code processes SSNs. Team's standing cross-vendor agreement does not override the gate."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B,R", "location": "import_customers.py:25", "scenario": "Any invalid row logs dict(row) including full SSN, name, email and phone to production logs nightly.", "fix": "Log only line number, parsed id and reason; test that logs contain no SSN pattern.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py:14", "scenario": "name and phone are dropped; billing receives incomplete customers despite 'load each valid row'.", "fix": "Map all requested columns or document billing schema; test sink payload.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py:22-24", "scenario": "Sink network/HTTP error aborts run mid-file leaving partial, non-idempotent load; sink ValueError miscounted as invalid row.", "fix": "Separate validation and load counters, per-row sink error handling with retry/timeout, idempotent upsert, explicit partial-run reporting.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "R", "location": "fixtures/customers.csv; context.md", "scenario": "If fixture rows are real, SSNs and contact data are in git history and every clone.", "fix": "Confirm provenance; purge history and treat as incident if real; use a documented synthetic generator.", "status": "held"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py:19-20", "scenario": "BOM-prefixed CSV makes header '\\ufeffid', every row KeyErrors, zero rows load while the job 'succeeds'; non-UTF-8 input crashes outside the try.", "fix": "encoding='utf-8-sig', validate header once and fail loudly; add BOM fixture.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "import_customers.py:9-14", "scenario": "Duplicate ids loaded twice; ' pro' or 'Pro' rejected; 'a@' accepted; ssn/phone/name unvalidated.", "fix": "Normalise fields, track seen ids, agree and test validity rules.", "status": ""},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A,B", "location": "import_customers.py:27", "scenario": "Counts are only returned; no summary, breakdown or alert, so mass rejection goes unnoticed.", "fix": "Emit per-reason summary, alert on threshold, non-zero exit on partial failure.", "status": ""},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "fixtures/customers.csv", "scenario": "All fixture rows are valid; invalid, BOM, duplicate and sink-error paths are untested.", "fix": "Add those fixtures and confirm each test fails against a broken copy.", "status": ""},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py:20", "scenario": "csv.Error from the reader (oversized field, NUL byte) is raised outside the try and aborts the run after a partial load.", "fix": "Wrap iteration, count malformed lines, decide continue/abort explicitly.", "status": ""},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B,R", "location": "import_customers.py:14", "scenario": "SSN forwarded to billing without demonstrated need; email lower-casing may merge identities.", "fix": "Confirm billing needs SSN; drop if not.", "status": ""}
  ]
}
```