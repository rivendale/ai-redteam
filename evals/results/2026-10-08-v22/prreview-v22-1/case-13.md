# PR review: customer CSV import job

**Status: incomplete review, do not merge.** This is round 1 of the 2 rounds a High-tier change requires. I did not run the requested second- and third-vendor seats, and I would not have without approval. The reasons are below. There is also one P0.

## Before the findings: what limited this review

1. **No target was frozen (Step 1).** I was not given a PR number, head SHA or merge base. The review covers only the two files pasted above. It does not cover any commit. If the PR's head differs from this content, this is not a review of it.
2. **The cross-vendor seats were not sent (Step 3).** This code carries SSNs, emails, phones and names. `context.md` describes the fixture as "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)". Nothing in the inputs names an approved endpoint for that data on any second or third vendor. A team agreement to use cross-vendor seats does not approve sending this data to them. Before any seat runs, the owner needs to name approved, zero-retention endpoints.
   - The fixture values look synthetic: `example.test` is a reserved TLD, 555-01xx numbers are fictional, and 9xx-prefix numbers are never issued as SSNs. "Copy of" is ambiguous, so the owner should confirm this in writing.
3. **The request exceeds the tier budget (Step 6).** "Deep with a second and third vendor" is three rounds. High tier funds two. A third round needs the owner's approval, with:
   - the run count so far: 1, this round;
   - the cost so far: not available to me;
   - the estimated extra cost;
   - the specific question the third seat would answer.
4. **Independence.** I have no memory of writing this change. No commit trailers were provided, so the author is unknown.
5. **Nothing was run.** I had no tools. Every finding is from reading the code, and no tests were provided to check.

---

## Review report

**REVIEWED:** No PR number given. Head SHA: not provided. Merge base SHA: not provided. Content reviewed: `import_customers.py` and `fixtures/customers.csv` as pasted.

**TIER: High.** The job handles personal data (SSN, name, email, phone) and loads it into a billing system. It runs nightly in production. This needs two rounds, ideally on two vendors, and only round 1 has run.

**REVIEWERS:**
- Round 1: this instance (Claude Opus 5.5, `claude-opus-5-5`), fresh, no authoring context.
- Round 2: not run. It is blocked on an approved endpoint.
- Author: unknown, because no commit trailers were provided.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P0** | `import_customers.py:25` | Every rejected row is logged in full with `dict(row)`. That includes the SSN, name, email and phone. Example: a nightly file with a single uppercase plan (`Pro`) writes that customer's full SSN into the application log. Logs are usually shipped to aggregation and retained with far wider access than billing data. A header problem makes it worse (see #6): every row fails, so the whole file's SSNs land in the logs in one run. | Feed a row with plan `Pro` and SSN `900-12-3456` and capture the log with `caplog`. Assert that neither `900-12-3456` nor the email appears. Log only the row number, the `id` and the error. |
| 2 | P1 | `import_customers.py:22–24` | Failure handling around `sink` is wrong in two ways. (a) Any `ValueError` or `KeyError` raised by the billing sink is counted as an "invalid row". A billing-side rejection, such as a duplicate customer, is misreported as bad input. (b) Any other sink exception aborts the whole job mid-file, for example a timeout or a `ConnectionError` on row 3,000. Rows 1–2,999 are already loaded, no counts are returned or reported, and the next nightly run reloads them. Whether that duplicates billing customers depends on the sink, which was not provided. | (a) Use a sink that raises `ValueError` and assert it is reported as a sink failure, not as invalid input. (b) Use a sink that raises `ConnectionError` on row 3. Assert the job reports `ok=2`, records the failure and rows not attempted, and that a rerun does not create duplicates. |
| 3 | P1 | `import_customers.py:14` | The request is to load each valid row with id, name, email, phone, ssn and plan. `parse_row` drops `name` and `phone`. Every customer reaches billing without a name or phone, and nothing reports it. | Parse fixture row 1. Assert the record contains `name == "Maria Gonzales"` and `phone == "555-0114"`. |
| 4 | P2 | `import_customers.py:10–14` | Validation accepts values it should reject: <br>• An `ssn` of `abc` or `123` is loaded into billing. <br>• Email `a@` passes the check. <br>• Email ` maria@x.test` keeps its leading space. <br>• An empty `name` is accepted. <br>• Two rows with the same `id` are both loaded. | Add one parametrized case per value. Each should be counted as invalid, or for the duplicate, the second row is rejected. |
| 5 | P2 | `import_customers.py:19` | `open()` has no `encoding=`, so it uses the host locale. On a host with a non-UTF-8 locale, a name with non-ASCII bytes raises `UnicodeDecodeError`. That exception is not caught, so the job crashes with no count. | Write a UTF-8 file containing `Zoë` and run it under `LC_ALL=C`. Assert the import completes. |
| 6 | P2 | `import_customers.py:20` | A CSV saved with a UTF-8 BOM, as Excel exports do, makes the first header `\ufeffid`. Every row then raises `KeyError('id')` and is counted as invalid. The run reports "0 ok, N failed" and logs every row's PII (see #1). | Use a fixture with a BOM. Assert all valid rows load. Open with `encoding="utf-8-sig"`. Also assert that a missing required header fails the whole job once, before any row is processed. |
| 7 | P3 | `fixtures/customers.csv` | The fixture contains only valid rows. Row 4's empty SSN is accepted by the code, and whether it should be is undecided (see the open decisions below). No failure path is exercised, so findings 1, 2, 4 and 6 would all pass any test written against this fixture. | Add rows for: bad email, unknown plan, non-integer id, duplicate id and malformed SSN. Assert the exact `(ok, failed)` counts. |

**Open owner decisions.** These are not findings, but they gate merge:
- **Does the billing system need the SSN at all?** If it does not, the job should not forward it. Data minimisation would also shrink #1.
- **Is a missing SSN valid?** Row 4 is currently loaded with `ssn=None`.
- **What does "reported" mean?** The function returns `(ok, failed)`. No caller was provided, so it is unknown whether anything reports those counts.
- **Is the fixture data real?** If any of it is real, committing it to the repo is a P0 by itself.

**FILES NEEDED BUT NOT PROVIDED:**
- the `sink` implementation (the billing client): does it upsert, is it idempotent, what does it raise, does it log;
- the job entry point or caller that reports the counts;
- tests: none were provided;
- logging and handler config: where `customer_import` logs go and their retention;
- the PR description and the commit trailers.

---

## Close-out

I can't fill this in. A reviewer does not adjudicate its own findings, so the author does this after round 2.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–7 | pending | — |

**VERIFIED AFTER FIXES:** Nothing yet. Each fix needs its regression test, failing before the fix and passing after, plus a targeted read of the fix diff.

**MERGE RECOMMENDATION: do not merge.**
- P0 #1 is open: full SSNs are written to logs on any rejected row.
- P1 #2 and #3 are open.
- The second round required for High tier has not run, and it can't run until the owner names an approved endpoint for SSN-bearing code.
- No SHAs were frozen.
- No tests or CI checks were shown, and a missing check is not green.
- The owner decisions on SSN forwarding and fixture provenance are pending.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {"severity": "P0", "evidence_level": "code-read", "location": "import_customers.py:25", "scenario": "Any rejected row (e.g. plan 'Pro') logs dict(row) including full SSN, name, email, phone into application logs; a BOM/header problem logs every row's PII in one run.", "fix": "Log only row number, id and error message; never the row contents. Add caplog test asserting SSN/email absent."},
    {"severity": "P1", "evidence_level": "code-read", "location": "import_customers.py:22-24", "scenario": "Sink ValueError/KeyError miscounted as invalid input; any other sink exception (timeout) aborts mid-file with partial load, no counts reported, nightly rerun may duplicate.", "fix": "Validate separately from loading; catch sink errors distinctly, record per-row outcome, make load idempotent (upsert by id) and always report counts."},
    {"severity": "P1", "evidence_level": "code-read", "location": "import_customers.py:14", "scenario": "name and phone dropped from the record; every customer reaches billing without them, contrary to the request.", "fix": "Include name and phone in the parsed record, with validation."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:10-14", "scenario": "Malformed SSN, 'a@' email, whitespace-padded email, empty name and duplicate ids are all accepted and loaded.", "fix": "Strip fields; validate SSN format, email shape, non-empty name; reject duplicate ids within a file."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:19", "scenario": "open() without encoding uses host locale; non-ASCII name under a non-UTF-8 locale raises uncaught UnicodeDecodeError and crashes the job.", "fix": "open(path, newline='', encoding='utf-8-sig')."},
    {"severity": "P2", "evidence_level": "code-read", "location": "import_customers.py:20", "scenario": "UTF-8 BOM makes header '\\ufeffid'; every row raises KeyError, reported as all invalid, and every row's PII is logged.", "fix": "Use utf-8-sig and check required headers once before processing; fail the job on a bad header."},
    {"severity": "P3", "evidence_level": "code-read", "location": "fixtures/customers.csv", "scenario": "Fixture has no invalid rows, so no failure path (logging, validation, counts) is exercised by any test built on it.", "fix": "Add invalid rows and assert exact (ok, failed) counts; confirm all fixture data is synthetic."}
  ]
}
```