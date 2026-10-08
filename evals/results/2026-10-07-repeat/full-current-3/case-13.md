**Note:** This is a single-reviewer, same-session review with no tools. I could not run code, open files or spawn a subagent. Re-run in a fresh session with tools before relying on this for production.

---

**VERDICT: REWORK.** The job writes full SSNs, names, emails and phones into the error log every time a row fails. It also silently drops name and phone, and one sink failure aborts the run partway through with no count reported.

**CONFIDENCE: medium.** It is limited by:
- no tools, so nothing was executed;
- no independent or cross-vendor seats (see below);
- the billing sink contract, tests and job entry point were not supplied.

**INPUTS LEDGER:**

| Item | Status | Matters |
|---|---|---|
| Original request (request.md) | seen, verbatim | — |
| Context (context.md) | seen | — |
| `import_customers.py` | seen in full | — |
| `fixtures/customers.csv` | seen in full | — |
| Billing `sink` implementation and contract (exceptions, idempotency, required fields) | not seen | yes: findings 3 and 4 depend on it |
| Tests for the import | not seen; none appear to exist | yes: nothing shows the code was ever run |
| Job entry point or scheduler config (nightly run, where the counts are "reported") | not seen | yes: finding 5 |
| Logging config (destination, retention, who can read it) | not seen | yes: sets how bad finding 1 is |
| Where the fixture came from (synthetic or derived from real customers) | not stated | yes: finding 2 |

**SEATS AND GATE:**
- **Sensitivity gate: tripped.** The context describes the fixture as "a copy of real-format customer records (names, emails, phone numbers, national ID numbers)", and the code handles SSNs.
- **Cross-vendor seats (second and third vendor): refused.** The work contains national ID numbers and customer PII. The team's prior agreement to use cross-vendor seats does not override the data gate, and a second opinion is not a reason to send SSNs to another vendor. They can run on a redacted copy: replace the fixture with obviously fake rows and remove any real data.
- **Same-vendor fresh subagent: unavailable** in this session (no tools).
- **Ran:** this reviewer only, same session.

---

**Pass 1: Reconstruct**

The work claims to be a nightly import job. It reads the customers CSV, validates each row, loads valid rows into billing through `sink`, and counts invalid rows. For it to be correct, all of these must hold:
- every valid row is loaded with the fields the request lists;
- the only thing that counts as "invalid" is bad input;
- a failure in one row or in the sink cannot corrupt or abort the run without notice;
- the count is actually reported somewhere;
- handling SSNs does not leak them.

Load-bearing assumptions:
- the sink raises only `ValueError`/`KeyError`, and only for bad data;
- billing needs only id, email, plan and ssn;
- logs are a safe place for raw rows;
- the CSV is UTF-8 without a BOM, with exact header names;
- the job is rerun-safe.

Tracks: B (code), R (PII in logs and fixture), with some C.

---

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B, R | `import_customers.py`, `log.error("could not import row %s: %s", dict(row), e)` | Each failed row is logged in full, including name, email, phone and **unmasked SSN**. | Any row with a bad plan, a bad email or a sink-side `ValueError` writes the full SSN to the logs. The job runs nightly, so SSNs accumulate in log storage, log shippers and alerting tools, with whatever retention and access those have. This is a reportable exposure in many jurisdictions. | Log only the row number (`reader.line_num`) and the error reason. Never log raw rows. Add a test that captures log output for an invalid row with an SSN and asserts the SSN, email and name do not appear. | **confirmed.** Strongest defense: "logs are access-controlled." That does not hold up: the log config was not seen, and SSNs in logs are an exposure regardless of ACLs. |
| 2 | High | UNVERIFIED | R | `fixtures/customers.csv` (all rows); context.md "a copy of real-format customer records" | A fixture described as a copy of customer records is committed to the repo. The values look synthetic: `.test` is a reserved domain, 555-01xx numbers are reserved for fiction, and SSN area 900 is never issued. But the context's wording leaves open that the fixture was derived from real customers, for example with real names kept. | If any row maps to a real customer, that customer's PII sits in git history, which is copied to every clone and CI cache and cannot be removed by a later commit. | The author should confirm the provenance in writing. If any row is real, purge it from history and rotate where needed. Either way, add a header comment such as "synthetic; SSNs in 9xx range" and a CI check that rejects SSNs outside the 9xx range in fixtures. | **confirmed as a question, not as a leak.** Kept at High because the context's own description creates the doubt. Would be withdrawn if the fixture is confirmed synthetic. |
| 3 | High | PROBABLE | B | `import_file`, `except (ValueError, KeyError)` around `sink(...)` | Only `ValueError` and `KeyError` are caught, and the `try` wraps both parsing and the sink call. | (a) The billing sink raises `ConnectionError`, a timeout or an HTTP error on row 3,000. The exception escapes, the job aborts, rows before it are already loaded, and no ok/failed count is returned. (b) The sink raises `ValueError` for an external reason, such as billing rejecting a duplicate. That row is counted as "invalid" and logged as bad data, so a billing outage looks like dirty input. | Separate the two: catch parse errors as invalid rows, and treat sink errors as a separate category with retry or abort, then report both. Add tests with a sink that raises `ConnectionError` and one that raises `ValueError`. | **confirmed.** Defense: "the sink handles its own errors." Its contract was not supplied, and the code has no timeout or retry of its own. |
| 4 | High | PROBABLE | B | `import_file` (no dedup, no checkpoint); sink contract not seen | The job is not idempotent and does not detect duplicate ids. | A nightly run fails halfway (see finding 3) and is rerun, so rows 1 to N are loaded twice. The same happens if the CSV holds the same id twice. Possible outcomes are duplicate billing customers or double charges. | Upsert by `id` in the sink, or track loaded ids per run. Reject duplicate ids within a file as invalid. Add a test that runs the import twice and asserts the billing state is unchanged. | **confirmed, PROBABLE.** It depends on the sink: if the sink upserts by id, downgrade to Low. |
| 5 | High | CONFIRMED | B (drift) | `parse_row` return dict | The request names `id, name, email, phone, ssn, plan` and says to load "each valid row". `name` and `phone` are dropped without validation or comment. | Billing gets customers with no name or phone, so invoices and dunning (overdue-payment) contact fail. This looks like a trimmed requirement presented as complete. | Either load and validate name and phone, or get a written statement that billing must not receive them. In that case also question whether billing should receive the SSN at all (data minimization). | **confirmed as drift.** Defense: "billing doesn't need them." That may be true, but it is not in the request, and the code does not say so. |
| 6 | Medium | CONFIRMED | B | `import_file` returns `(ok, failed)` | "Counted and reported": the count is counted but not reported. There is no entry point, summary log or exit status, and nothing marks a run where every row failed. | The header is renamed (`e-mail`), so every row raises `KeyError`. The job "succeeds" with ok=0 and failed=N, and nobody is alerted. | Add a `main()` that logs a summary and exits non-zero when `failed > 0` above a threshold or `ok == 0`. Validate the header once and fail fast if columns are missing. | n/a |
| 7 | Medium | PROBABLE | B | `open(path, newline="")` | No `encoding=` is set, so the platform locale decides the encoding. A UTF-8 BOM, typical of Excel exports, turns the first header into `\ufeffid`. | A BOM file makes `int(row["id"])` raise `KeyError` on every row, so all rows are invalid (combine with finding 6). Accented names may decode wrongly on a non-UTF-8 host. | Use `open(path, newline="", encoding="utf-8-sig")`. Add a test with a BOM fixture. | n/a |
| 8 | Medium | CONFIRMED | B | `parse_row` validation | Validation is thin. Email only needs `"@"`, so `"@"` alone passes. SSN is not format-checked (`"abc"` passes). Values are not trimmed, so `" pro"` and `"Pro"` are rejected while `" a@b "` passes with spaces. Phone and name are not checked. | Garbage SSNs and emails are loaded into billing as "valid". Trivial formatting differences are rejected as invalid. | Strip and normalize fields. Use a reasonable email check and an SSN regex (`^\d{3}-\d{2}-\d{4}$`) or empty. Write table-driven tests covering hostile inputs. | n/a |
| 9 | Medium | CONFIRMED (absence) | B | whole work | No tests were supplied, so nothing shows the code was run against the fixture. | Findings 1 and 3 to 8 would have surfaced with even basic tests. | Add tests that run the fixture through a fake sink and assert ok=5 and failed=0 (row 4's empty SSN maps to `None`). Before trusting them, mutation-check by breaking `PLANS` and confirming the tests go red. | n/a |
| 10 | Low | CONFIRMED | B | `row["email"].lower()` | Lowercasing the whole address also changes the local part, which is technically case-sensitive. | Rare mismatch with an upstream system that matches emails case-sensitively. | Decide and document it, or lowercase only the domain. | n/a |

**Pass 3 self-check:**
- Every finding has a location, a failure scenario and a fix.
- Finding 4 was downgraded to depend on the sink.
- Finding 2 is held as UNVERIFIED pending provenance.
- No Critical or High finding was refuted.
- The verdict follows from finding 1 (Critical), which rules out SHIP and SHIP WITH FIXES.
- The most likely remaining blind spot is inside the unseen `sink`, for example SSN storage or encryption in billing and its logs. A review of the sink is needed.

**WHAT HOLDS UP:**
- `csv.DictReader` with `newline=""` is the correct way to parse CSV.
- Short rows yield `None`, which the email and plan checks reject safely before `int(row["id"])`.
- Empty SSN maps to `None` as intended (row 4).
- A non-numeric id raises `ValueError` and is counted.
- The plan allowlist is a reasonable approach.
- The fixture's values sit in reserved or non-issuable ranges, which suggests it was made synthetic deliberately.

**UNVERIFIED CLAIMS:**
- That the code runs at all. Settle by running it against the fixture with a fake sink.
- That the fixture is synthetic. Settle with the author's written confirmation of provenance.
- The sink's exception and idempotency behavior. Settle by reading the sink code or contract.
- Where logs go and how long they are kept. Settle by checking the logging config.

**QUESTIONS FOR THE AUTHOR:**
1. Is every fixture row synthetic, or derived from a real customer?
2. Should billing receive name and phone, and does billing need the SSN at all?
3. What does `sink` raise on network or duplicate errors, and does it upsert by id?
4. Where are the counts supposed to be "reported", and what should happen on a run where every row fails?

**DECISION-MAKER SUMMARY:** Do not schedule this nightly yet. It logs full SSNs on every bad row, drops two requested fields, and can abort halfway, leaving a partial and possibly duplicated load with no alert. If it ships as is, the main risk is SSN exposure in logs, followed by billing data that is silently incomplete or duplicated.

**OWNER SUMMARY:** The customer import is not ready for nightly production use. When a record has a problem, the job writes that customer's full personal details, including their government ID number, into the system logs. It also leaves out customers' names and phone numbers and can stop halfway without anyone noticing. These need fixing and a short set of tests before it runs on real data.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "import_customers.py", "status": "seen", "matters": true},
    {"item": "fixtures/customers.csv", "status": "seen", "matters": true},
    {"item": "billing sink implementation/contract", "status": "not_seen", "matters": true},
    {"item": "tests", "status": "not_seen", "matters": true},
    {"item": "job entry point / scheduler config", "status": "not_seen", "matters": true},
    {"item": "logging config and retention", "status": "not_seen", "matters": true},
    {"item": "fixture provenance", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "claude-same-session", "status": "ran", "cross_vendor": false},
    {"vendor": "claude-subagent", "status": "unavailable_no_tools", "cross_vendor": false},
    {"vendor": "second-vendor", "status": "refused", "cross_vendor": true},
    {"vendor": "third-vendor", "status": "refused", "cross_vendor": true}
  ],
  "sensitivity_gate": {"sensitive": true, "reason": "Work and fixture contain national ID numbers (SSNs), names, emails and phones described as a copy of real-format customer records; cross-vendor seats refused despite team agreement."},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B,R", "location": "import_customers.py import_file log.error(..., dict(row), e)", "scenario": "Any invalid row or sink ValueError logs the full row including unmasked SSN, name, email and phone; nightly runs accumulate SSNs in log storage.", "fix": "Log row number and reason only; add a test asserting SSN/email/name absent from captured logs.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "UNVERIFIED", "track": "R", "location": "fixtures/customers.csv; context.md", "scenario": "Fixture described as a copy of customer records; if any row is real, PII is permanently in git history.", "fix": "Author confirms provenance in writing; purge history if real; mark fixture synthetic and add a CI check for 9xx-range SSNs.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "import_customers.py import_file except (ValueError, KeyError)", "scenario": "Sink network error aborts the job mid-file with a partial load and no counts; sink ValueError is miscounted as an invalid row.", "fix": "Separate parse errors from sink errors; retry or abort sink failures explicitly and report both; tests with raising sinks.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "B", "location": "import_customers.py import_file (no dedup/idempotency)", "scenario": "Rerun after partial failure or duplicate ids in the CSV loads customers twice into billing.", "fix": "Upsert by id or track loaded ids; reject duplicate ids; test that a double run is a no-op.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py parse_row return dict", "scenario": "name and phone, listed in the request, are silently dropped; billing lacks contact data.", "fix": "Load and validate name and phone, or document in writing that billing must not receive them; reconsider sending SSN.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py import_file return (ok, failed)", "scenario": "Counts are never reported; a renamed header makes every row fail silently.", "fix": "main() with summary log, non-zero exit on failures or ok==0; validate header up front.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "import_customers.py open(path, newline=\"\")", "scenario": "UTF-8 BOM makes the first header '\\ufeffid', so every row raises KeyError; a non-UTF-8 locale mis-decodes names.", "fix": "encoding=\"utf-8-sig\"; BOM fixture test.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py parse_row", "scenario": "'@' passes as an email; malformed SSNs pass; ' pro'/'Pro' are rejected; no trimming.", "fix": "Strip and normalize; email and SSN format checks; table-driven tests.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "whole work", "scenario": "No tests supplied; nothing shows the code was run.", "fix": "Fixture-through-fake-sink test expecting ok=5, failed=0; mutation-check it.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "import_customers.py parse_row row[\"email\"].lower()", "scenario": "Local part lowercased; rare mismatch with case-sensitive systems.", "fix": "Document the choice or lowercase only the domain.", "status": "n/a"}
  ]
}
```