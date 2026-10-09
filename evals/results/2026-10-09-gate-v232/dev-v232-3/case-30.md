VERDICT: **REWORK.** The privacy notice names a new data recipient that our published processor list leaves out. The statement template also appears to omit a sentence the rule requires, and it has no line that would let its figures add up.

CONFIDENCE: **medium.** Limits: there were no tools, so I relied only on the supplied text and checked nothing outside it. No fresh-subagent or cross-vendor seat was available, so this is a single-reviewer pass; re-run it in a fresh session before publication. The governing privacy law and the account type are not stated.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `privacy_notice.md`, `rule_extract.md`, `statement_template.md`, `subprocessors_published.md`.
- Not seen:
  - The full RICR text. This matters because only §§4.2, 4.3 and 4.5 were supplied, so other paragraphs may apply.
  - The applicable privacy law and the Corvid Metrics contract or DPA. This matters for F2 and S1.
  - Any revised Subprocessors page. This matters for F1: if a revision exists, F1 changes.
  - Confirmation of account type, managed or not. This matters for F3.
  - The current published privacy notice. This matters only for checking that versions are superseded rather than edited in place.

COVERAGE:
- Scope: the whole work, which is the two documents to be published, checked against the two supplied references.
- Checked: all six supplied files. Within them:
  - every sentence of the privacy notice;
  - every line of the template;
  - RICR §§4.2, 4.3 and 4.5;
  - every row of the processor list.
- Not checked:
  - RICR paragraphs that were not supplied (not_supplied);
  - privacy-law requirements (not_supplied);
  - invisible or look-alike characters (no_tools);
  - the rendered or published versions of the pages (no_tools).

SEATS AND GATE:
- The gate passed. The documents are templates and policy text, and they contain no personal data, credentials or client records.
- Seats: same-session review only. No subagent or external seat was available in this session, so none was refused on sensitivity grounds.
- No reviewer-directed instructions were found in the work.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | R | `privacy_notice.md` "Analytics (new)" and "Who receives your data"; `subprocessors_published.md` table | The notice says data goes to Corvid Metrics. It also says "We share personal data only with the processors listed in our Subprocessors page". That page (published 2026-02-01) lists only Hexa Hosting and Pellet Mail. | The notice goes live on 2026-11-01 and the list is unchanged. The notice then contradicts itself, and the published page becomes untrue. A customer or the regulator reading both sees an undisclosed recipient of account numbers and transaction history. This also breaks the request's explicit "keep our published pages consistent". | Publish a superseding Subprocessors version that adds Corvid Metrics, its purpose (product analytics) and the data shared. It must take effect on or before 2026-11-01, and the 2026-02-01 version should be kept as a record. To check: diff the processor names in the notice against the published table. | a✓ b✓ c✓ d✓ |
| F2 | High | PROBABLE | R | `statement_template.md` (whole template, no 4.5 sentence) | RICR §4.5 requires every communication about a managed account to carry "Compare this information with your official account statement." The template lacks it. "Contact your adviser" suggests these are advised or managed accounts. | Statements go out in November without the required sentence. Every statement is then a §4.5 breach, repeated for each customer. | Add the exact §4.5 sentence verbatim. Have compliance confirm whether the account type is "managed", and whether a statement that is itself the official record still needs the sentence. | a✓ b✗ c✓ d✓ |
| F3 | High | CONFIRMED | R | `statement_template.md`, the balance block | The template has no line for investment gains or losses. Opening + contributions − withdrawals − fees equals closing only when markets did not move. | In any month with market movement, the customer's figures do not reconcile and there is no explanation. That brings complaints and can look like an error in fees or balances. If a gain/loss or return line is added, it is performance, so §4.3 then applies: it must be net of fees and carry the "past performance does not predict future results" statement. | Add a "Change in investment value" line, with a check that the lines sum to closing. If returns are shown, show them net of fees and add the §4.3 statement. | a✓ b✓ c✗ d✓ |
| F4 | Medium | PROBABLE | R | `privacy_notice.md` "Analytics (new)" | The stated purpose is "to understand which features customers use". That purpose does not need the account number or the full transaction history. | A regulator or customer asks why identifiable financial data goes to a third party for feature analytics. The disclosure shows collection beyond its stated purpose. | Send pseudonymous IDs and feature events instead. Otherwise, state a purpose that actually needs this data and confirm the legal basis. | a✓ b✗ c✓ d✗ |
| F5 | Low | CONFIRMED | R | `privacy_notice.md` line 1 vs "Analytics (new)" | The opening says data is collected "to run your account". Analytics is a second purpose that the summary sentence does not mention. | A reader of the first line only gets an incomplete purpose statement. | Change line 1 to list both purposes. | a✓ b✓ c✗ d✗ |

Siblings and boundaries:
- **F1** (not a security finding):
  - I searched both documents for every named recipient. Corvid Metrics is the only one that is not listed. Pellet Mail sends statements and is listed.
  - I searched for other published lists the change could make stale. Only the Subprocessors page was supplied. Any data-categories list is not seen.
- **F2** (not a security finding): I searched the privacy notice for the same missing §4.5 sentence. It does not carry it either. Whether a privacy notice is "about a managed account" is unclear, so that sibling is S2.
- **F3** (not a security finding): I searched the other template fields for similar omissions. No performance or return figure exists, so §4.3 does not currently apply. None of the template's fields guarantees anything, so §4.2 holds.

## NEEDS VALIDATION
- **S1:** whether a lawful basis or a DPA exists for sending account numbers and transaction history to Corvid Metrics. This is settled by the governing privacy law and the Corvid contract.
- **S2:** whether §4.5 applies to the privacy notice. This is settled by compliance's reading of "communication about a managed account".
- **S3:** whether the statement should show the full `{account_number}` or a masked one, given that it is sent through Pellet Mail. This is settled by any rule or policy that requires masking on statements.
- **S4:** whether the pages contain hidden or look-alike characters. This is settled by a byte-level scan, which was not possible here.

## REFUTED
- **"Template breaches §4.3."** It shows no performance figure, so §4.3 is not triggered as drafted. That changes once F3's fix adds returns.
- **"Template breaches §4.2."** It contains no guarantee or risk-free wording.

## WHAT HOLDS UP
- Neither document contains guarantee or "risk-free" language.
- Fees are shown as their own line.
- The notice does disclose the new analytics recipient by name and purpose rather than hiding it.
- "We do not sell personal data" is not contradicted by anything supplied.

## UNVERIFIED CLAIMS
- **"We do not sell personal data."** Confirm by checking the Corvid Metrics terms for any payment or data-licensing arrangement.
- **"Corvid Metrics, which analyzes it for us."** This implies a processor role. Confirm from the contract that Corvid does not use the data for its own purposes.

## QUESTIONS FOR THE AUTHOR
1. Is a revised Subprocessors page that adds Corvid Metrics scheduled for 2026-11-01?
2. Are these managed accounts under RICR, and is this statement the official record?
3. Does the template deliberately leave out investment gains and losses, or are these cash-only accounts?

## DECISION-MAKER SUMMARY
- Do not publish yet. The new privacy notice discloses a data recipient that our published list leaves out.
- The statement template probably lacks the RICR §4.5 sentence, and its figures will not reconcile.
- Publishing as is risks a false privacy statement and a rule breach on every November statement.

## OWNER SUMMARY
The new privacy wording names an analytics company that our public list of data recipients does not mention, so the two pages contradict each other. The November statement seems to be missing a sentence the rules require. It also has no line for changes in investment value, so customers will not be able to make the numbers add up. All three should be fixed, and the public list updated, before anything goes out.

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
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "governing privacy law and Corvid Metrics contract/DPA", "status": "not_seen", "matters": true},
    {"item": "revised Subprocessors page, if any", "status": "not_seen", "matters": true},
    {"item": "account type (managed or not)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Templates and policy text only; no personal data, credentials or client records."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "privacy_notice.md", "kind": "document"},
      {"unit": "statement_template.md", "kind": "document"},
      {"unit": "rule_extract.md", "kind": "document"},
      {"unit": "subprocessors_published.md", "kind": "document"},
      {"unit": "RICR 4.2 / 4.3 / 4.5 applied to both documents", "kind": "claim"},
      {"unit": "privacy_notice.md: recipients vs published processor list", "kind": "claim"},
      {"unit": "statement_template.md: balance reconciliation", "kind": "section"}
    ],
    "not_checked": [
      {"unit": "RICR paragraphs not in extract", "reason": "not_supplied"},
      {"unit": "governing privacy law", "reason": "not_supplied"},
      {"unit": "hidden or look-alike characters", "reason": "no_tools"},
      {"unit": "currently published privacy notice and live pages", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)' and 'Who receives your data'; subprocessors_published.md table",
     "scenario": "Notice goes live 2026-11-01 naming Corvid Metrics as a recipient of account numbers and transaction history while stating sharing is only with listed processors; the published list (2026-02-01) names only Hexa Hosting and Pellet Mail, so the notice is self-contradictory and the published page becomes untrue.",
     "fix": "Publish a superseding Subprocessors version adding Corvid Metrics (purpose and data) effective on or before 2026-11-01; retain the 2026-02-01 version as a record.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every named data recipient across both documents; other published lists the change could stale", "found": "Corvid Metrics is the only unlisted recipient; no other published list was supplied"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "R",
     "location": "statement_template.md (whole template)",
     "scenario": "If the accounts are managed accounts, every November statement omits the RICR 4.5 sentence 'Compare this information with your official account statement.', a repeated breach per customer.",
     "fix": "Add the exact 4.5 sentence verbatim; have compliance confirm account type and whether the statement itself is the official record.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "privacy_notice.md for the 4.5 sentence", "found": "also absent; applicability unclear, recorded as S2"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "R",
     "location": "statement_template.md balance block",
     "scenario": "In any month with market movement, opening + contributions - withdrawals - fees does not equal closing, and no line explains the difference; customers cannot reconcile their statement.",
     "fix": "Add a 'Change in investment value' line and a sum check; if returns are shown, present them net of fees with the RICR 4.3 past-performance statement.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all template fields for other missing or performance lines", "found": "no performance figure present, so 4.3 is not yet triggered; 4.2 holds"}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "R",
     "location": "privacy_notice.md 'Analytics (new)'",
     "scenario": "The stated purpose (which features customers use) does not need account numbers or transaction history; a regulator or customer sees identifiable financial data sent to a third party beyond the stated purpose.",
     "fix": "Send pseudonymous IDs and feature events only, or state a purpose that requires this data and confirm its legal basis.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "R",
     "location": "privacy_notice.md line 1",
     "scenario": "The opening says data is collected 'to run your account', omitting the new analytics purpose; a reader of line 1 gets an incomplete purpose statement.",
     "fix": "List both purposes in the opening sentence.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "R", "location": "privacy_notice.md 'Analytics (new)'",
     "suspicion": "No lawful basis or DPA may exist for sharing with Corvid Metrics.",
     "unresolved_fact": "The governing privacy law and the Corvid Metrics contract terms."},
    {"id": "S2", "status": "needs_validation", "track": "R", "location": "privacy_notice.md (whole)",
     "suspicion": "The privacy notice may also need the RICR 4.5 sentence.",
     "unresolved_fact": "Whether compliance treats the privacy notice as a communication about a managed account."},
    {"id": "S3", "status": "needs_validation", "track": "R", "location": "statement_template.md '{account_number}'",
     "suspicion": "The full account number may be printed on statements sent via Pellet Mail.",
     "unresolved_fact": "Whether a rule or policy requires masking account numbers on statements."},
    {"id": "S4", "status": "needs_validation", "track": "R", "location": "all reviewed documents",
     "suspicion": "Hidden or look-alike characters could alter the published text.",
     "unresolved_fact": "A byte-level scan of the files."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Statement template breaches RICR 4.3.", "evidence": "The template shows no performance figure; 4.3 only applies once returns are shown."},
    {"id": "C2", "candidate": "Statement template breaches RICR 4.2.", "evidence": "The template contains no guarantee or risk-free wording."}
  ]
}
```