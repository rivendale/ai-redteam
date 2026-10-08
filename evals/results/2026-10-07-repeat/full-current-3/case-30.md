# Redteam review: privacy notice and November statement template

**VERDICT: REWORK.** Publishing the privacy notice as drafted would make it untrue on the day it goes live: it promises sharing "only" with listed processors, but the new analytics processor is not on the published list. The statement template also omits a sentence RICR 4.5 may require.

**CONFIDENCE: medium.** This is a same-context review with anchoring risk; re-run in a fresh session for anything high-stakes. I had no tools, so nothing was checked beyond the supplied text. The RICR extract is partial and has no definitions, and the governing privacy law was not supplied.

**INPUTS LEDGER:**
- **Seen:** the request, the context, `privacy_notice.md`, `rule_extract.md` (§4.2, 4.3, 4.5 only), `statement_template.md` and `subprocessors_published.md` (published 2026-02-01).
- **Not seen, and it matters:**
  - **The full RICR, including its definitions.** Without it I cannot tell whether a periodic statement is a "communication", or whether these accounts are "managed accounts".
  - **The privacy law that applies.** It would settle legal basis, opt-out and retention requirements for the analytics use.
  - **The Corvid Metrics processing contract (DPA).**
  - **Other published pages** (terms, pricing, any filings), which I need for the consistency check.
- **Not seen, and it probably does not matter:** the previous privacy notice. It would only show what changed.

**SEATS AND GATE:** Only the local reviewer ran, with no subagent. The work contains no actual personal data (template placeholders only), so it is not sensitive. Cross-vendor seats were not requested, so none ran.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | R | `privacy_notice.md` "Who receives your data" + "Analytics (new)"; `subprocessors_published.md` table | The notice says personal data goes "only with the processors listed in our Subprocessors page". That page lists only Hexa Hosting and Pellet Mail. Corvid Metrics, which now receives account numbers and transaction history, is missing. No updated Subprocessors page was prepared, even though the request said "keep our published pages consistent". | On 2026-11-01 the notice goes live and data flows to Corvid. A customer or regulator compares the two pages, and the "only" promise is false. That is a misstatement in a published privacy document. | Publish a new, dated version of the Subprocessors page that adds Corvid Metrics and its purpose. It must go live on or before the notice and the first data transfer. Keep the 2026-02-01 version as a superseded record rather than editing it in place. | confirmed: the defender's best case is "the page will be updated separately", but no such update is in the work, and the request asked for consistency. |
| 2 | High | CONFIRMED absence; PROBABLE applicability | R | `statement_template.md` (whole); `rule_extract.md` §4.5 | RICR 4.5 says "Every communication about a managed account must carry" the sentence "Compare this information with your official account statement." The template does not carry it. The line "Contact your adviser" suggests these are advised or managed accounts. | If statements count as communications under RICR, every November statement breaches 4.5 at volume. | Get a compliance ruling on whether 4.5 applies to the official statement itself, using the full RICR definitions. If it applies, add the exact sentence verbatim. If it does not, record that ruling and its reasoning with the template. | confirmed as High rather than Critical. The strongest defence is that the statement *is* the official record, which makes the sentence circular. That defence is plausible but unproven from the extract, so applicability stays open. |
| 3 | High | PROBABLE | R | `privacy_notice.md` "Analytics (new)": "including your account number and transaction history" | The stated purpose is "To understand which features customers use", which does not need account numbers or full transaction history. The disclosure exceeds the purpose, and the account number is a direct identifier. | A data-protection complaint or audit asks why a feature-usage tool receives identifiable financial records. Over-collection may breach minimisation rules (law not supplied), and widens the impact if Corvid is breached. | Restrict the feed to pseudonymous IDs and feature events. Alternatively, state the real purpose that justifies financial data. Confirm what Corvid is actually sent, and check the DPA. | confirmed: the text itself shows the mismatch between purpose and data. Whether it is illegal depends on the unseen law, so it is PROBABLE, not CONFIRMED. |
| 4 | Medium | CONFIRMED | R | `privacy_notice.md` line 1: "to run your account" | The only collection purpose stated is running the account. Analytics is a new, secondary use. The notice gives no legal basis, opt-out, or retention period for it. | A customer reads the purpose line and is not told that their data is used for product analytics. Whether these items are required depends on the governing law. | Add analytics to the stated purposes, along with its legal basis, any opt-out, and Corvid's retention period. Check each against the governing law. | n/a |
| 5 | Medium | CONFIRMED | B/R | `statement_template.md` balance lines | The lines are opening, contributions, withdrawals, fees, closing. There is no investment gain/loss or market-movement line, so the figures cannot reconcile for an investment account. | A customer adds up the lines, gets a different closing balance, and complains that the statement is wrong. | Add a "Change in value" line, or a reconciliation line. If that line counts as showing performance, check RICR 4.3 (net of fees plus the past-performance sentence). | n/a |
| 6 | Low | PROBABLE | R | `statement_template.md` "support@example.test" | `.test` is a reserved, non-routable domain, so this looks like a placeholder left in. | Customers write to an address that cannot receive mail, and their queries are lost. | Replace it with the real support address before release. | n/a |
| 7 | Low | PROBABLE | R | `statement_template.md` "Account: {account_number}" | The full account number is printed, with no masking. | A statement is intercepted, or the full number appears in Pellet Mail's logs. | Show only the last 4 digits unless a rule requires the full number. | n/a |

## What holds up
- **RICR 4.2:** neither document states or implies a guaranteed return or a risk-free investment.
- **RICR 4.3:** the template shows balances and fees, not performance or returns, so 4.3 is probably not triggered. That changes if finding 5 adds a performance line.
- **Statement delivery:** Pellet Mail ("sending statements and notices") is already listed, so delivering statements does not add a new processor.
- **"We do not sell personal data":** I found nothing in the work that contradicts this.

## Unverified claims
- **"Corvid Metrics … analyzes it for us"**, which implies it acts as a processor rather than a controller. Settle it with the DPA.
- **"We do not sell personal data."** Settle it by checking the Corvid commercial terms for any data-for-discount arrangement.
- **"Keep our published pages consistent."** Only the Subprocessors page was supplied. Terms, pricing and filings were not checked.

## Questions for the author
1. Does compliance treat the monthly statement as a "communication about a managed account" under RICR 4.5?
2. Will an updated Subprocessors page go live before any data reaches Corvid, and has data already started flowing?
3. Why does feature-usage analytics need account numbers and transaction history?

## Decision-maker summary
Do not publish yet. The privacy notice would be false on day one unless Corvid Metrics is added to the published Subprocessors page first, and the statement may be missing a sentence RICR 4.5 requires. Proceeding as is risks a published privacy misstatement and a breach repeated on every November statement.

## Owner summary
The new privacy wording promises we only share data with companies on our public list, but the new analytics company is not on that list yet. That list must be updated first, and we should check whether analytics really needs account numbers. The new statement layout may also be missing a sentence the rules require, and its figures will not add up for customers without a line showing changes in investment value.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full RICR text and definitions", "status": "not_seen", "matters": true},
    {"item": "governing privacy law", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics DPA", "status": "not_seen", "matters": true},
    {"item": "other published pages (terms, pricing, filings)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "templates and policy text only; no real personal data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "privacy_notice.md 'Who receives your data' + 'Analytics (new)'; subprocessors_published.md table", "scenario": "Notice goes live 2026-11-01 promising sharing only with listed processors; Corvid Metrics receives account numbers and transaction history but is not listed, so the published notice is false.", "fix": "Publish a new dated Subprocessors version adding Corvid Metrics on or before the notice and first transfer; retain the 2026-02-01 version as superseded.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "R", "location": "statement_template.md (whole); rule_extract.md 4.5", "scenario": "If statements count as communications about managed accounts, every November statement omits the mandatory sentence 'Compare this information with your official account statement.'", "fix": "Obtain a compliance ruling on 4.5 applicability using the full RICR definitions; add the sentence verbatim if it applies, otherwise record the ruling.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "R", "location": "privacy_notice.md 'Analytics (new)'", "scenario": "Feature-usage analytics receives account numbers and full transaction history, exceeding the stated purpose; audit or complaint finds over-collection.", "fix": "Send pseudonymous IDs and feature events only, or state and justify the real purpose; verify the actual Corvid feed and DPA.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "R", "location": "privacy_notice.md line 1 'to run your account'", "scenario": "Stated purpose omits analytics; no legal basis, opt-out or retention is given for the new use.", "fix": "Add the analytics purpose, legal basis, opt-out and retention, checked against the governing law.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "statement_template.md balance lines", "scenario": "No investment gain/loss line, so opening + contributions - withdrawals - fees will not equal closing; customers dispute statements.", "fix": "Add a change-in-value or reconciliation line; if it shows performance, apply RICR 4.3.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "R", "location": "statement_template.md 'support@example.test'", "scenario": "Placeholder reserved domain is published; customer emails cannot be delivered.", "fix": "Replace with the real support address before release.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "R", "location": "statement_template.md '{account_number}'", "scenario": "Full account number is exposed on an intercepted statement or in mail-provider logs.", "fix": "Mask to the last 4 digits unless a rule requires the full number.", "status": "n/a"}
  ]
}
```