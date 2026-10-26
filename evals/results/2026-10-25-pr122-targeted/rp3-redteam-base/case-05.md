VERDICT: **REWORK.** All four statements in the synthesis disagree with the sources it cites: two rule or paragraph numbers are wrong, one quote is fabricated, and the one configuration step names a setting value the product rejects.

CONFIDENCE: **high** for the text comparisons, since each one ties an exact synthesis line to an exact source line. It is limited by three things:
- This was a same-context review with no tools; no subagent or other reviewer was available. Re-run it in a fresh session for anything high-stakes.
- I could not check that the local source copies match the live URLs.
- Nothing tells me whether these rules apply to the organization.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `synthesis.md`, `sources/northline-rulebook.md`, `sources/eastport-gn3.md`, `sources/vaultline-retention.md`.
- **Not seen:** the live pages at the three source URLs, which I cannot open. This matters only if the local copies are stale or edited; they were retrieved 2026-10-20, five days ago.
- **Not seen:** anything showing whether the organization is a "processor of account data" under GN-3 3.1, or a Northline member. This matters because it decides whether either rule binds the organization at all.

COVERAGE: whole work. Checked: all four synthesis items, all three source files, and the request and context. Not checked: the live sources (no tools); whether the rules apply (not supplied).

SEATS AND GATE: one local same-context reviewer ran. No cross-vendor seats were requested. The material is not sensitive: it is public-style guidance and product documentation, with no personal data or credentials.

## CLAIMS TO EVIDENCE

| Label | Synthesis location and wording | Source passage | State | Link |
|---|---|---|---|---|
| C1 | synthesis.md item 1: "Rule 12 … requires 72 hours' notice before a planned outage" | northline-rulebook.md: "Rule 12. Reserved." and "Rule 14. Members give 72 hours' notice before a planned outage of a customer-facing service." | The content matches Rule 14. The citation is wrong. The scope ("customer-facing service") is dropped. | F3, F6 |
| C2 | item 2: "account data must be erased promptly, and in any case within 30 days" (presented as a quote) | eastport-gn3.md 3.4: "Account data is deleted within 45 days of account closure." | The quoted text does not exist in the source. The number differs (30 vs 45 days). The trigger ("of account closure") is missing. | F1 |
| C3 | item 3: "the deletion requirement is paragraph 3.2 of GN-3" | 3.2: "Backups are encrypted at rest." 3.4 is the deletion paragraph. | Wrong paragraph. | F2 |
| C4 | item 4: "set `retention_mode = strict` … to meet both rules" | vaultline-retention.md: accepts `off`, `standard` (30 days), `extended` (365 days). "There is no other value; an unknown value is rejected when the setting is saved." | `strict` is invalid. "Both rules" is unsupported, because the Northline rule concerns outage notice, not retention. | F4, F5 |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED | C | synthesis.md item 2 | A fabricated quote is attributed to the regulator. GN-3 3.4 says "deleted within 45 days of account closure". The words "must", "erased promptly" and "30 days" appear nowhere in GN-3. | Operations leads cite a regulator quote that does not exist in a compliance record or customer reply. They also build processes on a 30-day deadline with no stated trigger, and drive the retention choice in item 4 from it. | Replace it with the verbatim 3.4 text and its 45-day, from-account-closure trigger. Do not present paraphrase as a quote. | Y/Y/Y/Y |
| F2 | High | CONFIRMED | C | synthesis.md item 3 | GN-3 3.2 is the backup-encryption paragraph. The deletion paragraph is 3.4. | Anyone checking "3.2" finds an unrelated rule, and the deletion obligation is mis-cited in internal controls documents. | Change the citation to GN-3 3.4. | Y/Y/N/Y |
| F3 | High | CONFIRMED | C | synthesis.md item 1 | Rule 12 is "Reserved". The 72-hour notice is Rule 14. | Policies or audit evidence cite a reserved rule, and an auditor or the Council rejects the citation. | Change the citation to Rule 14. | Y/Y/N/Y |
| F4 | High | CONFIRMED | C | synthesis.md item 4 | `strict` is not a valid `retention_mode`. The source says unknown values are rejected on save. | Operations leads try to apply the one actionable instruction and the console rejects it. The fix is then improvised without guidance. Because the setting fails loudly, it does not silently misconfigure. | Name a valid value, and justify it against the 45-day GN-3 deadline (see S2). | Y/Y/Y/Y |
| F5 | Medium | CONFIRMED | C | synthesis.md item 4: "to meet both rules" | A storage retention setting has no bearing on the Northline outage-notice rule. The claim that it meets "both rules" has no support in any source. | Leads believe outage-notice compliance is handled by a storage setting and build no notice process. | Remove "both rules". State that outage notice needs a separate process. | Y/Y/N/N |
| F6 | Low | CONFIRMED | C | synthesis.md item 1 | The scope "of a customer-facing service" is dropped. | The rule gets applied to internal-only outages, causing unnecessary notices. | Restore the qualifier. | Y/Y/N/N |

**Siblings and boundaries** (for F1–F4): I compared every citation and quote in all four items against its source.
- Citation-number errors appear in two places, F2 and F3, recorded separately.
- The one quote (F1) is fabricated.
- The one product value (F4) is invalid.
- No other citations exist.
- None of these is a security finding, so there is no trust boundary to report.

## NEEDS VALIDATION
- **S1:** Whether GN-3 3.4 is binding or descriptive. It reads "is deleted", not "must", and it is a guidance note. Settled by the regulator's statement of GN-3's legal status.
- **S2:** Whether `retention_mode` retains data for at least N days or deletes it after N days. Settled by Vaultline's semantics for the setting. Under the second meaning, `standard` (30 days) would fall within 45 days, while `extended` (365 days) would breach the 45-day limit.
- **S3:** Whether the organization is in scope: a "processor of account data" (GN-3 3.1) and a Northline member. Settled by the organization's registration or membership records.
- **S4:** Whether the local copies match the live sources today. Settled by fetching the URLs and diffing them.

## REFUTED
- **"The 72-hour figure itself is wrong":** refuted. Rule 14 says 72 hours; only the rule number is wrong.

## WHAT HOLDS UP
- The 72-hour planned-outage notice obligation exists in the Northline Rule Book.
- GN-3 does contain a deletion deadline.
- Vaultline does have a `retention_mode` setting.
- Each item cites a source file, which made it fully checkable.

## UNVERIFIED CLAIMS
- That the local copies reflect the current live sources: fetch and diff them.
- That retention settings can satisfy a deletion obligation at all: confirm the Vaultline semantics (S2).

## QUESTIONS FOR THE AUTHOR
1. Where did the "erased promptly … within 30 days" wording come from? Is there another GN-3 version or a different document?
2. What did you intend by `strict`, and what retention behaviour is needed?
3. Is the organization in scope for GN-3 and a Northline member?

## DECISION-MAKER SUMMARY
Do not send the synthesis as is. Every item has a confirmed error, including a fabricated regulator quote and a console setting that will be rejected. If it goes out anyway, leads will cite non-existent rule text and wrong rule numbers, and will be unable to apply the retention step.

## OWNER SUMMARY
The summary does not match its own sources. One quote from the regulator is made up and gives the wrong deadline, two rule references point at the wrong rules, and the recommended storage setting does not exist. It needs to be corrected against the source documents before anyone acts on it.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "synthesis.md", "status": "seen", "matters": true},
    {"item": "sources/northline-rulebook.md", "status": "seen", "matters": true},
    {"item": "sources/eastport-gn3.md", "status": "seen", "matters": true},
    {"item": "sources/vaultline-retention.md", "status": "seen", "matters": true},
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "live source URLs", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "synthesis.md", "kind": "document"},
      {"unit": "sources/northline-rulebook.md", "kind": "document"},
      {"unit": "sources/eastport-gn3.md", "kind": "document"},
      {"unit": "sources/vaultline-retention.md", "kind": "document"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "C1 outage notice rule", "kind": "claim"},
      {"unit": "C2 deletion quote", "kind": "claim"},
      {"unit": "C3 deletion paragraph", "kind": "claim"},
      {"unit": "C4 retention_mode strict", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live source URLs", "reason": "no_tools"},
      {"unit": "organization in scope of GN-3 / Northline", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 2",
     "scenario": "Leads cite a regulator quote ('erased promptly ... within 30 days') that does not exist; GN-3 3.4 says 'deleted within 45 days of account closure', so compliance records misstate the obligation and its trigger.",
     "fix": "Replace with the verbatim GN-3 3.4 text (45 days from account closure); never present paraphrase as a quote.",
     "answers": {"a": true, "b": true, "c": true, "d": true}, "security": false,
     "siblings_searched": {"searched": "every quote and citation in synthesis items 1-4 against sources", "found": "no other quotes; citation errors recorded as F2, F3"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 3",
     "scenario": "The deletion requirement is cited as GN-3 3.2, which is the backup-encryption paragraph; reviewers checking the citation find an unrelated rule.",
     "fix": "Cite GN-3 3.4.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "all rule/paragraph numbers in synthesis", "found": "F3 (Rule 12 vs Rule 14)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "The 72-hour outage notice is cited as Northline Rule 12, which is 'Reserved'; policies cite a non-existent rule.",
     "fix": "Cite Rule 14.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "all rule/paragraph numbers in synthesis", "found": "F2 (GN-3 3.2 vs 3.4)"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "Leads set retention_mode = strict; Vaultline accepts only off, standard, extended and rejects unknown values on save, so the only actionable step fails.",
     "fix": "Name a valid value chosen against the 45-day GN-3 deadline after confirming retention semantics.",
     "answers": {"a": true, "b": true, "c": true, "d": true}, "security": false,
     "siblings_searched": {"searched": "all product settings/values named in synthesis", "found": "none other"}},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4 ('to meet both rules')",
     "scenario": "Leads assume a storage retention setting satisfies the Northline outage-notice rule and build no notice process.",
     "fix": "Remove 'both rules'; state outage notice requires a separate process.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Dropping 'of a customer-facing service' leads to the rule being applied to internal-only outages.",
     "fix": "Restore the qualifier from Rule 14.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/eastport-gn3.md 3.4",
     "suspicion": "GN-3 3.4 is descriptive ('is deleted') guidance, possibly not a binding requirement.",
     "unresolved_fact": "The regulator's statement of GN-3's legal status."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/vaultline-retention.md",
     "suspicion": "Retention mode may keep data at least N days rather than delete after N days; 'extended' (365) would breach 45 days.",
     "unresolved_fact": "Vaultline's documented semantics for retention_mode."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "sources/eastport-gn3.md 3.1; northline-rulebook.md",
     "suspicion": "The organization may not be in scope of GN-3 or a Northline member.",
     "unresolved_fact": "The organization's registration and membership status."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "sources/* (retrieved 2026-10-20)",
     "suspicion": "Local copies may differ from live sources.",
     "unresolved_fact": "A diff of each local copy against its live URL."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The 72-hour figure is wrong.", "evidence": "Rule 14 states 72 hours' notice; only the rule number is wrong."}
  ]
}
```