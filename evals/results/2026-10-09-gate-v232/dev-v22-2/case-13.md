# Redteam report: `import_customers.py` + `fixtures/customers.csv`

> **Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools in this session, so no subagent and no ability to run code. Every finding below comes from reading the supplied text line by line.

**VERDICT: REWORK.** The job writes every invalid row's SSN, name, email and phone into the error log. Invalid rows are an expected path every night, so this is a confirmed personal-data leak in a production job. It also silently drops two of the six requested fields, and a single billing-side error aborts the run partway through.

**CONFIDENCE: medium.** Three things limit it: this is a same-context review with no tools, and code paths were traced by hand rather than run. The `sink`/billing client, the logging configuration, the entrypoint and the tests were not supplied. The requested cross-vendor seats were refused (see the gate below).

**INPUTS LEDGER**
| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | — |
| `import_customers.py` | seen (27 lines) | — |
| `fixtures/customers.csv` | seen (5 rows) | — |
| `sink` / billing-system client | not supplied | **Yes.** It decides idempotency, which exceptions it raises, and whether name and phone are required. |
| Logging config (handlers, destinations, retention) | not supplied | **Yes.** It decides where the leaked SSNs end up. The leak is a finding either way. |
| Entrypoint / nightly scheduler | not supplied, apparently does not exist | Yes. Nothing shows how "report" happens. |
| Tests | none supplied | Yes. The invalid-row path is untested. |
| Source of fixture data | not supplied | Yes. It decides whether the repo holds real people's data. |

**COVERAGE**
- Checked: `import_customers.py` (`parse_row` lines 9–14, `import_file` lines 17–27), all 5 rows of `fixtures/customers.csv`, and the request's field list against the output dict.
- Not checked: sink, logging config, scheduler/entrypoint, tests, and the provenance of the fixture data.

**SEATS AND GATE**
- **Sensitivity gate: tripped.** The context describes the fixture as "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)". The code handles SSNs. The values look synthetic: `900-` area numbers are never issued as SSNs, `555-01xx` is the reserved fictional range, and `.test` is a reserved TLD. That is not verified, though, and the job processes real SSNs in production.
- **Cross-vendor seats (2nd and 3rd vendor): REFUSED.** Personal data and national ID numbers cannot go to an external vendor without confirmation that the data is synthetic and that the endpoint is approved for it. The team's standing agreement to use cross-vendor seats does not override this. To enable them, confirm the fixture is fully synthetic, or send the code only (without the fixture) to approved zero-retention endpoints.
- **Fresh same-vendor subagent:** unavailable (no tools).
- **Ran:** this same-context reviewer only.

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B, R | `import_customers.py:25` | `log.error("could not import row %s: %s", dict(row), e)` writes the whole raw row (name, email, phone, **ssn**) to the log for every invalid row. | Any nightly file with an invalid row (bad email, unknown plan, non-integer id) puts a customer's SSN in plaintext into the logs, and from there into log aggregation, backups and anyone with log access. The request makes invalid rows an expected case. | Log only the row number (`reader.line_num`) and the `id` (if non-PII), plus the error class. Never log `dict(row)`. **Repro:** feed a CSV with a row whose email is `nope`; capture the `customer_import` logger output; expect no SSN; observe `'ssn': '900-…'` in the message. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | B (drift) | `import_customers.py:14` | `parse_row` returns only `id, email, plan, ssn`. `name` and `phone` are read and then dropped. The request asks to load "each valid row" of a six-column file. | Every customer is created in billing with no name and no phone, every night. Invoices and dunning calls then have no addressee or number. PROBABLE only because the sink's required schema was not supplied. | Include `name` and `phone` (stripped), or document in the request why billing must not receive them. **Repro:** `parse_row({"id":"1","name":"A","email":"a@x.test","phone":"555","ssn":"","plan":"pro"})`; expect keys `name` and `phone`; observe that they are absent. | a✓ b✗ c✓ d✓ |
| F3 | High | CONFIRMED (code path) | B | `import_customers.py:21–26` | Only `ValueError`/`KeyError` are caught, and `sink()` sits inside the same `try`. Any other sink exception (timeout, `ConnectionError`, HTTP 5xx wrapper) propagates out of `import_file`. | The billing API blips on row 3,000 of 10,000. The job dies, rows 1–2,999 are loaded, the rest are not, and nothing reports `ok`/`failed`. If the next night's rerun of the same file is not idempotent, the first 2,999 customers may be created twice (needs_validation S1). | Separate the stages: validate with `parse_row` and count invalid rows; call `sink` in its own handler with retry/timeout; on sink failure either stop with a clear partial-run report or record per-row sink failures separately. **Repro:** `sink` raises `ConnectionError` on its 2nd call; expect a report of 1 ok and 1 sink failure; observe an uncaught exception and no counts. | a✓ b✓ c✓ d✓ |
| F4 | Medium | CONFIRMED | B | `import_customers.py:22,24` | A `ValueError`/`KeyError` raised **by the sink** (for example billing rejecting a duplicate) is counted as an "invalid row" and reported as such. | Billing rejects 200 rows for a server-side reason. The report says "200 invalid rows" and someone goes hunting for bad CSV data that does not exist. Combined with F1, those rows' SSNs are logged as well. | Same restructuring as F3: invalid input and load failure become separate counters. **Repro:** a sink that raises `ValueError` on every call, with a valid fixture; expect `invalid=0, load_failed=5`; observe `(0, 5)` reported as invalid. | a✓ b✓ c✗ d✗ |
| F5 | Medium | CONFIRMED | B | `import_customers.py:19,24` | A whole-file defect is counted as N invalid rows instead of failing the job. Examples: a UTF-8 BOM on the header (`\ufeffid`) or a renamed column. `open()` also has no `encoding=`, so decoding depends on the host locale. | An Excel-exported file with a BOM: `row["id"]`… is actually reached only after the email/plan checks pass, then `int(row["id"])` raises `KeyError`. Every row is "invalid", every row's SSN is logged (F1), and 0 customers load. The job still "succeeds". | Open with `encoding="utf-8-sig"`. Before the loop, check `reader.fieldnames` against the six expected columns and fail the job loudly if they differ. **Repro:** prepend `\ufeff` to the fixture; expect a job-level error; observe `(0, 5)`. | a✓ b✓ c✗ d✓ |
| F6 | Medium | CONFIRMED | B, D | `import_customers.py:17–27` (whole module) | "Invalid rows are counted and **reported**": the function returns a tuple, and nothing reports it. There is no entrypoint, no summary log line, no exit code and no alert. | The nightly run loads 0 of 10,000 rows (F5) and nobody is told. | Add a `main()` that logs a one-line summary (ok / invalid / load_failed), exits non-zero above a threshold, and is the thing the scheduler calls. **Repro:** n/a. The absence is visible in the file. | a✓ b✓ c✗ d✓ |
| F7 | Medium | CONFIRMED | B | `import_customers.py:10–14` | Validation is thin. Email only needs to contain `@`. Plan is case- and whitespace-sensitive (`" pro"` and `"Pro"` are rejected). Email is lowercased but not stripped. `ssn`, `phone` and `name` are unvalidated. Duplicate `id`s in the file are not detected. | `ssn` = `"N/A"` or `"123"` loads into billing as a national ID. A trailing space in `plan` from a spreadsheet rejects valid customers. | Strip all fields. Normalize the case of `plan`. Validate the SSN format (or drop it, see S2). Track seen ids and reject duplicates. **Repro:** a row with `plan=" pro"`, rejected; a row with `ssn="N/A"`, accepted. | a✓ b✓ c✗ d✗ |
| F8 | Low | CONFIRMED | B | `fixtures/customers.csv` | The fixture contains no invalid row, and no tests were supplied. The F1 leak path, the counting path and every rejection branch have never executed. | A regression in any rejection branch, or in the log scrubbing once F1 is fixed, goes unnoticed. | Add invalid rows (bad email, unknown plan, bad id, short row) and tests asserting the counts **and** that no SSN appears in captured logs. Confirm each test goes red against the current code (it should, for F1). | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1:** whether the sink is idempotent on `id`. **Settles it:** the billing client's create/upsert semantics. If it is create-only, F3's partial run plus rerun produces duplicate customers and possibly duplicate charges.
- **S2:** whether billing needs the SSN at all. **Settles it:** the billing system's data requirements and the privacy notice. If billing does not need it, line 14 is sending a national ID to a system without need, which is a data-minimization issue.
- **S3:** whether the fixture rows are derived from real people. **Settles it:** the fixture's provenance. The values look synthetic (see the gate), but the context says "a copy of… customer records". If any are real, they must be removed from the repo and its history.
- **S4:** where the `customer_import` logger is shipped and how long it is retained. **Settles it:** the logging config. This determines the size of F1's exposure and whether existing logs need purging. It does not change F1's severity.

## REFUTED
- **R1:** "A short or blank row raises an uncaught `TypeError` at `int(row["id"])`." `DictReader` skips blank lines. A short row leaves `plan=None`, which raises `ValueError` at line 12–13 before line 14. A row of only whitespace also fails at the plan check. No path reaches `int(None)`.
- **R2:** "Row 4 (empty SSN) is rejected or loaded as an empty string." Line 14 maps `""` to `None` explicitly, so it loads with `ssn=None`. That is a reasonable handling.
- **R3:** "Instructions addressed to the reviewer are embedded in the work." None found.

## WHAT HOLDS UP
- The email and plan checks run before `int()`, so the common malformed-row shapes are caught as `ValueError` rather than crashing (R1).
- `newline=""` is passed to `open`, which is correct for the `csv` module.
- The plan allowlist is a fixed set rather than free text.
- The fixture values use reserved fictional ranges (`.test`, `555-01xx`, `900-` SSNs), which is the right practice if it holds for all of the data.

## UNVERIFIED CLAIMS
- That the fixture is "real-format" but not real: confirm the provenance.
- That this function is what runs nightly: no entrypoint was supplied. Confirm it in the scheduler config.
- None of the code was executed. Every reproduction above is a hand trace. Run them in a scratch copy.

## QUESTIONS FOR THE AUTHOR
1. Is dropping `name` and `phone` intentional? If yes, F2 is withdrawn and the request should say so.
2. Is the billing sink an upsert on `id`? (S1)
3. Does billing require the SSN? (S2)
4. Were the fixture rows generated, or copied from production? (S3)

## DECISION-MAKER SUMMARY
Do not ship. Every invalid row writes a customer's SSN into the logs, and invalid rows are expected nightly. The job also drops name and phone, and it aborts partway on any billing error without reporting counts. Fix F1–F3 and add tests on the invalid path before the first production run. Proceeding as is means a likely personal-data exposure in log storage from night one.

## OWNER SUMMARY
The customer import job is not ready for production. When a row has a problem, the job copies that customer's full details, including their social security number, into its error logs, where far more people and systems can see it. It also leaves out customers' names and phone numbers, and if the billing system hiccups it stops halfway without telling anyone.

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
    {"item": "sink / billing-system client", "status": "not_seen", "matters": true},
    {"item": "logging configuration", "status": "not_seen", "matters": true},
    {"item": "entrypoint / nightly scheduler", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "fixture data provenance", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "same-context-claude", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "second-vendor", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Work handles SSNs, names, emails and phone numbers; the fixture is described as a copy of customer records with national ID numbers. Cross-vendor seats refused until the fixture is confirmed synthetic and endpoints are approved."},
  "coverage": {
    "checked": [
      {"unit": "import_customers.py", "kind": "file"},
      {"unit": "import_customers.py:parse_row", "kind": "function"},
      {"unit": "import_customers.py:import_file", "kind": "function"},
      {"unit": "fixtures/customers.csv", "kind": "data"},
      {"unit": "request field list vs parse_row output", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "sink / billing client", "reason": "not supplied"},
      {"unit": "logging configuration", "reason": "not supplied"},
      {"unit": "scheduler / entrypoint", "reason": "not supplied"},
      {"unit": "tests", "reason": "not supplied"},
      {"unit": "runtime behaviour", "reason": "no tools; hand-traced only"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:25",
     "scenario": "Any invalid row (bad email, unknown plan, bad id) causes log.error to write dict(row), including the plaintext SSN, name, email and phone, to the customer_import log on every nightly run.",
     "fix": "Log only row number, non-PII id and error class; never log dict(row). Add a test asserting no SSN appears in captured logs.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Run import_file on a CSV with a row whose email is 'nope'; capture the customer_import logger; expect no SSN; observe \"'ssn': '900-...'\" in the message."},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "import_customers.py:14",
     "scenario": "parse_row returns only id, email, plan, ssn; name and phone from the six-column CSV are dropped, so every customer is loaded into billing without name or phone.",
     "fix": "Include stripped name and phone in the returned record, or amend the request to state they must not be sent.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "parse_row({'id':'1','name':'A','email':'a@x.test','phone':'555','ssn':'','plan':'pro'}); expect keys name and phone; observe them absent."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:21-26",
     "scenario": "The sink raises ConnectionError or a timeout mid-file; only ValueError/KeyError are caught, so the job aborts with a partial load and returns no counts.",
     "fix": "Validate and load in separate handlers; add retry and timeout around sink; on sink failure emit a partial-run report and fail loudly, or count per-row load failures separately.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Use a sink that raises ConnectionError on its 2nd call with the 5-row fixture; expect a report of 1 ok and 1 load failure; observe an uncaught exception and no counts."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:22,24",
     "scenario": "A ValueError or KeyError raised by the sink (billing rejection) is counted and reported as an invalid CSV row, misdirecting operators and logging the row's PII.",
     "fix": "Separate the invalid-input counter from the load-failure counter.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Use a sink that always raises ValueError with the valid fixture; expect invalid=0 and load_failed=5; observe (0, 5) reported as invalid."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:19,24",
     "scenario": "A UTF-8 BOM header or a renamed column makes every row raise KeyError; all rows are counted invalid (and logged with PII), 0 rows load, and the job still returns normally.",
     "fix": "Open with encoding='utf-8-sig'; check reader.fieldnames against the expected six columns before the loop and fail the job if they differ.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Prepend \\ufeff to fixtures/customers.csv; expect a job-level error; observe (0, 5)."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:17-27",
     "scenario": "Invalid rows are counted but never reported: there is no entrypoint, summary line, exit code or alert, so a nightly run that loads nothing goes unnoticed.",
     "fix": "Add a main() that logs an ok/invalid/load_failed summary, exits non-zero above a threshold, and is what the scheduler invokes.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Inspect the module: no caller of import_file and no summary output exist."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:10-14",
     "scenario": "plan ' pro' or 'Pro' is rejected; ssn 'N/A' is loaded as a national ID; duplicate ids within the file are loaded twice; email is not stripped.",
     "fix": "Strip fields, normalize plan case, validate SSN format or drop it, and reject duplicate ids within the file.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "A row with plan=' pro' gets rejected; a row with ssn='N/A' gets accepted."},
    {"id": "F8", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "fixtures/customers.csv",
     "scenario": "The fixture has no invalid rows and no tests were supplied, so the rejection, counting and logging paths (including the F1 leak) have never run.",
     "fix": "Add invalid fixture rows and tests asserting counts and the absence of SSNs in logs; confirm the tests fail on the current code.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run import_file on the fixture with a counting sink: returns (5, 0); the except branch is never reached."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "import_customers.py:22",
     "suspicion": "A rerun after a partial failure (F3) may create duplicate billing customers.",
     "unresolved_fact": "Whether the billing sink upserts on id or only creates (sink not supplied)."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "import_customers.py:14",
     "suspicion": "SSN is sent to billing without need (data minimization).",
     "unresolved_fact": "Whether the billing system requires the SSN and whether the privacy notice covers sharing it."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "fixtures/customers.csv",
     "suspicion": "The fixture may contain real customers' personal data committed to the repo.",
     "unresolved_fact": "Provenance of the fixture rows (generated vs copied from production)."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "import_customers.py:5",
     "suspicion": "Leaked SSNs (F1) may be shipped to external log storage with long retention.",
     "unresolved_fact": "Handlers, destinations and retention of the customer_import logger."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A short or blank row reaches int(None) and raises an uncaught TypeError.",
     "evidence": "DictReader skips blank lines; a short row leaves plan=None, which raises ValueError at line 12-13 before int() at line 14."},
    {"id": "R2", "candidate": "Row 4's empty SSN is rejected or loaded as an empty string.",
     "evidence": "Line 14 maps '' to None via `row['ssn'] or None`."},
    {"id": "R3", "candidate": "The work contains instructions addressed to the reviewer.",
     "evidence": "No such text in either file."}
  ]
}
```