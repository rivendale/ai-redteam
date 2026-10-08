# pr-review: customer CSV import job

## Before the findings: what stopped this review short of done

**1. The target is not frozen.** No PR number, head SHA or merge base was provided. I also had no tools, so I could not check out a throwaway worktree or read commit trailers. These findings apply only to the two files pasted above, at an unknown commit.

**2. Tier is High.** The code reads, loads and logs national ID numbers (SSN), names, emails and phone numbers. Personal data puts it in High regardless of size. The job also runs nightly in production. High needs two independent rounds, and only one has run (this one). **This PR is not reviewed until a second round runs.**

**3. I did not run the cross-vendor seats.** The context asks for a second and third vendor as blind seats. Step 3 says to decide which endpoints are approved for this data *before* anything is sent, and none are named. The work under review includes `fixtures/customers.csv`, described as "a copy of real-format customer records (… national ID numbers)." A second vendor justifies a second opinion. It does not justify sending SSN-bearing data somewhere it may not be allowed to go. Before any further seat runs, the owner should:
   - name the approved endpoints, such as zero-retention keys, for code and fixtures carrying personal data; and
   - confirm where the fixture came from (finding 7). If the records are real, they should not be sent to any reviewer, and they should not be in the repo.

   If no approved second reviewer exists, the review stops here.

**4. Independence.** As far as I can tell, this instance did not write the change. I could not read the `Co-Authored-By` trailers, so authorship is unrecorded.

---

**Review report**

**REVIEWED:** customer CSV import (PR number not given). Head SHA: **not provided**. Merge base: **not provided**. Only `import_customers.py` and `fixtures/customers.csv` as pasted.

**TIER:** High. The code handles personal data (SSN, name, email, phone), and the job is nightly in production. Required rounds: 2. Rounds run: 1.

**REVIEWERS:** Round 1: this instance (claude-opus-5-5), static read only, no code executed. Round 2: **not run**, blocked on endpoint approval (Step 3). Author: unknown, trailers not available.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `import_customers.py:25` | Any invalid row (bad email, unknown plan, non-numeric id) is logged with `dict(row)`. That is the full record: name, email, phone and **SSN in cleartext**, written to the production logs every night and to wherever those logs ship. Example: row `6,A B,a@x.test,555,900-11-2222,gold` logs `'ssn': '900-11-2222'`. | Feed a row with `plan=gold`. Capture the log with `caplog`. Assert neither the SSN, email nor phone appears. Log only the row number or `id` and the reason. |
| 2 | **P1** | `import_customers.py:14` | The request says to load each valid row with id, name, email, phone, ssn, plan. `parse_row` returns only id, email, plan and ssn. **Name and phone are silently dropped**, so every customer loads into billing without a name or phone. | Import the fixture with a recording sink. Assert each record has `name` and `phone` equal to the CSV values. |
| 3 | **P1** | `import_customers.py:22,24` | `sink()` sits inside the same `try` as validation. (a) If the billing sink raises `ValueError` or `KeyError` (for example a duplicate id or an API rejection), a billing failure is counted and logged as an "invalid row", so the report misattributes it. (b) Any other exception, such as a connection error, timeout or `TypeError`, is uncaught. The job aborts partway through the file with some rows loaded, no counts returned and nothing reported. A nightly rerun then re-sends the rows that already loaded, unless the sink is idempotent (I could not see it). | (a) Use a sink raising `ValueError` on id 3. Assert it is reported as a sink failure, not an invalid row. (b) Use a sink raising `ConnectionError` on id 3. Assert the job returns or reports counts for rows 1–2 and the failure, and doesn't crash silently. Also test that a rerun does not duplicate ids 1–2. |
| 4 | P2 | `import_customers.py:19` | `open()` has no `encoding`, so it uses the host locale. If the file has a UTF-8 BOM (common in Excel exports), the first header becomes `\ufeffid`. `parse_row` then raises `KeyError` on `row["id"]` for **every** row, the job reports `ok=0, failed=N`, and it logs every record (see finding 1). On a non-UTF-8 locale, names like "Halvorsen" with diacritics break or decoding raises `UnicodeDecodeError`, which is uncaught and aborts the job. There is no header validation. | Write the fixture with `encoding="utf-8-sig"`. Assert `ok == 5`. Separately, assert that a missing or renamed header fails fast with one clear error, not N row errors. |
| 5 | P2 | `import_customers.py:10–13` | Validation is shallow. `"a@"`, `"@"` and `" maria@x.test "` (with spaces) all pass as emails. `"Pro"` and `" pro"` are rejected as unknown plans. SSN is accepted in any shape or left empty, so `"abc"` loads into billing as an SSN. Duplicate `id`s within a file are not detected. | Parametrized tests: `"a@"` → invalid. `" Pro "` → decide and assert the behavior. `ssn="abc"` → invalid. A duplicate id → second row rejected. |
| 6 | P3 | `import_customers.py:17–27` | "Invalid rows are counted and reported": the counts are returned, but the only "report" is per-row error logs, and those must change because of finding 1. Nothing summarizes `ok` and `failed`, or the reasons, for the nightly operator. A nightly run where 100% of rows fail looks the same as a success unless the caller checks the return value (caller not provided). | Assert a summary line or report (counts plus reasons by row number, no PII) is emitted. Assert a failure-rate threshold makes the job exit non-zero. |
| 7 | P0 *if real*, else none (owner decision) | `fixtures/customers.csv:2–6` | The context calls this "a copy of real-format customer records … national ID numbers." The values look synthetic: 900-prefixed SSNs are not issued, 555-01xx numbers are reserved fictional numbers, and the domain is `example.test`. That is unconfirmed. If any row is copied from real customers, real PII is committed to the repo and its history. | None. This needs a provenance answer from the owner. If the data is real, purge it from history and replace it with generated data. |

**Not findings, but open owner questions:**
- Does billing actually need the SSN? Loading it follows the request as written, but it widens where SSNs live. This is a data-minimization decision for the owner.
- No tests were included with the PR. "Valid rows load, invalid rows counted" is so far asserted, not demonstrated.

**FILES NEEDED BUT NOT PROVIDED:** the PR metadata (number, head SHA, merge base, commit trailers); the `sink` implementation and the billing client, needed to settle idempotency and the exceptions it raises; the caller or nightly scheduler, needed to judge how counts are reported and how failures surface; the logging config and log destinations, needed to size the exposure in finding 1; and the tests, if any exist.

---

**Close-out**

Pending. Per the skill, the reviewer does not adjudicate its own findings. The author adjudicates findings 1–6 (P0 and P1 items cannot be deferred), and the owner answers finding 7 and the endpoint question.

**ADJUDICATION:** none yet.
**VERIFIED AFTER FIXES:** nothing has been fixed yet.

**MERGE RECOMMENDATION: do not merge.**
- One open P0 (SSN and PII in production logs, finding 1) and two P1s (name and phone dropped, finding 2; sink errors miscounted or aborting mid-file, finding 3).
- Only one of the two High-tier rounds has run. The second is blocked until approved endpoints for personal data are named.
- An owner decision is pending on the fixture's provenance (finding 7).
- The head SHA was not recorded and no checks were visible, so nothing can be confirmed green.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {"severity": "P0", "evidence_level": "code_read", "location": "import_customers.py:25", "scenario": "Any invalid row is logged via dict(row), writing full name, email, phone and SSN in cleartext to production logs nightly.", "fix": "Log only row number/id and the reason; add a caplog test asserting no SSN/email/phone in log output."},
    {"severity": "P1", "evidence_level": "code_read", "location": "import_customers.py:14", "scenario": "parse_row omits name and phone, so every customer loads into billing without them, contrary to the request.", "fix": "Include name and phone in the returned record; test the sink receives all six fields."},
    {"severity": "P1", "evidence_level": "code_read_sink_not_seen", "location": "import_customers.py:22", "scenario": "sink() is inside the validation try: sink ValueError/KeyError is miscounted as an invalid row; any other sink exception aborts mid-file with partial load, no counts and no report; rerun may duplicate already-loaded rows.", "fix": "Separate validation from loading; catch and count sink failures distinctly; make the load idempotent or resumable; test with failing sinks."},
    {"severity": "P2", "evidence_level": "code_read", "location": "import_customers.py:19", "scenario": "No encoding: a UTF-8 BOM makes the header '\\ufeffid', every row fails with KeyError (and is logged with PII); a non-UTF-8 locale misdecodes or raises an uncaught UnicodeDecodeError.", "fix": "open(path, newline='', encoding='utf-8-sig'); validate headers once and fail fast."},
    {"severity": "P2", "evidence_level": "code_read", "location": "import_customers.py:10", "scenario": "Emails like 'a@' or with surrounding spaces pass; 'Pro' is rejected; SSN is unvalidated; duplicate ids are not detected.", "fix": "Strip and normalize fields, tighten email and SSN checks, detect duplicate ids; add parametrized tests."},
    {"severity": "P3", "evidence_level": "code_read_caller_not_seen", "location": "import_customers.py:27", "scenario": "Invalid rows are only reported as per-row logs; there is no PII-free summary, and a 100%-failure night is indistinguishable from success unless the caller checks the return value.", "fix": "Emit a summary report with counts and reasons by row number; exit non-zero above a failure threshold."},
    {"severity": "P0_if_real", "evidence_level": "unverified_owner_decision", "location": "fixtures/customers.csv:2", "scenario": "Described as a copy of real-format customer records with national IDs; values look synthetic (900- SSNs, 555-01xx, example.test), but if any row is real, PII is committed to the repo and must not be sent to unapproved reviewer endpoints.", "fix": "Owner confirms provenance; if real, purge from history and replace with generated data."}
  ]
}
```