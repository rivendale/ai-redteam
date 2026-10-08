# pr-review: customer CSV import job

**Review report**

**REVIEWED:** Not identifiable. No PR number, head SHA or merge base SHA was provided, and I have no tools to read them. This review covers only the two files pasted into this session (`import_customers.py`, `fixtures/customers.csv`). It is not bound to a commit. Any commit the owner later names must be checked against this text.

**TIER:** High. The job reads and forwards national ID numbers (SSN), emails and phone numbers, which is personal data. It also runs nightly in production against the billing system.

**REVIEWERS:**
- Round 1: this instance (Claude Opus 5.5, `claude-opus-5-5`). Nothing here shows this session wrote the change.
- Author: unknown. No commit trailers were provided.
- **Round 2 and the requested cross-vendor blind seats: not run.** Step 3 requires an approved endpoint for personal data before any code leaves this session. No approved second or third vendor endpoint has been named.
  - The fixture is described as "a copy of real-format customer records" with national ID numbers. Sending it to another vendor would publish that data where it may not be allowed to go.
  - I am stopping at round 1 rather than downgrading the tier silently. **A High-tier PR whose second round has not run is not reviewed.**
  - To proceed, the owner must name the approved endpoint(s), for example zero-retention keys cleared for personal data. Then send the code only, with the fixture replaced by obviously synthetic data.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `import_customers.py:25` | Any invalid row (e.g. plan `"enterprise"`, missing `@`) is logged with `dict(row)`. That writes the full record to the production logs every night: name, email, phone and **SSN**. Log pipelines usually have wider access and longer retention than the source data, so this is a personal-data breach by design. | Feed a row with `plan=enterprise`, `ssn=900-12-3456`. Capture logs with `caplog`. Assert that neither `900-12-3456` nor the email appears. Log only the row number (`reader.line_num`), `id` and the error reason. |
| 2 | **P1** | `import_customers.py:19` | The file is opened without `encoding=`. If the CSV is exported with a UTF-8 BOM (Excel's default "CSV UTF-8"), the first header becomes `"\ufeffid"`. `row["id"]` then raises `KeyError` on **every** row, so all rows count as "invalid" and the job returns `(0, N)` with no failure signal. Finding 1 compounds this: every customer's SSN is logged. On a non-UTF-8 host locale, accented names raise an uncaught `UnicodeDecodeError` and the job crashes. | Write the fixture with `encoding="utf-8-sig"`, run `import_file`, assert `ok == 4`. Fix: `open(path, newline="", encoding="utf-8-sig")`. Also validate the header once and abort if required columns are missing, instead of failing per row. |
| 3 | **P1** | `import_customers.py:21-26` | `sink(...)` is inside the same `try` as `parse_row`. (a) If the billing sink raises `ValueError`/`KeyError` (e.g. it rejects a duplicate), a *valid* row is reported as an *invalid* row. (b) Any other exception (timeout, connection reset) aborts the loop mid-file. Rows already sent stay loaded, no counts are returned, and the next nightly run re-sends them. Duplicates appear unless the sink is idempotent, and I have not seen the sink. | Use a sink that raises `ConnectionError` on row 3. Assert the job reports rows 1–2 loaded and row 3 as a load failure (separate from invalid), and that a rerun does not create duplicates. Fix: catch parse errors and sink errors separately and count them separately. |
| 4 | **P1** | `import_customers.py:14` | The request names columns id, name, email, phone, ssn, plan. `parse_row` returns only id, email, plan and ssn, so **name and phone are silently dropped**. Every customer reaches billing with no name. If dropping them is intended data minimization, it is undocumented. If it is not intended, billing records are incomplete. | Run `parse_row` on fixture row 1. Assert the output contains `name == "Maria Gonzales"` and `phone == "555-0114"`, or the request is amended to say those fields are excluded. |
| 5 | **P2** | `import_customers.py:10-14` | Validation is minimal: | Parametrized test with `" pro"`, `"x@"`, `"12-34"` and a duplicate `id`. Assert each is counted invalid (or plan normalized) and the duplicate is rejected. |
| | | | – `"@"` alone passes as an email. | |
| | | | – Values are not stripped, so `" a@b.test"` loads with a leading space and `"pro "` is rejected as an unknown plan. | |
| | | | – SSN is forwarded unvalidated (`"abc"` loads). | |
| | | | – Duplicate `id`s in one file are not detected and are loaded twice or overwrite each other. | |
| 6 | **P2** | `fixtures/customers.csv` (whole file) | The context calls this "a copy of real-format customer records." The values look synthetic: `900-` SSN area numbers are never issued, `555-01xx` is the fictional range, and `.test` is a reserved TLD. But provenance is not stated. If any row derives from a real customer, committing it puts personal data into git history permanently. It would also be sent to every reviewer and CI system. | A test or CI check asserting every fixture SSN starts with `9`, every email ends in `.test`, and every phone is `555-01xx`. Plus written owner confirmation that the file is synthetic. |
| 7 | **P2** | (no test file in the PR) | No tests were provided, so none of the behaviour above is verified. A nightly production job touching billing and SSNs has no regression coverage. | Tests 1–6 above, run in CI. |

**Open owner decision (not a finding):** should SSNs be sent to the billing system at all? Billing usually does not need a national ID. If it does not, the job should drop the column, which also removes most of the risk in findings 1 and 6.

**FILES NEEDED BUT NOT PROVIDED:**
- PR number, head SHA and merge base SHA
- Commit trailers (authorship)
- PR description
- Sink / billing-system client code, to judge idempotency and which exceptions it raises
- The job runner or scheduler, to see how `(ok, failed)` is reported and whether an all-failed run alerts
- Logging configuration (destination, retention, access)
- Tests
- CI check list

**Close-out:** not written. The reviewer does not adjudicate its own findings. The author adjudicates each finding, and whoever closes the PR writes the close-out.

**MERGE RECOMMENDATION (from reviewer's position): do not merge.**
- The High-tier second round has not run, because no approved endpoint exists for this data.
- P0 #1 and P1 #2–#4 are open.
- The SSN-to-billing decision is pending.
- No head SHA was named.
- No checks are visible.

```json
{
  "verdict": "do_not_merge",
  "notes": "High tier (SSN/PII, production billing). Only round 1 run; round 2 and cross-vendor seats withheld because no endpoint approved for personal data was named. No PR/head/base SHA provided. Owner decision pending on whether SSN should reach billing at all.",
  "findings": [
    {
      "severity": "P0",
      "evidence_level": "confirmed_by_code_reading",
      "location": "import_customers.py:25",
      "scenario": "Any invalid row is logged via dict(row), writing name, email, phone and SSN to production logs every nightly run.",
      "fix": "Log only line number, id and error reason; never the row. Add caplog test asserting no SSN/email in logs."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_by_code_reading",
      "location": "import_customers.py:19",
      "scenario": "No encoding specified: a UTF-8 BOM makes the header '\\ufeffid', every row raises KeyError, job returns (0, N) silently and logs every customer's SSN; a non-UTF-8 locale raises uncaught UnicodeDecodeError.",
      "fix": "open(path, newline='', encoding='utf-8-sig'); validate header once and abort on missing columns."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_by_code_reading",
      "location": "import_customers.py:21-26",
      "scenario": "sink() shares the try with parse_row: sink ValueError/KeyError miscounts valid rows as invalid; other sink exceptions abort mid-file with partial load and no report, and the nightly rerun can duplicate rows.",
      "fix": "Separate parse and load error handling and counts; make the load idempotent or resumable; test with a sink failing mid-file."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_by_code_reading",
      "location": "import_customers.py:14",
      "scenario": "parse_row drops name and phone, which the request lists; customers reach billing without a name.",
      "fix": "Include name and phone, or amend the request to document their exclusion."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_by_code_reading",
      "location": "import_customers.py:10-14",
      "scenario": "'x@' passes as email; untrimmed whitespace loads ' a@b.test' and rejects 'pro '; malformed SSN forwarded; duplicate ids not detected.",
      "fix": "Strip fields, stricter email check, validate or drop SSN, reject duplicate ids within a file; parametrized tests."
    },
    {
      "severity": "P2",
      "evidence_level": "needs_owner_confirmation",
      "location": "fixtures/customers.csv",
      "scenario": "Described as a copy of real-format customer records; values look synthetic (900- SSNs, 555-01xx, .test) but provenance is unstated; if any row is real, PII is committed to git history and sent to every reviewer and CI system.",
      "fix": "Owner confirms the fixture is synthetic; add a CI check that fixture values stay in reserved/fictional ranges."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed_absent_from_inputs",
      "location": "(no test file)",
      "scenario": "No tests accompany a nightly production job handling SSNs and billing; none of the behaviour is verified.",
      "fix": "Add the tests listed for findings 1-6 and run them in CI."
    }
  ]
}
```