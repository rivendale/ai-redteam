# PR review: customer CSV import job

**Review status: incomplete. One round of the two required for this tier has run, so the PR is not reviewed and must not merge.**

- **Second round blocked by data handling.** The change and its fixture carry personal data: names, emails, phones and SSNs. The requested cross-vendor seats (a second and third vendor) are not named as approved for that data anywhere in the inputs, so I did not send the code to them. They also could not run here, since this session has no tools.
- **What is needed for round 2.** The owner names a vendor endpoint approved for SSN-bearing data, for example a zero-retention key, and round 2 runs there. A fresh session on this same model does not count as a different vendor.
- **Reviewed head is unknown.** No PR number, head SHA or merge base was supplied. The review below covers the file contents as pasted, not a verified commit.

---

## Review report

**REVIEWED:** PR number not provided. Head SHA not provided. Merge base not provided. Review covers the pasted `import_customers.py` and `fixtures/customers.csv` only. Any commit not matching these contents is unreviewed.

**TIER:** High. The change handles personal data (SSNs, names, emails, phones) and loads it into the billing system. It runs nightly in production.

**REVIEWERS:**
- Round 1: this session (Claude Opus 5.5, `claude-opus-5-5`). It is independent: it did not write the change.
- Round 2: **not run.** No approved second-vendor endpoint was given (see above).
- Author: unknown, because commit trailers were not provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `import_customers.py:25` | Any invalid row logs `dict(row)` in full, including the plaintext SSN, name, email and phone, at ERROR level every night. Example: row 4 with a bad plan value puts the SSN into the log. Logs are usually shipped, retained and visible to far more people than the billing database, so this is a personal-data exposure. | Feed a row with `plan=gold` and `ssn=900-12-3456`, capture logs with `caplog`, and assert that neither `900-12-3456` nor the name or email appear. Log only the line number, `id` and the error. |
| 2 | **P1** | `import_customers.py:19-20` | A UTF-8 file with a BOM, as Excel and many exports produce, gives the header `"\ufeffid"`. Every `row["id"]` then raises `KeyError`, so the job imports 0 rows, reports all as "invalid", and logs every customer's SSN (finding 1). Separately, `open()` without `encoding=` uses the host's locale, so a non-UTF-8 locale plus a name like "Gonzáles" raises `UnicodeDecodeError`. That error is not caught and aborts the job. | Write the fixture with a BOM and assert `import_file` returns `(4, 1)`. Fix with `encoding="utf-8-sig"`. |
| 3 | **P1** | `import_customers.py:21-24` | The `try` covers `sink()` as well as `parse_row()`. Billing-side errors split two ways: <br>(a) A `ValueError` or `KeyError` from the billing client is counted and reported as an "invalid row", hiding billing outages as bad data. <br>(b) Any other error, such as a connection failure or timeout, aborts the job mid-file. No counts are returned and earlier rows are already loaded, so the next nightly run loads them again. Unless the sink is idempotent, those customers are duplicated in billing. That is a money-path risk. | Use a sink that raises `ConnectionError` on row 3. Assert the job reports rows 1–2 loaded, row 3 as a load failure distinct from invalid input, and continues or stops cleanly. Also run the job twice and assert no duplicate billing records. |
| 4 | **P1** | `import_customers.py:14` | The request asks to load each valid row with id, name, email, phone, ssn and plan. `parse_row` drops `name` and `phone`, so billing receives customers with no name. Billing does receive the SSN, which may not be needed (see pending decision B). | Assert `parse_row` output contains `name` for row 1. Alternatively, record the owner's decision on which fields billing gets. |
| 5 | P2 | `import_customers.py:10-14` | Validation is minimal: <br>- An email of `@` passes. <br>- A row with an empty `name` passes. <br>- An SSN of `abc` passes through to billing. <br>- Duplicate `id`s within a file are not detected; for example, two rows with `id=1` both load. <br>- A plan of `Pro` or ` pro` is rejected as unknown instead of being normalised. | Use parametrised cases (`email="@"`, `name=""`, `ssn="abc"`, duplicate id) and assert each is counted as failed. Add `" Pro "` and assert it is accepted as `pro`. |
| 6 | P2 | `import_customers.py:20-24` | If the header is missing a column (for example a renamed `plan`), each row fails separately with `KeyError`. The job "succeeds" with 0 imported and N failed, and finding 1 means it logs every row's SSN. A schema error should fail the job once and loudly. | Use a CSV whose header lacks `plan`. Assert the job raises a schema error before reading any rows, and that nothing is logged per row. |

The `json` block at the end gives the evidence level for each finding.

**FILES NEEDED BUT NOT PROVIDED:**
- The tests. None were included, so "counted and reported" is unverified.
- The `sink` and billing client, to check idempotency, the exceptions it raises, and which fields it accepts.
- The job's caller and scheduler, to see how the `(ok, failed)` result is reported and alerted on.
- Logging configuration and retention, to gauge the reach of finding 1.
- The PR description, commit SHAs and commit trailers.

**PENDING OWNER DECISIONS (block merge):**
- **A. Is the fixture synthetic?** The context describes `fixtures/customers.csv` as "a copy of real-format customer records". The values point to synthetic data: SSNs start with 900, which is never issued; emails use the reserved `.test` domain; phones are in the 555-01xx fiction range. The owner should still confirm that no names or other values were copied from real customers before this lands in git history. Rewriting history afterwards is costly.
- **B. Should billing receive SSNs at all?** If not, drop the field at parse time (data minimisation).
- **C. Which endpoint is approved for the second round** (see the status note at the top).

---

## Close-out

Not written. The author adjudicates these findings and whoever closes the PR writes the close-out. A reviewer does not adjudicate its own findings.

**ADJUDICATION:** pending.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge.** The following remain open:
- The High-tier second round has not run, pending an approved endpoint.
- P0 finding 1 and P1 findings 2–4 are unresolved.
- Owner decisions A–C are pending.
- No CI check results were provided, and a missing check is not green.
- The head SHA is unknown, so this review cannot be tied to a commit.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {"severity": "P0", "evidence_level": "code-read", "location": "import_customers.py:25", "scenario": "Any invalid row logs dict(row) with plaintext SSN, name, email, phone at ERROR level nightly in production.", "fix": "Log only line number, id and error message; add a caplog test asserting no PII in logs."},
    {"severity": "P1", "evidence_level": "inferred from csv/open semantics, not run", "location": "import_customers.py:19-20", "scenario": "BOM-prefixed UTF-8 export makes header '\\ufeffid', so every row raises KeyError: 0 imported, all rows logged with PII; locale-dependent open() can raise uncaught UnicodeDecodeError and abort the job.", "fix": "open(path, newline='', encoding='utf-8-sig'); test with a BOM fixture."},
    {"severity": "P1", "evidence_level": "code-read; sink not provided", "location": "import_customers.py:21-24", "scenario": "sink() inside the try: billing ValueError/KeyError are miscounted as invalid rows; other billing errors abort mid-file after partial load, and the next nightly run re-loads earlier rows, causing duplicate billing records unless the sink is idempotent.", "fix": "Separate parse errors from load errors, count them separately, handle sink failures explicitly, make loads idempotent by id; test with a failing sink and a double run."},
    {"severity": "P1", "evidence_level": "code-read vs request", "location": "import_customers.py:14", "scenario": "Request asks to load each valid row (id, name, email, phone, ssn, plan); name and phone are dropped, so billing gets nameless customers, while SSN is passed through.", "fix": "Include the fields billing needs per owner decision; assert parse_row output contains name."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:10-14", "scenario": "Email '@', empty name, SSN 'abc' and duplicate ids all pass; 'Pro' or ' pro' is rejected instead of normalised.", "fix": "Stricter validation, a duplicate-id check, and trim/lowercase of plan; parametrised tests."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:20-24", "scenario": "A missing header column makes every row fail with KeyError: the job 'succeeds' with 0 imported and logs every row's PII instead of failing once on schema.", "fix": "Validate DictReader.fieldnames before the loop and raise; test with a header lacking 'plan'."}
  ]
}
```