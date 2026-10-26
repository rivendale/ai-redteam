# Review report: research synthesis fact-check (Track C)

**REVIEWED:** This is not a pull request. The work is `synthesis.md` plus three local source copies (`sources/eastport-gn3.md`, `sources/northline-rulebook.md`, `sources/vaultline-retention.md`), all retrieved 2026-10-20 and supplied inline. The working directory is not a git repository, so there is **no head SHA and no merge base**. The review covers exactly the text supplied in this session. Any later edit is unreviewed.

**TIER: High.** This is regulatory text (outage notice, data deletion) that operations leads will act on. High tier requires **two independent rounds, ideally on two vendors. Only this one round has run.** Under Step 2 the review is therefore incomplete until a second round is done.

**REVIEWERS:** Round 1 was a fresh Claude instance (Opus 5.5, `claude-opus-5-5`) with no part in writing the synthesis. No commit trailers exist, so the author is unknown. Data handling: the sources are public regulatory and vendor documentation, so no restricted data was sent anywhere.

**Method:** Every claim and citation in `synthesis.md` was compared word for word against the cited local copy. I had no tools, so nothing was run and no links were opened. The local copies are taken as the sources and were not checked against the live URLs.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `synthesis.md:3` (item 1) | The synthesis cites **Rule 12** as the 72-hour notice rule, but `sources/northline-rulebook.md:5` says Rule 12 is "Reserved." The obligation is **Rule 14** (`northline-rulebook.md:6`). The synthesis also drops the scope: Rule 14 covers a planned outage *of a customer-facing service*, not every planned outage. A lead citing Rule 12 to a regulator or customer cites an empty rule, and the dropped scope may lead to wrong notice decisions. | Citation check: the rule number cited for "72 hours' notice" must resolve to the source line containing that text. This fails today (Rule 12 → "Reserved"). |
| 2 | P1 | `synthesis.md:5` (item 2) | The text in quotation marks, "account data must be erased promptly, and in any case within 30 days", **does not appear in the source**. GN-3 3.4 (`eastport-gn3.md:8`) says "Account data is deleted within **45** days **of account closure**." The synthesis fabricates a quotation, changes the period (30 vs 45), adds "promptly" and "must", and drops the trigger (account closure). Leads would build deletion SLAs and audit evidence on a quote that a regulator's text does not contain. | Verbatim check: every string in quotation marks attributed to a source must appear in that source. This fails today. |
| 3 | P1 | `synthesis.md:7` (item 3) | The synthesis places the deletion requirement in **paragraph 3.2** of GN-3. Paragraph 3.2 is *Backups* (`eastport-gn3.md:6`). Deletion is **3.4** (`eastport-gn3.md:8`). Anyone checking compliance against 3.2 finds the wrong requirement, and backup encryption could be mistaken for the deletion control. | Citation check: the paragraph number cited for the deletion claim must contain "deleted". This fails today. |
| 4 | P1 | `synthesis.md:8` (item 4) | The synthesis says to set `retention_mode = strict`. The source accepts only `off`, `standard` (30 days) and `extended` (365 days) and states "an unknown value is rejected when the setting is saved" (`vaultline-retention.md:4-5`). An operator following the instruction gets a rejected save, and the intended control is not applied. The synthesis also claims this "meets both rules", but no source links Vaultline retention to Northline outage notice or to GN-3 deletion. The Vaultline source does not say the setting governs deletion of account data after closure. This claim is unsupported, not just mis-valued. | (a) Value check: every config value the synthesis prescribes must appear in the source's allowed list. This fails today (`strict`). (b) Every "meets rule X" claim must cite a source stating that link. This fails today. |

**Note on fixes, not a finding:** do not simply substitute `standard` (30 days) as the fix for #4. Nothing in the sources shows that `retention_mode` controls post-closure deletion of account data. That link needs evidence from Vaultline documentation or the system owner first.

**Clean items:** No claim in the synthesis was fully accurate. Every one of its four items has a defect.

**FILES NEEDED BUT NOT PROVIDED:**
- Live versions of the three source URLs, to confirm the 2026-10-20 copies are current. The review covers the local copies only.
- Any Vaultline documentation linking `retention_mode` to deletion of account data, which claim 4 would need.

---

### Close-out

**Not written.** A reviewer does not adjudicate its own findings. The author must record Accepted / Rejected for each finding. All four are P1, so none can be Deferred.

**ADJUDICATION:** pending (author).

**VERIFIED AFTER FIXES:** none; no fixes yet.

**MERGE RECOMMENDATION: do not release to operations leads.**
- All four claims are wrong or unsupported against their own cited sources: two wrong citations, one fabricated quotation with the wrong deadline, and one invalid config value with an unsupported compliance claim.
- The High tier's second independent round has not run. It should run on a different vendor after the fixes.
- Fixes should then be checked by a targeted re-read of each corrected claim against the source line. A full re-review is not needed for that.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed_against_source",
      "location": "synthesis.md:3",
      "scenario": "Cites Northline Rule 12 for 72-hour planned-outage notice; Rule 12 is 'Reserved' (northline-rulebook.md:5). The obligation is Rule 14 (northline-rulebook.md:6), and it is limited to customer-facing services, a scope the synthesis drops.",
      "fix": "Cite Rule 14 and state its scope: planned outages of a customer-facing service."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_against_source",
      "location": "synthesis.md:5",
      "scenario": "Quoted text 'account data must be erased promptly, and in any case within 30 days' does not appear in GN-3. Source 3.4 says 'deleted within 45 days of account closure' (eastport-gn3.md:8). The quote is fabricated, the deadline is wrong, and the trigger is missing.",
      "fix": "Replace with the verbatim source text: 'Account data is deleted within 45 days of account closure.' Remove the invented wording."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_against_source",
      "location": "synthesis.md:7",
      "scenario": "Places the deletion requirement in GN-3 paragraph 3.2, which is Backups (eastport-gn3.md:6). Deletion is 3.4 (eastport-gn3.md:8).",
      "fix": "Cite paragraph 3.4."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed_against_source",
      "location": "synthesis.md:8",
      "scenario": "Prescribes retention_mode = strict. Valid values are off/standard/extended, and unknown values are rejected on save (vaultline-retention.md:4-5), so the instruction fails. The claim that it 'meets both rules' is unsupported: no source links retention_mode to outage notice or to post-closure deletion.",
      "fix": "Remove the invalid value and the 'meets both rules' claim. Prescribe a setting only with a source showing that retention_mode governs post-closure account-data deletion."
    }
  ]
}
```