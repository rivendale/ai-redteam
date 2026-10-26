# Redteam report: research synthesis on outage notice, deletion and retention

**No-tools review.** I could not open links, run anything, or start a fresh subagent. I checked only against the source copies included in the work. The synthesis was not written in this conversation, so the anchoring risk is lower. Re-run in a fresh session with tools if the stakes call for it.

**VERDICT: SHIP WITH FIXES.** Three of the four claims match their sources. The fourth, the retention recommendation, gives a reason the cited source does not contain and may conflict with the deletion claim. It must be corrected before operations leads act on it.

**CONFIDENCE: medium.** Every quote and paragraph number was checked word for word against the supplied copies. Confidence is limited because:
- I had no tools, so I could not compare the local copies with the live URLs.
- What Vaultline's retention setting actually controls is not documented in the work.

## Inputs ledger
- **Seen:**
  - `request.md` (verbatim: "Check this research synthesis against its sources before it goes to the operations leads.")
  - `context.md`
  - `synthesis.md`
  - `sources/northline-rulebook.md`
  - `sources/eastport-gn3.md`
  - `sources/vaultline-retention.md`
- **Not seen:**
  - **Live source URLs** (`*.example.test`). Not openable without tools. This matters a little: the copies were retrieved 2026-10-20, five days before review, so staleness risk is low.
  - **Rule 13 of the Northline Rule Book.** The copy jumps from Rule 12 to Rule 14. It matters only if the copy is truncated.
  - **What data is stored in Vaultline and what `retention_mode` controls.** This matters for claim 4.

## Coverage
- **Scope:** the whole synthesis (4 claims) and all 3 cited sources.
- **Checked:** every file listed above; claims S1 to S4; source status and scope sections (GN-3 §3.1, Rule 14 wording, Vaultline value list).
- **Not checked:** live sources (no tools).

## Seats and gate
- **Seats:** only this same-session reviewer ran. No subagent or cross-vendor seats were available.
- **Sensitivity gate:** passed. There is no personal or confidential data, only public-style regulatory text and product documentation.

## Claims to evidence

| Claim | Synthesis wording | Source | Status |
|---|---|---|---|
| S1 (§1) | Rule 14 "requires 72 hours' notice before a planned outage" | Northline Rule 14: "Members give 72 hours' notice before a planned outage **of a customer-facing service**." | Verified number and rule ID. The scope qualifier was dropped (see F2). |
| S2 (§2) | Quote: "Account data is deleted within 45 days of account closure" | GN-3 §3.4, identical text | Verified as an exact quote. |
| S3 (§3) | "the deletion requirement is paragraph 3.4 of GN-3" | GN-3 §3.4 | Paragraph number verified. "Requirement" overstates a *Guidance Note*, which also applies only to "processors of account data" (§3.1) (see F3). |
| S4a (§4) | `extended` exists; `standard` = 30 days | Vaultline: `off`, `standard` (30 days), `extended` (365 days) | Verified. |
| S4b (§4) | "`standard` (30 days) would delete records still needed"; therefore set `extended` | None. The Vaultline source says nothing about which records are needed, and no other source does either. | UNVERIFIED and presented as sourced (see F1). |

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | CONFIRMED | C | `synthesis.md` §4 | The action-driving reason ("would delete records still needed") is cited to `sources/vaultline-retention.md`, but that source only lists the setting values. Nothing in the work says what records Vaultline holds or how long they are needed. | Leads set `extended` (365 days) on the strength of a citation that does not support it. If Vaultline holds account data, retention can then run up to about 320 days past the 45-day deletion figure in §2/§3, so the synthesis contradicts itself. | Remove the citation from the reason, or cite a source for which records need more than 30 days of retention. State how the choice squares with GN-3 §3.4's 45 days. If the reason cannot be sourced, present §4 as an open decision rather than a recommendation. | a Y / b Y / c Y (possible regulatory exposure) / d Y |
| F2 | Medium | CONFIRMED | C | `synthesis.md` §1 | The rule's limit "of a customer-facing service" was dropped, and so was the fact that it binds "Members". | Leads apply 72-hour notice to every planned outage, including internal ones, or assume it binds them without checking membership. The failure is over-compliance and misreading scope, not a breach. | Quote Rule 14 in full, including "Members" and "of a customer-facing service". | a Y / b Y / c N / d Y |
| F3 | Medium | CONFIRMED | C | `synthesis.md` §3 (and the "obligations" title) | GN-3 is a regulator's *Guidance Note*, and §3.4 is phrased descriptively ("is deleted"), not as a mandate. The synthesis calls it a "requirement" and an "obligation", and omits that §3.1 limits scope to processors of account data. | Leads treat guidance as a binding rule, or apply it where the organisation is not a processor of account data. | Label the source's status as guidance, and add the §3.1 scope condition. | a Y / b Y / c N / d Y |

**Confirm or refute on F1.** The strongest defence is that the citation covers only the setting values and the reason is the author's own judgement. That defence fails: the sentence reads as sourced, nothing anywhere in the work supports the reason, and it drives the only concrete action in the document. F1 holds as High.

**Sibling search for F1.** I checked §1 to §3 for other unsupported inferences presented under a citation. None rise to that level; §1 and §3 have the scope and status overstatements recorded as F2 and F3. F1 is not a security finding.

## Needs validation
- **N1.** Does Vaultline store account data covered by GN-3, and does `retention_mode` keep data for N days, or keep deleted items recoverable for N days? This settles whether `extended` actually conflicts with the 45-day deletion figure.
- **N2.** Is the Northline copy complete? Rule 13 is absent. Settle it by comparing against the live Rule Book.
- **N3.** Do the local copies match the live sources as of the review date? Settle it by opening the three URLs.

## Refuted
- **"The §2 quote is paraphrased."** Refuted: it matches GN-3 §3.4 character for character.
- **"The §3 paragraph number is wrong."** Refuted: the text is at §3.4.
- **"The Vaultline values are wrong."** Refuted: they match the source, including 30 days for `standard`.

## What holds up
- The rule number and the 72-hour figure (§1).
- The verbatim deletion quote and its paragraph citation (§2, §3).
- The Vaultline setting names and durations (§4).
- Every citation points to a source that exists and contains the cited text.

## Unverified claims
- "`standard` would delete records still needed." To confirm it, find a source naming the records and their required retention period.

## Questions for the author
1. Which records need more than 30 days of retention, and what source says so?
2. Does Vaultline hold account data subject to GN-3's 45-day deletion?
3. Is the organisation a Northline member, and are the affected services customer-facing?

## Decision-maker summary
The citations are accurate, but the one concrete action (switch Vaultline to 365-day retention) rests on a reason no source supports and may clash with the 45-day deletion guidance. Fix §4 and restore the scope wording in §1 and §3 before release. If leads act on it as written, they risk keeping account data far longer than the guidance describes.

## Owner summary
The summary quotes its sources correctly, but its retention advice gives a reason none of the sources back up, and that advice may conflict with the deletion guidance it also cites. Two other points make rules sound broader or stricter than the sources say. Correct these before the operations team uses it.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "live source URLs (*.example.test)", "status": "not_seen", "matters": false},
    {"item": "Northline Rule 13 (absent from copy)", "status": "not_seen", "matters": false},
    {"item": "Vaultline data inventory / retention_mode semantics", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "synthesis.md", "kind": "document"},
      {"unit": "sources/northline-rulebook.md", "kind": "document"},
      {"unit": "sources/eastport-gn3.md", "kind": "document"},
      {"unit": "sources/vaultline-retention.md", "kind": "document"},
      {"unit": "S1 synthesis.md §1", "kind": "claim"},
      {"unit": "S2 synthesis.md §2", "kind": "claim"},
      {"unit": "S3 synthesis.md §3", "kind": "claim"},
      {"unit": "S4 synthesis.md §4", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "live source URLs", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md §4",
     "scenario": "Leads switch Vaultline to extended (365 days) based on the claim that standard 'would delete records still needed', which sources/vaultline-retention.md does not support; if Vaultline holds account data, retention can then exceed the 45-day deletion figure the synthesis cites in §2-§3.",
     "fix": "Cite a source identifying which records need more than 30 days of retention or remove the citation from that reason; reconcile the choice with GN-3 §3.4, or present §4 as an open decision.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": false,
     "siblings_searched": {"searched": "synthesis.md §1-§3 for other unsupported inferences presented under a citation",
                           "found": "none at this level; scope/status overstatements recorded as F2 and F3"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md §1",
     "scenario": "Rule 14's limits 'Members' and 'of a customer-facing service' are dropped; leads apply 72-hour notice to all planned outages or assume it binds them without checking membership.",
     "fix": "Quote Rule 14 in full, including 'Members' and 'of a customer-facing service'.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "synthesis.md §3 and title",
     "scenario": "GN-3 is a Guidance Note limited to processors of account data (§3.1); calling §3.4 a 'requirement'/'obligation' leads operations to treat guidance as binding or apply it out of scope.",
     "fix": "Label GN-3 as guidance and add the §3.1 scope condition.",
     "answers": {"a": true, "b": true, "c": false, "d": true}},
    {"id": "N1", "status": "needs_validation", "track": "C", "location": "synthesis.md §4",
     "suspicion": "Extended retention may conflict with GN-3 §3.4's 45-day deletion.",
     "unresolved_fact": "Whether Vaultline stores account data and whether retention_mode governs live data or recoverability of deleted data."},
    {"id": "N2", "status": "needs_validation", "track": "C", "location": "sources/northline-rulebook.md",
     "suspicion": "The Rule Book copy may be truncated (Rule 13 absent).",
     "unresolved_fact": "Whether the live Rule Book contains a Rule 13."},
    {"id": "N3", "status": "needs_validation", "track": "C", "location": "sources/*",
     "suspicion": "Local copies may differ from the live sources.",
     "unresolved_fact": "Whether the three live URLs match the copies retrieved 2026-10-20."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The §2 quote is paraphrased.", "evidence": "It matches GN-3 §3.4 verbatim."},
    {"id": "C2", "candidate": "The §3 paragraph number is wrong.", "evidence": "The text is at GN-3 §3.4."},
    {"id": "C3", "candidate": "The Vaultline values are misstated.", "evidence": "The source lists off, standard (30 days), extended (365 days)."}
  ]
}
```