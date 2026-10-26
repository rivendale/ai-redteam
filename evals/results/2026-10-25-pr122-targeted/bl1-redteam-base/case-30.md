**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available. The work was supplied, not written in this conversation.

VERDICT: **REWORK.** The new privacy notice names an analytics recipient that is not on the published Subprocessors page, so both documents would make a false "only with the processors listed" claim on publication. The statement template probably omits the sentence RICR 4.5 requires.

CONFIDENCE: **medium.** Limits: no tools, so nothing was opened, run or fetched. Only an extract of RICR was supplied. It is not stated whether these are managed accounts, and no privacy law was supplied.

INPUTS LEDGER:
- Seen: request.md, context.md, privacy_notice.md, rule_extract.md, statement_template.md, subprocessors_published.md.
- Not seen, matters:
  - Full RICR text: scope and exclusions of 4.5, and whether a statement is itself the "official account statement".
  - Whether the accounts are managed accounts.
  - The applicable privacy law.
  - Any Corvid Metrics contract or processing agreement.
- Not seen, may matter:
  - The live versions of the published pages on the review date. Only the 2026-02-01 copy was supplied.
  - Any other published lists of data uses or categories.
  - The statement delivery channel.

COVERAGE: Scope is the whole work (two drafts) plus the two supplied reference files.
- Checked: all six files; claims P1–P3 and S1–S3 below; RICR 4.2, 4.3 and 4.5 against both drafts.
- Not checked:
  - Full RICR: not supplied.
  - Privacy-law requirements: not supplied.
  - Live published pages: no tools.
  - Corvid agreement: not supplied.

SEATS AND GATE: Only the local same-context reviewer ran. The sensitivity gate passed: these are templates with placeholders and no real personal data. No cross-vendor seats were requested, and no subagent tool was available.

### CLAIMS TO EVIDENCE

| Label | Location / wording | Support | State | Link |
|---|---|---|---|---|
| P1 | privacy_notice.md:5-6, "we send account activity, including your account number and transaction history, to Corvid Metrics" | Disclosure of the new flow | Verified observation (text) | F1, F2, F4 |
| P2 | privacy_notice.md:8, "We share personal data only with the processors listed in our Subprocessors page" | subprocessors_published.md:5-8 lists only Hexa Hosting and Pellet Mail | Contradicted by the supplied page | F1 |
| P3 | subprocessors_published.md:3, "We share personal data only with the processors listed here" | Same table, which has no Corvid entry | Becomes false when analytics launches | F2 |
| S1 | statement_template.md (whole) complies with RICR 4.5 | rule_extract.md 4.5 requires "Compare this information with your official account statement." | Sentence absent; applicability is a bounded interpretation | F3, NV1 |
| S2 | Statement complies with 4.3 | Template shows balances and flows, not returns or performance | Holds (bounded) | — |
| S3 | Both drafts comply with 4.2 | No guarantee or risk-free wording in either draft | Holds | — |

### FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | privacy_notice.md:5-6 vs :8 | The notice discloses sharing with Corvid Metrics, then says sharing happens only with processors on the Subprocessors page, which does not list Corvid. | The notice is published 2026-11-01 while the page still shows only Hexa and Pellet. The notice contradicts itself and the published page. A customer or regulator sees undisclosed sharing of account numbers and transaction history. This is also drift from "keep our published pages consistent". | Add Corvid Metrics (purpose: product analytics) to the Subprocessors page. Publish it as a new dated version, superseding rather than editing in place, no later than the notice. Re-read both pages together before release. | Y/Y/Y/Y |
| F2 | Critical | CONFIRMED | R | subprocessors_published.md:3, 5-8 | The page's own "only with the processors listed here" statement becomes untrue once analytics starts. No updated page was produced. | The analytics feature goes live on 2026-11-01 and data flows to Corvid. The published page now makes a false exclusivity claim, independent of the notice. | Same fix as F1. Gate the feature launch on the updated page being live. | Y/Y/Y/Y |
| F3 | High | PROBABLE | R | statement_template.md (end, after line 11) | RICR 4.5's mandatory sentence is absent. The template references an adviser, so these are probably managed accounts. | November statements go out to managed-account customers without the required sentence, which is a rule breach on every statement. | Add verbatim: "Compare this information with your official account statement." Confirm whether 4.5 applies (see NV1). | Y/N/Y/Y |
| F4 | Medium | PROBABLE | R | privacy_notice.md:5-6 | The stated purpose ("which features customers use") does not need account numbers or full transaction history. More identifying financial data is sent to a third party than the purpose requires. | Corvid suffers a breach, or the notice is challenged on data minimisation. Account numbers and transaction histories are exposed for a feature-usage purpose. | Send pseudonymous IDs and feature events only. If the data is genuinely needed, state why in the notice. | Y/N/N/N |

**Confirm-or-refute and sibling search:**
- **F1 and F2.** The strongest defence is that the page might be updated separately. Nothing supplied shows that, and the request asked for consistency, so both hold. They share one root cause: the published list was not updated. I also searched both drafts for other "only" or exclusivity claims and found none beyond these two. These are not security findings: there is no crossed trust boundary; they are regulatory and customer findings.
- **F3.** The strongest defence is that the statement *is* the official record, or that the accounts are not managed. Neither is established, and the extract has no exclusion, so it holds as PROBABLE. Sibling search: the privacy notice also lacks the sentence, but whether it counts as a "communication about a managed account" is unclear (NV2). Not a security finding.

### NEEDS VALIDATION
- **NV1:** Whether the accounts are managed accounts, and whether full RICR exempts the official statement itself from 4.5.
- **NV2:** Whether the privacy notice counts as a "communication about a managed account" under 4.5.
- **NV3:** Which privacy law applies, and whether the notice must state:
  - lawful basis,
  - retention,
  - opt-out rights,
  - Corvid's location or international transfers.
- **NV4:** Whether a processing agreement with Corvid exists that restricts it to processing "for us" only.
- **NV5:** Whether emailed statements via Pellet Mail carry the full account number, and whether policy requires masking it.
- **NV6:** Whether the live Subprocessors page on 2026-10-25 still matches the supplied 2026-02-01 copy.

### REFUTED
- **RICR 4.3 breach in the statement template:** refuted. The template shows balances, contributions, withdrawals and fees, but no return or performance figure, so 4.3 is not triggered.
- **RICR 4.2 breach in either draft:** refuted. Neither draft contains guarantee or risk-free wording.

### WHAT HOLDS UP
- The notice is candid: it names the recipient and the data, including account number and transaction history.
- "We do not sell personal data" is consistent with everything supplied.
- The statement template shows fees explicitly and makes no performance or guarantee claims.

### UNVERIFIED CLAIMS
- "Corvid Metrics… analyzes it for us" (processor role): confirm via the contract.
- "We do not sell personal data": confirm against the Corvid commercial terms.

### QUESTIONS FOR THE AUTHOR
1. Are these managed accounts, and does full RICR exempt the official statement from 4.5?
2. Will an updated Subprocessors page listing Corvid be published on or before 2026-11-01?
3. Does analytics actually need account numbers and transaction history?

### DECISION-MAKER SUMMARY
Do not publish yet. Add Corvid Metrics to a new dated Subprocessors page and add the RICR 4.5 sentence to the statement template once its applicability is confirmed. Publishing as-is puts two false "only these processors" statements in front of customers and the regulator, and probably breaches 4.5 on every November statement.

### OWNER SUMMARY
The new privacy notice says we share data with a new analytics company, but our public list of companies we share data with does not include it. As a result, both pages would be untrue on launch day. The statement template also appears to be missing a sentence the rules require, and the analytics feature sends more financial detail than it seems to need.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "privacy_notice.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "statement_template.md", "status": "seen", "matters": true},
    {"item": "subprocessors_published.md", "status": "seen", "matters": true},
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "managed-account status of the accounts", "status": "not_seen", "matters": true},
    {"item": "applicable privacy law", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics processing agreement", "status": "not_seen", "matters": true},
    {"item": "live published pages on review date", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Templates with placeholders; no real personal data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "privacy_notice.md", "kind": "document"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "statement_template.md", "kind": "document"},
      {"unit": "subprocessors_published.md", "kind": "document"},
      {"unit": "P1 analytics disclosure", "kind": "claim"},
      {"unit": "P2 notice 'only listed processors'", "kind": "claim"},
      {"unit": "P3 subprocessors page 'only listed here'", "kind": "claim"},
      {"unit": "S1 RICR 4.5 compliance", "kind": "claim"},
      {"unit": "S2 RICR 4.3 compliance", "kind": "claim"},
      {"unit": "S3 RICR 4.2 compliance", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "full RICR text", "reason": "not_supplied"},
      {"unit": "applicable privacy law", "reason": "not_supplied"},
      {"unit": "Corvid Metrics agreement", "reason": "not_supplied"},
      {"unit": "live published pages", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md:5-6 vs privacy_notice.md:8",
     "scenario": "Notice published 2026-11-01 discloses sharing with Corvid Metrics while stating data goes only to processors on the Subprocessors page, which lists only Hexa Hosting and Pellet Mail; customers and the regulator see a self-contradictory notice and undisclosed sharing of account numbers and transaction history.",
     "fix": "Add Corvid Metrics (product analytics) to a new dated version of the Subprocessors page published no later than the notice; re-read both together before release.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all exclusivity or 'only' sharing statements in both drafts and the published subprocessors page",
                           "found": "subprocessors_published.md:3 (F2)"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "subprocessors_published.md:3, 5-8",
     "scenario": "When analytics goes live, personal data flows to Corvid Metrics while the published page still says data is shared only with the two listed processors, making the published page false.",
     "fix": "Publish a superseding Subprocessors page listing Corvid Metrics; gate the analytics launch on it being live.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all exclusivity or 'only' sharing statements in both drafts and the published subprocessors page",
                           "found": "privacy_notice.md:8 (F1)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (end, after line 11)",
     "scenario": "November statements sent to managed-account customers lack RICR 4.5's mandatory sentence, a rule breach on every statement.",
     "fix": "Add verbatim: \"Compare this information with your official account statement.\" after confirming 4.5 applies to statements of these accounts.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "both drafts for the 4.5 sentence",
                           "found": "privacy_notice.md also lacks it; applicability unclear (NV2)"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "privacy_notice.md:5-6",
     "scenario": "Account numbers and full transaction histories are sent to a third party for a feature-usage purpose that does not need them; a Corvid breach or a minimisation challenge exposes identifying financial data.",
     "fix": "Send pseudonymous identifiers and feature events only, or state in the notice why account numbers and transactions are necessary.",
     "answers": {"a": true, "b": false, "c": false, "d": false}},
    {"id": "NV1", "status": "needs_validation", "track": "R", "location": "statement_template.md",
     "suspicion": "RICR 4.5 may or may not apply to the statement itself.",
     "unresolved_fact": "Whether the accounts are managed accounts and whether full RICR exempts the official statement."},
    {"id": "NV2", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "The privacy notice may need the RICR 4.5 sentence.",
     "unresolved_fact": "Whether a privacy notice is a 'communication about a managed account' under RICR."},
    {"id": "NV3", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "Notice may omit legally required content (lawful basis, retention, opt-out, transfers).",
     "unresolved_fact": "Which privacy law applies and its required notice contents."},
    {"id": "NV4", "status": "needs_validation", "track": "R", "location": "privacy_notice.md:5-6",
     "suspicion": "Corvid Metrics may not be bound to act only as a processor.",
     "unresolved_fact": "Whether a processing agreement restricting Corvid to processing on our behalf exists."},
    {"id": "NV5", "status": "needs_validation", "track": "R", "location": "statement_template.md:3",
     "suspicion": "Full account number may be emailed via Pellet Mail unmasked.",
     "unresolved_fact": "Delivery channel and the masking policy for account numbers in statements."},
    {"id": "NV6", "status": "needs_validation", "track": "R", "location": "subprocessors_published.md",
     "suspicion": "The supplied copy may not match the live page.",
     "unresolved_fact": "Content of the live Subprocessors page on 2026-10-25."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "statement_template.md breaches RICR 4.3 (performance net of fees and past-performance warning).",
     "evidence": "The template shows balances, flows and fees but no return or performance figure, so 4.3 is not triggered."},
    {"id": "C2", "candidate": "Either draft breaches RICR 4.2.",
     "evidence": "Neither draft contains guarantee or risk-free wording."}
  ]
}
```