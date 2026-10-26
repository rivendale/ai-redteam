# Review report

**REVIEWED:** Research synthesis `synthesis.md` (Track C), checked against the local source copies in `work/sources/`. This is not a git PR, so there is no head SHA or merge base. The frozen target is the four files exactly as supplied in this session. Any later edit to them is unreviewed.

**TIER:** High. The synthesis restates regulator guidance and standards-body rules (regulated text), and operations leads will act on it. Under Step 2, High requires two rounds, ideally on two vendors. **Only one round has run (this one).** The review is not complete until a second independent round runs.

**REVIEWERS:**
- Reviewer: one fresh instance, Claude Opus 5.5 (`claude-opus-5-5`). It has no memory of writing the synthesis and no tools, so it worked by static reading of the supplied text only.
- Author: unknown. There are no commit trailers because this is not a repo.
- Data handling (Step 3): the content is public regulatory and vendor-doc text with no personal data. Nothing was sent outside this session.

**Source status (Step 5.7):**

| Source | Status | Source date | Quote present? |
|---|---|---|---|
| `sources/northline-rulebook.md` | Binding on members (standards-council rule book). Its applicability to this organization is not stated. | Retrieved 2026-10-20. No issue date given. | The 72-hour notice rule is present, but as Rule 14, not Rule 12. |
| `sources/eastport-gn3.md` | **Guidance** ("Guidance Note"), not binding regulation. | Retrieved 2026-10-20. No issue date given. | **No.** The quoted sentence does not appear. |
| `sources/vaultline-retention.md` | Vendor documentation. | Retrieved 2026-10-20. No issue date given. | Not a quote. The claimed value `strict` does not exist. |

Currency of all three against the live URLs is **UNVERIFIED**, because there was no network by design.

**Document classification (Step 5.6):** `synthesis.md` is a living document (it is undated), so in-place correction is appropriate. The source files are dated retrieval copies and need no change.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `synthesis.md:3` (vs `sources/northline-rulebook.md:5-6`) | The synthesis attributes the 72-hour planned-outage notice to **Rule 12**. Rule 12 is "Reserved"; the requirement is **Rule 14**. A lead who cites Rule 12 to a customer, auditor or the Council cites an empty rule. | A citation check: for each "Rule N" in the synthesis, the cited rule's text in the source must contain the claimed requirement. This fails today (Rule 12 = "Reserved") and passes after the change to Rule 14. |
| 2 | P2 | `synthesis.md:3-4` (vs `sources/northline-rulebook.md:6`) | The synthesis drops the scope qualifier "of a customer-facing service". Leads may apply 72-hour notice to every planned outage, including internal ones, which over-constrains maintenance. They may also miss that the rule binds only members. | A qualifier check: the synthesis sentence must carry the source's scope ("customer-facing service", "members"). |
| 3 | P1 | `synthesis.md:5` (vs `sources/eastport-gn3.md:7`) | The quoted text "account data must be erased promptly, and in any case within 30 days" **does not appear in GN-3**. The source says "Account data is deleted within 45 days of account closure". The synthesis therefore fabricates a quote, changes the deadline (30 vs 45 days), drops the trigger ("of account closure"), and turns descriptive guidance into "must". Leads would put a non-existent regulator quote and the wrong deadline into procedures or external statements. | A verbatim-quote check: every quoted string must appear exactly in the cited source. This fails today. |
| 4 | P1 | `synthesis.md:7` (vs `sources/eastport-gn3.md:5,7`) | The synthesis says the deletion requirement is **paragraph 3.2**. Paragraph 3.2 is "Backups"; deletion is **paragraph 3.4**. A reader who checks the citation finds the backup-encryption clause, and any downstream control mapping points to the wrong paragraph. | A paragraph-citation check: the text at the cited paragraph must match the claimed topic. This fails today (3.2 = Backups). |
| 5 | P2 | `synthesis.md:1`, `synthesis.md:5` (vs `sources/eastport-gn3.md:1`) | The title frames everything as "obligations", and item 2 uses "must". GN-3 is a **guidance note**, not a binding rule. Leads may treat guidance as a hard legal requirement, or report it that way, without knowing its actual status. | A status check: each cited source in the synthesis is labelled binding, guidance, proposal or withdrawn, and the label matches the source's own description. |
| 6 | P1 | `synthesis.md:8` (vs `sources/vaultline-retention.md:4-5`) | The synthesis instructs `retention_mode = strict`. Vaultline accepts only `off`, `standard` or `extended`, and "an unknown value is rejected when the setting is saved". An operator following this instruction gets a rejected save, and the intended retention control is never applied. | A config-value check: every setting value named in the synthesis must be in the vendor's documented allowed set. `strict` is not in {off, standard, extended}, so the check fails today. |
| 7 | P1 | `synthesis.md:8` (vs `sources/vaultline-retention.md:4`, `sources/northline-rulebook.md:6`, `sources/eastport-gn3.md:7`) | The synthesis claims one retention setting "meets both rules", which fails on two counts. First, the outage-notice rule (Northline Rule 14) has nothing to do with storage retention. Second, the Vaultline source does not say that any `retention_mode` deletes account data after account closure. It describes 30-day and 365-day retention windows with no stated relation to closure-triggered deletion. Leads may believe both obligations are satisfied by a console toggle when neither is shown to be. | A claim-to-evidence check: each "meets rule X" assertion must cite source text showing the mechanism satisfies rule X. Today there is no such text for either rule. |

**Note on fixes:** the corrections implied above for #1, #3 and #4 (Rule 14, the GN-3 3.4 wording with 45 days, paragraph 3.4) are each checked against the cited source text at the lines given.

Any replacement for #6 and #7 is **UNVERIFIED**. For example, `standard` (30 days) looks like it fits inside 45 days, but the source does not establish that retention expiry performs closure-triggered deletion of account data. That needs Vaultline documentation or a test in a non-production tenant, plus an owner decision.

**FILES NEEDED BUT NOT PROVIDED:**
- Current live versions or issue dates of GN-3, the Northline Rule Book and the Vaultline retention page, to confirm currency.
- Confirmation that the organization is a Northline member and an Eastport "processor of account data".
- Vaultline documentation on how `retention_mode` interacts with deleting data after account closure.

---

# Close-out

*Pending. A reviewer does not adjudicate its own findings (Output format rule). The synthesis author must record a decision for each finding below.*

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–7 | Pending author | — |

Constraint from Step 7: findings #1, #3, #4, #6 and #7 are P1 and **cannot be Deferred**. They must be Accepted (fixed) or Rejected with evidence.

**VERIFIED AFTER FIXES:** None yet. Corrections should be verified by a targeted re-read of the changed lines against the cited source lines, not by a full new review (Step 6).

**MERGE RECOMMENDATION: do not send to the operations leads.**

Step 8: "Recommend merge only when all of these hold: every round the tier requires has run, and every finding has a written decision; … no unresolved blocker remains." Neither condition holds:
- Only one of the two High-tier rounds has run.
- Five P1 findings are open. Between them they cover a fabricated regulator quote with the wrong deadline, two wrong citations, a config value the console rejects, and an unsupported "meets both rules" claim.

All four numbered claims in the synthesis fail against their own sources.

Open items:
- Author adjudication of #1–#7.
- The second independent review round.
- An owner decision on which Vaultline setting, if any, supports the 45-day deletion guidance.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed against source",
      "location": "synthesis.md:3",
      "scenario": "Cites Northline Rule 12 for 72-hour outage notice; Rule 12 is 'Reserved' and the requirement is Rule 14 (sources/northline-rulebook.md:5-6).",
      "fix": "Change citation to Rule 14."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed against source",
      "location": "synthesis.md:3-4",
      "scenario": "Drops scope 'of a customer-facing service' and the members-only applicability; leads may apply notice to all planned outages.",
      "fix": "Restore the qualifier: members give 72 hours' notice before a planned outage of a customer-facing service."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed against source",
      "location": "synthesis.md:5",
      "scenario": "Quoted text 'erased promptly, and in any case within 30 days' does not appear in GN-3; source says deleted within 45 days of account closure (sources/eastport-gn3.md:7). Fabricated quote, wrong deadline, trigger dropped.",
      "fix": "Replace with the source wording: 'Account data is deleted within 45 days of account closure.'"
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed against source",
      "location": "synthesis.md:7",
      "scenario": "Says the deletion requirement is GN-3 paragraph 3.2; 3.2 is Backups, deletion is 3.4 (sources/eastport-gn3.md:5,7).",
      "fix": "Change to paragraph 3.4."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed against source",
      "location": "synthesis.md:1",
      "scenario": "Frames GN-3 as an 'obligation' with 'must'; the source is a guidance note, so leads may misstate its legal status.",
      "fix": "Label each source's status (GN-3: guidance; Northline: binding on members)."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed against source",
      "location": "synthesis.md:8",
      "scenario": "Instructs retention_mode = strict; allowed values are off/standard/extended and unknown values are rejected on save (sources/vaultline-retention.md:4-5). The operator's change fails and no control is applied.",
      "fix": "UNVERIFIED: choose a documented value only after confirming its effect on closure-triggered deletion; owner decision required."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed against source",
      "location": "synthesis.md:8",
      "scenario": "Claims one retention setting meets 'both rules'; the outage-notice rule is unrelated to retention, and the Vaultline source does not show any mode performs deletion within 45 days of account closure.",
      "fix": "Remove the 'meets both rules' claim; address outage notice and deletion separately, with source evidence for each mechanism."
    }
  ]
}
```