# Redteam review: privacy notice and November statement template

**VERDICT: REWORK.** As drafted, the privacy notice tells customers their data goes only to listed processors. The published list does not include the new analytics processor, so the notice is false on the day it would go live.

**CONFIDENCE: medium.**
- I had no tools, so everything below comes from reading the supplied text. No links, contracts or live pages were opened.
- No fresh subagent or other-vendor reviewer was available, so this is a single-reviewer, same-session review. The work was not written in this conversation, which lowers anchoring risk, but re-run it in a fresh session before relying on it for publication.
- The RICR extract has no definitions, so "managed account" and "communication" cannot be confirmed.

## Inputs ledger

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes |
| context.md | seen | yes |
| privacy_notice.md (draft for 2026-11-01) | seen | yes |
| statement_template.md (template for 2026-11-01) | seen | yes |
| rule_extract.md (RICR 4.2, 4.3, 4.5) | seen | yes |
| subprocessors_published.md (published 2026-02-01) | seen | yes |
| Full RICR text, including definitions of "communication" and "managed account" | not supplied | yes: decides whether 4.5 applies to each document |
| Currently published privacy notice and other published pages (terms, pricing) | not supplied | yes: "keep our published pages consistent" cannot be fully checked |
| Corvid Metrics contract or data processing agreement | not supplied | yes: the processor role and the "do not sell" claim depend on it |
| Whether customer accounts are managed accounts | not supplied | yes: decides F2 |

## Coverage

- **Scope:** both drafts, in full, checked against the request, the RICR extract and the published subprocessor list.
- **Checked:**
  - All six supplied files.
  - Every sentence of the privacy notice.
  - Every line of the statement template.
  - RICR 4.2, 4.3 and 4.5, each applied to each draft.
- **Not checked:**
  - Other published pages (not supplied).
  - RICR definitions (not supplied).
  - Corvid's contract (not supplied).
  - The live site and the mail pipeline (no tools).

## Seats and gate

- **Sensitivity gate:** passed. These are templates and a draft policy with placeholders and no real personal data.
- **Seats:** single reviewer, same session. No subagent or other-vendor seat was available in this session; none was refused on sensitivity grounds.

## Claims to evidence

| Label | Location and wording | Support | Status | Link |
|---|---|---|---|---|
| C1 | privacy_notice.md, "Who receives your data": "We share personal data only with the processors listed in our Subprocessors page." | subprocessors_published.md lists only Hexa Hosting and Pellet Mail. The same draft's Analytics paragraph sends data to Corvid Metrics. | Contradicted by supplied text | F1 |
| C2 | privacy_notice.md: "We do not sell personal data." | No contract supplied | UNVERIFIED | S3 |
| C3 | privacy_notice.md, Analytics: "Corvid Metrics, which analyzes it for us" (processor role) | No contract supplied | UNVERIFIED | S3 |
| C4 | privacy_notice.md, line 1: "We collect your name, contact details and account activity" | The Analytics paragraph shares "your account number", which is not among the listed categories | Bounded interpretation | F3 |
| C5 | statement_template.md complies with RICR ("Follow RICR" in the request) | RICR 4.2: no guarantee or risk-free wording (holds). RICR 4.3: no performance or return figure shown, so not triggered (bounded interpretation). RICR 4.5: required sentence absent (verified observation). | Mixed | F2 |
| C6 | Assumption: these are managed accounts | Inferred from "Contact your adviser" in statement_template.md | PROBABLE | F2, S1 |
| C7 | statement_template.md: "write to support@example.test" is a working contact | `.test` is a reserved domain that never resolves | UNVERIFIED that it is meant as a placeholder | S2 |

## Findings

**F1: Critical (CONFIRMED, Track R)**
- **Location:** privacy_notice.md, "Who receives your data". Read it together with the Analytics paragraph and subprocessors_published.md.
- **What is wrong:**
  - The notice says data goes "only" to processors "listed in our Subprocessors page".
  - It also sends account number and transaction history to Corvid Metrics.
  - Corvid is absent from the published page (dated 2026-02-01).
  - The request explicitly asked to "keep our published pages consistent", so this is also drift from the request.
- **Failure scenario:** The notice goes live on 2026-11-01 with the subprocessor page unchanged. A customer or the regulator reads both pages, and the published list is now untrue. Account numbers and transaction histories flow to a vendor the customer was told does not receive them.
- **Fix:**
  - Publish a new, dated version of the Subprocessors page that adds Corvid Metrics (purpose: product analytics). It must take effect on or before the privacy notice's effective date.
  - Do not edit the 2026-02-01 version in place; supersede it.
  - Hold the privacy notice until the new list is live.
- **a/b/c/d:** yes / yes / yes / yes.

**F2: High (PROBABLE, Track R)**
- **Location:** statement_template.md, whole template. The required sentence is missing.
- **What is wrong:**
  - RICR 4.5 says: "Every communication about a managed account must carry this sentence: 'Compare this information with your official account statement.'"
  - The template does not carry it.
  - The template points customers to "your adviser", which suggests these are managed accounts.
  - The rule as supplied has no exception for the statement itself.
- **Failure scenario:** If the accounts are managed, every November statement goes out in breach of RICR 4.5.
- **Fix:**
  - Add the sentence verbatim.
  - If the accounts are not managed accounts, record that determination and its basis instead.
- **a/b/c/d:** yes / no (whether the accounts are managed is inferred) / yes / yes.

**F3: Medium (PROBABLE, Track R)**
- **Location:** privacy_notice.md, line 1 ("We collect your name, contact details and account activity") compared with the Analytics paragraph ("including your account number and transaction history").
- **What is wrong:**
  - The list of collected data does not name the account number, yet the notice says the account number is shared.
  - The stated purpose ("to run your account") does not cover analytics.
- **Failure scenario:** A customer reads the collection list as complete and does not expect their account number to be collected for, or shared for, analytics.
- **Fix:**
  - Name account identifiers and transaction history in the collection list.
  - Add analytics as a purpose.
- **a/b/c/d:** yes / no / no (no supplied rule governs this) / yes.

**Confirm-or-refute round**
- **F1, strongest defense:** "the subprocessor page will be updated separately." No such update was supplied, and the request made consistency part of this job. A second defense is that Corvid is not a processor. That fails too: the "only" sentence is false whatever role Corvid has. F1 holds.
- **F2, strongest defense:** "the accounts are not managed", or "the statement is itself the official statement, so the sentence is circular." The first is an unresolved fact, which is why the evidence is PROBABLE. The second is not an exception the supplied rule contains. F2 holds at High, with PROBABLE evidence.

**Siblings searched (for F1 and F2):**
- For F1, I searched both drafts for other published lists. Only the privacy notice's own collection list exists, and its gap is recorded separately as F3.
- For F2, I checked the privacy notice for the 4.5 sentence. It is also absent there; whether that matters is recorded under S4.

Neither F1 nor F2 is a security finding, because no trust boundary is crossed.

## Needs validation (no severity)

- **S1:** Are customer accounts managed accounts under RICR? This settles F2 and S4.
- **S2:** Is `support@example.test` a placeholder? It must be replaced with a real, monitored address before publication.
- **S3:** Does the Corvid Metrics contract make Corvid a processor, bar it from using the data for its own purposes, and involve no payment for data? This settles C2 and C3.
- **S4:** Does RICR's definition of "communication about a managed account" cover a privacy notice? If yes, the privacy notice also needs the 4.5 sentence.

## Refuted

- **RICR 4.3 breach in the statement:**
  - The template shows balances, flows and fees, but no return or performance figure, so 4.3 is not triggered as written.
  - If a performance line is added later, it must be net of fees and must carry the past-performance sentence.
- **RICR 4.2 breach:** neither draft contains guarantee or risk-free wording.

## What holds up

- The analytics feature is disclosed, not hidden.
- The statement template contains no prohibited promises.
- Fees are shown as their own line.

## Unverified claims

- "We do not sell personal data": confirm against the Corvid contract.
- Corvid's processor role: confirm against the same contract.
- Consistency with other published pages (terms, pricing, the current privacy notice): compare each page against the drafts.

## Questions for the author

1. Are these managed accounts under RICR?
2. Will a new, dated Subprocessors page listing Corvid Metrics be published before 2026-11-01?
3. Does analytics need the account number at all, or would a pseudonymous identifier do?

## Decision-maker summary

Do not publish until the subprocessor list is reissued with Corvid Metrics and the privacy notice's data categories are corrected. Add the RICR 4.5 sentence to the statement unless the accounts are confirmed not to be managed. If you proceed anyway, the notice misstates who receives customer data, and statements may breach RICR 4.5 from the first issue.

## Owner summary

The new privacy wording says we only share data with companies on our published list. The new analytics company is not on that list, so the list must be updated first. The monthly statement is probably missing a sentence the rules require, and its support email address looks like a placeholder.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "privacy_notice.md", "status": "seen", "matters": true},
    {"item": "statement_template.md", "status": "seen", "matters": true},
    {"item": "rule_extract.md", "status": "seen", "matters": true},
    {"item": "subprocessors_published.md", "status": "seen", "matters": true},
    {"item": "Full RICR text and definitions", "status": "not_seen", "matters": true},
    {"item": "Other published pages (current privacy notice, terms, pricing)", "status": "not_seen", "matters": true},
    {"item": "Corvid Metrics contract or data processing agreement", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Templates and draft policy text with placeholders; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "privacy_notice.md", "kind": "document"},
      {"unit": "statement_template.md", "kind": "document"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "subprocessors_published.md", "kind": "document"},
      {"unit": "C1 only-listed-processors claim", "kind": "claim"},
      {"unit": "C4 collected data categories", "kind": "claim"},
      {"unit": "C5 RICR 4.2/4.3/4.5 compliance of statement template", "kind": "claim"},
      {"unit": "C6 accounts are managed accounts", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "Full RICR text and definitions", "reason": "not_supplied"},
      {"unit": "Other published pages", "reason": "not_supplied"},
      {"unit": "Corvid Metrics contract", "reason": "not_supplied"},
      {"unit": "Live site and mail pipeline", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Who receives your data' vs Analytics paragraph and subprocessors_published.md",
     "scenario": "The notice goes live 2026-11-01 saying data is shared only with listed processors, while account numbers and transaction history go to Corvid Metrics, which is absent from the 2026-02-01 published list; customers and the regulator read a false statement.",
     "fix": "Publish a new dated Subprocessors page adding Corvid Metrics (analytics), effective on or before 2026-11-01, superseding the 2026-02-01 version rather than editing it; hold the notice until it is live.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "Both drafts for other published lists or category lists that the new feature could make untrue", "found": "The privacy notice's own collection list omits the account number (F3)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (whole template; RICR 4.5 sentence absent)",
     "scenario": "If the accounts are managed (the template refers customers to 'your adviser'), every November statement omits the sentence RICR 4.5 requires: 'Compare this information with your official account statement.'",
     "fix": "Add the RICR 4.5 sentence verbatim, or record the determination that the accounts are not managed accounts.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "privacy_notice.md for the RICR 4.5 sentence", "found": "Absent; applicability unresolved (S4)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "privacy_notice.md line 1 vs Analytics paragraph",
     "scenario": "A customer reads the collection list (name, contact details, account activity) as complete and does not expect their account number to be collected or shared for analytics.",
     "fix": "Name account identifiers and transaction history in the collection list and add analytics as a stated purpose.",
     "answers": {"a": true, "b": false, "c": false, "d": true}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "statement_template.md",
     "suspicion": "RICR 4.5 applies to these statements.",
     "unresolved_fact": "Whether customer accounts are managed accounts under RICR."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "statement_template.md, contact line",
     "suspicion": "support@example.test is a non-resolving placeholder that would ship as the customer contact.",
     "unresolved_fact": "Whether a real, monitored address replaces it before publication."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "privacy_notice.md, Analytics and 'We do not sell personal data'",
     "suspicion": "Corvid may not act purely as a processor, or the arrangement may count as a sale or exchange of data.",
     "unresolved_fact": "The terms of the Corvid Metrics contract or data processing agreement."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "privacy_notice.md",
     "suspicion": "The privacy notice may also need the RICR 4.5 sentence.",
     "unresolved_fact": "Whether RICR's definition of 'communication about a managed account' covers a privacy notice."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The statement template breaches RICR 4.3.", "evidence": "The template shows balances, flows and fees but no performance or return figure, so 4.3 is not triggered as written."},
    {"id": "C2", "candidate": "A draft breaches RICR 4.2.", "evidence": "Neither draft contains guarantee or risk-free wording."}
  ]
}
```