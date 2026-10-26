# Redteam review: research synthesis (outage notice, deletion and retention)

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available, so I reviewed the files as pasted into this session.

**VERDICT: REWORK.** Item 4 recommends 365-day retention for a reason its cited source never gives. That recommendation also appears to conflict with the 45-day deletion rule in item 2 of the same synthesis.

**CONFIDENCE: medium.** All four local files were read in full. Three things limit confidence:
- This is a same-context review.
- I could not compare the local copies with the live URLs.
- Nothing tells me what data Vaultline stores, or whether the organisation falls under Eastport's or Northline's scope.

**INPUTS LEDGER**
- **Seen:**
  - `request.md`
  - `context.md`
  - `synthesis.md`
  - `sources/northline-rulebook.md`
  - `sources/eastport-gn3.md`
  - `sources/vaultline-retention.md`
- **Not seen:**
  - **Live source URLs.** There was no network. This matters a little: the copies are dated 2026-10-20 and could have changed.
  - **What Vaultline stores, and whether it holds account data after closure.** This matters for F1.
  - **Whether the organisation is a Northline "Member" or an Eastport "processor of account data".** This matters for whether items 1 to 3 apply at all.

**COVERAGE**
- **Scope:** the whole synthesis, checked against all three cited sources.
- **Checked:** synthesis items 1 to 4; Northline Rules 11, 12 and 14; GN-3 sections 3.1 to 3.4; the Vaultline retention page.
- **Not checked:** live sources (`no_tools`).

**SEATS AND GATE**
- **Reviewers:** only the local same-context reviewer ran. No subagent or cross-vendor seats were available.
- **Sensitivity gate:** passed. The files contain no personal, credential or confidential data.
- **Embedded instructions:** the work contains no text addressed to the reviewer.

## CLAIMS TO EVIDENCE

| Label | Synthesis claim | Source text | State |
|---|---|---|---|
| C1 | Item 1: "Rule 14 … requires 72 hours' notice before a planned outage" | Rule 14: "Members give 72 hours' notice before a planned outage of a **customer-facing service**." | Rule number and 72 hours verified. The scope is dropped: it applies to customer-facing services, and only to Members. → F3, V1 |
| C2 | Item 2: quote "Account data is deleted within 45 days of account closure" | GN-3 §3.4, word for word | Verified observation |
| C3 | Item 3: "the deletion **requirement** is paragraph 3.4 of GN-3" | §3.4 is correctly located. It sits in a *guidance note*, written as a description ("is deleted"), not as "must" | Paragraph verified. Calling it a "requirement" is the synthesis's interpretation. → F4, V2 |
| C4a | Item 4: `retention_mode` values; `standard` is 30 days | Source lists `off`, `standard` (30 days) and `extended` (365 days) | Verified observation |
| C4b | Item 4: `standard` "would delete records still needed" | Not in the source. The source says nothing about which records are needed | Unsupported by the cited source. → F2 |
| C4c | Item 4: recommendation to "set `retention_mode = extended`" | Derived from C4b. The 365-day period is far longer than the 45 days in C2 | Not supported, and it conflicts with C2. → F1 |

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | PROBABLE | C | `synthesis.md` item 4 against item 2 | The synthesis recommends `extended` (365 days) retention. Item 2 of the same document cites deletion within 45 days of account closure. The synthesis does not reconcile the two. | Vaultline holds account data, including backups (GN-3 §3.2 brings backups into scope). Operations sets `extended` as told. Closed accounts' data then survives up to 365 days, against the 45 days in GN-3 §3.4. | State what data Vaultline holds. Either reconcile the setting with the 45-day deletion rule (`standard` at 30 days falls within it), or document why that data is out of scope. | a Y, b N, c Y, d Y |
| F2 | High | CONFIRMED | C | `synthesis.md` item 4: "would delete records still needed (sources/vaultline-retention.md)" | The justification is credited to a source that does not contain it. That source only lists setting values. | Operations leads trust the citation and change the configuration. The only basis is an unsourced belief that records are still needed. | Name the records and the retention rule that requires keeping them, and cite it. Otherwise remove the recommendation. | a Y, b Y, c N, d Y |
| F3 | Medium | CONFIRMED | C | `synthesis.md` item 1 | The rule's scope "of a customer-facing service" is dropped, so the obligation reads as covering all planned outages. | Operations sends 72-hour notices for internal maintenance. Or operations misjudges which services the rule covers. | Restore the qualifier word for word, and name which of our services count as customer-facing. | a Y, b Y, c N, d N |
| F4 | Medium | CONFIRMED | C, R | `synthesis.md` item 3 ("requirement") and the title ("obligations") | GN-3 is a regulator's *guidance note* written as a description. The synthesis presents it as a binding requirement without checking its legal status or the §3.1 scope. | Leads treat guidance as a mandatory deadline, or tell customers it is one. It is presented as regulatory fact without support. | Call it "GN-3 guidance §3.4". Confirm whether it binds, and whether we are a "processor of account data" (§3.1). | a Y, b Y, c N, d N |

**Severity check.** F1 and F2 are the two High findings. I re-examined each the way its strongest defender would:
- **F1 holds, but stays PROBABLE.** The best defence is that Vaultline may not store account data. The synthesis groups the two items together under one title and never says so. Until the data is identified, the evidence level stays PROBABLE.
- **F2 holds.** The source text is short and complete, and it has no such statement.

**Siblings.** For both High findings I searched items 1 to 3 for two things: support credited to a source that lacks it, and recommendations that conflict with each other.
- **Unsupported support:** none found. Items 1 to 3 each trace to real source text.
- **Conflicts between items:** none beyond F1.
- **Scope and wording problems:** these appear separately as F3 and F4.
- **Security:** neither High finding is a security finding.

**NEEDS VALIDATION**
- **V1:** whether the organisation is a Northline "Member". If it is not, Rule 14 does not apply.
- **V2:** whether GN-3 is binding, and whether the organisation is a "processor of account data" under §3.1.
- **V3:** whether the local copies, dated 2026-10-20, still match the live URLs.
- **V4:** what Vaultline retains, and whether `retention_mode` governs account data after closure. This settles whether F1 should move from PROBABLE to CONFIRMED.

**REFUTED**
- **Candidate:** item 2 misquotes GN-3. The text matches §3.4 word for word.
- **Candidate:** item 3 cites the wrong paragraph. Deletion is §3.4.
- **Candidate:** item 4 gets the setting values wrong. `standard` is 30 days and `extended` is 365 days, matching the source.

**WHAT HOLDS UP**
- The rule and paragraph numbers are correct (Rule 14, §3.4).
- The 72-hour and 45-day figures are correct.
- The quotation is word for word.
- The Vaultline values are accurate.

**UNVERIFIED CLAIMS**
- **"Records still needed" (C4b).** Confirm it by naming the records and the rule that requires keeping them.
- **The binding status of all three "obligations".** Confirm it against the issuers' authority and our membership or processor status.

**QUESTIONS FOR THE AUTHOR**
1. Which records does `standard` retention lose, and what requires keeping them?
2. Does Vaultline hold account data from closed accounts?
3. Are we a Northline Member, and a GN-3 processor?

**DECISION-MAKER SUMMARY.** Do not act on item 4 yet. Its reason for 365-day retention is not in its cited source, and the setting likely conflicts with the 45-day deletion guidance in item 2. Items 1 to 3 cite their sources accurately, but they need the dropped scope restored and a check that the rules actually apply to us.

**OWNER SUMMARY.** The summary quotes its sources accurately for outage notice and deletion. However, it leaves out which services the outage rule covers, and it treats guidance as a firm rule. Its advice to keep stored records for a full year has no support in its source, and it may clash with the 45-day deletion limit, so hold that change until someone confirms what data is affected.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "synthesis.md", "status": "seen", "matters": true},
    {"item": "sources/northline-rulebook.md", "status": "seen", "matters": true},
    {"item": "sources/eastport-gn3.md", "status": "seen", "matters": true},
    {"item": "sources/vaultline-retention.md", "status": "seen", "matters": true},
    {"item": "live source URLs", "status": "not_seen", "matters": false},
    {"item": "what data Vaultline stores", "status": "not_seen", "matters": true},
    {"item": "organisation's Northline membership / GN-3 processor status", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
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
      {"unit": "C3 GN-3 paragraph and requirement status", "kind": "claim"},
      {"unit": "C4 Vaultline retention recommendation", "kind": "claim"}
    ],
    "not_checked": [{"unit": "live source URLs", "reason": "no_tools"}]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "C",
     "location": "synthesis.md item 4 vs item 2",
     "scenario": "If Vaultline holds account data (incl. backups, GN-3 3.2), setting retention_mode=extended keeps closed-account data up to 365 days, beyond the 45-day deletion in GN-3 3.4 cited in item 2.",
     "fix": "Identify what Vaultline stores; reconcile retention with the 45-day deletion guidance (standard=30 days fits) or document why that data is out of scope.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "items 1-3 for recommendations conflicting with another item", "found": "none"}},
    {"id": "F2", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 4: 'would delete records still needed (sources/vaultline-retention.md)'",
     "scenario": "Ops leads change production retention on a justification attributed to a source that only lists setting values and says nothing about needed records.",
     "fix": "Name the records and the rule requiring their retention with a real citation, or drop the recommendation.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "security": false,
     "siblings_searched": {"searched": "items 1-3 for support attributed to a source that lacks it", "found": "none; items 1-3 trace to real source text (scope issues filed as F3, F4)"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 1",
     "scenario": "Dropping 'of a customer-facing service' leads ops to apply 72-hour notice to all planned outages or misjudge which services are covered.",
     "fix": "Restore the qualifier verbatim and list which services are customer-facing.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md item 3 ('requirement') and title ('obligations')",
     "scenario": "A descriptive guidance note (GN-3 3.4) is presented as a binding requirement without checking its status or the 3.1 processor scope; leads may misstate it as a regulatory mandate.",
     "fix": "Describe it as GN-3 guidance 3.4; confirm binding status and whether the organisation is a processor of account data.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "V1", "status": "needs_validation", "track": "C", "location": "synthesis.md item 1",
     "suspicion": "Rule 14 may not apply to the organisation.", "unresolved_fact": "Whether the organisation is a Northline Member."},
    {"id": "V2", "status": "needs_validation", "track": "C", "location": "synthesis.md items 2-3",
     "suspicion": "GN-3 may not bind the organisation.", "unresolved_fact": "GN-3's legal status and whether the organisation is a processor of account data (3.1)."},
    {"id": "V3", "status": "needs_validation", "track": "C", "location": "sources/*",
     "suspicion": "Local copies may differ from live sources.", "unresolved_fact": "Whether the 2026-10-20 copies match the live URLs today."},
    {"id": "V4", "status": "needs_validation", "track": "C", "location": "synthesis.md item 4",
     "suspicion": "Retention setting may govern account data after closure.", "unresolved_fact": "What data Vaultline retains and what retention_mode applies to."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Item 2 misquotes GN-3.", "evidence": "Text matches GN-3 3.4 verbatim."},
    {"id": "R2", "candidate": "Item 3 cites the wrong paragraph.", "evidence": "Deletion is GN-3 3.4."},
    {"id": "R3", "candidate": "Item 4 misstates the setting values.", "evidence": "Source lists standard (30 days) and extended (365 days)."}
  ]
}
```