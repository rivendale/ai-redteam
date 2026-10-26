# pr-review: Fact check of research synthesis (Track C)

**Review report**

**REVIEWED:** `work/synthesis.md` and its three cited local sources. This is not a git PR, so there is no head SHA and no merge base SHA. The target is frozen as the file contents supplied in this session. Any later edit to `synthesis.md` or `sources/` is not covered by this review.

**TIER:** High. The synthesis states regulatory and standards obligations, which counts as regulated text, and the operations leads will act on it. Step 2 requires two rounds for High, ideally on two vendors. **This report is round 1 of 2.** Under Step 2, "a High-tier PR whose second round has not run is not reviewed."

**REVIEWERS:**
- Round 1 was done by this instance, Claude Opus 5.5 (`claude-opus-5-5`), in a session with no tools and no memory of writing the synthesis.
- The author is unknown. There are no commit trailers because there is no repository.
- Step 3 data check: the material is standards and guidance text and product documentation. It carries no personal data, so this endpoint is acceptable.

**Method and limits**
- I read every claim against the local source copy it cites (Step 5.7).
- I could not open the source URLs. Whether the local copies match the live documents is therefore **UNVERIFIED**.
- No source copy states an issue date, effective date or withdrawal status. Only the retrieval date of 2026-10-20 is known, so the currency of each source is UNVERIFIED.
- File classification (Step 5.6): the three `sources/*.md` files are dated records (retrieved copies). `synthesis.md` is a living document.

**Claim-by-claim check**

| Claim | Quote or fact in source? | Source status | Result |
|---|---|---|---|
| 1. Rule 14 requires 72 h notice before a planned outage | Partly. Rule 14 reads "Members give 72 hours' notice before a planned outage **of a customer-facing service**." | Rule book; reads as binding on members. Date not stated. | Scope is dropped (F2) |
| 2. Eastport quote on 45-day deletion | Yes, verbatim from GN-3 §3.4 | Guidance note: guidance, not binding. Scope is processors of account data (§3.1). | Correct as worded ("guidance says") |
| 3. "The deletion requirement is paragraph 3.4" | Paragraph number is correct | Guidance, not a requirement | Status mislabelled (F3) |
| 4. Set `retention_mode = extended`; `standard` would delete needed records | The values and durations are correct. The source gives no basis for the recommendation or for "records still needed". | Vendor documentation | Unsupported recommendation that may conflict with claim 2 (F1) |

**FINDINGS**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | `synthesis.md:4` (item 4) | See detail below the table. In short, the recommendation is inference that no source supports, and it may cut against item 2. | Every recommendation in the synthesis cites a source line that states it. Item 4 fails today. It passes once the recommendation is either removed or tied to a cited retention requirement and reconciled with GN-3 §3.4. |
| F2 | P2 | `synthesis.md:1` (item 1) | Rule 14 covers only planned outages "of a customer-facing service" and only binds Members. The synthesis drops both limits. Operations leads would apply a 72-hour notice gate to internal or non-customer-facing maintenance that the rule does not cover. The over-compliance slows operations, and the lead's understanding of the rule's scope becomes wrong. | Compare the claim text with Rule 14 phrase by phrase. It fails today because "customer-facing service" and "Members" are missing. It passes once the scope is restored. |
| F3 | P2 | `synthesis.md:3` (item 3) | Item 3 calls §3.4 "the deletion requirement". GN-3 is a Guidance Note: its title says so, and item 2 itself says "guidance says". §3.1 also limits it to processors of account data. Leads may treat a guidance norm as a binding regulatory requirement. They may also apply it outside its scope, or misstate it to auditors or customers. | Every obligation in the synthesis carries its source status (binding, guidance, proposal or withdrawn) and its scope. Item 3 fails today. It passes once it reads as Eastport *guidance* for processors of account data. |
| F4 | P3 | `synthesis.md` (all items) | No item gives the source's effective or issue date or confirms it is current. The only date available is the retrieval date, 2026-10-20. If any source was revised or withdrawn after that date, leads act on stale text with no warning. | The synthesis records each source's date and status, plus the retrieval date. It fails today. It passes once those are added, or once the synthesis explicitly says "currency unverified". |

**F1 detail (P1, item 4)**

1. The Vaultline source only lists the allowed values (`off`, `standard` 30 days, `extended` 365 days).
2. The source does not say which records must be kept. It also does not say whether "retention" means a minimum keep period or an automatic deletion deadline. "Standard would delete records still needed" is the synthesis author's inference, presented as if the source supported it.
3. Item 2 states that account data is deleted within 45 days of account closure. If the Vaultline store holds account data, a 365-day `extended` retention could keep it well past that 45-day point. Leads following item 4 could then act against the deletion guidance in item 2.
4. I am not asserting the conflict exists. The sources do not establish what Vaultline stores. The point is that the synthesis gives an operational instruction with no supporting source and with a possible conflict left unaddressed.

**PR-addressed instructions (Step 5.4):** none found.

**FILES NEEDED BUT NOT PROVIDED**
- Live versions of the three source URLs, or dated publisher copies, to confirm currency and status.
- Any requirement that defines which records must be retained, and for how long (needed for F1).
- A statement of what data the Vaultline store holds (needed to resolve the F1 conflict with GN-3 §3.4).
- The second-round review required for the High tier.

---

**Close-out**

Not written by this reviewer. Step 7 and the Output format say "a reviewer never adjudicates its own findings." The synthesis author must record Accepted, Deferred or Rejected for F1–F4. F1 is P1, so it cannot be deferred.

**ADJUDICATION:** pending, to be done by the author.

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | pending | |
| F2 | pending | |
| F3 | pending | |
| F4 | pending | |

**VERIFIED AFTER FIXES:** nothing yet. No fixes exist.

**MERGE RECOMMENDATION: do not release to the operations leads yet.**

Step 8 says: "Recommend merge only when all of these hold: every round the tier requires has run, and every finding has a written decision; … no unresolved blocker remains." Three conditions fail today:
1. The second High-tier round has not run.
2. F1–F4 have no decisions.
3. F1 is an unresolved P1.

Items 2 and 3 are accurate on the quote and paragraph number. Item 1's number and the 72-hour figure are correct. The defects are scope, status and one unsupported recommendation.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "source_compared_inference_flagged",
      "location": "synthesis.md:4",
      "scenario": "Item 4 recommends retention_mode=extended and claims standard (30 days) would delete records still needed; sources/vaultline-retention.md only lists the allowed values and says nothing about which records must be kept or whether retention is a minimum or a deletion deadline. Leads would make an unsupported production change, and a 365-day retention may conflict with GN-3 3.4 (account data deleted within 45 days of closure) if the store holds account data.",
      "fix": "Remove the recommendation or cite the retention requirement that supports it; state what data the store holds and reconcile with GN-3 3.4."
    },
    {
      "severity": "P2",
      "evidence_level": "verified_against_local_source",
      "location": "synthesis.md:1",
      "scenario": "Rule 14 applies only to Members and only to planned outages of a customer-facing service; the synthesis drops both limits, so leads would apply a 72-hour notice gate to outages the rule does not cover.",
      "fix": "Restate as: Rule 14 requires Members to give 72 hours' notice before a planned outage of a customer-facing service."
    },
    {
      "severity": "P2",
      "evidence_level": "verified_against_local_source",
      "location": "synthesis.md:3",
      "scenario": "Item 3 calls GN-3 3.4 a 'requirement', but GN-3 is a Guidance Note scoped (3.1) to processors of account data; leads may treat guidance as binding or apply it outside its scope.",
      "fix": "Label it Eastport guidance (GN-3 3.4), applicable to processors of account data."
    },
    {
      "severity": "P3",
      "evidence_level": "verified_against_local_source",
      "location": "synthesis.md (all items)",
      "scenario": "No source's issue or effective date or current status is recorded (only a retrieval date of 2026-10-20 on the local copies, and the live URLs could not be checked); a revised or withdrawn source would be acted on without warning.",
      "fix": "Record each source's date, status and retrieval date, or mark currency as unverified."
    }
  ]
}
```