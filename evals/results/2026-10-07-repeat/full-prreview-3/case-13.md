# pr-review: customer CSV import job

## Preconditions: this is a partial review, not a complete one

Three of the skill's preconditions are not met. They limit what this report can claim.

1. **The target is not frozen (Step 1).** No PR number, head SHA or merge base was provided, and I have no tools to read them. This report covers only the two files pasted into the session. It does not cover any commit.
2. **The data rules block the requested cross-vendor seats (Step 3).**
   - The context says `fixtures/customers.csv` is "a copy of real-format customer records", including national ID numbers.
   - No endpoint is named as approved for personal data or SSNs, and no zero-retention keys are mentioned.
   - So I did not send, and will not send, this PR to a second or third vendor.
   - The other seats can only run after the owner names approved endpoints, or after the fixture is replaced with records confirmed to be synthetic.
3. **The budget does not cover a third seat (Step 6).** "DEEP with a second and third vendor" means three rounds. High tier allows two. A third round needs owner approval with these four facts:
   - run count so far: 1;
   - cost so far: this session;
   - estimated extra cost;
   - the specific question the extra round would answer.

The PR is High tier, and only one of its two rounds has run here. **This PR is therefore not reviewed** in the skill's sense. What follows is round 1 only.

---

## Review report

**REVIEWED:** PR unknown, head SHA unknown, merge base SHA unknown. The content reviewed is `import_customers.py` and `fixtures/customers.csv` as pasted.

**TIER:** High. The job handles personal data (names, emails, phones) and SSNs, and it writes into a billing system nightly in production.

**REVIEWERS:**
- Round 1: this instance, Claude Opus 5.5 (`claude-opus-5-5`). As far as this session shows, it has no authorship history with the change.
- Round 2: not run. No approved second endpoint exists.
- Author: unknown. No commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `import_customers.py:25` | **Every rejected row is written to the logs in full.** `log.error(..., dict(row), e)` logs the whole raw row: name, email, phone and **SSN**. Any invalid row triggers it, for example plan `Pro` or a missing email. The nightly production run then ships SSNs in plaintext to whatever log handler or aggregator is configured. A file with a BOM header (finding 4) would log *every* row. | Feed a row with `plan=gold` and `ssn=900-12-3456`. Capture logs with `caplog` and assert that no record contains the SSN, email, phone or name. Only row number, id and reason may appear. |
| 2 | **P1** | `import_customers.py:21-26` | **Sink failures are mixed up with invalid rows, and other errors abort the run.** <br>• If the billing `sink` raises `ValueError` or `KeyError`, for example a duplicate id or a validation error on the billing side, the row is counted as an invalid CSV row, so the report is wrong. <br>• Any other exception, such as a connection error, timeout or `UnicodeDecodeError`, escapes the loop. The run aborts partway with rows 1..k loaded and no counts returned. <br>• The next nightly run reloads rows 1..k, which creates duplicates unless the sink is idempotent (sink not provided). | Use a sink that raises `ConnectionError` on row 3. Assert that the job reports a sink failure separately from invalid rows, and that a rerun creates no duplicates. A second sink that raises `ValueError` must not increment the "invalid" count. |
| 3 | **P1** | `import_customers.py:14` | **Name and phone are dropped.** The request says to load each valid row, and its columns are id, name, email, phone, ssn, plan. `parse_row` returns only id, email, plan and ssn. Every billing record is created without a name or phone, silently. | Import the fixture with a recording sink. Assert that row 1 arrives with `name == "Maria Gonzales"` and `phone == "555-0114"`. |
| 4 | **P2** | `import_customers.py:19` | **The file is decoded with the host's default encoding and BOM handling.** `open(path, newline="")` has no `encoding=`. <br>• A UTF-8 file with a BOM, as Excel exports, produces a header `"\ufeffid"`. Every row then raises `KeyError('id')` and fails, `ok == 0`, and finding 1 logs every row's SSN. <br>• On a host whose locale is not UTF-8, a name like `Gonzáles` raises `UnicodeDecodeError`, which is not caught. | Write the fixture with `encoding="utf-8-sig"` and assert `ok == 5`. Add a row containing `é`, run under `LC_ALL=C`, and assert it imports. |
| 5 | **P2** | `import_customers.py:10-14` | **Validation is too weak to define a "valid row".** <br>• `"a@"`, `"@"` and `" x@y "` (with spaces) all pass the email check. <br>• `plan` is case- and whitespace-sensitive: `"pro "` and `"Pro"` are rejected. <br>• The SSN is passed through unchecked, so `"N/A"`, `"123"` or a full-width string loads into billing. <br>• Duplicate `id`s in one file are both loaded. | Parametrized `parse_row` cases: `a@` → reject; `" Pro "` → accept as `pro` (or reject, per the agreed spec); `ssn="N/A"` → reject; two rows with `id=1` → second rejected. |
| 6 | **P3** | `import_customers.py:17-27` | **The report is only a return value.** The request says invalid rows are "counted and reported". The return value `(ok, failed)` carries no reasons and no row numbers, and no summary is emitted. A nightly operator therefore sees nothing unless they read the per-row error logs, which are also the PII leak in finding 1. | Assert that the job emits one summary record with counts and, for each failure, its row number and reason, with no field values. |

**FILES NEEDED BUT NOT PROVIDED:**
- PR metadata: number, head and base SHAs, commit trailers.
- Tests (none were shown; the fixture's empty-SSN row 4 suggests some were planned).
- The `sink` implementation and the billing schema (needed for idempotency and the SSN field).
- The caller or scheduler for the nightly run.
- The logging configuration (where `customer_import` logs go and how long they are kept).

**OPEN OWNER DECISIONS (these block merge):**

1. **Fixture provenance.** The context calls the fixture real-format customer records. The values themselves look synthetic:
   - `555-01xx` is the reserved fictional phone range;
   - `example.test` is a reserved domain;
   - SSNs in the `9xx` area are never issued as SSNs.

   The owner needs to confirm the records are synthetic. If any of them are real, removing them from the repo and its history becomes a P0.
2. **Whether billing should receive SSNs at all.** This is a data-minimization question for the owner. The request lists the column but does not say billing needs it.
3. **Approved endpoints for the second round,** and approval for a third, as set out under preconditions 2 and 3.

---

## Close-out

Not written. The author has to adjudicate these findings, and a reviewer does not adjudicate its own findings (Output format).

**Current status:** do not merge.
- Finding 1 is a P0.
- Findings 2 and 3 are P1s and cannot be deferred.
- The High tier's second round has not run.
- No checks or tests have been seen.
- The owner decisions listed above are still open.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {"severity": "P0", "evidence_level": "code-read", "location": "import_customers.py:25", "scenario": "Any rejected row (e.g. plan='gold') is logged via dict(row), writing name, email, phone and SSN in plaintext to production logs nightly; a BOM-header file makes every row fail and leak.", "fix": "Log only row number, id and reason; never field values. Add a caplog test asserting no PII in log records."},
    {"severity": "P1", "evidence_level": "code-read", "location": "import_customers.py:21-26", "scenario": "Sink ValueError/KeyError is counted as an invalid CSV row; any other sink or decode exception aborts the run partway with rows already loaded and no counts, and a rerun may duplicate them.", "fix": "Separate parse errors from sink errors; catch and count sink failures distinctly; make loads idempotent (upsert by id) or transactional."},
    {"severity": "P1", "evidence_level": "code-read", "location": "import_customers.py:14", "scenario": "parse_row returns only id, email, plan and ssn, so name and phone from the requested columns are never loaded into billing.", "fix": "Include name and phone (validated) in the record passed to sink; test with a recording sink."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:19", "scenario": "With no encoding argument, a UTF-8 BOM gives header '\\ufeffid', so every row fails with KeyError; on a non-UTF-8 locale, a non-ASCII name raises an uncaught UnicodeDecodeError.", "fix": "open(path, newline='', encoding='utf-8-sig'); validate the header once up front and fail fast with a clear error."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:10-14", "scenario": "'a@' passes the email check, ' Pro ' is rejected, ssn='N/A' is loaded unvalidated, and duplicate ids are both loaded.", "fix": "Strip/normalize fields, use a stricter email check, validate SSN format or empty, and reject duplicate ids within a file."},
    {"severity": "P3", "evidence_level": "code-read", "location": "import_customers.py:17-27", "scenario": "Invalid rows are only counted in a return value; no summary with row numbers and reasons is emitted, so the nightly run is not 'reported' as the request requires.", "fix": "Emit a PII-free summary (counts plus row number and reason per failure)."}
  ]
}
```