**Redteam review: privacy notice and November statement template**

*Reviewer note: single reviewer, no tools, and no subagent available. The work was not written in this session, but nothing was run or fetched. Every check was made by reading the four supplied files.*

---

**VERDICT: REWORK.** The draft privacy notice says data goes only to listed processors and then names one, Corvid Metrics, that is not on the published list. The statement template also leaves out the sentence RICR 4.5 requires.

**CONFIDENCE: medium.** It is limited by the following:
- No tools were used.
- Only an extract of RICR was supplied.
- The current published privacy notice was not supplied.
- Nothing says whether these accounts are managed accounts.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| privacy_notice.md (draft) | seen | yes |
| statement_template.md (draft) | seen | yes |
| rule_extract.md (RICR 4.2, 4.3, 4.5 only) | seen; **partial** | yes. Exemptions or definitions, such as whether an official statement is itself exempt from 4.5, may sit in clauses not supplied. |
| subprocessors_published.md (2026-02-01) | seen | yes |
| Currently published privacy notice (the version being replaced) | not supplied | yes. A diff against the live version is not possible. |
| Corvid Metrics contract or DPA (role, retention, onward use) | not supplied | yes. "Analyzes it for us" and "we do not sell" cannot be verified. |
| Account type (managed or not) | not supplied | yes. It decides whether 4.5 applies. |
| Other published pages (terms, data-category lists) | not supplied | medium |

**SEATS AND GATE**
- Reviewers: one local reviewer ran. No cross-vendor seats were requested, and none could be run without tools.
- Sensitivity: the drafts contain no real personal data, only templates and placeholders, so the gate passes.

---

**Pass 1: Reconstruct**

The work does two things:
- It adds an analytics disclosure to the privacy notice: account activity, including account number and transaction history, goes to Corvid Metrics.
- It provides a November monthly statement template.

For it to be correct, three things must hold:
1. Every recipient named in the notice must appear on the published subprocessors list, because the notice relies on that list.
2. The statement must meet RICR 4.2, 4.3 and 4.5.
3. Published pages must stay mutually consistent. The request asked for this explicitly.

Load-bearing assumptions:
- The Subprocessors page will be updated. This is unstated, and the page is not in the work.
- The statement is either not a "communication about a managed account" or is exempt from 4.5.
- Corvid acts as a processor, not a controller or seller.

Tracks reviewed: **R** (main), with C and D in places.

---

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | R | privacy_notice.md "Analytics (new)" and "Who receives your data"; subprocessors_published.md table | The notice says "We share personal data only with the processors listed in our Subprocessors page." It also says data goes to Corvid Metrics. The published list (2026-02-01) has only Hexa Hosting and Pellet Mail. The work does not update the list. This is also drift from "keep our published pages consistent." | The notice is published on 2026-11-01 with the list unchanged. From that day the public notice contradicts itself, and the published list is untrue. A customer or regulator reading both pages finds an undisclosed recipient of account numbers and transaction history. | Publish a new, dated version of the Subprocessors page that adds "Corvid Metrics: product usage analytics." Supersede the 2026-02-01 version rather than editing it in place. Publish it no later than the notice. Check that no other published list (data categories, integrations) is now stale. | confirmed. The strongest defence is "the list will be updated separately," but nothing in the work or context shows that, and the request made consistency part of the task. |
| 2 | Critical (High if the accounts are not managed) | absence CONFIRMED; applicability PROBABLE | R | statement_template.md, whole file; rule_extract.md 4.5 | RICR 4.5 says every communication about a managed account must carry: "Compare this information with your official account statement." The template does not contain this sentence. The line "Contact your adviser" suggests advised or managed accounts. | November statements go out without the required sentence, on every customer's statement, which is a breach of 4.5. | Add the exact sentence verbatim. If the firm holds that its own statement is the "official account statement" and is exempt, cite the RICR clause granting the exemption. The extract contains none. | confirmed, subject to account type. The defence that "the statement *is* the official record" is plausible, but it is not supported by any text supplied. Settle it by checking the full RICR definitions or exemptions and the account type. |
| 3 | Medium | PROBABLE | R / D | privacy_notice.md "Analytics (new)" | The stated purpose is "to understand which features customers use." That purpose does not need the account number or full transaction history. Sending direct identifiers and financial history to a third party for feature analytics is beyond what the purpose needs. | A Corvid breach or onward use exposes account numbers together with transaction histories. A regulator or customer asks why feature-usage analytics needs them, and there is no answer. | Send pseudonymised IDs and event-level feature usage, not account numbers or transactions. Then reword the disclosure to match what is actually sent. If full data is truly needed, record why. | not applicable (Medium) |
| 4 | Medium | CONFIRMED | R | privacy_notice.md line 1 versus "Analytics (new)" | Line 1 says data is collected "to run your account." The new section adds a second purpose, analytics, without updating the purpose statement. | The notice understates the purposes of use in its main sentence. Readers who stop at line 1 are misinformed. | Revise line 1 to list both purposes, for example: "to run your account and to understand how our services are used." | not applicable |
| 5 | Medium | CONFIRMED | B / R | statement_template.md, balance lines | The template has no line for investment gain or loss. Opening + contributions − withdrawals − fees will not equal closing for an investment account whose value moves. | Customers see a closing balance that does not reconcile and raise complaints. If a "change in value" line is added later, it becomes performance under 4.3: it must be net of fees and carry the past-performance statement. | Add a "Change in value" line. Check that the template reconciles with sample numbers. If any return figure is shown, show it net of fees and add the 4.3 statement. | not applicable |
| 6 | Low | UNVERIFIED | C | privacy_notice.md "We do not sell personal data" | The Corvid terms were not supplied. If Corvid may use the data for its own purposes, "analyzes it for us" and "do not sell" may not hold. | The claim is inaccurate under the contract's actual terms. | Confirm Corvid's processor role, restrictions on onward use, and retention period from the signed DPA. | not applicable |
| 7 | Low | CONFIRMED | R | both drafts' headings | The drafts say "draft for 2026-11-01" but give no effective date, version identifier or link to the superseded version. | The audit trail of which notice applied when is unclear. | Add a version number and effective date, and archive the prior version. | not applicable |
| 8 | Low | CONFIRMED | R | statement_template.md "support@example.test" | This is a placeholder domain. | It ships unchanged, and customers cannot reach support. | Replace it with the real address, and add a pre-publish check for `example.` strings. | not applicable |

---

**WHAT HOLDS UP**
- **RICR 4.2:** neither document states or implies a guaranteed return or freedom from risk.
- **RICR 4.3:** the statement shows no performance figures, so 4.3 is not triggered as drafted. See finding 5 for the risk if that changes.
- **Plain disclosure:** the privacy notice does name the new recipient and the data sent. The problem is consistency (finding 1), not concealment.
- **Fees line:** the statement shows fees separately.

**UNVERIFIED CLAIMS**
- "Corvid Metrics … analyzes it for us" (processor role). Settle it with the signed DPA.
- "We do not sell personal data." Settle it with the Corvid contract terms.
- Whether RICR 4.5 applies to, or exempts, the statement itself. Settle it with the full RICR text and the account type.

**QUESTIONS FOR THE AUTHOR**
1. Will a revised Subprocessors page that includes Corvid Metrics be published on or before 2026-11-01?
2. Are these managed accounts, and does any RICR clause exempt the official statement from 4.5?
3. Does Corvid actually need account numbers and transaction history, or would pseudonymised usage events do?

**DECISION-MAKER SUMMARY**
Do not publish yet. First update the Subprocessors list to include Corvid Metrics, and add the RICR 4.5 sentence to the statement or document why it does not apply. Publishing as is creates a self-contradicting privacy notice and a likely rule breach on every November statement.

**OWNER SUMMARY**
The new privacy notice names an analytics company that is missing from our public list of companies we share data with, so the two pages contradict each other. The monthly statement also leaves out a sentence the rules appear to require. Both are quick to fix, but they should be fixed before anything is published, and it is worth asking whether the analytics company needs account numbers at all.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "rule_extract.md (RICR extract only)", "status": "partial", "matters": true},
    {"item": "currently published privacy notice", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics contract/DPA", "status": "not_seen", "matters": true},
    {"item": "account type (managed or not)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "templates and drafts only; no real personal data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "R", "location": "privacy_notice.md 'Who receives your data' + 'Analytics (new)'; subprocessors_published.md table", "scenario": "Notice says data goes only to listed processors and names Corvid Metrics, which is absent from the published list; on publication the public pages contradict each other and the list is untrue.", "fix": "Publish a new dated Subprocessors version adding Corvid Metrics no later than the notice; supersede rather than edit in place; check other published lists.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "PROBABLE", "track": "R", "location": "statement_template.md (whole); rule_extract.md 4.5", "scenario": "Template omits the RICR 4.5 sentence 'Compare this information with your official account statement.'; if accounts are managed, every November statement breaches 4.5.", "fix": "Add the sentence verbatim, or cite the RICR clause that exempts the official statement.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "R", "location": "privacy_notice.md 'Analytics (new)'", "scenario": "Account numbers and transaction history sent to a third party for feature-usage analytics exceed the stated purpose; breach or challenge exposes this.", "fix": "Send pseudonymised usage events; align disclosure with what is actually sent.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "R", "location": "privacy_notice.md line 1", "scenario": "Purpose statement says 'to run your account' only; new analytics purpose not reflected.", "fix": "Revise line 1 to include the analytics purpose.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "statement_template.md balance lines", "scenario": "No change-in-value line, so balances do not reconcile for investment accounts; adding one later triggers RICR 4.3.", "fix": "Add change-in-value line; if returns shown, net of fees with the 4.3 past-performance statement.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "UNVERIFIED", "track": "C", "location": "privacy_notice.md 'We do not sell personal data'", "scenario": "Corvid terms unseen; onward use could make the claim inaccurate.", "fix": "Confirm processor role and onward-use limits in the signed DPA.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "R", "location": "both drafts' headings", "scenario": "No version or effective-date record; audit trail of which notice applied is unclear.", "fix": "Add version and effective date; archive prior versions.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "R", "location": "statement_template.md 'support@example.test'", "scenario": "Placeholder address ships; customers cannot reach support.", "fix": "Replace with real address; add pre-publish check for 'example.' strings.", "status": "n/a"}
  ]
}
```