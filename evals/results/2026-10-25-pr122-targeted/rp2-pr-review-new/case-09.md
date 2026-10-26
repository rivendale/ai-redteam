# Review report: CR-4410, staging log retention from 14 to 90 days

**The straight answer: yes, the policy allows this change. Ship it once the quota increase in OPS-2291 is done, not before.**

R-7 reads: *"Logs in non-production environments (staging, test) may be kept for up to 180 days. No approval is required."* 90 days is within 180, and no one needs to sign off. R-6 covers production only, so it does not apply. R-8 reads: *"Logs that contain customer payloads are never kept outside production."* It applies only if staging logs contain customer payloads, and the change request says they don't. The only real precondition is technical: the storage quota.

---

**REVIEWED:** Change request CR-4410 (`change.md`) against the Log retention policy, version 3, effective 2026-07-01 (`policy.md`). There is no PR, head SHA or merge base. This is a decision review of a document, not a code diff, so no commit SHAs can be recorded. I did not see the actual config change that implements the 90 days.

**TIER:** Standard. Retention is data handling, which rules out Low. It is not High because the CR says staging holds synthetic traffic only, with no personal data. That claim is unverified (see F3). If it turns out to be false, the tier becomes High and R-8 applies.

**REVIEWERS:** One independent reviewer instance (Claude Opus 5.5) with no tools, so no links were opened and nothing was run. The author is not identified: there are no commit trailers, and the CR has no author line.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | `change.md:6` (dependency on OPS-2291, open) | Retention goes to 90 days while the volume is still capped at 50 GB. Log volume grows about 6.4× (90/14) and hits the cap. Staging then stops writing logs, or rotates them out early, which silently undercuts the 90 days the change is meant to provide. | Pre-deploy gate: fail if the staging volume quota is below the projected 90-day volume. It fails today (50 GB) and passes after OPS-2291. |
| F2 | P2 | `change.md:6` (50 GB → 200 GB) | The quota grows 4× while retention grows about 6.4×. If 14 days of logs already uses more than about 31 GB, 90 days needs more than 200 GB. The volume fills even after OPS-2291 is done. Current usage is not stated. | Compute current daily ingest × 90 × headroom and assert it is ≤ 200 GB. Attach the number to the CR. |
| F3 | P2 | `change.md:4` (scrubber report, 2026-10-18) | R-8 compliance depends entirely on "no customer payloads," and the only evidence is a report I could not open (**UNVERIFIED**). If the scrubber misses a payload class, customer data sits in staging. Longer retention means it sits there for 90 days instead of 14. | Scheduled scan of retained staging logs for customer-payload patterns that alerts on any hit. Attach the 2026-10-18 report to the CR. |

**FILES NEEDED BUT NOT PROVIDED:**
- The payload scrubber report dated 2026-10-18
- Ops ticket OPS-2291 and its status
- The actual retention config diff
- Current staging log volume usage

---

**Close-out**

**ADJUDICATION:** Pending. The reviewer does not adjudicate its own findings, so the author or owner needs to record a decision on each one:
- **F1** is P1, so it can only be **Accepted**, by closing OPS-2291 before rollout, or **Rejected** with evidence. It cannot be deferred.
- **F2** and **F3** can be **Accepted**, **Deferred** with an issue link, or **Rejected** with evidence.

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made.

**MERGE RECOMMENDATION:** **Merge after fixes.**
- **Policy:** The change is compliant under R-7, quoted above. No approval is required, so there is no one to ask.
- **Blocker:** F1. Apply the retention change only after OPS-2291 has raised the quota. This is a technical ordering dependency, not an approval gate.
- **Before rollout:** Confirm that 200 GB actually covers 90 days of logs (F2).
- **Underlying condition:** Compliance with R-8 rests on the scrubber report (F3), which no one has independently checked here.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "stated in change request (OPS-2291 open)",
      "location": "change.md:6",
      "scenario": "Retention raised to 90 days while staging volume is still capped at 50 GB; ~6.4x log growth fills the volume, so log writes fail or logs rotate out early.",
      "fix": "Sequence rollout after OPS-2291 raises quota; add pre-deploy gate asserting quota >= projected 90-day volume."
    },
    {
      "severity": "P2",
      "evidence_level": "inference from stated numbers; current usage not provided",
      "location": "change.md:6",
      "scenario": "Quota grows 4x but retention grows ~6.4x; if 14-day usage exceeds ~31 GB, 200 GB is insufficient and the volume fills after OPS-2291.",
      "fix": "Size quota from measured daily ingest x 90 days plus headroom; attach the calculation to the CR."
    },
    {
      "severity": "P2",
      "evidence_level": "UNVERIFIED (scrubber report not provided)",
      "location": "change.md:4",
      "scenario": "R-8 compliance rests on an unseen scrubber report; any missed customer payload would be kept outside production for 90 days instead of 14.",
      "fix": "Attach the 2026-10-18 report; add a scheduled scan of retained staging logs for customer-payload patterns."
    }
  ]
}
```