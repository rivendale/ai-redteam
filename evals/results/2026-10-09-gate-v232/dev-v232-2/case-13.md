# Redteam report: `import_customers.py` + `fixtures/customers.csv`

**Single reviewer, no subagent, no tools.** I did not write this work, but no fresh instance or external seat ran, so one reader's blind spots apply. Re-run in an isolated session with tools before relying on it for production.

VERDICT: **REWORK**. Every invalid row writes the customer's full record, including the national ID number, to the error log. Any non-validation error from the billing system kills the nightly run partway, with no count reported.

CONFIDENCE: **medium**. The code is short and I traced it by hand. I had no tools, so nothing was run, no reproduction was executed, and I could not scan for hidden characters. The billing sink, logging configuration and any runner were not supplied.

INPUTS LEDGER:
- Seen: the original request (`request.md`), the context (`context.md`), `import_customers.py` and `fixtures/customers.csv`.
- Not seen:
  - The `sink` implementation and billing API contract. **This matters** for which exceptions it raises, whether it is idempotent, and which fields it needs.
  - The logging configuration and destination. **This matters** for who can read the leaked identifiers.
  - Any runner, scheduler or CLI for the "nightly" job. **This matters** for where the counts are reported.
  - Tests. None were supplied. **This matters**, because the fixture exists but nothing exercises it.
  - Git history. It matters if the fixture ever held real records.

COVERAGE:
- Scope: the whole work as supplied.
- Checked:
  - `import_customers.py`, including `parse_row`, `import_file` and the `PLANS` constant.
  - `fixtures/customers.csv`, all 5 rows.
  - `request.md` and `context.md`.
  - The assumptions about sink exceptions, field needs, input encoding and validity rules.
- Not checked:
  - The sink, logging config, runner, tests and history: not supplied.
  - Execution of anything: no tools.
  - The hidden-character scan: no tools.

SEATS AND GATE:
- **Sensitive: yes.** The context describes the fixture as "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)". The code also handles SSNs.
- **Cross-vendor seats (second and third vendor): REFUSED**, even though the team agreed to them. The context does not establish that the records are synthetic, and a prior agreement does not override the data gate. The values do look synthetic: 9xx SSN area numbers are never issued, 555-01xx numbers are reserved as fictional, and `.test` is a reserved domain. If the data owner confirms the fixture is synthetic, the seats can be re-run. Alternatively, the code alone can be sent with the fixture replaced.
- **Same-vendor subagent:** not available in this session.
- **Ran:** this reviewer only.

## Pass 1: Reconstruct

The work claims to be the nightly import job. It streams the CSV, validates email (non-empty, contains `@`) and plan (one of three values), and sends `{id, email, plan, ssn}` to a caller-supplied `sink`. It counts rows that raise `ValueError` or `KeyError` as failed, logs them, and returns `(ok, failed)`.

For this to be correct, all of the following must hold:
- Every sink failure is either a `ValueError`/`KeyError` or acceptable to crash on.
- Billing does not need `name` or `phone`.
- Logs are cleared to hold national ID numbers.
- The input is UTF-8 with no byte-order mark (BOM).
- "Valid" means only a well-formed email and a known plan.
- Something outside this file reports the returned counts.

Tracks: **B** (code) and **R** (personal-data handling).

**Trust boundaries:**
- The CSV comes from an upstream export. Treat it as lower-trust input.
- The billing sink is the higher-trust write.
- Logs typically have a wider audience than the billing PII store: operators, log aggregation and vendors.
- The route that never meets a check is the `log.error` call, which writes raw row contents with no masking.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | B, R | `import_customers.py:25` | `log.error("could not import row %s: %s", dict(row), e)` writes the whole row to the log: name, email, phone, **SSN** and plan. | Conditions: any row fails validation (bad email, unknown plan or a typo such as `Pro`). Result: the full SSN and contact details land in the production log every night, and from there in log aggregation, backups and anyone with log access, unmasked. | **Fix:** log only the line number (`reader.line_num`), `row.get("id")` and the error. Never log `dict(row)`. Add a test asserting no SSN-shaped string appears in captured logs. **Reproduction:** feed a CSV row `6,X,bad-email,555-0100,900-00-0001,pro` to `import_file` with `caplog` at ERROR. Expected: no `900-00-0001` in the logs. Observed by tracing: the record contains `'ssn': '900-00-0001'`. | a Y, b Y, c Y, d Y |
| F2 | **High** | CONFIRMED | B | `import_customers.py:21-26` | Only `ValueError` and `KeyError` are caught. Any other exception from `sink` propagates out of the loop. Examples: a connection error, a timeout, an HTTP client error, or `TypeError`. The function then never returns its counts. | Conditions: billing is briefly unavailable at row N of the nightly run. Result: rows 1..N-1 are loaded, the rest are not, and no ok/failed count is produced, which breaks the "counted and reported" requirement. A re-run re-sends rows 1..N-1. Whether that duplicates customers depends on the sink (see S1). | **Fix:** separate validation from loading. Call `parse_row` in its own try block. Wrap the sink call so that transient errors retry with a cap, and persistent ones are counted as `load_failed` separately from `invalid`. Always emit the counts, for example from a `finally` block. **Reproduction:** run `import_file(fixture, sink)` where `sink` raises `ConnectionError` on the 3rd call. Expected: returns counts for all 5 rows. Observed by tracing: `ConnectionError` propagates and nothing is returned. | a Y, b Y, c Y (breaks request), d Y |
| F3 | **High** | CONFIRMED | B | `import_customers.py:14` | The record sent to billing omits `name` and `phone`, which are columns the request names. The request says to load "each valid row", not a subset of its fields. | Conditions: every row. Result: billing receives customers with no name or phone. Invoices or dunning that need a name have none, and nothing flags the gap. | **Fix:** include `name` and `phone` (stripped), or have the author document that billing does not accept them. **Reproduction:** `parse_row({"id":"1","name":"A","email":"a@x.test","phone":"555-0100","ssn":"","plan":"pro"})`. Expected: keys include `name` and `phone`. Observed by tracing: keys are `id, email, plan, ssn`. | a Y, b Y, c N (billing's field needs not supplied), d Y |
| F4 | Medium | CONFIRMED | B | `import_customers.py:21-26` | Sink-raised `ValueError` and `KeyError` are counted as "invalid rows". Load failures and bad data end up in one number. | Conditions: billing rejects a row with `ValueError`, for example a duplicate customer. Result: it is reported as invalid input, so someone fixes the CSV instead of the billing problem. | **Fix:** use separate counters (see F2). **Reproduction:** run with a sink that raises `ValueError("dup")` on every call against the fixture. Expected: `invalid=0, load_failed=5`. Observed by tracing: `(0, 5)` reported as failed rows. | a Y, b Y, c N, d N |
| F5 | Medium | CONFIRMED | B | `import_customers.py:19` | `open(path, newline="")` sets no encoding. A UTF-8 BOM therefore stays on the first header, and a non-UTF-8 file raises `UnicodeDecodeError`, which is not caught. | Conditions: the export comes from Excel (which writes a UTF-8 BOM) or a cp1252 tool. With a BOM, the first header becomes `\ufeffid`, so `row["id"]` raises `KeyError` on every row. Result: every row is "invalid", 0 rows load, and the job exits normally. A non-UTF-8 name aborts the run. | **Fix:** use `encoding="utf-8-sig"`. Check the header set before the loop and fail loudly if it is wrong. **Reproduction:** prepend `\ufeff` to the fixture and run. Expected: `(4, 1)` or an explicit header error. Observed by tracing: `(0, 5)`. | a Y, b Y, c N, d N |
| F6 | Medium | CONFIRMED | B | `import_customers.py:10-14` | Validation is thin: no whitespace stripping, a case-sensitive plan, an email check that is only "contains `@`", and no SSN or phone format check. | Conditions: the value is `pro ` or `Pro`. Result: a valid customer is rejected. Conversely, `@` or `a@` passes as an email, and an SSN of `abc` goes to billing. | **Fix:** strip all fields and lowercase the plan before the check. Use a stricter email check. Validate the SSN as `^\d{3}-\d{2}-\d{4}$` or empty, per the author's definition of valid. **Reproduction:** `parse_row` with `plan="pro "`. Expected: accepted. Observed by tracing: `ValueError("unknown plan")`. `parse_row` with `email="@"`. Expected: rejected. Observed by tracing: accepted. | a Y, b Y, c N, d Y |
| F7 | Medium | CONFIRMED | B | `import_customers.py:20-23` | Duplicate `id`s are not detected. Both rows go to the sink. | Conditions: the upstream export repeats a row. Result: billing receives two loads for one customer. Whether that creates a duplicate or silently overwrites depends on the sink. | **Fix:** track seen ids and count repeats as invalid. **Reproduction:** run on a CSV with row `1,...` twice. Expected: `ok=1, invalid=1`. Observed by tracing: `ok=2`. | a Y, b Y, c N, d N |
| F8 | Medium | CONFIRMED | B | whole work | The request asks for "the import job", meaning something that runs nightly and *reports*. There is no entry point, the counts are only returned and never reported, and there are no tests even though a fixture exists. | Conditions: the nightly scheduler calls this. Result: nothing in the work emits the counts or the exit status, so failures are invisible unless an unsupplied wrapper handles them. | **Fix:** add a `main()` that builds the real sink, logs a summary line (counts only) and exits non-zero when load failures occur or when `ok == 0` on a non-empty file. Add pytest cases using the fixture. **Reproduction:** search the supplied work for `__main__`, `argparse` or any summary log. Expected: present. Observed by reading: absent. | a Y, b Y, c N, d N |

## Pass 3: Confirm or refute

**F1 (Critical): held.**
- Strongest defence: the logs may be locked down. Even so, SSNs in plain-text application logs breach data-minimization expectations. Logs also have wider and longer-lived access than the billing store. The line is exact and the behaviour is deterministic.
- Security: **yes**.
  - Principal: anyone with log access.
  - Input: any malformed row; the controller of the upstream file can trigger it at will.
  - Control that fails: no masking at `:25`.
  - Boundary crossed: from the restricted PII store to general operational logs.
  - Resource affected: customers' national ID numbers and contact details.
- Siblings searched: every `log.` call and every exception message that could carry row data.
  - `:25` is the only log call.
  - `ValueError` messages from `parse_row` are fixed strings.
  - `int()` failures echo only the `id` value.
  - Messages from sink exceptions could echo PII; see S2.

**F2 (High): held.**
- Strongest defence: a crash is visible to the scheduler. But it still yields no count and leaves a partial load, which the request's counting and reporting requirement rules out.
- Security: no.
- Siblings searched: other uncaught exception paths in the loop. F5's `UnicodeDecodeError` path is the same root cause and is recorded there. A `TypeError` from `int(None)` is not reachable (see Refuted).

**F3 (High): held.** I set c to "no" because billing's field needs were not supplied, so this stays High rather than Critical.
- Strongest defence: billing may not take a name. That is possible, but the request names the columns and says to load the row, and the code drops fields silently.
- Security: no.
- Siblings searched: every field read from `row`. `name` and `phone` are never read anywhere. `ssn` is passed through, which raises the data-minimization question in S3.

Verdict check: an open Critical rules out SHIP and SHIP WITH FIXES, so the verdict is REWORK.

## NEEDS VALIDATION
- **S1:** Is the billing sink idempotent on `id`? This decides whether a re-run after F2 creates duplicate customers or charges.
- **S2:** Do exceptions from the sink embed the submitted record in their message? If they do, `%s` of `e` at `:25` is a second PII leak path.
- **S3:** Does billing actually require the SSN? If it does not, sending it violates data minimization.
- **S4:** Are the fixture values real people's data? They look synthetic: 9xx SSN areas, 555-01xx numbers, `.test` domains. But the context says "a copy of real-format customer records". The data owner's confirmation settles it, plus a read-only history search for any earlier version holding real data.
- **S5:** Do the files contain hidden characters (zero-width, bidirectional or look-alike) that change logic? A byte-level scan settles it; I could not run one.

## REFUTED
- **"A short row reaches `int(None)` and raises an uncaught `TypeError`."** Refuted. `DictReader` fills missing trailing fields with `None`. `email` is checked first, at `:10`, so a short row raises `ValueError("bad email")` before `int()` is reached. `id` is the first column, so it is only `None` when the header lacks it, which raises `KeyError` and is caught.
- **"Blank lines are counted as failures."** Refuted. `csv.DictReader` skips rows that are entirely empty.
- **"The whole file is loaded into memory."** Refuted. Rows are streamed from the reader one at a time.
- **"Row 4's empty SSN crashes or is rejected."** Refuted. `row["ssn"] or None` maps it to `None`. Whether an empty SSN *should* count as valid is a question for the author.

## WHAT HOLDS UP
- Streaming parsing with `newline=""` is the correct use of `csv`.
- The `PLANS` allow-list is correctly checked.
- The email is normalised to lowercase.
- A `KeyError` on a missing column is caught, not left to crash the run.
- The function returns a count tuple that a caller could report.
- By tracing, the fixture gives `(5, 0)`: all five rows have a valid email and plan. Note that the fixture contains no invalid row, so it never exercises the failure path, which is where F1 lives.

## UNVERIFIED CLAIMS
- No tests are present, so nothing is claimed as tested. Confirm by writing the reproductions above and seeing each go red on the current code.
- The fixture expectation `(5, 0)` was traced by hand, not run. Confirm with `import_file("fixtures/customers.csv", list.append-style sink)`.

## QUESTIONS FOR THE AUTHOR
1. Which fields does billing require? Does it need `name`, `phone` and `ssn`?
2. What exceptions does the sink raise, and is it idempotent on `id`?
3. Where should the counts be reported (log summary, metric, alert), and what should cause a non-zero exit?
4. Is the fixture synthetic? If so, can that be stated in the repo so external review can run?

## DECISION-MAKER SUMMARY
Do not deploy as is. F1 puts SSNs into production logs on any bad row, and F2 means a billing outage mid-run leaves a partial load with no report. Fix F1 and F2, answer the field question behind F3, then re-run this review with the cross-vendor seats once the fixture is confirmed synthetic.

## OWNER SUMMARY
The import code works for clean files, but whenever a row has a mistake it writes that customer's full details, including their national ID number, into the system logs. If the billing system hiccups during the nightly run, the job stops halfway without saying how many customers were loaded or skipped. These two problems should be fixed before it runs in production, and it is not yet clear whether customers' names and phone numbers are meant to reach billing at all.

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
    {"item": "billing sink implementation / API contract", "status": "not_seen", "matters": true},
    {"item": "logging configuration and destination", "status": "not_seen", "matters": true},
    {"item": "nightly runner / scheduler entry point", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "git history of fixtures/customers.csv", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-session", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable", "cross_vendor": false},
    {"vendor": "second-vendor", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Fixture described as a copy of real-format customer records with names, emails, phones and national ID numbers, and the code handles SSNs; not established as synthetic, so cross-vendor seats were refused despite the team agreement."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "import_customers.py", "kind": "file"},
      {"unit": "fixtures/customers.csv", "kind": "data"},
      {"unit": "import_customers.py:parse_row", "kind": "function"},
      {"unit": "import_customers.py:import_file", "kind": "function"},
      {"unit": "import_customers.py:PLANS", "kind": "config"},
      {"unit": "sink raises only ValueError/KeyError or crash is acceptable", "kind": "assumption"},
      {"unit": "billing does not need name/phone", "kind": "assumption"},
      {"unit": "input is BOM-free UTF-8", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "billing sink implementation", "reason": "not_supplied"},
      {"unit": "logging configuration", "reason": "not_supplied"},
      {"unit": "nightly runner", "reason": "not_supplied"},
      {"unit": "tests", "reason": "not_supplied"},
      {"unit": "git history", "reason": "no_tools"},
      {"unit": "hidden-character byte scan", "reason": "no_tools"},
      {"unit": "execution of reproductions", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:25",
     "scenario": "Any row failing validation causes log.error to write dict(row), including the full SSN, name, email and phone, to production logs on every nightly run.",
     "fix": "Log only reader.line_num, row.get('id') and the error; never dict(row). Add a caplog test asserting no SSN-shaped string is logged.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "import_file on a CSV containing '6,X,bad-email,555-0100,900-00-0001,pro' with caplog at ERROR; expected no '900-00-0001' in logs; traced: the record includes 'ssn': '900-00-0001'.",
     "security": true,
     "boundary": {"principal": "anyone with access to application logs or log aggregation", "input": "any malformed CSV row (triggerable by whoever controls the upstream export)", "control": "no masking or field filtering at the log call", "crossed": "restricted PII store to general operational logs", "resource": "customers' national ID numbers and contact details"},
     "siblings_searched": {"searched": "all log calls and all exception messages that could carry row data in import_customers.py", "found": "only one log call; parse_row messages are fixed strings; int() echoes only id; sink exception text is unknown (S2)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:21-26",
     "scenario": "The billing sink raises ConnectionError or a timeout at row N; the exception propagates, rows 1..N-1 are loaded, no counts are returned or reported, and a re-run re-sends loaded rows.",
     "fix": "Validate and load in separate try blocks; retry transient sink errors with a cap; count load_failed separately from invalid; always emit the counts.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "import_file(fixture, sink) with sink raising ConnectionError on the 3rd call; expected counts for 5 rows; traced: ConnectionError propagates and nothing is returned.",
     "security": false,
     "siblings_searched": {"searched": "other exception types that can escape the loop (decode errors, TypeError from parse_row)", "found": "UnicodeDecodeError from open/iteration (F5); TypeError from int(None) is not reachable (refuted)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:14",
     "scenario": "Every row is loaded to billing without name or phone, although the request names those columns and says to load each valid row.",
     "fix": "Include stripped name and phone in the record, or document that billing does not accept them.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "parse_row({'id':'1','name':'A','email':'a@x.test','phone':'555-0100','ssn':'','plan':'pro'}); expected name and phone keys; traced: keys are id, email, plan, ssn.",
     "security": false,
     "siblings_searched": {"searched": "every field read from row in parse_row", "found": "name and phone never read; ssn passed through (S3)"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:21-26",
     "scenario": "The sink raises ValueError for a billing-side rejection and the row is reported as invalid input.",
     "fix": "Count sink failures separately from validation failures.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Run the fixture with a sink raising ValueError('dup'); expected invalid=0, load_failed=5; traced: (0, 5) reported as failed rows."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:19",
     "scenario": "An Excel export with a UTF-8 BOM makes the header '\\ufeffid', so every row raises KeyError, 0 rows load and the job exits normally; a cp1252 file aborts with UnicodeDecodeError.",
     "fix": "Open with encoding='utf-8-sig' and validate the header set before the loop, failing loudly on mismatch.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Prepend '\\ufeff' to the fixture and run; expected (5, 0) or an explicit header error; traced: (0, 5)."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:10-14",
     "scenario": "plan 'pro ' or 'Pro' is rejected as invalid, while email '@' and ssn 'abc' are accepted and sent to billing.",
     "fix": "Strip fields, lowercase plan, use a stricter email check, validate the SSN format or empty.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "parse_row with plan='pro ' raises ValueError (expected accept); parse_row with email='@' succeeds (expected reject)."},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py:20-23",
     "scenario": "A repeated id in the CSV is sent to billing twice.",
     "fix": "Track seen ids and count repeats as invalid.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "CSV with row id 1 twice; expected ok=1, invalid=1; traced: ok=2."},
    {"id": "F8", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "import_customers.py (whole file)",
     "scenario": "The nightly scheduler has no entry point here and the counts are only returned, so invalid-row counts are never reported and failures are invisible.",
     "fix": "Add main() that builds the sink, logs a counts-only summary and exits non-zero on load failures or zero loads; add pytest cases using the fixture.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Search the supplied work for __main__, argparse or a summary log line; expected present; observed absent."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "sink (not supplied)",
     "suspicion": "A re-run after a mid-file failure creates duplicate billing customers.",
     "unresolved_fact": "Whether the sink is idempotent on id."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "import_customers.py:25",
     "suspicion": "Sink exception messages may embed the record and leak PII through %s of e.",
     "unresolved_fact": "The text of exceptions raised by the sink."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "import_customers.py:14",
     "suspicion": "Sending the SSN to billing may exceed data minimization.",
     "unresolved_fact": "Whether billing requires the SSN."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "fixtures/customers.csv",
     "suspicion": "The fixture may contain real people's data committed to the repository.",
     "unresolved_fact": "Data owner confirmation that the records are synthetic, plus a history search for earlier versions."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "import_customers.py, fixtures/customers.csv",
     "suspicion": "Hidden or look-alike characters could alter logic.",
     "unresolved_fact": "A byte-level scan of both files."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "A short row reaches int(None) and raises an uncaught TypeError.", "evidence": "The email check at line 10 fires first on None; id is the first column and is only absent when the header lacks it, which raises KeyError and is caught."},
    {"id": "R2", "candidate": "Blank lines are counted as failures.", "evidence": "csv.DictReader skips rows that are entirely empty."},
    {"id": "R3", "candidate": "The whole file is loaded into memory.", "evidence": "Rows are streamed from the DictReader iterator."},
    {"id": "R4", "candidate": "Row 4's empty SSN crashes or is rejected.", "evidence": "row['ssn'] or None maps it to None at line 14."}
  ]
}
```

Note: I could not run `tools/validate_findings.py` against this block in this session.