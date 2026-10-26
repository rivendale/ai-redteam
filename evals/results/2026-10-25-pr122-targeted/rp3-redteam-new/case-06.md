# Redteam review: research synthesis (Track C)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so nothing was opened or run beyond the text supplied here.

**VERDICT: SHIP WITH FIXES.** Three of the four items match their sources. Item 4's reason for choosing `extended` retention does not appear in its cited source, and the synthesis overstates the legal status and scope of items 1–3.

**CONFIDENCE: medium.** Limits:
- This is a same-context review.
- The local source copies could not be compared with the live URLs.
- Nothing establishes whether the organisation is a Northline member, an Eastport "processor", or stores account data in Vaultline.

## INPUTS LEDGER

**Seen:**
- request.md
- context.md
- synthesis.md
- sources/northline-rulebook.md
- sources/eastport-gn3.md
- sources/vaultline-retention.md

All are short and were read in full.

**Not seen:**
- **Live versions of the three source URLs** (`*.example.test`, no network). This matters a little: the copies are dated 2026-10-20, five days ago, so drift is unlikely but not ruled out.
- **The organisation's membership, processor status and data map.** This matters: whether items 1–4 apply at all depends on these facts.
- **Northline Rule 13.** It is missing from the copy, which jumps from Rule 12 to Rule 14. It does not matter for any claim unless Rule 13 modifies Rule 14.

## COVERAGE

- **Scope:** the whole synthesis plus all three cited sources.
- **Checked:**
  - Synthesis title and items 1–4.
  - Each source in full: GN-3 §3.1–3.4, Rule Book Rules 11/12/14, Vaultline retention text.
  - The quote at item 2 against GN-3 §3.4, character by character.
  - The paragraph number at item 3.
  - The value names and day counts at item 4.
- **Not checked:**
  - Live sources (no tools).
  - Whether each rule applies to the organisation (not supplied).

## SEATS AND GATE

- Only a local same-context review ran.
- The sensitivity gate was negative: the material is public-style regulatory and vendor text with no personal or confidential data.
- No cross-vendor seats ran, because none were requested and no tools were available.

## CLAIMS TO EVIDENCE

| Claim | Location / wording | Source | Status |
|---|---|---|---|
| C1 | Item 1: "Rule 14 … requires 72 hours' notice before a planned outage" | Rule Book Rule 14: "Members give 72 hours' notice before a planned outage of a customer-facing service." | 72 hours and rule number are **verified**. Scope ("Members", "customer-facing service") is dropped → F3. Membership is unresolved → S1. |
| C2 | Item 2: quote "Account data is deleted within 45 days of account closure" | GN-3 §3.4, same wording | **Verified verbatim.** |
| C3 | Item 3: "the deletion requirement is paragraph 3.4 of GN-3" | GN-3 §3.4 | Paragraph is **verified**. Calling it a "requirement" is not supported, because the source is a *Guidance Note* → F2. |
| C4a | Item 4: `extended` value exists; `standard` = 30 days | Vaultline: `off`, `standard` (30 days), `extended` (365 days) | **Verified.** |
| C4b | Item 4: "`standard` (30 days) would delete records still needed" | Not in the source. The source does not say what happens at the end of the period or which records are needed. | **UNVERIFIED** interpretation → F1 |
| C5 | Title: "obligations" for all four items | Item 4 is a vendor setting; item 2/3 is guidance | Overstated → F2 |

The "not in source" result for C4b has a positive control. The same read of the two-line Vaultline file did find `standard`, `30 days`, `extended` and `365 days`, so the absence is real and not a missed read.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | synthesis.md item 4 | The reason given for `extended` ("would delete records still needed") is cited to a source that says nothing about deletion behaviour or which records are needed. The source also does not say whether the period keeps data for N days or deletes after N days. | Operations leads set `extended` (365 days) on the strength of this citation. If that store holds account data, keeping it 365 days may conflict with the 45-day deletion in GN-3 §3.4 (item 2). The synthesis never reconciles items 2 and 4. | Cite the internal record-keeping need (owner, record type, required period) as the reason, or drop the reason. Add a note reconciling the setting with GN-3 §3.4 for any account data in Vaultline. | a✓ b✓ c✗ d✓ |
| F2 | Medium | CONFIRMED | C | synthesis.md title ("obligations") and item 3 ("deletion requirement") | GN-3 is titled a *Guidance Note*. Its §3.4 is descriptive ("is deleted"), not a stated legal duty. The synthesis presents it as a requirement and its title calls everything, including a vendor setting, an "obligation". | Leads treat guidance as binding when weighing it against other duties, such as the retention need in item 4, or describe it to auditors as a legal requirement. | Label each item by status: Rule Book rule (binding on members), regulator guidance, vendor configuration. Retitle accordingly. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | C | synthesis.md item 1 | Drops the scope of Rule 14. The rule applies to "Members" and only to outages "of a customer-facing service". | Leads issue 72-hour notices for internal-only maintenance (wasted effort), or assume the rule binds them without confirming membership. | Quote Rule 14 in full, including "Members" and "customer-facing service". | a✓ b✓ c✗ d✗ |

**Sibling search for F1** (an interpretation attributed to a source): items 1–3 were checked against their sources and contain no other added rationale. F1 is not a security finding.

## NEEDS VALIDATION

- **S1:** Whether the organisation is a Northline Standards Council member. This decides whether Rule 14 applies at all.
- **S2:** Whether the organisation is a "processor of account data" under GN-3 §3.1. This decides whether §3.4 applies.
- **S3:** Whether Vaultline stores account data, and whether `retention_mode` means "keep for N days" or "delete after N days". This decides whether F1's conflict with the 45-day deletion is real.
- **S4:** Whether the live sources still match the 2026-10-20 copies.

## REFUTED

- **Item 2's quote is paraphrased or altered:** refuted. It matches GN-3 §3.4 word for word.
- **Item 3's paragraph number is wrong:** refuted. The text is at §3.4.
- **`extended` is not a valid value:** refuted. The source lists it with 365 days.

## WHAT HOLDS UP

- Rule 14's number and its 72-hour period.
- The GN-3 quote and its paragraph citation.
- Vaultline's value names and day counts.
- Every citation points to a source that exists locally and contains the cited passage.

## UNVERIFIED CLAIMS

C4b, the reason for choosing `extended`. To confirm it, obtain the internal requirement that says which records must be kept and for how long, and obtain Vaultline's documentation of what happens when the retention period ends.

## QUESTIONS FOR THE AUTHOR

1. What is the source for "records still needed"?
2. Does Vaultline hold account data covered by GN-3?
3. Are we a Northline member, and an Eastport processor?

## DECISION-MAKER SUMMARY

Items 1–3 are accurately quoted, but they need status and scope labels. Item 4's recommendation rests on a reason its source does not contain. Do not set `extended` retention until the record-keeping need is documented and reconciled with Eastport's 45-day deletion guidance; proceeding risks keeping closed-account data for up to a year against regulator guidance.

## OWNER SUMMARY

Most of the summary repeats its sources correctly, but it sometimes presents advice as a hard rule and leaves out who a rule applies to. Its recommendation for the storage retention setting gives a reason that the cited document does not support. That reason could clash with the guidance on deleting closed accounts, so it should be confirmed before anyone changes the setting.

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
    {"item": "live source URLs (*.example.test)", "status": "not_seen", "matters": false},
    {"item": "organisation membership, processor status, data map", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "synthesis.md", "kind": "document"},
      {"unit": "sources/northline-rulebook.md", "kind": "document"},
      {"unit": "sources/eastport-gn3.md", "kind": "document"},
      {"unit": "sources/vaultline-retention.md", "kind": "document"},
      {"unit": "C1 item 1 Rule 14", "kind": "claim"},
      {"unit": "C2 item 2 quote", "kind": "claim"},
      {"unit": "C3 item 3 paragraph", "kind": "claim"},
      {"unit": "C4a item 4 values", "kind": "claim"},
      {"unit": "C4b item 4 rationale", "kind": "claim"},
      {"unit": "C5 title obligations", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live source URLs", "reason": "no_tools"},
      {"unit": "organisation applicability facts", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4",
     "scenario": "Leads set retention_mode=extended (365 days) on a rationale ('standard would delete records still needed') absent from the cited Vaultline source; if Vaultline holds account data this may conflict with the 45-day deletion in GN-3 3.4, which the synthesis never reconciles.",
     "fix": "Cite the internal record-keeping requirement or remove the rationale; add a reconciliation with GN-3 3.4 for any account data in Vaultline.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "items 1-3 for interpretations attributed to sources", "found": "none"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md title and item 3",
     "scenario": "A Guidance Note paragraph and a vendor setting are presented as 'requirement'/'obligations'; leads treat guidance as binding when weighing it against other duties or describe it so to auditors.",
     "fix": "Label each item's status (member rule, regulator guidance, vendor configuration) and retitle.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Omitting 'Members' and 'customer-facing service' leads to notices for internal-only outages or an assumption that the rule applies without confirmed membership.",
     "fix": "Quote Rule 14 in full, including its scope.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "synthesis.md item 1",
     "suspicion": "Rule 14 may not apply to the organisation.",
     "unresolved_fact": "Whether the organisation is a Northline Standards Council member."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "synthesis.md items 2-3",
     "suspicion": "GN-3 may not apply.",
     "unresolved_fact": "Whether the organisation is a processor of account data (GN-3 3.1)."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "synthesis.md item 4",
     "suspicion": "Extended retention may keep closed-account data past 45 days.",
     "unresolved_fact": "Whether Vaultline stores account data and what retention_mode does at period end."},
    {"id": "S4", "status": "needs_validation", "track": "C", "location": "sources/*",
     "suspicion": "Local copies may differ from live sources.",
     "unresolved_fact": "Comparison of each copy with its live URL."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Item 2 quote is not verbatim.", "evidence": "Matches GN-3 3.4 word for word."},
    {"id": "R2", "candidate": "Item 3 paragraph number is wrong.", "evidence": "Deletion text is at GN-3 3.4."},
    {"id": "R3", "candidate": "'extended' is not a valid retention_mode value.", "evidence": "Vaultline source lists extended (365 days)."}
  ]
}
```