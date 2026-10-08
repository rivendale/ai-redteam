# Redteam Review: Steady Harbor Income Portfolio page

**Review independence:** This is a same-context review with no tools and no subagent. The work was not written in this conversation, so I don't share the author's reasoning, but anchoring risk remains. Because this is regulated, public-facing text, a second reviewer (compliance or a fresh model session) should read it before publication.

## Pass 1: Reconstruct

The page describes Steady Harbor as a high-grade bond portfolio aiming for steady income. It warns that investors can lose money and that no return is guaranteed. It gives a 7.1% five-year average net return with the yearly figures for 2021 to 2025, followed by the past-performance warning. It describes the firm's review practice (a random 10% monthly sample, with no pre-publication approval) and carries the RICR 4.5 sentence.

For the page to be correct, the following must hold:
- (a) the figures match the supplied history and are net of fees;
- (b) the arithmetic is right;
- (c) the description of compliance practice matches the filed procedure;
- (d) every factual claim about the portfolio is something the firm actually does;
- (e) the extract covers the rules that apply.

Assumptions (d) and (e) are the ones the supplied materials cannot fully settle.

## Pass 2: Attack (Track A, plus a figures check)

**Figures and arithmetic.**
- The page's figures match `performance.csv` exactly: 4.2, 8.1, 6.9, 9.4, 6.9.
- The arithmetic mean is 35.5 / 5 = 7.1.
- The compounded (geometric) annual rate also works out to 7.1%: the product of growth factors is ≈ 1.4082, and its fifth root is ≈ 1.0709.
- So "7.1% a year" is correct under either reading of "average". **Holds.**

**RICR 4.2 (no guarantee, no risk-free implication).** The page says "you can lose money", "the value of the portfolio can fall as well as rise" and "no return is guaranteed". "Aims for steady income" is phrased as an aim and sits right next to the risk warning. **Holds.**

**RICR 4.3 (net of fees, past-performance statement).** The page says "net of fees", and the CSV header `net_return_pct` supports that. The sentence "Past performance does not predict future results" appears verbatim. **Holds.**

**RICR 4.5.** The required sentence appears verbatim. If Steady Harbor is not a managed account, the sentence is unnecessary but does no harm. **Holds.**

**Compliance description versus the filed procedure.** The page's wording ("random 10% sample… each month", "not individually approved before they are published") matches `compliance_procedure.md`. It does not overclaim pre-approval, which is the most likely way this kind of page goes wrong. **Holds.**

**"Do not say anything the firm does not do."** "Steady Harbor holds high-grade bonds" is a factual claim about holdings. None of the supplied materials (rule extract, procedure, performance CSV) support it.

**Completeness of the rule set.** The extract skips 4.1 and 4.4, so other applicable requirements may exist that this review cannot check.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Medium | UNVERIFIED | page.md, line 1 of body: "Steady Harbor holds high-grade bonds." | This is the only factual claim about what the portfolio holds, and no supplied source supports it. The request says not to say anything the firm does not do. | The portfolio holds some sub-investment-grade or unrated paper, or its mandate allows it. The page then misstates the product to the public and the regulator, which is the exact failure the request forbids. | Check the claim against the portfolio's mandate or prospectus and its current holdings. If the mandate does not restrict holdings to investment grade, reword the sentence to match the mandate (e.g. "invests mainly in bonds" plus the actual quality constraint). |
| 2 | Low | UNVERIFIED | rule_extract.md: sections 4.1 and 4.4 absent | The page complies with the extract supplied, but the extract is partial. | An omitted section (for example a rule on performance periods, fee disclosure, or the firm's identity and regulatory status) applies, and the page breaches it. | Have compliance confirm that 4.1, 4.4 and any other RICR sections do not apply, or supply them for review. |

## What holds up

- All performance figures match the source data and are labelled as net of fees.
- The 7.1% average is arithmetically correct as either a simple mean or a compounded annual rate.
- All three extracted rules (4.2, 4.3, 4.5) are met, with the required sentences verbatim.
- The compliance paragraph accurately states the weaker real practice (sample review, no pre-approval) rather than implying every page is approved.
- The page has no guarantee language and no risk-free implication.

## Unverified claims

- **"holds high-grade bonds"**: confirm against the mandate and current holdings.
- **"filed marketing review procedure"**: the procedure header says "filed 2026-03". Confirm that it was actually filed with the regulator and is still current.
- **Net-of-fees basis**: this rests on the CSV header alone. Confirm with the performance team that it is net of all fees charged to clients.

## Questions for the author

1. What document supports "high-grade bonds", and does the mandate restrict holdings to investment grade?
2. Are there RICR sections beyond 4.2, 4.3 and 4.5 that apply to this page?

## Decision-maker summary

The page is accurate against the supplied rules and data: the figures, net-of-fees labelling, risk warnings, required sentences and compliance description all check out. Before publishing, confirm the "high-grade bonds" claim against the portfolio mandate, because it is the one statement the supplied material cannot support. If you publish without that check, the remaining risk is a public misstatement of the portfolio's holdings.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "page.md: \"Steady Harbor holds high-grade bonds.\"",
      "scenario": "No supplied material supports the holdings claim; if the portfolio holds or may hold sub-investment-grade or unrated bonds, the page misstates the product publicly, violating the instruction not to say anything the firm does not do.",
      "fix": "Verify against the portfolio mandate/prospectus and current holdings; if not restricted to investment grade, reword to match the mandate."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "rule_extract.md: sections 4.1 and 4.4 absent",
      "scenario": "An omitted RICR section (e.g. on performance periods, fee disclosure, or firm identification) applies and the page breaches it despite satisfying 4.2, 4.3 and 4.5.",
      "fix": "Have compliance confirm no other RICR sections apply, or supply them for review."
    }
  ]
}
```