# pr-review: customer CSV import job

## Before the findings: what this review is and is not

- **No frozen target (Step 1 not met).** I was given file contents with no PR number, head SHA or merge base. This was not done in a worktree at a known commit. These findings apply only to the text shown above. Before anything is acted on, someone needs to record the SHA it matches.
- **Tier: High.** The job reads and forwards national ID numbers (SSNs), names, emails and phone numbers. It runs nightly in production.
- **Cross-vendor seats were not run (Step 3).** The context asks for a second and third vendor as blind seats. Nobody has said which endpoints are approved for code and fixtures carrying SSNs, so I have sent nothing anywhere. I have no tools in this session anyway. A second vendor justifies a second opinion. It does not justify sending personal data somewhere it may not be allowed to go. **This is round 1 of the 2 that High requires, so the PR is not reviewed yet.** To finish, the owner needs to name an approved endpoint, such as a zero-retention key, and run round 2 there.
- **Independence:** this session did not write the change. There are no commit trailers to read, so the author is unknown.

---

## Review report

**REVIEWED:** PR unknown, head SHA unknown, merge base unknown. These are file contents as supplied.
**TIER:** High, because of personal data (SSN, name, email, phone) in a nightly production job.
**REVIEWERS:** Round 1 is this instance (claude-opus-5-5), reading only, with no code executed. Round 2 has not run. The author is unknown because no commit trailers were supplied.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `import_customers.py:25` | Any invalid row, for example `plan=Pro` or an email with no `@`, logs `dict(row)`. That writes the full SSN, name, email and phone into the application logs every night. Log pipelines usually have wider access and longer retention than the billing store, so this puts SSNs in logs, a personal data exposure. | Feed a row with `ssn=900-12-3456, plan=bogus`, capture logs with `caplog`, and assert `"900-12-3456"` and the email are not in `caplog.text`. Log only the line number and `id`. |
| 2 | **P1** | `import_customers.py:14` | The request says each valid row is loaded with its columns: id, name, email, phone, ssn, plan. `parse_row` drops `name` and `phone`, so billing receives customers with no name or phone. It still forwards `ssn`, which billing may have no need for. Either the request is not met or the data minimisation choice is undocumented. **This needs an owner decision on whether billing should get the SSN.** | Pass a valid row through `parse_row` and assert that the output field set equals exactly the agreed set. Today it fails because `name` and `phone` are missing. |
| 3 | **P1** | `import_customers.py:21-26` | If `sink` raises anything other than `ValueError`/`KeyError` (a timeout, `ConnectionError`, or a 5xx wrapped as `RuntimeError`), the job stops partway through the file. It returns no counts and leaves earlier rows loaded. The next night's rerun loads those rows again, and nothing shows the sink is idempotent. The reverse also happens: if the sink raises `ValueError`, a billing failure is counted as an "invalid row". | Use a sink that raises `ConnectionError` on row 3 of 5. Assert that the job reports this as a sink failure, separate from invalid rows, and that the behaviour is defined, whether that is abort-with-report or continue. |
| 4 | P2 | `import_customers.py:20-21` | If the header is missing a column, has a BOM (`\ufeffid`), or renames a column, every row raises `KeyError`. The job returns `(0, N)` and logs N rows of PII, which combines with #1. It does not fail fast on a bad file. The lack of an `encoding=` argument makes BOM and locale problems more likely. | Use a CSV with a UTF-8 BOM header and assert that the job raises a clear "bad header" error before processing any rows. |
| 5 | P2 | `import_customers.py:11-14` | Validation is thin. ` pro`, `Pro` and `pro ` are rejected instead of normalised. Emails are not stripped. `ssn` and `phone` are never checked for format, so `ssn="N/A"` or `"123"` is forwarded to billing as valid. | Check that `ssn="abc"` is counted invalid and that `plan=" pro"` is either normalised or rejected, depending on what the spec says. |
| 6 | P2 | `import_customers.py:19-27` | Duplicate `id` values in one file are both loaded. What billing then does is unknown: it might overwrite or create duplicates. | Use two rows with `id=1` and assert that the second is counted invalid or flagged. |
| 7 | P1 (unverified) | `fixtures/customers.csv` | The context calls this "a copy of real-format customer records". The values look synthetic: SSNs in the 900- range are never issued as SSNs, the phones use the fictional 555-01xx range, and the emails are on the reserved `.test` domain. If any of the values came from real customers, this is SSNs committed to git history, which would be P0. **Get written confirmation that the fixture is synthetic.** | A CI check that fails if a fixture SSN falls outside 900-999 or an email domain is not `example.test`. |
| 8 | P2 | `fixtures/customers.csv` | All 5 rows are valid. Row 4's empty SSN maps to `None` and passes. So the invalid-row path, where #1 lives, is never exercised. No tests were supplied either, so the "counted and reported" requirement is untested. | Add invalid rows (bad email, unknown plan, non-integer id) and assert that `import_file` returns `(5, 3)` or whatever the expected counts are. |

**FILES NEEDED BUT NOT PROVIDED:** the test file(s), the `sink` implementation and billing API contract (needed to judge idempotency and which fields billing requires), the logging config and its retention/access rules, the nightly job wrapper (to see how the exit status and counts are reported), the PR description, and the commit SHAs.

---

## Close-out

This part is not written yet. The skill says a reviewer never adjudicates its own findings. The author adjudicates, and whoever closes the PR writes this section.

**ADJUDICATION:** pending for #1–#8.
**VERIFIED AFTER FIXES:** none yet.
**MERGE RECOMMENDATION:** **Do not merge.**
- The High tier's second round has not run, because no approved endpoint has been named for SSN-bearing code.
- P0 #1 (SSNs in logs) is open.
- P1 #2, #3 and #7 are open.
- Owner decisions are pending: should billing receive the SSN (#2), and is the fixture synthetic (#7)?
- No head SHA is recorded and no checks were seen.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {"severity": "P0", "evidence_level": "code-read", "location": "import_customers.py:25", "scenario": "Any invalid row logs dict(row), writing SSN, name, email and phone to application logs nightly.", "fix": "Log only line number and id; add a caplog test asserting no SSN/email in log output."},
    {"severity": "P1", "evidence_level": "code-read", "location": "import_customers.py:14", "scenario": "parse_row drops name and phone required by the request while forwarding ssn to billing; billing gets incomplete records plus an SSN it may not need.", "fix": "Owner decides the billing field set (likely exclude ssn); test parse_row output keys equal that set."},
    {"severity": "P1", "evidence_level": "code-read", "location": "import_customers.py:21-26", "scenario": "Sink errors other than ValueError/KeyError abort mid-file with no counts and partial load; reruns may duplicate. Sink ValueErrors are miscounted as invalid rows.", "fix": "Separate parse errors from sink errors; define abort-or-continue behaviour and idempotency; test with a failing sink."},
    {"severity": "P1", "evidence_level": "unverified", "location": "fixtures/customers.csv", "scenario": "Context says the fixture is a copy of real-format customer records; if any values are real, SSNs are committed to git history (P0).", "fix": "Confirm in writing that the data is synthetic; add a CI guard on fixture SSN range and email domain."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:20-21", "scenario": "Missing/renamed header or UTF-8 BOM makes every row a KeyError: job returns (0, N) and logs N PII rows instead of failing fast.", "fix": "Validate the header before the loop, open with encoding='utf-8-sig', and raise on mismatch."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:11-14", "scenario": "No normalisation or format checks: ' pro'/'Pro' rejected, ssn='N/A' or phone garbage forwarded as valid.", "fix": "Strip and normalise fields; validate ssn and phone formats; add tests."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:19-27", "scenario": "Duplicate ids within a file are all loaded into billing.", "fix": "Track seen ids and count duplicates as invalid; test with two id=1 rows."},
    {"severity": "P2", "evidence_level": "code-read", "location": "fixtures/customers.csv", "scenario": "Fixture contains only valid rows and no tests were supplied, so the invalid-row counting and logging path is untested.", "fix": "Add invalid rows and assert exact (ok, failed) counts."}
  ]
}
```