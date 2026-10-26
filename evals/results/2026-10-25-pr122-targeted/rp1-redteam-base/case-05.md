# Redteam report: research synthesis on outage notice, deletion and retention

**VERDICT: REWORK.** All four claims misstate their own supplied sources: one fabricated quote, two wrong citations, and a configuration value the vendor says will be rejected.

**CONFIDENCE: high** for the confirmed findings, because each one rests on an exact quote from the source copies supplied inline. Three things limit it:
- I had no tools, so I could not open the live URLs, check that the copies are current, or scan for hidden characters.
- This is a single review with no independent second reviewer.
- The work was not written in this conversation, so I am not anchored on it.

**INPUTS LEDGER**
- **Seen:**
  - `request.md`
  - `context.md`
  - `synthesis.md`
  - `sources/northline-rulebook.md`
  - `sources/eastport-gn3.md`
  - `sources/vaultline-retention.md`
- **Not seen:** the live versions of the three source URLs (copies dated 2026-10-20, five days before this review).
  - This matters only if a source changed after 2026-10-20. It does not affect the findings, which compare the synthesis to the copies it cites.
- **Not seen:** what Vaultline's "retention" period actually governs.
  - This matters for working out the correct setting (see S1).

**COVERAGE**
- **Scope:** the whole work, which is four claims and three sources.
- **Checked:** every claim (C1 to C4) against its cited source, every rule and paragraph in each source, and the one quote in the synthesis.
- **Not checked:**
  - Live sources: no tools.
  - Hidden or look-alike characters: no tools; I reviewed the visible text only.
- **Prompt-injection check:** the work contains no text addressed to a reviewer.

**SEATS AND GATE:** I was the only reviewer, with no tools and no subagent or cross-vendor seats. The sensitivity gate passed: the work contains no personal or confidential data.

## Claims to evidence

| Claim | Location | Synthesis says | Source actually says | Status |
|---|---|---|---|---|
| C1 | synthesis.md item 1 | "Rule 12 … requires 72 hours' notice" | Rule 12: "Reserved." Rule 14: "Members give 72 hours' notice before a planned outage of a customer-facing service." | Substance matches Rule 14; citation wrong → F3, F5 |
| C2 | item 2 | Quote: "account data must be erased promptly, and in any case within 30 days" | 3.4: "Account data is deleted within 45 days of account closure." | Quote is not in the source; number wrong (30 vs 45 days); trigger "of account closure" missing → F1 |
| C3 | item 3 | Deletion requirement is paragraph 3.2 | 3.2 covers backups; deletion is 3.4 | Wrong → F2 |
| C4a | item 4 | Set `retention_mode = strict` | Valid values are only `off`, `standard` (30d) and `extended` (365d); "an unknown value is rejected when the setting is saved" | Wrong → F4 |
| C4b | item 4 | The setting "meet[s] both rules" | Neither rule mentions storage retention; the outage-notice rule cannot be met by a storage setting | Not supported → F6; correct value is an open question → S1 |

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | synthesis.md item 2 | The quote is fabricated. GN-3 contains neither "promptly" nor "erased … within 30 days". The real text is 3.4, "deleted within 45 days of account closure". | Leads quote a regulator to staff, auditors or customers with words it never wrote. Deadlines get set to the wrong figure and lose the "account closure" trigger. | Replace with the verbatim 3.4 text, cited as GN-3 ¶3.4. | y/y/y/y |
| F2 | High | CONFIRMED | C | item 3 | Paragraph 3.2 is "Backups … encrypted at rest". The deletion text is 3.4. | Compliance records or audit responses cite ¶3.2 for deletion, and a reviewer finds the reference wrong. | Change to ¶3.4. | y/y/n/y |
| F3 | High | CONFIRMED | C | item 1 | Rule 12 is "Reserved". The 72-hour notice is Rule 14. | Outage procedures or a regulator response cite Rule 12, which says nothing. | Change to Rule 14. | y/y/n/y |
| F4 | High | CONFIRMED | C | item 4 | `strict` is not a valid value. The source says there is "no other value" and unknown values are rejected on save. | An operator follows the instruction, the console rejects it, and the operator guesses a different value with no guidance. | Remove `strict`. State the valid values and choose one only after S1 is settled. | y/y/n/y |
| F5 | Low | CONFIRMED | C | item 1 | Drops the qualifiers "Members" and "of a customer-facing service". | Teams apply the rule more broadly than required; this costs effort but harms no one. | Restore the qualifiers. | y/y/n/n |
| F6 | Medium | CONFIRMED | C | item 4 | Claims a storage retention setting satisfies "both rules", but one of the rules is the outage-notice rule, which has nothing to do with retention. | Leads believe a console change covers outage notice and drop the notice process. This is unlikely, but the claim is false as written. | Say retention relates at most to the GN-3 deletion rule. | y/y/n/n |

F6 was considered for High but downgraded: realistic misuse (d) is unlikely.

**Severity questions:** (a) concrete failure scenario, (b) CONFIRMED rather than probable, (c) breaks the request or creates legal, regulatory or customer harm, (d) likely under realistic use.

**Sibling search:**
- For F1, I checked for other quotes: this is the only one.
- For F2 and F3, I checked every citation: both wrong citations are listed, and no others exist.
- For F4, I checked for other configuration values: this is the only one.

None of the findings is a security finding.

## Needs validation

- **S1: which `retention_mode` value, if any, meets GN-3 ¶3.4?** This depends on what the retention period governs: how long deleted data or backups are kept, or something else. If it governs deleted data, `extended` (365 days) would break the 45-day rule. `standard` (30 days) might comply, but not if other copies exist, such as the backups in ¶3.2.
- **S2: is GN-3 binding?** It is a "Guidance Note" written descriptively ("is deleted"). Whether ¶3.4 is a binding obligation or a description of expected practice depends on the Eastport regulator's legal framework. That framework was not supplied.
- **S3: are the copies current?** The source copies are dated 2026-10-20. They need comparing with the live URLs before the synthesis is sent out.

## Refuted

- **Candidate:** the 72-hour figure in item 1 is wrong.
  - **Refuted:** Rule 14 states 72 hours. Only the rule number is wrong (F3).

## What holds up

- The 72-hour planned-outage notice obligation exists (Rule 14).
- A deletion deadline exists in GN-3 (¶3.4).
- Vaultline retention can be configured.

## Unverified claims

None of the claims depends on anything outside the supplied copies, except the open questions S1 to S3, which list what would settle them.

## Questions for the author

1. Where did the "promptly … within 30 days" wording come from? Is there another source that was not supplied?
2. What does Vaultline's retention period apply to?

## Decision-maker summary

Do not send this synthesis. Every one of its four claims misstates its source, including a fabricated regulator quote and a deadline of 30 days instead of 45. Leads acting on it would cite the wrong rules and attempt a console setting that will be rejected.

## Owner summary

The research summary gets its sources wrong in every point it makes: it invents a quote, cites the wrong rule and paragraph numbers, and recommends a setting that doesn't exist. It needs to be corrected against the source documents before anyone uses it. Someone also needs to confirm which storage setting actually meets the 45-day deletion rule.

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
    {"item": "live source URLs", "status": "not_seen", "matters": false},
    {"item": "Vaultline retention semantics", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"}, {"unit": "context.md", "kind": "document"},
      {"unit": "synthesis.md", "kind": "file"}, {"unit": "sources/northline-rulebook.md", "kind": "file"},
      {"unit": "sources/eastport-gn3.md", "kind": "file"}, {"unit": "sources/vaultline-retention.md", "kind": "file"},
      {"unit": "C1", "kind": "claim"}, {"unit": "C2", "kind": "claim"}, {"unit": "C3", "kind": "claim"},
      {"unit": "C4a", "kind": "claim"}, {"unit": "C4b", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live versions of source URLs", "reason": "no_tools"},
      {"unit": "hidden/look-alike character scan", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 2",
     "scenario": "Leads quote GN-3 as requiring erasure 'promptly ... within 30 days'; the source says 'deleted within 45 days of account closure', so a fabricated regulator quote and wrong deadline enter procedures and external communications.",
     "fix": "Replace with the verbatim GN-3 ¶3.4 text and cite ¶3.4.",
     "answers": {"a": true, "b": true, "c": true, "d": true}, "security": false,
     "siblings_searched": {"searched": "all quotations in synthesis.md", "found": "no other quotations"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 3",
     "scenario": "Deletion requirement cited as GN-3 ¶3.2, which covers backup encryption; an audit response citing it is wrong.",
     "fix": "Cite GN-3 ¶3.4.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "every rule/paragraph citation in synthesis.md", "found": "item 1 also miscited (F3)"}},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Outage-notice obligation cited as Northline Rule 12, which is 'Reserved'; procedures citing it point at an empty rule.",
     "fix": "Cite Rule 14.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "every rule/paragraph citation in synthesis.md", "found": "item 3 also miscited (F2)"}},
    {"id": "F4", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "Operator sets retention_mode = strict; Vaultline rejects unknown values on save, leaving the retention configuration unaddressed.",
     "fix": "Remove 'strict'; list valid values off/standard/extended and choose one once S1 is resolved.",
     "answers": {"a": true, "b": true, "c": false, "d": true}, "security": false,
     "siblings_searched": {"searched": "all configuration values in synthesis.md", "found": "no others"}},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "Claims a storage retention setting meets 'both rules', but the Northline rule concerns outage notice; leads could believe notice is handled by a console setting.",
     "fix": "Limit the claim to GN-3 ¶3.4 deletion, if supported.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Omits 'Members' and 'customer-facing service' qualifiers from Rule 14, causing over-broad application.",
     "fix": "Restore the qualifiers.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "synthesis.md item 4",
     "suspicion": "Which retention_mode value, if any, satisfies the 45-day deletion rule; 'extended' (365 days) may violate it.",
     "unresolved_fact": "What Vaultline's retention period applies to (deleted data, backups, or other)."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "sources/eastport-gn3.md ¶3.4",
     "suspicion": "GN-3 is descriptive guidance; the synthesis presents it as a binding 'must'.",
     "unresolved_fact": "Whether GN-3 ¶3.4 is binding under Eastport's legal framework."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "all sources",
     "suspicion": "Source copies dated 2026-10-20 may be stale.",
     "unresolved_fact": "Whether the live URLs match the local copies as of review date."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "The 72-hour notice figure in item 1 is wrong.",
     "evidence": "Northline Rule 14 states 72 hours' notice; only the rule number is wrong (F3)."}
  ]
}
```