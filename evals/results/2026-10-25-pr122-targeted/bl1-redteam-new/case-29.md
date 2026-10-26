VERDICT: **SHIP.** The page meets RICR 4.2, 4.3 and 4.5 as extracted, its performance figures match the supplied data, and it describes the filed review procedure accurately without inventing a control.

CONFIDENCE: **medium.**
- I had no tools, and this is a single-reviewer pass with no subagent.
- I could not scan for invisible or look-alike characters.
- The holdings claim and the account type are not supported by any supplied input.
- Only an extract of RICR was supplied, not the full rule.

INPUTS LEDGER:
- **Seen:** request.md, context.md, page.md, compliance_procedure.md, performance.csv, rule_extract.md.
- **Not seen:**
  - The full RICR text. This matters a little: other paragraphs could impose requirements the extract omits.
  - Portfolio holdings or the investment mandate. This matters for the "high-grade bonds" claim.
  - The account or product structure. This matters for whether RICR 4.5 applies, but the page carries the sentence anyway, so the gap is harmless.
  - The fee methodology behind "net". The CSV column is labelled `net_return_pct`, which is accepted as the record.

COVERAGE:
- **Scope:** the whole page.
- **Checked:** every sentence of page.md; every row of performance.csv; RICR 4.2, 4.3 and 4.5; every clause of compliance_procedure.md; request.md; context.md.
- **Not checked:**
  - RICR paragraphs outside the extract (not_supplied).
  - Holdings (not_supplied).
  - Invisible-character scan (no_tools).

SEATS AND GATE:
- **Sensitivity gate:** passed. There is no personal data, no client records and no credentials.
- **Seats:** no subagent or cross-vendor seat was available, so this is a single-reviewer pass without tools. The work was not authored in this conversation, so there is no anchoring on my own output. A re-run with tools would close the invisible-character gap.

CLAIMS TO EVIDENCE:

| Claim | Source | Status |
|---|---|---|
| C1 "holds high-grade bonds" (page ¶1) | none supplied | **UNVERIFIED** → S1 |
| C2 "aims for steady income… can lose money… no return is guaranteed" (¶1) | RICR 4.2 | Verified: the wording disclaims a guarantee. "Aims" is an objective, not a promise. |
| C3 "five-year average 7.1% a year, net of fees" (¶2) | performance.csv, 2021–2025, net, five annual returns | Derived and recomputed. Arithmetic mean: 35.5/5 = 7.10%. Geometric (compound) mean: 1.042×1.081×1.069×1.094×1.069 = 1.4082; its fifth root is 1.0709, about 7.09%, which rounds to 7.1%. The figure holds under either method. |
| C4 yearly figures 4.2, 8.1, 6.9, 9.4, 6.9 (¶2) | performance.csv rows 2021–2025 | Verified: all five match exactly. |
| C5 "Past performance does not predict future results." (¶2) | RICR 4.3 | Verified: verbatim match with the rule's required statement. |
| C6 random 10% monthly sample; pages not individually pre-approved (¶3) | compliance_procedure.md lines 1–2 | Verified. The page describes the practice as the firm's own filed procedure, not as a legal requirement. |
| C7 "Compare this information with your official account statement." (¶4) | RICR 4.5 | Verified: verbatim match. |

FINDINGS: none confirmed.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | No confirmed findings | — | — | — |

NEEDS VALIDATION:
- **S1** (page.md ¶1, "Steady Harbor holds high-grade bonds"): the request forbids saying anything the firm does not do, and no holdings or mandate document was supplied.
  - Settled by: the current holdings report or investment mandate showing the portfolio is invested in high-grade (investment-grade) bonds.
- **S2** (page.md ¶4 and RICR 4.5): it is unknown whether the portfolio is a "managed account" under RICR. Either way the sentence is present and verbatim, so this cannot cause non-compliance.
  - Settled by: the product's account classification.

REFUTED:
- **"Steady income" or "Steady Harbor" implies a guaranteed return (RICR 4.2).** Refuted. The page says it "aims for" income and immediately states "you can lose money… no return is guaranteed."
- **The "average" is ambiguous and may overstate returns.** Refuted. The arithmetic and compound means both round to 7.1%, as recomputed under C3.
- **The page should state that each page is pre-approved, or the firm needs a pre-approval gate.** Refuted.
  - The filed procedure says "Posts and pages are not individually approved before they are published", and the page says exactly that.
  - None of RICR 4.2, 4.3 or 4.5 requires pre-approval.
  - Adding such a claim would describe a control that does not operate.
- **The compliance description presents a practice as a legal requirement.** Refuted. The page attributes it to "our filed marketing review procedure".

WHAT HOLDS UP:
- All three extracted rules are met. The required sentences are verbatim, and performance is shown net of fees.
- Every performance figure reproduces from the supplied data.
- The risk wording is clear.
- The control description matches the filed procedure word for word in substance and claims nothing extra.

UNVERIFIED CLAIMS:
- "High-grade bonds" (S1). Confirm against holdings or the mandate.
- That the CSV returns are genuinely net of all fees. The column label is the only evidence; confirm against the performance calculation methodology.
- The absence of hidden characters. Confirm with a Unicode scan for zero-width, bidirectional and tag characters before publishing.

QUESTIONS FOR THE AUTHOR:
1. Which document shows the portfolio holds high-grade bonds?
2. Does the full RICR contain other paragraphs (for example on the period length, benchmarks or fee disclosure) that apply to this page?

DECISION-MAKER SUMMARY: The page complies with the supplied rule extract and accurately describes the firm's filed review procedure, so it can be published. Before publishing, confirm the "high-grade bonds" description against the holdings, because that is the one statement no supplied document supports. If the portfolio holds lower-grade bonds, the page would describe something the firm does not do.

OWNER SUMMARY: The page reads well and follows the rules we were given: it shows returns after fees, warns that money can be lost, and includes the required statements. The return figures check out against our records. Before it goes live, someone should confirm that the portfolio really holds high-grade bonds, since nothing we were given shows that.

The findings list below holds only the two needs_validation items. Neither carries a severity, because the skill forbids one on unresolved items; both have `"severity": null`.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "portfolio holdings / mandate", "status": "not_seen", "matters": true},
    {"item": "account classification", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-session-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "No personal, client or credential data."},
  "coverage": {
    "checked": [
      {"unit": "page.md", "kind": "document"},
      {"unit": "compliance_procedure.md", "kind": "document"},
      {"unit": "performance.csv", "kind": "data"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "C3 five-year average 7.1% net", "kind": "claim"},
      {"unit": "C5/C7 required statements verbatim", "kind": "claim"},
      {"unit": "C6 review procedure description", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "RICR beyond extract", "reason": "not_supplied"},
      {"unit": "holdings supporting 'high-grade bonds'", "reason": "not_supplied"},
      {"unit": "invisible-character scan of page.md", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "S1", "status": "needs_validation", "severity": null, "evidence_level": "UNVERIFIED", "track": "R",
     "location": "page.md ¶1 'Steady Harbor holds high-grade bonds'",
     "scenario": "If holdings are not high-grade, the page states something the firm does not do, contrary to the request.",
     "fix": "Confirm against the current holdings report or mandate before publishing.",
     "suspicion": "Holdings claim has no supplied support.",
     "unresolved_fact": "Whether current holdings/mandate are high-grade (investment-grade) bonds."},
    {"id": "S2", "status": "needs_validation", "severity": null, "evidence_level": "UNVERIFIED", "track": "R",
     "location": "page.md ¶4; rule_extract.md 4.5",
     "scenario": "None: the RICR 4.5 sentence is present verbatim whether or not the rule applies.",
     "fix": "None needed; record the account classification for the file.",
     "suspicion": "Applicability of RICR 4.5 unknown.",
     "unresolved_fact": "Whether the portfolio is a managed account under RICR."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "'Steady income' implies a guarantee (RICR 4.2).", "evidence": "Page says 'aims for' and 'you can lose money... no return is guaranteed'."},
    {"id": "R2", "candidate": "7.1% average misstated.", "evidence": "Arithmetic mean 35.5/5=7.10%; geometric 1.4082^(1/5)-1=7.09%; both round to 7.1%."},
    {"id": "R3", "candidate": "Page should claim pre-approval.", "evidence": "Filed procedure: 'Posts and pages are not individually approved before they are published'; RICR 4.2/4.3/4.5 impose no pre-approval."}
  ]
}
```