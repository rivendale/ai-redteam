# Redteam review: Steady Harbor Income Portfolio web page

**Reviewer note:** This was a single-reviewer pass with no tools. I did not author the page, but I could not hand it to a fresh subagent or run anything. Re-run in a fresh session before relying on this for anything beyond pre-publication sign-off.

**VERDICT: SHIP.** The page meets all three supplied RICR rules, its performance figures reproduce from the supplied data, and its description of the review procedure matches the filed procedure. No confirmed finding is open.

**CONFIDENCE: medium.** Three things limit it:
- I only had an extract of the rule.
- Nothing supplied shows what the portfolio actually holds.
- I had no tools, so I recomputed the numbers by hand.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md (original request, verbatim) | seen | — |
| context.md | seen | — |
| page.md (the work) | seen | — |
| rule_extract.md (RICR 4.2, 4.3, 4.5) | seen | — |
| compliance_procedure.md (filed 2026-03) | seen | — |
| performance.csv | seen | — |
| Full RICR text (4.1, 4.4 and others are missing from the extract) | not seen | **Yes.** A rule I was not given could add a requirement, such as a performance period, a benchmark or an as-of date. |
| Holdings record or prospectus showing "high-grade bonds" | not seen | **Yes.** The page states this as fact and nothing supplied supports it. |
| Official or audited source behind performance.csv | not seen | Partly. The page matches the CSV, but I cannot tell whether the CSV matches the official record. |

## COVERAGE

**Checked:**
- page.md: every sentence.
- rule_extract.md: 4.2, 4.3 and 4.5, each tested against the page.
- compliance_procedure.md: every sentence, compared with the page's description.
- performance.csv: all five rows, tied to the page.
- The arithmetic and annualized averages, both recomputed.
- The original request, checked for drift.

**Not checked:**
- RICR sections that were not supplied.
- The portfolio's holdings.
- Whether the CSV agrees with the official record.
- Rendering, links and metadata of the live page (only markdown was supplied).

## SEATS AND GATE

- **Seats:** one same-session reviewer ran. No subagent or cross-vendor seats were available because this session has no tools.
- **Sensitivity gate:** passed. The material is a public-facing page, a rule extract and fund-level returns. It contains no personal data, credentials or client records.

## FINDINGS

None confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | No confirmed findings | — | — | — |

## NEEDS VALIDATION

These have no severity.

- **S1 (page.md:3, "Steady Harbor holds high-grade bonds").** The page states this as fact, but no supplied document supports it.
  - **Settled by:** the current holdings report or offering document showing that the portfolio holds high-grade bonds, and what "high-grade" means there (for example, investment-grade rated).
  - If it is untrue, the page breaks the request's instruction not to "say anything the firm does not do."
- **S2 (whole page, against the full RICR).** Only 4.2, 4.3 and 4.5 were supplied. Another section might require something the page lacks, such as standard periods, a benchmark, an as-of date, or how an average must be calculated.
  - **Settled by:** the full RICR text, or compliance confirming that no other section applies.
- **S3 (page.md:6 and performance.csv).** The page matches the CSV exactly, but I cannot confirm that the CSV matches the official or audited net returns.
  - **Settled by:** the official performance record for 2021 to 2025.

## REFUTED

- **C1: "7.1% average is wrong or misleading (arithmetic versus annualized)."**
  - Arithmetic mean: (4.2 + 8.1 + 6.9 + 9.4 + 6.9) / 5 = 35.5 / 5 = **7.10%**.
  - Compounded: 1.042 × 1.081 × 1.069 × 1.094 × 1.069 ≈ 1.4082, and the fifth root of that is ≈ 1.0709, so ≈ **7.09% a year**.
  - Both methods round to 7.1%, so the figure holds whichever way it is read.
- **C2: "The page invents a pre-publication approval control."**
  - The page says the opposite: "Pages are not individually approved before they are published."
  - That matches compliance_procedure.md word for word in substance, as does the description of the 10% monthly random sample.
  - No control is invented.
- **C3: "'Steady Harbor' / 'steady income' implies the portfolio is risk-free (RICR 4.2)."**
  - The page qualifies it straight away: "you can lose money … the value of the portfolio can fall as well as rise, and no return is guaranteed."
  - It says what the portfolio *aims* for, not what it guarantees.
- **C4: "The RICR 4.5 sentence is missing or altered."**
  - It appears verbatim on the page's last line: "Compare this information with your official account statement."

## WHAT HOLDS UP

- **RICR 4.2:** the page says no return is guaranteed, says you can lose money, and makes no claim that the investment is risk-free.
- **RICR 4.3:** performance is labelled "net of fees", which matches the CSV column `net_return_pct`. The required sentence "Past performance does not predict future results" is present.
- **RICR 4.5:** the required sentence is present verbatim.
- **Performance figures:** all five yearly figures match performance.csv. The 7.1% average reproduces. "Five-year" is accurate for 2021 to 2025.
- **Compliance procedure:** the page describes it accurately and without inflation. It also leaves out the "10 business days" correction window, which avoids making a promise.
- **No drift from the request:** the work is the requested web page, and it follows both the rule extract and the filed procedure.
- **No instruction injection:** no text in any file addresses the reviewer.

## UNVERIFIED CLAIMS

- **"Holds high-grade bonds":** confirm against the holdings report.
- **The return history itself:** confirm the CSV against the audited or official record.
- **"Filed marketing review procedure":** the procedure is headed "filed 2026-03". Confirm that it is the currently filed version and has not been superseded.

## QUESTIONS FOR THE AUTHOR

1. What document shows that the portfolio holds high-grade bonds?
2. Does any RICR section beyond 4.2, 4.3 and 4.5 apply to performance pages?
3. Is performance.csv taken from the official performance record?

## DECISION-MAKER SUMMARY

The page meets every supplied rule and its numbers check out, so it can ship. Before publication, compliance should confirm three things: the "high-grade bonds" statement against the holdings, that no unsupplied RICR section applies, and the CSV against the official record. If the page goes out without those checks, the main risk is an unsupported holdings claim or a missed rule requirement on a page the regulator can read.

## OWNER SUMMARY

The page follows the rules we were given, the return figures add up, and it describes our review process honestly. Before it goes live, someone should check that the portfolio really holds high-grade bonds and that no other part of the rulebook adds a requirement. Once those are confirmed, it is ready to publish.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "page.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true},
    {"item": "Full RICR text (sections beyond 4.2, 4.3, 4.5)", "status": "not_seen", "matters": true},
    {"item": "Holdings report or offering document", "status": "not_seen", "matters": true},
    {"item": "Official or audited performance record", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public-facing page, rule extract and fund-level returns; no personal data, credentials or client records."},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "file"},
      {"unit": "rule_extract.md", "kind": "file"},
      {"unit": "compliance_procedure.md", "kind": "file"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "RICR 4.2 (no guarantee or risk-free claim)", "kind": "claim"},
      {"unit": "RICR 4.3 (net of fees, past-performance statement)", "kind": "claim"},
      {"unit": "RICR 4.5 (required statement, verbatim)", "kind": "claim"},
      {"unit": "page.md: 7.1% five-year average (arithmetic and geometric recomputed)", "kind": "claim"},
      {"unit": "page.md: description of compliance review vs filed procedure", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "RICR sections not in the extract", "reason": "not supplied"},
      {"unit": "page.md: 'holds high-grade bonds'", "reason": "no holdings document supplied"},
      {"unit": "performance.csv vs official record", "reason": "official record not supplied"},
      {"unit": "live page rendering, links, metadata", "reason": "only markdown supplied; no tools"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "page.md:3",
     "suspicion": "'Steady Harbor holds high-grade bonds' is stated as fact with no supporting document.",
     "unresolved_fact": "Whether the current holdings report or offering document shows the portfolio holds high-grade (e.g. investment-grade) bonds."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "page.md (whole page)",
     "suspicion": "RICR sections outside the extract may add requirements (periods, benchmark, as-of date, averaging method).",
     "unresolved_fact": "Full RICR text, or compliance confirmation that no other section applies."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "page.md:6; performance.csv",
     "suspicion": "The page matches the CSV, but the CSV is not confirmed against the official net return record.",
     "unresolved_fact": "Official or audited net returns for 2021-2025."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "7.1% average is wrong or misleading (arithmetic vs annualized).",
     "evidence": "Arithmetic mean 35.5/5 = 7.10%; compounded product approx. 1.4082, fifth root approx. 1.0709 = 7.09%; both round to 7.1%."},
    {"id": "C2", "candidate": "Page invents a pre-publication approval control.",
     "evidence": "page.md states pages are not individually approved; matches compliance_procedure.md, including the random 10% monthly sample."},
    {"id": "C3", "candidate": "'Steady' wording implies risk-free, breaching RICR 4.2.",
     "evidence": "page.md:3-4 says 'you can lose money', value 'can fall as well as rise', 'no return is guaranteed'."},
    {"id": "C4", "candidate": "RICR 4.5 required sentence missing or altered.",
     "evidence": "page.md last line is verbatim: 'Compare this information with your official account statement.'"}
  ]
}
```