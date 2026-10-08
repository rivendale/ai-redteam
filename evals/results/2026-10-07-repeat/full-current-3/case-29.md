# Redteam review: Steady Harbor Income Portfolio web page

**VERDICT: SHIP.** The page meets every RICR paragraph supplied (4.2, 4.3, 4.5), its figures reproduce from the return history, and it describes the firm's filed review procedure accurately without inventing a control.

**CONFIDENCE: medium.** I had no tools and no subagent, so this is a single reviewer working from the supplied text. I recomputed all the numbers by hand. Confidence is limited because the rule is an extract (4.1 and 4.4 are missing) and nothing supplied backs the holdings claim or the fee basis.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md, context.md | seen | baseline |
| page.md (work) | seen | n/a |
| rule_extract.md (4.2, 4.3, 4.5) | seen | n/a |
| compliance_procedure.md (filed 2026-03) | seen | n/a |
| performance.csv | seen | n/a |
| Full RICR text, including 4.1, 4.4 and any later paragraphs | **not seen** | **Yes.** An omitted paragraph could set extra requirements, such as standard periods or benchmark rules. |
| Portfolio holdings or mandate document | not seen | Yes, for the "high-grade bonds" claim |
| Fee schedule and how net returns were calculated | not seen | Partly. The CSV is labelled net, but I could not check how. |
| Whether Steady Harbor is a "managed account" under 4.5 | not seen | No. The sentence is present either way. |

**SEATS AND GATE:** One local reviewer ran. The sensitivity gate passed: the material is public-facing marketing text and aggregate returns, with no personal data. I did not ask for cross-vendor seats, and no subagent tool was available.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Low | PROBABLE | R | page.md title and line 1: "Steady Harbor", "aims for steady income" | The words "steady" and "harbor" lean toward safety. | A regulator reading under 4.2 sees an implied low-risk or safe product. This is unlikely to hold up, because the next sentence says "you can lose money … no return is guaranteed". | Optional: change "steady income" to "regular income". The product name is a firm-level decision. | n/a (Low) |

There are no Critical, High or Medium findings. I checked for them and did not invent any.

## What holds up

- **RICR 4.2.** The page states that you can lose money, that the value can fall, and that no return is guaranteed. It contains no "safe", "risk-free" or guarantee language.
- **RICR 4.3.** Performance is shown "net of fees". The required sentence appears verbatim: "Past performance does not predict future results."
- **RICR 4.5.** The required sentence appears verbatim: "Compare this information with your official account statement."
- **Numbers (confirmed by recomputation).**
  - The yearly figures on the page match performance.csv exactly.
  - Arithmetic mean: 4.2 + 8.1 + 6.9 + 9.4 + 6.9 = 35.5, and 35.5 / 5 = 7.1%.
  - Compound annual rate: the product of the yearly growth factors is about 1.4082, and its fifth root is about 1.0709, or 7.1%.
  - So "7.1% a year" is correct whether "average" means the arithmetic mean or the annualized rate.
- **Practice vs requirement, and invented controls.** The page describes the filed procedure faithfully: a monthly random 10% sample, and no individual pre-publication approval. It openly says pages are not individually approved. It does not dress the sample up as an approval step and does not say any rule requires it. This meets "do not say anything the firm does not do."
- **Freshness.** The calendar years 2021 to 2025 are the latest complete years as of 2026-10-07.

## Unverified claims

1. **"Steady Harbor holds high-grade bonds."** No holdings or mandate document was supplied. To settle it, check the current holdings report or the portfolio mandate.
2. **That the returns are net of all fees.** The CSV is only labelled net. To settle it, check the return calculation against the fee schedule.
3. **That no other RICR paragraph applies.** To settle it, read the full rule, especially 4.1, 4.4 and any paragraphs on time periods or benchmarks.

## Questions for the author

1. Does the full RICR include requirements beyond 4.2, 4.3 and 4.5, such as standard 1-, 5- and 10-year periods or showing returns since inception?
2. Is "high-grade" defined in the portfolio's mandate, for example as investment-grade only?

## Decision-maker summary

The page meets every rule paragraph supplied, its numbers are correct, and its description of the firm's review procedure matches the filed procedure. Before publishing, confirm the bond-quality claim and check the full rule text for paragraphs not in the extract. If you skip those checks, the remaining risk is an unseen rule requirement or an unsupported holdings statement.

## Owner summary

The web page follows the rules we were given, its return figures add up correctly, and it describes the firm's review process honestly. Before it goes live, someone should confirm that the portfolio really holds only high-grade bonds and check the full rulebook for any further requirements. Otherwise it is ready to publish.

```json
{
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "rule_extract.md (4.2, 4.3, 4.5)", "status": "seen", "matters": true},
    {"item": "full RICR text (4.1, 4.4, others)", "status": "not_seen", "matters": true},
    {"item": "holdings/mandate document", "status": "not_seen", "matters": true},
    {"item": "fee schedule / net return methodology", "status": "not_seen", "matters": true},
    {"item": "compliance_procedure.md", "status": "seen", "matters": true},
    {"item": "performance.csv", "status": "seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public marketing text and aggregate returns only"},
  "findings": [
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "R",
     "location": "page.md title and line 1: 'Steady Harbor', 'aims for steady income'",
     "scenario": "A reader or regulator takes 'steady' as implying low risk under RICR 4.2; largely offset by the explicit loss and no-guarantee statement that follows.",
     "fix": "Optionally say 'regular income' instead of 'steady income'.",
     "status": "n/a"}
  ]
}
```