VERDICT: **REWORK**. All four claims in the synthesis misstate their sources: two cite the wrong paragraph, one quote does not exist and gives the wrong number, and the recommended setting cannot be saved.

CONFIDENCE: **high** on the findings, because every source was supplied as text and each claim was checked against it word for word. Three things limit it:
- I had no tools. I could not open the live URLs to confirm the local copies match.
- I am a single reviewer with no fresh-subagent seat. The work was not written in this conversation, so the review is still independent of the author.
- No run was needed: this is a fact check, not code.

INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | yes |
| context.md | seen | yes |
| synthesis.md | seen | yes |
| sources/northline-rulebook.md | seen | yes |
| sources/eastport-gn3.md | seen | yes |
| sources/vaultline-retention.md | seen | yes |
| Live source URLs (`*.example.test`) | not openable (no tools/network) | low; the context says the local copies are the sources |
| Northline Rule 13 | not present in the copy (the Rule Book jumps from 12 to 14) | low; no claim depends on it, but the copy may be partial |

COVERAGE: whole work, all four numbered claims. Checked: synthesis items 1–4, and every paragraph of all three sources (GN-3 3.1–3.4, Northline Rules 11/12/14, Vaultline `retention_mode`). Not checked: the live sources (no tools) and whether the local copies are complete.

SEATS AND GATE: one reviewer (this session), with no subagent or other tools available. The sensitivity gate passed: no personal, credential or confidential data. No cross-vendor seats were requested. I found no text inside the work addressed to the reviewer.

## CLAIMS TO EVIDENCE

| Claim | Location | Synthesis says | Source actually says | State | Link |
|---|---|---|---|---|---|
| C1 | synthesis.md item 1 | "Rule 12 … requires 72 hours' notice before a planned outage" | Rule 12: "Reserved." Rule 14: "72 hours' notice before a planned outage of a customer-facing service" | Obligation correct; rule number wrong; scope ("customer-facing") dropped | F2, F6 |
| C2 | synthesis.md item 2 | Quote: "account data must be erased promptly, and in any case within 30 days" | 3.4: "Account data is deleted within 45 days of account closure." No "promptly", no "must", no "30 days" | CONFIRMED wrong: the quote is fabricated and the number is wrong | F1, F5 |
| C3 | synthesis.md item 3 | Deletion is GN-3 ¶3.2 | ¶3.2 is "Backups. Backups are encrypted at rest." Deletion is ¶3.4 | CONFIRMED wrong | F3 |
| C4a | synthesis.md item 4 | Set `retention_mode = strict` | Valid values are `off`, `standard` (30 days) and `extended` (365 days); "an unknown value is rejected when the setting is saved" | CONFIRMED wrong | F4 |
| C4b | synthesis.md item 4 | The setting will "meet both rules" | The Vaultline source does not say what `retention_mode` governs. An outage-notice rule has no connection to a retention setting | Unsupported interpretation | F7, S1 |

## FINDINGS (ordered by severity)

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | synthesis.md item 2 | The quoted text does not appear in GN-3. The real period is 45 days from account closure, not 30. The words "promptly" and "must" are invented. | Operations leads build a deletion process to a 30-day "regulator" figure. They may also repeat a fabricated quote from the regulator to auditors or customers, which misrepresents the regulator. | Replace it with the verbatim ¶3.4 text: "Account data is deleted within 45 days of account closure." Keep the trigger (account closure) and remove the quotation marks around anything that is not verbatim. | y/y/y/y |
| F2 | High | CONFIRMED | C | synthesis.md item 1 | The 72-hour outage notice is cited to Rule 12, which is "Reserved." The obligation is Rule 14. | Someone checks or cites "Rule 12" in an outage policy or customer notice and finds nothing. The citation discredits the policy and fails an audit trace. | Cite Rule 14 and quote it verbatim. | y/y/n/y |
| F3 | High | CONFIRMED | C | synthesis.md item 3 | The deletion requirement is placed at GN-3 ¶3.2, which is the Backups paragraph. Deletion is ¶3.4. | A lead cites ¶3.2 as the deletion basis, and a reader of GN-3 finds a backups-encryption clause instead. | Change it to ¶3.4. | y/y/n/y |
| F4 | High | CONFIRMED | C | synthesis.md item 4 | `strict` is not a valid `retention_mode` value. The source says unknown values are rejected on save. | Operations tries to apply the instruction and the save fails. Under pressure, someone picks a value by guess. `extended` (365 days) could keep data far beyond a 45-day deletion window. | Remove `strict`. State which valid value (if any) is intended, with reasoning tied to what the setting actually controls (see S1). | y/y/n/y |
| F5 | Medium | CONFIRMED | C | synthesis.md item 2 | GN-3 is a *Guidance Note* written descriptively ("is deleted"). The synthesis presents it as a mandatory "must" requirement. | Leads treat guidance as a binding rule, or describe it externally as a legal requirement. | Label the status as guidance, and say whether some separate binding instrument exists. | y/y/n/n |
| F6 | Medium | CONFIRMED | C | synthesis.md item 1 | The scope qualifier was dropped. Rule 14 covers outages "of a customer-facing service" only. | Leads apply 72-hour notice to internal-only maintenance (unneeded burden), or misread what the rule covers. | Include "customer-facing service" in the summary. | y/y/n/n |
| F7 | Medium | CONFIRMED | C | synthesis.md item 4 | "To meet both rules" does not follow. A storage retention setting cannot satisfy an outage-notice rule, and the Vaultline source makes no claim about either rule. | Leads believe one console change completes both obligations, and the outage-notice process is never set up. | Remove "meet both rules." Treat the outage notice as a separate process step. | y/y/n/n |

Sibling search for High/Critical items: I checked all four claims for the same root causes.
- **Wrong pinpoint citation:** found at items 1 and 3, logged separately as F2 and F3. Item 2 cites the right file but quotes text that does not exist in it (F1).
- **Value not in source:** found only at item 4 (F4).
- None of these are security findings: no trust boundary is crossed.

## NEEDS VALIDATION
- **S1:** Does Vaultline `retention_mode` control deletion of account data after account closure, or something else (for example, backup or version retention)? Settling it needs the Vaultline documentation on what `retention_mode` applies to. If it does govern deletion, `standard` (30 days) appears to fit inside 45 days and `extended` (365 days) would not. That is a conditional reading, not a finding.
- **S2:** Do the local copies, retrieved 2026-10-20, match the live sources as of the review date? The Northline copy omits Rule 13. Settling it needs a comparison against the live URLs and confirmation that the Rule Book copy is complete.

## REFUTED
- **Candidate: the 72-hour figure itself is wrong.** Refuted. Rule 14 states 72 hours exactly; only the rule number and scope are wrong.

## WHAT HOLDS UP
- The 72-hour planned-outage notice obligation exists in the Northline Rule Book.
- Each claim points to the correct source *file*.
- Retrieval dates are recorded on every source copy.

## UNVERIFIED CLAIMS
- That any `retention_mode` value satisfies Eastport's deletion guidance. This needs Vaultline's description of what the setting governs (S1).
- That the local copies are current and complete (S2).

## QUESTIONS FOR THE AUTHOR
1. Where did the 30-day quote come from? Is there another Eastport document that was not supplied?
2. What does `retention_mode` apply to, and which value did you intend?
3. Is there a binding Eastport instrument behind GN-3, or is guidance the highest authority?

## DECISION-MAKER SUMMARY
Do not circulate this synthesis: every claim misstates its source, including a fabricated regulator quote (30 days, where the source says 45) and a console setting that cannot be saved. Send it back for correction against the verbatim source text: Rule 14, GN-3 ¶3.4 at 45 days after closure, and a valid retention value whose effect is documented. If it goes out as is, leads may build processes to the wrong deadline, cite rules that do not exist, and believe the outage-notice duty is covered by a storage setting.

## OWNER SUMMARY
The summary of the rules got several facts wrong: it points to the wrong sections, quotes a regulator saying something it did not say, and recommends a setting that does not exist. The real deletion window is 45 days after an account closes. Outage notices are a separate task from any storage setting. Please have it corrected before anyone acts on it.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "synthesis.md", "status": "seen", "matters": true},
    {"item": "sources/northline-rulebook.md", "status": "seen", "matters": true},
    {"item": "sources/eastport-gn3.md", "status": "seen", "matters": true},
    {"item": "sources/vaultline-retention.md", "status": "seen", "matters": true},
    {"item": "live source URLs", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-single-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "synthesis.md", "kind": "document"},
      {"unit": "sources/northline-rulebook.md", "kind": "document"},
      {"unit": "sources/eastport-gn3.md", "kind": "document"},
      {"unit": "sources/vaultline-retention.md", "kind": "document"},
      {"unit": "C1 synthesis item 1", "kind": "claim"},
      {"unit": "C2 synthesis item 2", "kind": "claim"},
      {"unit": "C3 synthesis item 3", "kind": "claim"},
      {"unit": "C4 synthesis item 4", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live source URLs", "reason": "no_tools"},
      {"unit": "Northline Rule 13 / completeness of rulebook copy", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 2",
     "scenario": "Quoted text does not appear in GN-3; source 3.4 says 45 days after account closure, not 30, with no 'promptly' or 'must'. Leads build to a wrong deadline and may repeat a fabricated regulator quote externally.",
     "fix": "Replace with the verbatim GN-3 3.4 text: 'Account data is deleted within 45 days of account closure.'",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all four synthesis claims for quotes or values not present in their cited source", "found": "item 4 (logged as F4); no other fabricated quote"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Outage notice is cited to Rule 12, which reads 'Reserved.'; a policy or audit tracing Rule 12 finds nothing.",
     "fix": "Cite Northline Rule 14 and quote it verbatim.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all pinpoint citations in synthesis items 1-4", "found": "item 3 (logged as F3)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 3",
     "scenario": "Deletion is placed at GN-3 3.2, which is the Backups paragraph; anyone citing 3.2 points to a backups-encryption clause.",
     "fix": "Change the citation to GN-3 paragraph 3.4.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all pinpoint citations in synthesis items 1-4", "found": "item 1 (logged as F2)"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "'strict' is not a valid retention_mode value (only off, standard, extended); the console rejects it on save, and an improvised choice such as extended (365 days) could retain data past a 45-day deletion window.",
     "fix": "Remove 'strict'; name a valid value with reasoning tied to what retention_mode actually governs.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all configuration values and figures in the synthesis against their sources", "found": "item 2's 30-day figure (logged as F1)"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 2",
     "scenario": "GN-3 is a guidance note written descriptively; the synthesis presents it as a mandatory 'must', so leads may describe guidance as a legal requirement.",
     "fix": "Label GN-3 as guidance and state whether any binding instrument exists.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Rule 14 is limited to customer-facing services; the synthesis drops that scope, so leads may apply or describe the rule too broadly.",
     "fix": "Include 'of a customer-facing service' in the summary.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F7", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "'Meet both rules' implies a retention setting satisfies the outage-notice rule; leads may never set up the outage-notice process.",
     "fix": "Remove 'meet both rules'; treat outage notice as a separate process step.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "synthesis.md item 4",
     "suspicion": "It is unclear whether any retention_mode value satisfies Eastport deletion guidance.",
     "unresolved_fact": "Whether Vaultline retention_mode governs deletion of account data after account closure (the source does not say)."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/*",
     "suspicion": "Local copies may be stale or partial (Rule 13 absent).",
     "unresolved_fact": "Whether the 2026-10-20 local copies match the live sources and are complete."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 72-hour figure itself is wrong.",
     "evidence": "Northline Rule 14 states 72 hours' notice before a planned outage; only the rule number and scope are wrong."}
  ]
}
```