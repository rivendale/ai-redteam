VERDICT: **REWORK.** The privacy notice says personal data goes only to the processors on the Subprocessors page, but the new processor (Corvid Metrics) is not on that page, so the notice would be untrue the day it is published. The statement template also appears to be missing the sentence RICR 4.5 requires.

CONFIDENCE: **medium.** Three things limit it. I reviewed this myself, with no fresh subagent and no tools; the work was not written in this conversation, so anchoring risk is lower, but this is not a fully independent review. I only had a three-paragraph RICR extract, with no definitions or scope section. I did not have the currently published privacy notice or the Corvid contract.

INPUTS LEDGER:
- **Seen:** request.md, context.md, privacy_notice.md (draft), statement_template.md (draft), rule_extract.md (RICR 4.2, 4.3, 4.5 only), subprocessors_published.md (dated 2026-02-01).
- **Not seen, and it matters:**
  - Full RICR text: whether a statement counts as a "communication", and what a "managed account" is. Finding 2 depends on this.
  - The currently published privacy notice: needed to diff what changed and what was dropped.
  - The Corvid Metrics contract or data processing agreement: needed to know whether Corvid is really only a processor.
  - Whether the accounts are managed accounts.
  - How statements are delivered.
- **Not seen, matters less:** filed regulatory documents and terms, for consistency of fee and custody wording.

SEATS AND GATE:
- One reviewer ran: this session, local Claude.
- The sensitivity gate passed. These are draft templates and policy text with placeholders and no real customer data.
- No cross-vendor seats ran: none were requested and no tools were available.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | R | privacy_notice.md "Who receives your data"; subprocessors_published.md table | The notice says "We share personal data only with the processors listed in our Subprocessors page". It also says account data goes to Corvid Metrics. The published page (2026-02-01) lists only Hexa Hosting and Pellet Mail. No update to the page is part of the work, even though the request says "keep our published pages consistent" (drift). | On 2026-11-01 the notice goes live and data flows to Corvid. The notice's own "only" statement is false. A customer or regulator comparing the two pages finds an undisclosed recipient of account numbers and transaction history. | Add Corvid Metrics (purpose: product usage analytics) to the Subprocessors page. Publish it as a new dated version that supersedes 2026-02-01, not as an edit in place. Publish it no later than the notice and before any data flows. | confirmed. Strongest defence: "the page will be updated at release." Nothing supplied shows that, and the request made it part of this task. |
| 2 | High | PROBABLE | R | statement_template.md (whole file); RICR 4.5 | RICR 4.5 says every communication about a managed account must carry "Compare this information with your official account statement." The template does not have it. "Contact your adviser" suggests the accounts are advised or managed. | The statement goes out without a required statement, which is a rule breach on every statement sent. | Get a compliance decision on whether the statement is a 4.5 "communication" or is itself the official statement. If it is in scope, add the sentence verbatim. Also decide whether the privacy notice is a "communication about a managed account". | confirmed as open. It depends on scope definitions not in the extract. |
| 3 | Medium | CONFIRMED (text) | R | privacy_notice.md line 1 "to run your account" vs Analytics paragraph | The stated purpose of collection ("to run your account") no longer covers what is done with the data. Analytics is a new purpose, but the purpose statement was not updated. | A reader of the purpose statement is misled. Purpose-limitation complaints become easier to make. | Add analytics or product improvement to the purposes. State the basis and any opt-out. | n/a |
| 4 | Medium | PROBABLE | R / D | privacy_notice.md Analytics paragraph | "Which features customers use" does not need account numbers or full transaction history. The notice discloses sending more data than its stated aim needs. | Identifiable financial data sits with a third party for a feature-usage purpose. A breach at Corvid, or a minimisation challenge, exposes it. | Confirm the actual payload. Send pseudonymous IDs and feature events instead. Then make the notice describe what is really sent. | n/a |
| 5 | Medium | PROBABLE | B / R | statement_template.md balance lines | Opening + contributions − withdrawals − fees = closing has no line for market gain or loss. For any invested account the figures will not reconcile. | Customers see balances that do not add up, which leads to complaints and disputes. | Add a "change in value" line. If it is shown as a return, RICR 4.3 applies: show it net of fees and include the past-performance sentence. | n/a |
| 6 | Low | PROBABLE | R | statement_template.md `{account_number}` | The full account number is printed. If statements go out by email through Pellet Mail, this exposes it in transit and in inboxes. | A misdirected or compromised email reveals a full account number. | Mask all but the last 4 digits unless a rule requires the full number. | n/a |

WHAT HOLDS UP:
- **RICR 4.2:** neither document states or implies a guaranteed return or a risk-free investment.
- **RICR 4.3:** the template shows balances and flows but no performance figure, so 4.3 is not triggered as drafted. This changes if finding 5's fix adds a return.
- **Analytics disclosure:** the notice names the new recipient and the data categories plainly. That is the right approach; only the cross-page consistency fails.
- **Template contents:** the template carries fees explicitly and gives a contact route.

UNVERIFIED CLAIMS:
- "We do not sell personal data." Settle this with the Corvid contract: confirm Corvid has no right to use the data for its own purposes.
- "Corvid Metrics, which analyzes it for us" (that Corvid is only a processor). Settle with the data processing agreement.
- That data does not flow to Corvid before 2026-11-01. Settle with the release plan or the integration's go-live date.
- Corvid's data location and any international transfer. The notice is silent on this; check the contract.

QUESTIONS FOR THE AUTHOR:
1. Is the Subprocessors page being re-issued with Corvid, and on what date?
2. Are these managed accounts, and does compliance treat the monthly statement as a 4.5 "communication"?
3. Does the analytics feed really need account numbers and transaction history?
4. Will the statement ever show gains or returns?

DECISION-MAKER SUMMARY: Do not publish yet. The privacy notice contradicts the published processor list, and the statement may lack a rule-required sentence. Re-issue the processor list with Corvid, get a compliance ruling on RICR 4.5 scope, and fix the purpose statement. Publishing as is puts out a false statement to customers and the regulator about who receives their financial data.

OWNER SUMMARY: The new privacy text says we only share data with the companies on our public list, but the new analytics company is not on that list yet, so the two pages contradict each other. The monthly statement may also be missing a sentence the regulator requires. Both need fixing before anything goes live, and the analytics feed may be sending more customer detail than it needs.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full RICR text (scope/definitions)", "status": "not_seen", "matters": true},
    {"item": "current published privacy notice", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics contract/DPA", "status": "not_seen", "matters": true},
    {"item": "statement delivery channel", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "draft templates and policy text with placeholders only"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "privacy_notice.md 'Who receives your data'; subprocessors_published.md table",
     "scenario": "Notice says data goes only to listed processors; Corvid Metrics receives account number and transaction history but is absent from the 2026-02-01 list, so the notice is false on publication",
     "fix": "Publish a new dated Subprocessors version adding Corvid Metrics (analytics), superseding 2026-02-01, no later than the notice and before data flows", "status": "confirmed"},
    {"severity": "High", "evidence_level": "PROBABLE", "track": "R", "location": "statement_template.md; RICR 4.5",
     "scenario": "If the statement is a communication about a managed account, every statement sent omits the required sentence",
     "fix": "Obtain compliance ruling on 4.5 scope; if in scope add 'Compare this information with your official account statement.' verbatim", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "R", "location": "privacy_notice.md line 1",
     "scenario": "Stated collection purpose 'to run your account' omits the new analytics purpose", "fix": "Add analytics purpose, basis and any opt-out", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "R", "location": "privacy_notice.md Analytics paragraph",
     "scenario": "Account numbers and full transaction history sent to third party for feature-usage analytics; exposure exceeds need",
     "fix": "Minimise to pseudonymous IDs and feature events; align notice with actual payload", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "statement_template.md balance lines",
     "scenario": "No gain/loss line, so invested accounts' figures do not reconcile",
     "fix": "Add change-in-value line; if shown as return, apply RICR 4.3 (net of fees, past-performance sentence)", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "R", "location": "statement_template.md {account_number}",
     "scenario": "Full account number exposed in emailed statements", "fix": "Mask to last 4 digits unless a rule requires the full number", "status": "n/a"}
  ]
}
```