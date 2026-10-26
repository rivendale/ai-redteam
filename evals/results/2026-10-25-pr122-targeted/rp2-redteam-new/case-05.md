# Redteam report: outage, deletion and retention synthesis

**VERDICT: REWORK.** All four claims fail against the bundled sources: two cite the wrong locator, one quotes the regulator with words that do not appear in the source, and one tells operations to use a setting value that the console rejects.

**CONFIDENCE: medium.** The sources were supplied inline and every claim was checked word for word against them. Three things limit confidence:
- This was a single reviewer with no tools and no fresh subagent.
- The live source URLs were not opened, so later changes after the 2026-10-20 copies are not reflected.
- Whether the organisation is actually bound by each source is unknown.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, synthesis.md, sources/eastport-gn3.md, sources/northline-rulebook.md, sources/vaultline-retention.md.
- **Not seen:** the live pages at the three source URLs.
  - This matters only if a source changed after 2026-10-20.
- **Not seen:** any record of whether the organisation is a Northline member or an Eastport-regulated processor.
  - This matters because it decides whether each "obligation" applies at all.

**COVERAGE**
- **Scope:** the whole work (synthesis plus three sources).
- **Checked:**
  - all six files;
  - claims S1 to S4;
  - the title's framing of the contents as "obligations".
- **Not checked:**
  - live source URLs (no_tools);
  - organisational applicability (not_supplied).

**SEATS AND GATE**
- **Sensitivity:** none found. The material is public guidance and product documentation, with no personal or confidential data.
- **Seats:** only this local reviewer ran.
  - No subagent or cross-vendor seat was available in this session.
  - The work was not authored in this conversation, so anchoring risk is lower, but this is still a single-reviewer pass.

## CLAIMS TO EVIDENCE

| Claim | Location | Exact wording | Source passage | Status | Link |
|---|---|---|---|---|---|
| S1 | synthesis.md item 1 | "Rule 12 … requires 72 hours' notice before a planned outage" | northline-rulebook.md: "Rule 12. Reserved." / "Rule 14. Members give 72 hours' notice before a planned outage of a customer-facing service." | The obligation is verified, but at Rule 14. The locator is wrong, and the scope qualifier "customer-facing service" is dropped. | F2, F6 |
| S2 | synthesis.md item 2 | "account data must be erased promptly, and in any case within 30 days" | eastport-gn3.md 3.4: "Account data is deleted within 45 days of account closure." | The quoted text is not in the source. The figure is wrong (30 vs 45 days), and the trigger ("account closure") is omitted. | F1, F5 |
| S3 | synthesis.md item 3 | "the deletion requirement is paragraph 3.2 of GN-3" | 3.2 is "Backups. Backups are encrypted at rest."; deletion is 3.4. | Wrong locator. | F3 |
| S4a | synthesis.md item 4 | "set `retention_mode = strict`" | vaultline-retention.md: values are `off`, `standard` (30 days), `extended` (365 days); "an unknown value is rejected when the setting is saved." | `strict` does not exist and will be rejected. | F4 |
| S4b | synthesis.md item 4 | "to meet both rules" | Neither Northline Rule 14 (outage notice) nor GN-3 3.4 (deletion) mentions storage retention settings. | Unsupported inference. | F7, NV1 |
| S0 | synthesis.md title | "obligations" | GN-3 is a "Guidance Note" written descriptively ("is deleted"); Northline rules bind "Members". | Status is overstated. | F5, NV2 |

## FINDINGS, ordered by severity

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | synthesis.md item 2 | A fabricated quotation is attributed to the regulator. The source says "deleted within 45 days of account closure". The phrases "must", "erased promptly" and "30 days" appear nowhere in GN-3. | Operations leads build a 30-day deletion process and cite the "quote" to customers or the regulator. The regulator's own text contradicts it, and the organisation has misrepresented the regulator. Teams also bear needless cost against a 45-day window. | Replace with the verbatim GN-3 3.4 text: "Account data is deleted within 45 days of account closure." If 30 days is an internal choice, label it as policy, not regulation. | y/y/y/y |
| F2 | High | CONFIRMED | C | synthesis.md item 1 | The citation points to Rule 12, which reads "Reserved." The 72-hour notice rule is Rule 14. | A lead or auditor who checks Rule 12 finds nothing, and the obligation looks unsupported or gets dropped. Any external citation of "Rule 12" is wrong. | Change the citation to Rule 14 and quote it verbatim. | y/y/n/y |
| F3 | High | CONFIRMED | C | synthesis.md item 3 | The synthesis puts the deletion requirement at paragraph 3.2. Paragraph 3.2 is about backup encryption; deletion is in 3.4. | Controls get mapped to the wrong paragraph. A compliance matrix pairs deletion evidence with the backup-encryption clause, so the real 3.4 obligation has no control mapped to it. | Cite GN-3 paragraph 3.4. | y/y/n/y |
| F4 | High | CONFIRMED | C | synthesis.md item 4 | The instruction uses a value that does not exist. The source lists only `off`, `standard` and `extended`, and says an unknown value "is rejected when the setting is saved". | An engineer follows the instruction and the console rejects the save, so retention stays at whatever it was before. If the error is missed, nothing changes while the team believes the requirement is met. | Remove `strict`. Name a valid value only after deciding what the retention setting must achieve (see NV1). | y/y/n/y |
| F7 | High | CONFIRMED | C | synthesis.md item 4 | "To meet both rules" is unsupported. One rule is about outage notice, which no storage setting can satisfy. The other is about deleting account data, and the Vaultline source does not say that `retention_mode` deletes account data. | Leads believe a console toggle discharges both the 72-hour outage-notice duty and the deletion duty. No outage-notice process is built, and deletion is assumed rather than verified. | Drop the claim. List outage notice and deletion as separate controls, each with its own evidence. | y/y/n/y |
| F5 | Medium | CONFIRMED | C | synthesis.md title, item 2 | Guidance is presented as binding. GN-3 is a "Guidance Note" with descriptive wording, but the synthesis calls it an "obligation" with "must". | Leads treat guidance as mandatory, or argue about its force without knowing its status. | State each source's status: Northline rule (binding on members) or Eastport guidance note. | y/y/n/n |
| F6 | Low | CONFIRMED | C | synthesis.md item 1 | The scope qualifier is dropped. Rule 14 covers outages "of a customer-facing service" only. | The notice process is applied to internal services too, causing overhead and noise. | Restore the qualifier. | y/y/n/n |

**Sibling search for the High and Critical findings:** all four synthesis items were compared against their cited source text.
- **Wrong-locator root cause:** found at items 1 and 3, recorded separately as F2 and F3.
- **Text not supported by the source:** found at item 2 (F1) and item 4 (F4, F7).
- **Security:** none of these are security findings, and no trust boundary is crossed.

## NEEDS VALIDATION

- **NV1:** Does Vaultline `retention_mode` control deletion of account data, or only how long backups or versions are kept? This decides whether any value can help with GN-3 3.4.
  - If it is backup retention, `extended` (365 days) could keep closed-account data beyond 45 days.
  - The source does not say either way.
- **NV2:** Is the organisation a Northline member and an Eastport "processor of account data" (GN-3 3.1)? This decides whether each item applies at all.
- **NV3:** Do the live pages still match the 2026-10-20 copies?

## REFUTED

- **Candidate: "72 hours" is itself wrong.** Refuted. Rule 14 says exactly "72 hours' notice". Only the rule number is wrong.

## WHAT HOLDS UP

- The 72-hour planned-outage notice duty exists in the Northline Rule Book.
- Each item cites a source file that was supplied.
- The source copies are dated, which makes them auditable.

## UNVERIFIED CLAIMS

- That the source copies match the live URLs. Confirm by opening each URL and diffing it against the local copy.
- That any Vaultline setting affects compliance with GN-3 3.4. Confirm with Vaultline documentation on what `retention_mode` governs.

## QUESTIONS FOR THE AUTHOR

1. Where did the "erased promptly … within 30 days" wording come from? Was it a different document or version of GN-3?
2. What should the retention setting achieve, and against which rule?
3. Is 30 days an internal policy choice rather than a regulatory requirement?

## DECISION-MAKER SUMMARY

Do not send this synthesis to the operations leads yet. The Eastport quote is fabricated, two citations point to the wrong rule or paragraph, and the Vaultline instruction names a setting value the console rejects. If it goes out as written, leads will build controls against invented requirements and will believe a single console setting covers duties it cannot.

## OWNER SUMMARY

The summary we were asked to check does not match its sources. It quotes the regulator with words the regulator never wrote, uses the wrong deletion deadline, points readers to the wrong sections, and tells staff to pick a storage setting that does not exist. It needs to be corrected and checked again before anyone acts on it.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "live source URLs (3)", "status": "not_seen", "matters": true},
    {"item": "organisational applicability (membership / processor status)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public guidance and product documentation only"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "synthesis.md", "kind": "document"},
      {"unit": "sources/eastport-gn3.md", "kind": "document"},
      {"unit": "sources/northline-rulebook.md", "kind": "document"},
      {"unit": "sources/vaultline-retention.md", "kind": "document"},
      {"unit": "S1 outage notice rule citation", "kind": "claim"},
      {"unit": "S2 Eastport deletion quote", "kind": "claim"},
      {"unit": "S3 GN-3 paragraph locator", "kind": "claim"},
      {"unit": "S4 Vaultline retention_mode instruction", "kind": "claim"},
      {"unit": "S0 sources framed as obligations", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live source URLs", "reason": "no_tools"},
      {"unit": "organisational applicability of each source", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 2",
     "scenario": "Leads build a 30-day deletion process and cite a regulator quote that does not exist; GN-3 3.4 actually says 'deleted within 45 days of account closure', so any external citation misrepresents the regulator.",
     "fix": "Quote GN-3 3.4 verbatim; label any 30-day target as internal policy.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all four synthesis items against cited source text", "found": "unsupported text also at item 4 (F4, F7)"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "A reader checking Northline Rule 12 finds 'Reserved.'; the 72-hour notice rule is Rule 14, so the obligation appears unsupported or is cited wrongly externally.",
     "fix": "Cite Rule 14 and quote it verbatim.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every rule or paragraph locator in synthesis.md", "found": "item 3 also wrong (F3)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 3",
     "scenario": "Deletion controls are mapped to GN-3 3.2 (backup encryption), leaving the real deletion paragraph 3.4 without a mapped control.",
     "fix": "Cite GN-3 paragraph 3.4.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "every rule or paragraph locator in synthesis.md", "found": "item 1 also wrong (F2)"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "An engineer sets retention_mode = strict; Vaultline accepts only off/standard/extended and rejects unknown values on save, so the setting never changes while the team believes it is configured.",
     "fix": "Remove 'strict'; choose a valid value only after NV1 establishes what the setting governs.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all configuration instructions in synthesis.md", "found": "only item 4 gives a configuration instruction"}},
    {"id": "F7", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4 ('to meet both rules')",
     "scenario": "Leads treat one storage setting as satisfying both the 72-hour outage-notice rule and the deletion guidance, so no outage-notice process is built and deletion is assumed rather than verified.",
     "fix": "Delete the claim; list outage notice and deletion as separate controls with separate evidence.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "all cross-source inferences in synthesis.md", "found": "no other cross-source inference"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md title and item 2",
     "scenario": "A guidance note with descriptive wording is presented as a 'must' obligation, so leads misjudge its binding force.",
     "fix": "State each source's status (members' rule vs regulator guidance note).",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "The 'customer-facing service' qualifier from Rule 14 is dropped, so the notice process is applied to internal services as well.",
     "fix": "Restore the qualifier from Rule 14.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "NV1", "status": "needs_validation", "track": "C", "location": "synthesis.md item 4",
     "suspicion": "retention_mode may govern backup or version retention rather than account-data deletion; 'extended' could keep closed-account data beyond 45 days.",
     "unresolved_fact": "What data Vaultline retention_mode applies to."},
    {"id": "NV2", "status": "needs_validation", "track": "C", "location": "synthesis.md title",
     "suspicion": "The listed obligations may not apply to the organisation.",
     "unresolved_fact": "Whether the organisation is a Northline member and an Eastport processor of account data (GN-3 3.1)."},
    {"id": "NV3", "status": "needs_validation", "track": "C", "location": "sources/*",
     "suspicion": "The source copies may be stale.",
     "unresolved_fact": "Whether the live pages match the 2026-10-20 copies."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The 72-hour figure is wrong.",
     "evidence": "Northline Rule 14 reads '72 hours' notice before a planned outage'."}
  ]
}
```