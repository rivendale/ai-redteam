# Redteam report: `import_customers.py` (customers CSV to billing import)

> **Single-reviewer, no-tools review.** No subagent and no seats were available, and nothing was run. Every behavioral claim below comes from reading the code. Re-run in a fresh session with tools before relying on this for production.

**VERDICT: REWORK.** The job writes full customer records, including national ID numbers, to the error log for every rejected row. It also silently drops name and phone, and it treats billing-system failures as "invalid rows".

**CONFIDENCE: medium.** Limits: no tools, so no code or tests were run. The billing sink's contract and the real CSV export format were not supplied. The cross-vendor seats were refused (see below).

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| Original request (`request.md`) | seen | n/a |
| Context (`context.md`) | seen | n/a |
| `import_customers.py` | seen | n/a |
| `fixtures/customers.csv` | seen | n/a |
| `__pycache__/import_customers.cpython-312.pyc` | seen, partially readable; matches the source as far as legible | no |
| `sink` (billing client): its signature, errors, idempotency and required fields | **not seen** | **yes**: findings 3 and 6 depend on it |
| A sample of the real nightly export (encoding, BOM, header casing) | **not seen** | **yes**: finding 5 |
| Tests | **none supplied**, and the work claims none | yes: finding 7 |
| Log destination, retention and access controls | **not seen** | yes: affects how bad finding 1 is |

**SEATS AND GATE**
- **Sensitivity gate: triggered.** The context describes `fixtures/customers.csv` as "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)". The code also handles SSNs by design.
- **Cross-vendor seats (2nd and 3rd vendor): refused.** Even though the team agreed to them for its changes, this work contains or handles national ID numbers and personal data. A second opinion is not a reason to send that data to another vendor.
- **Same-vendor subagent: unavailable**, because there are no tools in this session.
- **What ran:** this single local review only.
- **To get independent seats:** re-run with a scrubbed fixture (synthetic, clearly fake IDs) and only on endpoints approved for this data.

### Pass 1: Reconstruct

The work claims to:
- read the customers CSV;
- validate email (non-empty, contains "@"), plan (one of basic, pro, team) and id (an integer);
- send each valid row to `sink`;
- count rejected rows, log them, and return `(ok, failed)`.

For this to be correct, all of the following must hold:
- the billing system needs exactly `{id, email, plan, ssn}`;
- `sink` raises only on real outages, never with `ValueError` or `KeyError` for a business rejection;
- the CSV is clean UTF-8 with exactly these headers;
- the logs are an acceptable place for full customer records;
- re-running nightly is safe.

Tracks: **B** (code), **R** (personal data in logs and records), and **A** (fit to the request).

### Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | **Critical** | CONFIRMED | R, B | `import_customers.py` `import_file`, `log.error("could not import row %s: %s", dict(row), e)` | Every rejected row is logged in full: name, email, phone, **SSN** and plan. | Nightly, any row with a bad email or plan (or every row, if the header drifts; see #5) writes national ID numbers into application logs. Log shippers, retention and broad access make this a data-exposure and regulatory problem, and it repeats every night. | Log only the line number (`reader.line_num`), the id (if it parses) and the reason. Never log `dict(row)`. Test: feed a row with a bad plan, capture the logs, and assert that no SSN pattern or email appears. | **confirmed.** Defender's case: "the logs are access-controlled". Even so, SSNs in general-purpose logs are not minimized, and the log setup was not supplied. |
| 2 | **High** | CONFIRMED (code); PROBABLE (drift) | A, B | `parse_row` return dict | `name` and `phone` are read but never sent to billing. The request says to load *each valid row*. | Customers are created in billing with no name or phone. Invoices and dunning go out without names, and support cannot match customers. | Either map all the fields billing needs, or have the author state the billing schema explicitly and document the omission. | **confirmed** that the fields are dropped. Defender's case: "billing doesn't need them". That cannot be known without the sink contract, so this is held as a question (Q1). |
| 3 | **High** | CONFIRMED | B | `import_file` `try` around `sink(parse_row(row))`, `except (ValueError, KeyError)` | The `try` wraps the sink call too, which causes two failures. (a) A `ValueError` or `KeyError` raised *by the billing client* (for example a rejected record, or a missing key in a response) is counted as an "invalid row", so outages masquerade as bad data. (b) Any other sink exception (timeout, connection error) aborts the whole file mid-way, with no count of what was already loaded. | When billing has a hiccup at row 4,000 of 10,000, the job crashes. Rows 1 to 3,999 are already loaded, and tomorrow's run re-sends them (see #6). Alternatively, the billing client raises `ValueError` on a 4xx, and the report says "500 invalid rows" when the CSV was fine. | Validate first, outside the sink `try`. Then catch sink errors separately: count them as `sink_failed` and decide whether to retry or abort. Return three counts. Test: a stub sink that raises `ValueError` once and `ConnectionError` once, asserting distinct counts and no crash (or a deliberate abort). | **confirmed** from the code structure. |
| 4 | **High** | CONFIRMED | R, A | `parse_row`, `"ssn": row["ssn"] or None` | The SSN is forwarded to the billing system with no stated need. Billing rarely needs a national ID. | National IDs spread to another system and widen the breach and compliance surface. They may also exceed what the privacy notice says billing receives. | Confirm that billing requires SSN (Q2). If it does not, drop the field. If it does, document the legal basis and ensure the field is encrypted or tokenized in transit and at rest. | **confirmed** as a data-minimization gap. The severity depends on Q2; if billing legitimately requires SSN, downgrade to Medium. |
| 5 | Medium | PROBABLE | B | `open(path, newline="")`, which has no `encoding=`; header keys accessed by exact name | Platform-default encoding is used and a UTF-8 BOM is not handled. Header names must match exactly, including case and whitespace. | If the export starts with a BOM (common from Excel), the first header becomes `"\ufeffid"` and every row raises `KeyError`. The result is 0 loaded and N "invalid", each logged with its SSN (#1). Non-UTF-8 locales can garble names. | Use `open(path, newline="", encoding="utf-8-sig")`. Validate the header once, before the loop, and fail fast with a clear error. Test: a CSV with a BOM and a CSV with a renamed column. | **confirmed** for the code behavior. Whether the real export has a BOM is UNVERIFIED, hence Medium. |
| 6 | Medium | UNVERIFIED | B | `import_file` overall | No idempotency or duplicate handling. Duplicate ids within the file are both sent, and nightly re-runs re-send everything. | If `sink` creates rather than upserts, a re-run or crash recovery (#3) creates duplicate billing customers, which can mean double charges. | Confirm the sink's semantics (Q3). Detect duplicate ids within the file and reject the later ones. Make the load an upsert keyed on `id`. | Not a Critical/High candidate; it depends on the unseen sink. |
| 7 | Medium | CONFIRMED | B | `fixtures/customers.csv`; no tests | The fixture contains only valid rows (row 4's empty SSN is accepted), so the invalid-row path is never exercised. No tests were supplied. The "counted and reported" behavior is untested. | A regression in validation or counting ships unnoticed. | Add fixture rows for: bad email, unknown plan, non-integer id, short row, duplicate id. Assert the `(ok, failed)` counts and the log content. Mutation check: remove the plan check and confirm a test goes red. | — |
| 8 | Medium | CONFIRMED | A | `import_file` return value; `log.error` | "Reported" means only per-row log lines plus a return tuple. There is no end-of-run summary and no failure threshold. | A run where 100% of rows fail returns `(0, N)` and exits normally. A nightly scheduler sees success. | Log a summary (`ok`, `invalid`, `sink_failed`) and exit non-zero, or alert, when the failure rate is above a threshold or `ok == 0`. | — |
| 9 | Medium | UNVERIFIED | R | `fixtures/customers.csv` | The context calls the fixture "a copy of real-format customer records". The values look synthetic (900- SSN prefix, 555-01xx phone numbers, `example.test` domain), but provenance is not stated. | If any row was derived from a real customer, national IDs are committed to git history and are hard to remove. | Have the author confirm the data is fully synthetic, and label the fixture as such in a comment or README. If any of it is real, purge it from history. | — |
| 10 | Low | CONFIRMED | B | `plan` check; `email` check | Validation is shallow. `"Pro"` and `" pro"` are rejected while `"@"` alone passes as an email. The email is lowercased, but the plan is neither normalized nor stripped. | Legitimate rows with casing or whitespace noise are rejected, and junk emails reach billing. | Use `.strip().lower()` on the plan and a basic email shape check. Decide the policy explicitly. | — |
| 11 | Low | CONFIRMED | B | `__pycache__/*.pyc` in the work | A compiled artifact is committed, and it embeds an absolute build path. | Repo noise; a stale `.pyc` can mislead reviewers. | Remove it and add `__pycache__/` to `.gitignore`. | — |

### Pass 3: Self-check

- Every finding above has a location, a failure scenario and a fix.
- The verdict is consistent with the findings: an open Critical (#1) rules out both SHIP and SHIP WITH FIXES.
- **Most serious thing likely still missed:** what the billing client does with what it receives, and what it logs on its side, since it now receives SSNs (#4). This would hide in the unseen `sink` implementation.

### WHAT HOLDS UP
- `csv.DictReader` with `newline=""` is the correct way to read the file, so quoted fields with embedded commas or newlines parse correctly.
- Short rows yield `None` values, which the email and plan checks reject (`not None` and `None not in PLANS`) instead of crashing.
- A non-integer `id` raises `ValueError`, which is caught and counted.
- A missing column raises `KeyError`, which is caught. (It is mis-reported per row rather than failing fast; see #5.)
- An empty SSN normalizes to `None`.
- The `.pyc` agrees with the source as far as it is legible.

### UNVERIFIED CLAIMS
- **The job works end to end.** No tests exist and nothing was run. Settle it with the tests in #7 against a stub sink.
- **The fixture is synthetic.** Settle it with an author statement plus the provenance of the data.
- **The sink upserts and raises only on outages.** Settle it with the billing client's code or API documentation.

### QUESTIONS FOR THE AUTHOR
1. What fields does the billing system require? Specifically, why are `name` and `phone` dropped?
2. Does billing actually need SSN? If so, under what basis, and is it protected in transit and at rest?
3. What does `sink` raise on rejection versus outage, and is it an upsert or a create?
4. Is any row in `fixtures/customers.csv` derived from a real customer?

### DECISION-MAKER SUMMARY
Do not run this in production. As written, it writes customers' national ID numbers into logs every time a row is rejected. It also drops names and phone numbers, and it can half-load a file and then mislabel billing outages as bad data. Fix the logging, separate validation from billing errors, confirm the field mapping, and add tests before the first nightly run. The risk of proceeding is repeated personal-data exposure in logs and incomplete or duplicated billing records.

### OWNER SUMMARY
The nightly customer import is not ready for production. It writes sensitive customer details, including ID numbers, into system logs whenever a record is rejected, and it leaves out names and phone numbers when creating billing accounts. It also cannot tell bad data apart from a billing-system outage, so these problems should be fixed and tested before it runs.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "import_customers.py", "status": "seen", "matters": true},
    {"item": "fixtures/customers.csv", "status": "seen", "matters": true},
    {"item": "__pycache__/import_customers.cpython-312.pyc", "status": "seen", "matters": false},
    {"item": "billing sink implementation/contract", "status": "not_seen", "matters": true},
    {"item": "sample of real nightly CSV export", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "log destination/retention config", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "local-reviewer (single reviewer, no tools)", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "second-vendor blind seat", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor blind seat", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Work handles and fixture contains personal data including national ID numbers (SSN), names, emails, phones; cross-vendor seats refused despite team agreement."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "import_customers.py import_file: log.error(\"could not import row %s: %s\", dict(row), e)",
      "scenario": "Any rejected row (or every row on header drift) writes name, email, phone and SSN into application logs nightly.",
      "fix": "Log only line number, id and reason; test that captured logs contain no SSN or email for a rejected row.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "A", "location": "import_customers.py parse_row return dict",
      "scenario": "name and phone are never sent to billing; customers are created without name/phone, contrary to 'loads each valid row'.",
      "fix": "Map all required billing fields or document the billing schema and the omission; test the payload includes name and phone.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py import_file try/except around sink(parse_row(row))",
      "scenario": "Sink ValueError/KeyError is miscounted as an invalid row; any other sink exception aborts mid-file after a partial load with no counts.",
      "fix": "Validate outside the sink try; catch sink errors separately with a sink_failed count and an explicit retry/abort policy; test with a stub sink that raises.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "R", "location": "import_customers.py parse_row \"ssn\": row[\"ssn\"] or None",
      "scenario": "National ID numbers are forwarded to billing with no stated need, widening exposure and possibly exceeding the privacy notice.",
      "fix": "Drop SSN unless billing requires it; if required, document the basis and tokenize or encrypt it.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "import_customers.py open(path, newline=\"\")",
      "scenario": "A UTF-8 BOM makes the first header '\\ufeffid', so every row fails with KeyError and is logged with PII; locale-dependent decoding garbles names.",
      "fix": "Use encoding='utf-8-sig'; validate the header once and fail fast; test with a BOM CSV and a renamed column.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "import_customers.py import_file",
      "scenario": "Duplicate ids in the file or nightly re-runs create duplicate billing customers if the sink is create-only.",
      "fix": "Detect duplicate ids in the file; make the load an upsert keyed on id; confirm sink semantics.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "fixtures/customers.csv; no tests supplied",
      "scenario": "The fixture has only valid rows, so the invalid path and counts are never exercised; regressions ship unnoticed.",
      "fix": "Add invalid fixture rows and tests asserting (ok, failed) and log content; mutation-check by removing the plan validation.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "A", "location": "import_customers.py import_file return (ok, failed)",
      "scenario": "A 100% failure run exits normally; the nightly scheduler reports success.",
      "fix": "Emit a summary and exit non-zero or alert when ok == 0 or the failure rate exceeds a threshold.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "R", "location": "fixtures/customers.csv",
      "scenario": "The context calls it a copy of real-format records; if any row is real, national IDs are committed to git history.",
      "fix": "Confirm the fixture is fully synthetic and label it; purge from history if any row is real.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py parse_row plan and email checks",
      "scenario": "'Pro' and ' pro' are rejected while '@' alone passes as an email.",
      "fix": "Apply strip().lower() to plan and a basic email shape check.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "__pycache__/import_customers.cpython-312.pyc",
      "scenario": "A compiled artifact with an embedded absolute path is committed; it can go stale and mislead reviewers.",
      "fix": "Remove it and gitignore __pycache__/.", "status": "n/a"}
  ]
}
```
