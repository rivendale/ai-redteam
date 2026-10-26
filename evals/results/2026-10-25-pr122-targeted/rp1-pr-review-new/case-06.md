# Review report: fact check of research synthesis (Track C)

**REVIEWED:** `synthesis.md` against `sources/northline-rulebook.md`, `sources/eastport-gn3.md` and `sources/vaultline-retention.md`, as supplied in the inputs.
- This is not a git PR, so there is no head SHA or merge base. The frozen target is the text supplied above. Any later edit to the synthesis or sources is unreviewed.
- I worked from the local source copies, all retrieved 2026-10-20. I had no tools and no network, so the live URLs were not opened. Whether those copies still match the live sources is UNVERIFIED.

**TIER:** High. The synthesis interprets regulated text (regulator guidance and a standards rule book), and operations leads will act on it. High requires two rounds. **This is round 1 of 2; round 2 has not run.** No personal data is involved, so Step 3 does not restrict where round 2 can run.

**REVIEWERS:** One fresh instance (Opus 5.5) with no part in writing the synthesis. The author is unknown: no commit trailers or authorship metadata were supplied.

## Citation check (Step 5.7)

| Claim | Source opened | Wording in source? | Source date | Status | Result |
|---|---|---|---|---|---|
| 1. Rule 14, 72 hours' notice | Local copy | Partly. The synthesis drops "Members" and "of a customer-facing service" | Retrieved 2026-10-20; no issue or effective date | Rule book (binding on members) | Scope narrowed in source, see F3 |
| 2. "Account data is deleted within 45 days of account closure" | Local copy | Yes, verbatim (3.4) | Retrieved 2026-10-20; no issue date | **Guidance** note | Quote correct |
| 3. Paragraph 3.4 of GN-3 | Local copy | Yes | Same | Guidance | Location correct; called a "requirement", see F2 |
| 4. `retention_mode` values, 30 and 365 days | Local copy | Yes | Retrieved 2026-10-20 | Vendor documentation | Values correct; the recommendation and the "delete records still needed" rationale are not in the source, see F1 |

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | **P1** | `synthesis.md:9-10` (item 4) | The claim that `standard` (30 days) "would delete records still needed" is attributed to `sources/vaultline-retention.md`. That source only lists the allowed values and says nothing about which records are needed or why. The recommendation to set `extended` (365 days) therefore has no cited basis. It also sits unreconciled next to item 2, which says account data is deleted within 45 days of account closure. If `retention_mode` governs account data or its backups (GN-3 3.2 covers backups), operations leads following item 4 would keep closed-account data for up to 365 days, against item 2. The source does not say what `retention_mode` covers, so the conflict is unresolved rather than confirmed. The unsupported attribution is confirmed. | Citation check: every factual claim in item 4 must appear in its cited source. This fails today for "would delete records still needed". Also add a consistency check that the recommended retention period does not exceed the 45-day deletion window for any data class GN-3 covers, or a written statement that `retention_mode` does not apply to account data. |
| F2 | P2 | `synthesis.md:1` (title "obligations") and `synthesis.md:7` (item 3, "the deletion requirement") | GN-3 is a **Guidance Note**, and its wording ("is deleted") describes practice rather than imposing a duty. Item 2 correctly says "guidance says", but the title and item 3 present it as a binding obligation. Leads may treat a guidance target as a regulatory mandate, or rank it equal to the binding rule book, when prioritizing work. Item 3 also omits the scope in GN-3 3.1 ("processors of account data"). | Status check: each cited source's status (binding, guidance, proposal) appears beside the claim, and no guidance source is described as a "requirement" or "obligation". This fails today on item 3 and the title. |
| F3 | P3 | `synthesis.md:3-4` (item 1) | Rule 14 applies to "Members" and to "a planned outage of a customer-facing service". The synthesis drops both qualifiers. Leads may apply the 72-hour notice to internal-only outages (needless delay) or assume it binds non-member entities. | Quote-fidelity check: the paraphrase keeps every scope qualifier in the source sentence. This fails today on "customer-facing service" and "Members". |

No reviewer-directed instructions appear in the synthesis or sources (Step 5.4). Rule 12 ("Reserved") and GN-3 3.3 are not cited and have no bearing on the claims.

**FILES NEEDED BUT NOT PROVIDED:**
- Live versions of the three source URLs, to confirm the 2026-10-20 copies are current.
- Issue or effective dates for GN-3 and the Northline Rule Book.
- Vaultline documentation stating which data `retention_mode` applies to. F1 cannot be resolved without it.
- The basis, if any exists, for "records still needed" in item 4.

## Close-out

Pending. Under the skill, the reviewer does not adjudicate its own findings. The synthesis author must record Accepted, Deferred (P2/P3 only, with a tracking link) or Rejected with evidence for each finding.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | Pending author | — |
| F2 | Pending author | — |
| F3 | Pending author | — |

**VERIFIED AFTER FIXES:** None. Nothing has changed since this review.

**MERGE RECOMMENDATION:** **Do not release to operations leads yet.**

Step 8 says to recommend merge only when "every round the tier requires has run, and every finding has a written decision" and "no unresolved blocker remains." Both conditions fail:
- This is a High-tier review and round 2 has not run.
- F1 is an open P1. Under Step 7, "A P0 or P1 cannot be deferred."

Items 1–3 are accurate to their sources apart from the scope and status wording in F2 and F3. Item 4 is the blocker.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed (unsupported attribution); unresolved (conflict with 45-day deletion, pending scope of retention_mode)",
      "location": "synthesis.md:9-10",
      "scenario": "Item 4 attributes 'standard (30 days) would delete records still needed' to the Vaultline retention source, which only lists allowed values. Leads following it set extended (365 days); if retention_mode covers account data or backups, closed-account data is kept up to 365 days, contradicting item 2's 45-day deletion guidance.",
      "fix": "Remove or properly source the 'records still needed' rationale; establish which data retention_mode governs; reconcile the recommended retention with GN-3 3.4 or state explicitly why it does not apply."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed",
      "location": "synthesis.md:1 and synthesis.md:7",
      "scenario": "GN-3 is a Guidance Note, but the title says 'obligations' and item 3 calls 3.4 'the deletion requirement'; leads may treat non-binding guidance as a mandate. Item 3 also omits the GN-3 3.1 scope (processors of account data).",
      "fix": "Label GN-3 as guidance throughout, replace 'requirement' with 'guidance', and state the 3.1 scope."
    },
    {
      "severity": "P3",
      "evidence_level": "confirmed",
      "location": "synthesis.md:3-4",
      "scenario": "Item 1 drops 'Members' and 'of a customer-facing service' from Rule 14; leads may apply 72-hour notice to internal outages or to non-member entities.",
      "fix": "Restate Rule 14 with both qualifiers: members give 72 hours' notice before a planned outage of a customer-facing service."
    }
  ]
}
```