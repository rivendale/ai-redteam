VERDICT: SHIP WITH FIXES. Items 1–3 match their sources, but item 4's retention recommendation cites a source that does not support its reasoning, and it may conflict with the 45-day deletion rule reported in item 2.

CONFIDENCE: medium. Limits: no tools and no subagent, so this is a single-reviewer pass (anchoring risk is lower because the work was not written in this conversation). I checked the local source copies only, not the live URLs. Three facts are unknown: whether the organisation is a Northline member, whether it is an Eastport "processor of account data", and what Vaultline's `retention_mode` actually retains.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `synthesis.md`, `sources/northline-rulebook.md`, `sources/eastport-gn3.md`, `sources/vaultline-retention.md`.
- Not seen or not openable:
  - The live source URLs (no network). This matters somewhat: the copies are dated 2026-10-20 and the review is dated 2026-10-25.
  - Any document stating which records operations still needs. This matters for item 4.
  - Any statement of whether GN-3 is binding. This matters for item 3.
- No embedded reviewer instructions found. No sensitive data found.

COVERAGE:
- Scope: the whole synthesis.
- Checked: all six files, synthesis items 1–4, and every cited passage.
- Not checked:
  - Live URLs (no_tools).
  - `tools/validate_findings.py` against this report (no_tools). The JSON was written to schema 2.3 by hand and has not been validated.

SEATS AND GATE: one local reviewer ran. Cross-vendor seats were not requested and depth is standard. The sensitivity gate passed: no personal, client or credential data.

CLAIMS TO EVIDENCE:

| Claim | Location | Wording | Source | Status |
|---|---|---|---|---|
| C1 | synthesis item 1 | Rule 14 "requires 72 hours' notice before a planned outage" | northline Rule 14: "Members give 72 hours' notice before a planned outage of a customer-facing service." | Verified, but scope is dropped ("Members", "customer-facing service") → F4 |
| C2 | item 2 | quoted deletion text | GN-3 3.4, verbatim match | Verified. Scope 3.1 ("processors of account data") omitted → F5 |
| C3 | item 3 | "the deletion requirement is paragraph 3.4 of GN-3" | Paragraph number verified. "Requirement": the source is a *Guidance Note* written descriptively ("is deleted"); its binding status is not stated | Bounded interpretation → F3 |
| C4a | item 4 | values `standard` = 30 days, `extended` = 365 days | vaultline-retention, verbatim | Verified |
| C4b | item 4 | "`standard` (30 days) would delete records still needed" | No passage in any source | UNVERIFIED → F1 |
| C4c | item 4 | "set `retention_mode = extended`" | Derived from C4b. 365 days > 45 days (GN-3 3.4) | Interpretation → F1, F2 |

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | synthesis.md item 4, "would delete records still needed" | The cited source only lists the setting's values and durations. No supplied source says any record must be kept past 30 days. The recommendation rests on an unsourced claim presented as if it were sourced. | Operations leads switch to `extended` believing a cited source requires it. Nobody can later show why 365 days was chosen, or which records needed it. | Cite the source or owner that defines which records must be kept, and for how long. Otherwise remove the recommendation or mark it as an unsourced operational judgment. | T/T/F/T |
| F2 | Medium | PROBABLE | C | synthesis.md items 2 vs 4 | The recommended 365-day retention exceeds the 45-day deletion window the synthesis itself reports (GN-3 3.4). The synthesis never reconciles the two. | If Vaultline holds account data for closed accounts and the organisation is in GN-3's scope, setting `extended` keeps that data up to 365 days, against 3.4. | State what `retention_mode` governs and whether it covers account data. If it does, reconcile with 3.4 (for example, 30 days is within 45) before recommending. | T/F/T/F |
| F3 | Medium | CONFIRMED | C/R | synthesis.md item 3, "the deletion requirement" | GN-3 is labelled a guidance note and phrased descriptively. Nothing in the copy says it is mandatory. | Leads, or customer-facing staff, describe 45-day deletion as legally required when the regulator issued it as guidance. | Use "GN-3 paragraph 3.4 states…". Call it a requirement only after confirming its binding status. | T/T/F/F |
| F4 | Low | CONFIRMED | C | synthesis.md item 1 | The rule's scope ("Members", "customer-facing service") is dropped. | Leads apply 72-hour notice to internal outages, or assume it applies whether or not the organisation is a member. | Restore the rule's full wording and state whether the organisation is a member. | T/T/F/F |
| F5 | Low | CONFIRMED | C | synthesis.md item 2 | The GN-3 3.1 scope ("processors of account data") is omitted. | Leads apply or skip the 45-day rule without checking whether the organisation is in scope. | Add the 3.1 scope and the organisation's applicability. | T/T/F/F |

The F1 sibling search covered each item for claims that go beyond their source. It found the scope and characterisation gaps recorded as F3–F5, and no other unsourced rationale. F1 is not a security finding.

NEEDS VALIDATION:
- Is the organisation a Northline member? Is it a processor of account data under GN-3 3.1?
- What does `retention_mode` retain? Does it include account data of closed accounts? (This decides whether F2 rises to High.)
- Is GN-3 binding guidance or advisory?
- Do the live URLs still match the copies retrieved on 2026-10-20?

REFUTED:
- "Item 1 cites the wrong rule number": the 72-hour text is at Rule 14.
- "Item 2's quote is paraphrased": it is verbatim to 3.4.
- "Item 4 misstates the setting values": `standard` = 30 days and `extended` = 365 days match the source.
- F1 confirm-or-refute: the defence that "records still needed" is the author's own operational knowledge does not hold. Item 4 presents it with a citation, and the request was to check against sources. F1 is held.

WHAT HOLDS UP:
- Item 1's rule number and 72-hour figure.
- Item 2's quotation.
- Item 3's paragraph location.
- Item 4's description of the setting values.
- Every citation points to an existing local source.

UNVERIFIED CLAIMS: C4b (records still needed), and whether the local copies are current. To confirm either, get the records-retention requirement from its owner and re-check each source URL.

QUESTIONS FOR THE AUTHOR:
1. Which records need more than 30 days of retention, and what is the source for that?
2. Does Vaultline store account data covered by GN-3?
3. Is GN-3 binding, and is the organisation a Northline member?

DECISION-MAKER SUMMARY: Items 1–3 are accurate to their sources once their scope wording is restored. Item 4's recommendation to switch to 365-day retention has no supporting source. Hold item 4 until its basis and its fit with the 45-day deletion rule are confirmed; acting on it as written risks keeping data longer than the regulator's guidance allows.

OWNER SUMMARY: The outage-notice and deletion points in this summary match the documents they cite. The advice to switch storage retention to the longer setting is not backed by any of those documents, and it may keep data far longer than the regulator's 45-day deletion guidance. Please confirm why longer retention is needed before anyone changes the setting.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "synthesis.md", "status": "seen", "matters": true},
    {"item": "sources/northline-rulebook.md", "status": "seen", "matters": true},
    {"item": "sources/eastport-gn3.md", "status": "seen", "matters": true},
    {"item": "sources/vaultline-retention.md", "status": "seen", "matters": true},
    {"item": "live source URLs", "status": "not_seen", "matters": true},
    {"item": "records-retention need for item 4", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-single-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "synthesis.md", "kind": "file"},
      {"unit": "sources/northline-rulebook.md", "kind": "file"},
      {"unit": "sources/eastport-gn3.md", "kind": "file"},
      {"unit": "sources/vaultline-retention.md", "kind": "file"},
      {"unit": "C1 Rule 14 notice", "kind": "claim"},
      {"unit": "C2 GN-3 quote", "kind": "claim"},
      {"unit": "C3 GN-3 paragraph 3.4", "kind": "claim"},
      {"unit": "C4 retention recommendation", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live source URLs", "reason": "no_tools"},
      {"unit": "tools/validate_findings.py run", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4: 'would delete records still needed'",
     "scenario": "Operations leads switch retention_mode to extended on the belief that a cited source requires records beyond 30 days; no supplied source says so, so the change has no documented basis.",
     "fix": "Cite the source or owner defining which records must be kept and for how long, or remove the recommendation or mark it as unsourced judgment.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "items 1-4 of synthesis.md for claims or characterizations beyond their cited passage",
                           "found": "scope or characterization gaps in items 1, 2 and 3 (F3-F5); no other unsourced rationale"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "C",
     "location": "synthesis.md items 2 and 4",
     "scenario": "If Vaultline holds account data for closed accounts and the organisation is in GN-3 scope, setting extended keeps that data up to 365 days, contrary to the 45-day deletion in GN-3 3.4.",
     "fix": "State what retention_mode governs and reconcile it with GN-3 3.4 before recommending a value.",
     "answers": {"a": true, "b": false, "c": true, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 3: 'the deletion requirement'",
     "scenario": "GN-3 is a guidance note whose binding status is not stated; leads or customer-facing staff describe 45-day deletion as legally required.",
     "fix": "Write 'GN-3 paragraph 3.4 states'; call it a requirement only after confirming binding status.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Dropping 'Members' and 'customer-facing service' leads ops to apply 72-hour notice to internal outages or regardless of membership.",
     "fix": "Restore the full rule wording and state membership.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 2",
     "scenario": "Omitting GN-3 3.1 scope ('processors of account data') leads ops to apply or skip the rule without checking applicability.",
     "fix": "Add the 3.1 scope and the organisation's applicability.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "synthesis.md item 4",
     "suspicion": "retention_mode may cover account data subject to GN-3 3.4.",
     "unresolved_fact": "What data Vaultline retention_mode retains, and whether it includes closed-account data."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "synthesis.md items 1-3",
     "suspicion": "The cited rules may not apply to the organisation, or GN-3 may be advisory.",
     "unresolved_fact": "Northline membership, GN-3 processor status, and GN-3 binding status."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "sources/*",
     "suspicion": "The local copies retrieved on 2026-10-20 may differ from the live sources.",
     "unresolved_fact": "Whether each source URL currently matches its local copy."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Item 1 cites the wrong rule number.", "evidence": "The 72-hour notice text is Rule 14 in northline-rulebook.md."},
    {"id": "R2", "candidate": "Item 2's quote is paraphrased.", "evidence": "It matches GN-3 3.4 verbatim."},
    {"id": "R3", "candidate": "Item 4 misstates the setting values.", "evidence": "The source lists standard (30 days) and extended (365 days)."}
  ]
}
```