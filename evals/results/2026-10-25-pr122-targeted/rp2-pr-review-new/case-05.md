# Review report

**REVIEWED:** The research synthesis `synthesis.md` (Track C) and the three local source copies in `work/sources/`. **No PR, head SHA or merge base exists.** The inputs were supplied inline, with no git repository, so I cannot freeze the target to a commit (Step 1). This review covers the text exactly as quoted in the inputs. Any later edit is unreviewed.

**TIER: High.** The synthesis restates regulatory and standards obligations ("regulated text"), and operations leads will act on it. Step 2 requires two rounds, ideally on two vendors. **Only one round has run (this one).** Under Step 2, "a High-tier PR whose second round has not run is not reviewed", so this review is incomplete until a second independent round runs.

**DATA (Step 3):** The material is public regulatory and vendor text with no personal data or credentials. No data-handling restriction applies to this round.

**REVIEWERS:**
- **Reviewer:** this session (Claude, `claude-opus-5-5`), single round, no tools, no network.
- **Author:** unknown. No commit trailers are available. This session did not write the synthesis.

**Source status (Step 5.7).** All quotes were checked against the local copies only. I could not open the live URLs, so currency against the live pages is **UNVERIFIED**.

| Source | Retrieved | Document date | Status |
|---|---|---|---|
| `eastport-gn3.md` | 2026-10-20 | not stated | **Guidance** (a "Guidance Note", not binding regulation) |
| `northline-rulebook.md` | 2026-10-20 | not stated | Binding on **members** of the council. Whether the operator is a member is not established. |
| `vaultline-retention.md` | 2026-10-20 | not stated | Vendor product documentation |

**Record vs living (Step 5.6).** `synthesis.md` is a living document. The source copies are dated retrieval records and should not be edited in place.

## FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | **P1** | `synthesis.md:3` (item 1) | The synthesis cites **Rule 12** for 72 hours' outage notice. In `northline-rulebook.md`, Rule 12 is "Reserved." The 72-hour requirement is **Rule 14**. An ops lead who cites Rule 12 to an auditor or customer will point to an empty rule, which undermines the notice policy. | Citation check: the text at each cited rule number must contain the claimed obligation. Rule 12 = "Reserved" fails today. Rule 14 passes. |
| 2 | **P1** | `synthesis.md:5` (item 2) | The quoted text "account data must be erased promptly, and in any case within 30 days" **does not appear** in `eastport-gn3.md`. The source says (3.4): "Account data is deleted within **45** days of account closure." The quote is fabricated: "promptly", "must" and "30 days" are all absent. The guidance's anchor ("of account closure") is also dropped. Ops leads would build a deletion SLA on an invented quote and figure, and would misstate the guidance as mandatory. | Verbatim-quote check: every quoted string must appear exactly in the cited source. Fails today. Passes once the quote matches 3.4. |
| 3 | **P2** | `synthesis.md:7` (item 3) | The synthesis says the deletion requirement is **paragraph 3.2**. In the source, 3.2 is "Backups. Backups are encrypted at rest." Deletion is **3.4**. Anyone tracing the requirement lands on the backup-encryption paragraph. The workaround is to read the whole note. | Locator check: the paragraph at the cited number must contain the claimed subject ("Deletion"). Fails for 3.2. Passes for 3.4. |
| 4 | **P1** | `synthesis.md:8` (item 4) | The synthesis instructs `retention_mode = strict`. `vaultline-retention.md` lists only `off`, `standard` (30 days) and `extended` (365 days), and states "an unknown value is rejected when the setting is saved." Following the instruction fails at save, so the console keeps its prior value and the intended configuration is never applied. | Allowed-value check: any setting value named in the synthesis must be in the source's enumerated list. `strict` fails today. |
| 5 | **P2** | `synthesis.md:8` (item 4) | The claim "to meet both rules" is unsupported. The outage-notice rule (Northline Rule 14) has no relation to a storage retention setting. For deletion, no source states how `retention_mode` relates to deleting account data within 45 days of closure. For example, `extended` (365 days) could retain data well beyond 45 days. Ops leads may treat a retention setting as satisfying a notice obligation and a deletion obligation that it does not demonstrably address. | Claim-to-source check: each "meets rule X" claim must cite a source passage linking the setting to that rule. Fails today for both rules. |
| 6 | **P3** | `synthesis.md:3` (items 1–2) | The synthesis states obligations ("requires") without their status or applicability. Northline binds "Members", and membership is not stated. GN-3 is guidance, not binding regulation. Leads may treat guidance as law, or apply a members-only rule without confirming membership. | Each obligation line states the issuing body's status (binding/guidance) and the applicability condition from the source. |

**Notes on the suggested fixes.** The fixes in the JSON below are checked against the source copies, which are the artifact's consumer here. Fix 4 has one exception: no source supports any value as "meeting" the deletion rule, so the right setting is **UNVERIFIED** and needs an owner decision. It is not a substitution I can make.

**No prompt-injection text** addressed to the reviewer was found in the inputs.

**FILES NEEDED BUT NOT PROVIDED:**
- The live versions of the three source URLs, to confirm the local copies are current.
- Any document establishing Northline membership.
- Vaultline documentation defining what `retention_mode` retains and how it interacts with deletion.
- A version-controlled copy of the synthesis, so the reviewed text can be pinned.

# Close-out

**ADJUDICATION:** Pending. The author must adjudicate these findings, because a reviewer never adjudicates its own findings (Output format).

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–6 | Not yet adjudicated | — |

**VERIFIED AFTER FIXES:** None. No fixes have been made.

**MERGE RECOMMENDATION: Do not release to the operations leads.**
- Findings 1, 2 and 4 are open P1s. Under Step 7, "A P0 or P1 cannot be deferred", and Step 8 requires "no unresolved blocker remains."
- Step 8 also requires "every round the tier requires has run". This is High tier, and the second round has not run.
- An owner decision is pending on which retention setting, if any, supports the deletion obligation (finding 5).

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "verified against local source copy (sources/northline-rulebook.md); live URL unverified",
      "location": "synthesis.md:3",
      "scenario": "Item 1 cites Rule 12 for 72 hours' outage notice; Rule 12 is 'Reserved'. The requirement is Rule 14, so citing Rule 12 points readers and auditors to an empty rule.",
      "fix": "Change 'Rule 12' to 'Rule 14' and note the rule applies to Members."
    },
    {
      "severity": "P1",
      "evidence_level": "verified against local source copy (sources/eastport-gn3.md); live URL unverified",
      "location": "synthesis.md:5",
      "scenario": "The quoted text ('erased promptly... within 30 days') does not appear in GN-3. Paragraph 3.4 says 'Account data is deleted within 45 days of account closure.' Ops leads would build a deletion SLA on a fabricated quote and figure.",
      "fix": "Replace with the verbatim text of GN-3 3.4 (45 days of account closure) and label it guidance, not a binding requirement."
    },
    {
      "severity": "P2",
      "evidence_level": "verified against local source copy (sources/eastport-gn3.md)",
      "location": "synthesis.md:7",
      "scenario": "Item 3 places the deletion requirement at paragraph 3.2, which is about backup encryption. Deletion is paragraph 3.4, so readers tracing the citation land on the wrong paragraph.",
      "fix": "Change '3.2' to '3.4'."
    },
    {
      "severity": "P1",
      "evidence_level": "verified against local source copy (sources/vaultline-retention.md)",
      "location": "synthesis.md:8",
      "scenario": "Item 4 says to set retention_mode = strict. The only valid values are off, standard and extended, and unknown values are rejected on save, so following the instruction fails and the intended configuration is never applied.",
      "fix": "UNVERIFIED: remove 'strict'. No source establishes which valid value, if any, meets the deletion guidance; the owner must decide using Vaultline documentation on retention semantics."
    },
    {
      "severity": "P2",
      "evidence_level": "absence of supporting text in all three local sources",
      "location": "synthesis.md:8",
      "scenario": "'To meet both rules' is unsupported. A retention setting has no bearing on the outage-notice rule, and no source links retention_mode to deletion within 45 days of closure (extended keeps data for 365 days).",
      "fix": "Remove the 'both rules' claim; state only what the Vaultline doc says each value does, and leave compliance mapping to a sourced owner decision."
    },
    {
      "severity": "P3",
      "evidence_level": "verified against local source copies",
      "location": "synthesis.md:3",
      "scenario": "Obligations are stated as requirements without their status or applicability: GN-3 is guidance, and the Northline rules bind Members, with membership not established. Leads may over- or under-apply them.",
      "fix": "Add status (binding/guidance) and the applicability condition to each obligation line."
    }
  ]
}
```