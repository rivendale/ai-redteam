# Redteam report: `import_customers.py` + `fixtures/customers.csv`

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session. Nothing was executed, so every finding comes from reading the supplied text.

**VERDICT: REWORK.** Every invalid row is written to the error log in full, including the national ID number, email and phone. The job also stops partway with no report when the billing system raises an unexpected error.

**CONFIDENCE: medium.** Three things limit it:
- This is a same-context review with no tools, so no code was run.
- The billing sink, its field contract and its idempotency were not supplied.
- The requested cross-vendor seats were refused (see below), so this is a single reviewer and not the deep multi-seat review the context asked for.

**INPUTS LEDGER**
- **Seen:**
  - The original request, verbatim.
  - The context.
  - `import_customers.py`.
  - `fixtures/customers.csv`.
- **Not seen (and why it matters):**
  - The `sink` implementation and billing API contract. *Matters:* it decides which fields billing needs, which exceptions it raises, and whether a re-run creates duplicates.
  - Tests. None were supplied. *Matters.*
  - The nightly runner or scheduler and how it treats the return value and exit code. *Matters.*
  - Logging configuration, meaning where `customer_import` logs go and how long they are kept. *Matters*, because it sets how far F1 spreads.
  - The source of the fixture data. *Matters* for the fixture-sensitivity question (S1).

**COVERAGE**
- **Checked:**
  - `import_customers.py` (`parse_row`, `import_file`, `PLANS`, the logging call).
  - `fixtures/customers.csv`, all 5 rows traced by hand. The result is `(5, 0)`: row 4's empty ssn becomes `None` and is still accepted.
  - Requirement fit against the request.
- **Not checked:**
  - The sink and billing contract (not supplied).
  - The runner (not supplied).
  - Runtime behaviour (no tools).

**SEATS AND GATE**
- The sensitivity gate **tripped**. The context calls the fixture "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)", and the work sends national ID numbers through logs and to billing.
- **Cross-vendor seats 2 and 3 were refused.** Customer PII and national IDs cannot go to an external vendor, even for a review the team agreed to. To get those seats, rerun them with a fully synthetic fixture and the code alone, on endpoints approved for this data.
- The local reviewer (this session) ran. No fresh subagent was available.
- This report does not repeat any value from the fixture.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B, R | `import_customers.py` `import_file`, `log.error("could not import row %s: %s", dict(row), e)` | Every rejected row is logged whole: name, email, phone and **ssn** in plain text. | Each night, any row with a bad email or plan, or a non-integer id, writes that customer's national ID into application logs. Those logs are often shipped to aggregators, kept long-term and readable by many people. That is a PII breach with regulatory exposure, and it repeats every night. The request expects invalid rows, so this path is normal operation, not an edge case. | Log only the row number (`reader.line_num`) and the error reason, never row contents. Collect failures as `(line_num, reason)` for the report. **Repro:** fixture row with `email=bad`; run `import_file` under `caplog`; assert the ssn and email values are absent from `caplog.text`. This fails on the current code. | a✓ b✓ c✓ d✓ |
| F2 | High | CONFIRMED | B | `import_file`, `except (ValueError, KeyError)` around `sink(...)` | Sink errors are mishandled in two ways. (1) A sink failure of any other type (connection error, timeout, HTTP error) is not caught, so the job aborts mid-file with rows 1..k loaded, the rest not attempted, and no counts returned. (2) A sink failure that happens to raise `ValueError` is counted as an "invalid row", which mixes data errors with system errors. | The billing API times out on row 3,000 of 10,000. The job crashes, nothing is reported, and the next nightly run resends rows 1..3,000. If the sink is not an upsert, billing gets duplicates (see S2). | Validate first, then call the sink in a separate `try`. Count `invalid` and `sink_failed` separately. Decide on purpose whether to abort or continue on sink errors, and make re-runs idempotent. **Repro:** a sink that raises `ConnectionError` on its 2nd call. Expected: counts returned with a sink failure recorded. Observed: an uncaught exception and no counts. | a✓ b✓ c✗ d✓ |
| F3 | High | CONFIRMED | B | `parse_row` return dict | The loaded record holds only `id, email, plan, ssn`. **name and phone are silently dropped**, although the request says to load "each valid row". The most sensitive field is kept while the customer's name is discarded. | Billing receives customers with no name or phone, which shows up in invoices, dunning and support lookups. | Ask the author whether billing needs name and phone. If it does, pass them through. If billing does *not* need the ssn, drop it instead (data minimisation; see S3). **Repro:** `parse_row(fixture row 1)`; expect a `name` key, observe that none exists. | a✓ b✓ c✗* d✓ |
| F4 | Medium | CONFIRMED | B | `import_file` return; the request says "counted and reported" | The "report" is just a returned `(ok, failed)` tuple plus PII log lines. Nothing says which rows failed or why. Nothing gives a non-zero exit or alert when failures happen. | A nightly run rejects 40% of rows because of an upstream format change. The job "succeeds" and nobody notices. | Return or write a structured summary: totals, plus failures by line number and reason with no PII. Exit non-zero, or alert, when failures go over a threshold. **Repro:** run the job on a file of all-invalid rows; the scheduler still sees success. | a✓ b✓ c✗ d✓ |
| F5 | Medium | CONFIRMED | B | `parse_row` checks | Validation is thin. Email only needs to contain `@`. Plan and email are not trimmed (`" pro"` and `"Pro"` are rejected; `" a@b"` is accepted with a leading space). Duplicate `id`s are not detected, so both copies are loaded. The ssn format and the phone are never validated. | A CSV export with stray spaces or capitalised plans makes good customers count as invalid. A duplicated id loads twice. | Apply `.strip()`, and compare plan with `.lower()`. Track seen ids. Agree on the rules for each field. **Repro:** a row with `plan=Pro` → counted as failed; two rows with `id=1` → `ok=2`. | a✓ b✓ c✗ d✗ |
| F6 | Medium | PROBABLE | B | `open(path, newline="")` with no `encoding=` | The encoding depends on the host locale. A UTF-8 BOM (common in Excel exports) turns the header into `\ufeffid`, so `row["id"]` raises `KeyError` on every row. Every row is then "invalid", and because of F1 every row is logged with its PII. | The upstream system switches to an Excel export. The nightly run rejects all customers and dumps the whole file into the logs. | Use `open(path, newline="", encoding="utf-8-sig")`, and check the header against the expected columns before the loop. **Repro:** prepend a BOM to the fixture; expect `(5, 0)`, observe `(0, 5)`. | a✓ b✗ c✓ d✗ |
| F7 | Medium | CONFIRMED | B | `fixtures/customers.csv` (and no tests were supplied) | Every row in the fixture is valid. The invalid-row path, which is where F1, F4 and F5 live, is never exercised, and there are no tests at all. | The PII-logging and sink-failure behaviour reaches production untested. | Add invalid rows: bad email, unknown plan, non-integer id, duplicate id, padded fields, BOM. Add tests for counts, report content, absence of PII in logs, and sink failure. Confirm each test goes red against the current code. | a✓ b✓ c✗ d✓ |

\*F3 (c): it is unconfirmed whether the billing contract needs name and phone. If it does, this is drift from the request and c becomes true.

## NEEDS VALIDATION
- **S1: Fixture contents.** It is unclear whether the fixture is derived from real customer records. The context says "a copy of real-format customer records"; the emails use `.test`, the phones use the 555-01xx fictional range, and the ID numbers start with 900. *Settling fact:* the provenance of the fixture rows (names especially). Note that the 9xx range is the ITIN range, which are real taxpayer IDs, so "starts with 9" does not by itself prove the values are fake. If any row is real, removing it from the repo and its history is urgent.
- **S2: Re-runs.** It is unknown whether nightly re-runs, or a re-run after an F2 crash, create duplicate billing customers. *Settling fact:* whether the sink upserts by `id`.
- **S3: Need for the ssn.** It is unknown whether billing needs the ssn at all. *Settling fact:* the billing API contract and the data-processing basis for sending national IDs to billing.
- **S4: Where the logs go.** The reach of F1 depends on where `customer_import` logs are shipped and how long they are kept. *Settling fact:* the logging configuration and retention policy.

## REFUTED
- **R1: A short row with `id=None` would raise an uncaught `TypeError` from `int(None)`.** Refuted. `DictReader` skips blank lines, so `id` is the first field and is always present. Any shorter row fails the email or plan check first, and those raise the caught `ValueError`.
- **R2: An empty ssn crashes the job or is rejected.** Refuted. `row["ssn"] or None` maps the empty value to `None`, and fixture row 4 loads.

## WHAT HOLDS UP
- The plan allow-list is correct.
- A non-integer `id` is caught.
- A missing column raises a caught `KeyError` instead of crashing.
- A failure on one row does not stop the others, as long as the sink raises only `ValueError` or `KeyError`.
- `newline=""` is the correct way to call `csv`.
- The main path loads the fixture as `(5, 0)` by hand trace.

## UNVERIFIED CLAIMS
- The work makes no explicit claims such as "tested" or "verified".
- The implied claim that it is "ready for nightly production" is unverified. Settling it needs the runner, the sink contract and tests.

## QUESTIONS FOR THE AUTHOR
1. Which fields does the billing API need? Does it need name, phone and ssn?
2. Is the sink an upsert keyed on `id`?
3. Where do these logs go, and how long are they kept?
4. Are any of the fixture rows taken from real customers?

## DECISION-MAKER SUMMARY
Do not run this nightly yet. The current code writes the national ID and contact details of every rejected customer into the logs, and a billing outage leaves a partial load with no report. Fix the logging (F1) and sink handling (F2), and confirm the field contract (F3) first. Proceeding anyway risks a repeating PII exposure and duplicate or incomplete billing records.

## OWNER SUMMARY
The import job works when the file is clean. When it meets a bad row, though, it writes that customer's full personal details, including their national ID number, into the system logs, and that has to stop before it goes live. It also stops halfway without saying so if the billing system has a hiccup, and it drops customer names and phone numbers it was asked to load.

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
    {"item": "billing sink implementation and API contract", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "nightly runner / scheduler", "status": "not_seen", "matters": true},
    {"item": "logging configuration and retention", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-context", "status": "ran", "cross_vendor": false},
    {"vendor": "cross-vendor-seat-2", "status": "refused", "cross_vendor": true},
    {"vendor": "cross-vendor-seat-3", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Fixture described as a copy of real-format customer records with names, emails, phones and national ID numbers; code routes national IDs to logs and billing. No external vendor may receive it."},
  "coverage": {
    "checked": [
      {"unit": "import_customers.py", "kind": "file"},
      {"unit": "import_customers.py:parse_row", "kind": "function"},
      {"unit": "import_customers.py:import_file", "kind": "function"},
      {"unit": "fixtures/customers.csv", "kind": "data"}
    ],
    "not_checked": [
      {"unit": "billing sink", "reason": "not supplied"},
      {"unit": "tests", "reason": "not supplied"},
      {"unit": "nightly runner", "reason": "not supplied"},
      {"unit": "logging configuration", "reason": "not supplied"},
      {"unit": "runtime behaviour", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file log.error(... dict(row) ...)",
     "scenario": "Any invalid row (bad email, unknown plan, non-integer id) is logged in full, writing the customer's national ID, email, phone and name to application logs every night.",
     "fix": "Log only line number and reason; never row contents. Collect failures as (line_num, reason).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Fixture row with email=bad; run import_file under caplog; assert ssn and email values absent from caplog.text; fails on current code."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file except (ValueError, KeyError) around sink()",
     "scenario": "Sink raises ConnectionError/timeout mid-file: job aborts with partial load and no counts; a re-run resends earlier rows. A sink ValueError is miscounted as an invalid row.",
     "fix": "Validate outside the sink try; count invalid and sink_failed separately; define abort/continue policy; make re-runs idempotent.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Sink that raises ConnectionError on 2nd call; expect counts with a sink failure recorded; observe uncaught exception."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:parse_row return dict",
     "scenario": "name and phone are dropped, so billing receives customers without names or phones, contrary to 'loads each valid row'; ssn is kept.",
     "fix": "Confirm the billing field contract; pass name and phone if needed; drop ssn if billing does not need it.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "parse_row(fixture row 1); expect a 'name' key; observe none."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:import_file return (ok, failed)",
     "scenario": "No per-row report and no failure exit code; a run rejecting most rows still looks successful to the scheduler.",
     "fix": "Emit a structured PII-free summary with failures by line and reason; exit non-zero or alert above a threshold.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run on an all-invalid file; the scheduler still sees success."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:parse_row validation",
     "scenario": "Padded or capitalised plans are rejected; emails are not trimmed; duplicate ids load twice; ssn and phone are unvalidated.",
     "fix": "Strip and normalise fields; track seen ids; agree on validation rules per field.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Row with plan=Pro is counted failed; two rows with id=1 give ok=2."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "import_customers.py:import_file open(path, newline=\"\")",
     "scenario": "A UTF-8 BOM makes the header '\\ufeffid', so every row raises KeyError, all rows are rejected, and all are logged with PII (via F1).",
     "fix": "open(..., encoding=\"utf-8-sig\"); validate the header before the loop.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Prepend a BOM to the fixture; expect (5, 0); observe (0, 5)."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "fixtures/customers.csv (no tests supplied)",
     "scenario": "The fixture has no invalid rows, so the failure path, logging and reporting are never exercised before production.",
     "fix": "Add invalid, duplicate, padded and BOM rows plus tests for counts, report content, absence of PII in logs, and sink failure; confirm each goes red on current code.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Trace the fixture: every row passes, so failed=0 and the except branch never runs."},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "fixtures/customers.csv",
     "suspicion": "Fixture rows may be derived from real customers; the 9xx prefix is also the ITIN range.",
     "unresolved_fact": "Provenance of the fixture rows."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "sink (not supplied)",
     "suspicion": "Nightly or post-crash re-runs may create duplicate billing customers.",
     "unresolved_fact": "Whether the sink upserts by id."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "import_customers.py:parse_row ssn field",
     "suspicion": "National IDs may be sent to billing without need.",
     "unresolved_fact": "Billing API contract and data-processing basis for ssn."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "logging configuration (not supplied)",
     "suspicion": "The reach of the F1 exposure depends on where logs go and how long they are kept.",
     "unresolved_fact": "Log destinations and retention for customer_import."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A short row gives id=None and int(None) raises an uncaught TypeError.",
     "evidence": "DictReader skips blank lines and id is the first column; shorter rows fail the email or plan check (caught ValueError) first."},
    {"id": "R2", "candidate": "An empty ssn crashes the job or rejects the row.",
     "evidence": "row['ssn'] or None maps it to None; fixture row 4 loads."}
  ]
}
```

I could not run `tools/validate_findings.py`, so the JSON's conformance to schema 2.2 is unchecked. It includes the per-finding fields the output note asks for (severity, evidence_level, location, scenario, fix).