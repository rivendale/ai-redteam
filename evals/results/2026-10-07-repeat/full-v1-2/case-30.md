# Redteam review: privacy notice and November statement template

This is a same-context review: no subagent or tools were available, so I could not open links or check anything outside the four supplied files. The work was not written earlier in this conversation, so the anchoring risk is small.

**VERDICT: SHIP WITH FIXES.** Neither document can be published as is. The privacy notice contradicts the published Subprocessors page, and the statement template leaves out the RICR 4.5 sentence. Both fixes are bounded edits, plus one update to the published page.

**CONFIDENCE IN VERDICT: medium.** Three things limit it:
- No data-protection law or jurisdiction was supplied, so the privacy findings rest on general principles.
- I cannot tell whether these accounts are "managed accounts" under RICR 4.5.
- I cannot see the contract with Corvid Metrics.

## Pass 1: Reconstruct

The work has two drafts dated 2026-11-01:
- **Privacy notice.** It discloses a new analytics flow: account activity, account number and transaction history go to Corvid Metrics. It also says data goes only to processors listed on the Subprocessors page.
- **Statement template.** It shows opening and closing balances, contributions, withdrawals and fees, with a contact line.

For the work to be correct, these must be true:
- The Subprocessors page will list Corvid Metrics by 2026-11-01.
- RICR either does not apply to statements, or the template meets it.
- Corvid Metrics acts only as a processor.
- Sending account numbers and transaction history is justified for "understanding which features customers use."

There is also an unstated assumption: the template's balance lines reconcile without a line for change in market value.

## Findings

| # | Severity | Evidence level | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | privacy_notice.md, "Who receives your data" vs. subprocessors_published.md table | The notice says data goes "only with the processors listed in our Subprocessors page." That page (published 2026-02-01) lists only Hexa Hosting and Pellet Mail. The notice itself names Corvid Metrics as a recipient. The request said to "keep our published pages consistent," but no updated Subprocessors page was produced. | The notice goes live on 2026-11-01 and the page is unchanged. A customer or regulator reads both and finds a false statement in a regulated, customer-facing disclosure. This also means undisclosed sharing with Corvid. | Add a row: "Corvid Metrics, product usage analytics." Publish it on or before the notice's effective date. Check whether contracts or law require advance notice of new subprocessors (today is 2026-10-07, so there is little lead time). |
| 2 | High | CONFIRMED (sentence absent); UNVERIFIED (whether 4.5 applies) | statement_template.md, whole file; rule_extract.md 4.5 | Under RICR 4.5, "every communication about a managed account" must include "Compare this information with your official account statement." The template does not include it. "Contact your adviser" suggests advised or managed accounts. | If a statement counts as a communication about a managed account, every November statement breaches 4.5. | Confirm with compliance whether 4.5 covers the official statement itself. The sentence reads circularly there, so get a written position. If it is unclear, include the sentence. Also check whether the privacy notice falls under 4.5 (probably not). |
| 3 | Medium | PROBABLE | statement_template.md, balance lines | The fields are opening, contributions, withdrawals, fees and closing, with no line for investment gains or losses. For an investment account, closing will usually not equal opening + contributions − withdrawals − fees. | A customer adds up the lines, finds an unexplained difference, and complains or suspects an error. If a "change in value" line is added, it is performance under RICR 4.3: it must be shown net of fees and carry the past-performance statement. | Decide how market movement is shown. If it is shown as performance, show it net of fees and add the 4.3 statement. Test by filling the template with a month that had a market loss and checking that it reconciles. |
| 4 | Medium | PROBABLE | privacy_notice.md, "Analytics (new)" | The stated purpose, "which features customers use," does not need account numbers or transaction history. Feature usage can be measured with pseudonymous identifiers and event data. Sending full identifiers and financial history goes beyond the purpose (data minimisation). | A regulator or customer challenges the flow as disproportionate. If Corvid has a breach, it exposes identifiable financial history that never needed to leave. | Confirm with the analytics feature owner which fields are actually needed. Prefer pseudonymous IDs and no transaction amounts. Update the notice to match the real data flow. |
| 5 | Medium | UNVERIFIED | privacy_notice.md, line 1 ("to run your account") and Analytics paragraph | The opening sentence gives "to run your account" as the purpose of collection. Analytics is a new, separate purpose. No legal basis, opt-out or retention period is given for it. Whether these are mandatory depends on the jurisdiction, which was not supplied. | Under a GDPR-style regime, a purpose or legal basis that is not disclosed makes the notice deficient. | Name the regime that applies. Add the analytics purpose, its legal basis, any opt-out, and retention to the notice. |
| 6 | Low | UNVERIFIED | privacy_notice.md, "which analyzes it for us"; "We do not sell personal data" | Both statements are only true if Corvid acts strictly as a processor. They would be false if Corvid uses the data for its own models or benchmarks. | Corvid's terms allow aggregated or own-purpose use. Then the "processor" framing, and in some regimes the "do not sell" statement, become inaccurate. | Check the Corvid data processing agreement for limits on its own use of the data. |

## What holds up

- **RICR 4.2.** Neither document states or implies a guaranteed return or a risk-free investment.
- **RICR 4.3.** The template, as drafted, shows no performance figure. Fees are listed separately. 4.3 is triggered only if Finding 3 is resolved by adding a performance or change-in-value line.
- **Disclosure of the analytics flow.** The notice is open about the analytics flow and names the vendor. The problem is consistency and proportionality, not concealment.

## Unverified claims

- **Corvid Metrics "analyzes it for us"** (processor-only use). To confirm, read the data processing agreement.
- **"We do not sell personal data."** To confirm, read the Corvid terms against the definition of "sale" in the applicable law.
- **That the accounts are managed accounts within RICR 4.5.** To confirm, check the product classification with compliance.
- **That the full RICR text has no other provisions relevant to statements.** Only an extract (4.2, 4.3, 4.5) was supplied. To confirm, review the full rule.

## Questions for the author

1. Will the Subprocessors page be updated to list Corvid Metrics before 2026-11-01, and who owns that change?
2. Are these managed accounts, and has compliance said whether RICR 4.5 applies to the statement itself?
3. Does the analytics feature actually need account numbers and transaction history?
4. How should market gains and losses appear on the statement?

## Decision-maker summary

Do not publish yet. The privacy notice makes a false claim about the published Subprocessors page, and the statement template probably lacks a sentence that RICR 4.5 requires. Update the Subprocessors page, settle 4.5 applicability (or add the sentence), and confirm the analytics data fields. If you proceed anyway, the risk is a contradiction between published regulated documents and a likely rule breach on every November statement.

```json
{
  "verdict": "SHIP WITH FIXES",
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "location": "privacy_notice.md 'Who receives your data' vs subprocessors_published.md table",
      "scenario": "Notice goes live 2026-11-01 naming Corvid Metrics while claiming data is shared only with listed processors; published page lists only Hexa Hosting and Pellet Mail, so the notice is false and the sharing is undisclosed on the page.",
      "fix": "Add Corvid Metrics (product usage analytics) to the Subprocessors page and publish it on or before the notice's effective date; check any advance-notice obligation for new subprocessors."
    },
    {
      "severity": "High",
      "evidence_level": "CONFIRMED (absence); UNVERIFIED (applicability)",
      "location": "statement_template.md whole file; rule_extract.md 4.5",
      "scenario": "If the statement is a communication about a managed account, every November statement omits the mandatory sentence 'Compare this information with your official account statement.'",
      "fix": "Get a written compliance position on whether 4.5 covers the official statement; if unclear, include the sentence verbatim."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "statement_template.md balance lines",
      "scenario": "No line for market gains or losses, so closing balance does not reconcile with opening + contributions - withdrawals - fees; adding such a line triggers RICR 4.3 (net of fees, past-performance statement).",
      "fix": "Decide how value change is presented; if shown as performance, show it net of fees and add the 4.3 statement; test with a month that had a market loss."
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "location": "privacy_notice.md 'Analytics (new)'",
      "scenario": "Account numbers and transaction history go to a vendor for feature-usage analytics, which does not need them; this exceeds data minimisation and increases breach impact.",
      "fix": "Confirm the needed fields with the feature owner; use pseudonymous IDs and no transaction amounts; align the notice with the real flow."
    },
    {
      "severity": "Medium",
      "evidence_level": "UNVERIFIED",
      "location": "privacy_notice.md line 1 and Analytics paragraph",
      "scenario": "Collection purpose is stated as 'to run your account' only; the new analytics purpose has no stated legal basis, opt-out or retention, which may make the notice deficient under the applicable regime.",
      "fix": "Identify the applicable regime; add the analytics purpose, legal basis, opt-out and retention."
    },
    {
      "severity": "Low",
      "evidence_level": "UNVERIFIED",
      "location": "privacy_notice.md 'which analyzes it for us'; 'We do not sell personal data'",
      "scenario": "If Corvid's terms allow use for its own purposes, the processor framing and possibly the no-sale statement become inaccurate.",
      "fix": "Review the Corvid data processing agreement for limits on its own use of the data."
    }
  ]
}
```