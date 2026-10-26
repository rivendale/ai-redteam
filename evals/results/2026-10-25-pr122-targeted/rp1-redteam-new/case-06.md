# Redteam report: research synthesis on outage notice, deletion and retention

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available in this session. I did not write the work, but I checked everything by hand against the source text supplied inline.

**VERDICT: SHIP WITH FIXES.** Claims 1–3 match their sources apart from wording. Claim 4's reason for choosing a retention setting has no support in its cited source, and it may conflict with claim 2. Claim 4 must be supported or removed before the operations leads act on it.

**CONFIDENCE: medium.** Limits:
- Same-context review with no tools.
- I could not compare the local source copies with the live URLs.
- Nothing says whether the organisation is a Northline member or an Eastport "processor of account data", or what data Vaultline holds.

**INPUTS LEDGER**
- **Seen:**
  - `request.md`
  - `context.md`
  - `synthesis.md`
  - `sources/northline-rulebook.md`
  - `sources/eastport-gn3.md`
  - `sources/vaultline-retention.md` (all three source copies are dated 2026-10-20)
- **Not seen:**
  - The live pages at the three source URLs (no network). This matters little: the copies are five days old and context says they are the cited sources.
  - Any record of what data Vaultline stores, or which records "are still needed". **This matters**, because claim 4 depends on it.
  - Whether the organisation is a Northline member or an Eastport processor. This matters for whether the rules apply at all.
- **Embedded instructions:** none found in the work.

**COVERAGE**
- **Scope:** the whole synthesis (4 claims) against all 3 supplied sources.
- **Checked:**
  - all 5 files above
  - claims C1–C4
  - assumptions about applicability and about what the retention setting means
- **Not checked:**
  - live source URLs (no_tools)
  - hidden or look-alike characters in the files (no_tools; this needs a byte-level scan)

**SEATS AND GATE**
- Seats: local same-context reviewer only; no subagent or other-vendor seats were available.
- Sensitivity gate: passed. There is no personal, client or credential data.

## Claims to evidence

| Claim | Location | Source / derivation | Status | Link |
|---|---|---|---|---|
| C1: Rule 14 requires 72 hours' notice before a planned outage | synthesis.md item 1 | northline-rulebook.md Rule 14: "Members give 72 hours' notice before a planned outage of a customer-facing service." | Rule number, attribution and 72 h are verified. The scope words "Members" and "customer-facing service" are dropped. | F3, S2 |
| C2: Quote "Account data is deleted within 45 days of account closure" | item 2 | eastport-gn3.md 3.4 | The quote is verified verbatim. The source is labelled "Guidance Note", and the synthesis's "guidance" label is correct. | — |
| C3: The deletion requirement is paragraph 3.4 of GN-3 | item 3 | eastport-gn3.md 3.4 | The paragraph number is verified. Calling it a "requirement" is not supported: the document is a Guidance Note and 3.4 is written descriptively ("is deleted"), not as "must". 3.1 limits its scope to "processors of account data". | F2 |
| C4a: `extended` is a valid value, and `standard` = 30 days | item 4 | vaultline-retention.md | Verified. | — |
| C4b: `standard` "would delete records still needed", so set `extended` | item 4 | vaultline-retention.md contains only the list of values and the rejection rule | UNVERIFIED. The cited source does not say this. | F1, S1 |

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | synthesis.md item 4, "`standard` (30 days) would delete records still needed" | The recommendation and its reason are credited to `sources/vaultline-retention.md`. That source lists only the three values and says unknown values are rejected. It says nothing about which records are needed or what anyone should choose. | The operations leads act on the synthesis and set `extended` (365 days) on the strength of a citation that does not support it. If Vaultline holds account data, records from closed accounts are kept up to 365 days. That contradicts item 2's 45-day deletion statement, which the synthesis never reconciles with item 4. | Either cite the source that shows which records must outlive 30 days, or remove the recommendation. In both cases, state how `extended` fits with GN-3 3.4's 45 days. `standard` (30 days) fits inside 45 days; `extended` does not. | a Y / b Y / c N / d Y |
| F2 | Medium | CONFIRMED | C | synthesis.md item 3, "the deletion requirement" (the title's "obligations" repeats the framing) | GN-3 is a Guidance Note. Paragraph 3.4 describes a practice ("is deleted") and does not set a mandatory rule. The synthesis upgrades it to a "requirement". It also leaves out 3.1's scope ("applies to processors of account data"). | The operations leads, or anyone they forward this to, cite the 45-day deletion as a regulatory obligation. That misstates the regulator's position, and the organisation may not even be in scope. | Reword item 3 as "GN-3 ¶3.4 (guidance) states…". Add the scope limit from ¶3.1. Change "obligations" in the title to "obligations and guidance". | a Y / b Y / c N / d N |
| F3 | Low | CONFIRMED | C | synthesis.md item 1 | The synthesis drops two qualifiers from Rule 14: it applies to "Members", and only to outages "of a customer-facing service". | The operations leads apply 72-hour notice to internal-only maintenance. That is over-compliance and harms no one, but it misstates the rule. | Quote Rule 14 in full. | a Y / b Y / c N / d N |

Severity questions: (a) concrete failure scenario; (b) confirmed by evidence; (c) breaks the request, loses data, breaches security or causes harm; (d) likely in realistic use.

**F1 confirm-or-refute round.** I argued the strongest defence: the author may have known which records are needed from other context. Even so, the claim is attributed to a source that does not contain it, so as a fact-check finding it stands.
- **Sibling search:** I checked items 1–3 for other reasons or recommendations not found in their sources. None found; those items are restatements.
- **Security:** not a security finding, so no trust boundary applies.

## Needs validation (no severity)

- **S1:** Does Vaultline store Eastport-scoped account data, and does `retention_mode` control how long live records or backups are kept? This settles whether `extended` actually conflicts with GN-3 3.4.
- **S2:** Is the organisation a Northline member, and is it an Eastport "processor of account data"? This settles whether either source applies at all.
- **S3:** Do the live source URLs match the 2026-10-20 copies?

## Refuted

- **C3 paragraph number wrong:** refuted. ¶3.4 is the deletion paragraph.
- **C2 quote altered:** refuted. It is verbatim.
- **C4 value invented:** refuted. `extended` and 365 days are in the source.

## What holds up

- The rule and paragraph numbers are correct.
- The 72-hour, 45-day, 30-day and 365-day figures are correct.
- The Eastport quote is verbatim.
- Each claim cites a source that exists and was supplied.

## Unverified claims

- C4b, that `standard` would delete records still needed. This needs a records inventory or a business or legal retention requirement.

## Questions for the author

1. What source says records must be kept longer than 30 days?
2. Does Vaultline hold account data covered by GN-3?
3. Is the organisation a Northline member or an Eastport processor?

## Decision-maker summary

Fix the wording in items 1–3, and either support or remove the retention recommendation in item 4 before circulating. If it goes out as is, the operations leads may switch to 365-day retention on an unsupported reason. That could keep closed-account data well past the 45 days stated in the same document.

## Owner summary

Most of the summary accurately reflects its sources. Its advice to keep stored data for a year is not backed by the document it cites, and it may contradict the 45-day deletion point made earlier in the same summary. Two other points need small wording corrections so that guidance is not presented as a firm rule.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "synthesis.md", "status": "seen", "matters": true},
    {"item": "sources/northline-rulebook.md", "status": "seen", "matters": true},
    {"item": "sources/eastport-gn3.md", "status": "seen", "matters": true},
    {"item": "sources/vaultline-retention.md", "status": "seen", "matters": true},
    {"item": "live source URLs", "status": "not_seen", "matters": false},
    {"item": "inventory of data stored in Vaultline / records still needed", "status": "not_seen", "matters": true},
    {"item": "organisation's Northline membership and Eastport processor status", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "synthesis.md", "kind": "document"},
      {"unit": "sources/northline-rulebook.md", "kind": "document"},
      {"unit": "sources/eastport-gn3.md", "kind": "document"},
      {"unit": "sources/vaultline-retention.md", "kind": "document"},
      {"unit": "C1 Rule 14 72-hour notice", "kind": "claim"},
      {"unit": "C2 GN-3 deletion quote", "kind": "claim"},
      {"unit": "C3 GN-3 paragraph 3.4 as requirement", "kind": "claim"},
      {"unit": "C4 retention_mode extended recommendation", "kind": "claim"},
      {"unit": "organisation is in scope of both sources", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live source URLs", "reason": "no_tools"},
      {"unit": "hidden or look-alike characters in files", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "Operations leads set retention_mode = extended (365 days) on the claim that standard 'would delete records still needed', which the cited Vaultline source does not state; if Vaultline holds account data, closed-account data is kept up to 365 days, contrary to item 2's 45-day deletion statement.",
     "fix": "Cite a source establishing which records must outlive 30 days, or remove the recommendation; reconcile the chosen setting with GN-3 3.4 (standard fits within 45 days, extended does not).",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "synthesis.md items 1-3 for rationale or recommendations not present in their cited sources",
                           "found": "none; items 1-3 restate their sources"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 3",
     "scenario": "GN-3 is a Guidance Note and 3.4 is descriptive, but the synthesis calls it a 'requirement' and omits the 3.1 scope; readers cite it as a binding regulatory obligation, possibly where the organisation is not in scope.",
     "fix": "Reword as 'GN-3 para 3.4 (guidance) states...', add the 3.1 scope ('processors of account data'), and change 'obligations' in the title to 'obligations and guidance'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Rule 14 applies to Members and to planned outages 'of a customer-facing service'; the synthesis drops both qualifiers, so 72-hour notice is applied to internal-only maintenance.",
     "fix": "Quote Rule 14 in full, including 'Members' and 'customer-facing service'.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "synthesis.md items 2 and 4",
     "suspicion": "The 365-day extended retention conflicts with GN-3 3.4's 45-day deletion.",
     "unresolved_fact": "Whether Vaultline stores GN-3-scoped account data and what retention_mode governs (live records or backups)."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "synthesis.md items 1-3",
     "suspicion": "The Northline rule and Eastport guidance may not apply to the organisation.",
     "unresolved_fact": "Whether the organisation is a Northline member and an Eastport processor of account data."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "sources/*.md headers",
     "suspicion": "Local copies may differ from the live sources.",
     "unresolved_fact": "Whether the live URLs match the 2026-10-20 copies."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Paragraph number 3.4 is wrong.", "evidence": "eastport-gn3.md: '3.4 Deletion. Account data is deleted within 45 days of account closure.'"},
    {"id": "R2", "candidate": "The Eastport quote is altered.", "evidence": "synthesis item 2 matches 3.4 verbatim."},
    {"id": "R3", "candidate": "The 'extended' value or its 365-day period is invented.", "evidence": "vaultline-retention.md lists 'extended' (365 days)."}
  ]
}
```