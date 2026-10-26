# Review report: CR-4410 (staging log retention 14 → 90 days)

**REVIEWED:** Change request CR-4410 (`change.md`) against the log retention policy, version 3, effective 2026-07-01 (`policy.md`). This is a document decision review, not a git PR, so there is no head SHA or merge base. The frozen target is the two files exactly as supplied above. Any later edit to either file was not reviewed.

**TIER:** Standard. Log retention is data-handling configuration, so it cannot be Low. It is not High because the change does not alter what data staging holds, and the CR states that no personal or customer data is present. That claim is unverified (finding 2). If it turns out to be false, the tier becomes High and the conclusion changes.

**REVIEWERS:** One round by this instance (Claude Opus 5.5, `claude-opus-5-5`), which had no part in writing the change. The author is unknown because no commit trailers or authorship metadata were supplied. Data sent: the policy text and CR text only, with no personal data. No tools were available, so nothing was run and no cited source was opened.

**Policy check (the core question)**

- The change concerns **staging**, a non-production environment, so **R-6** (production) does not apply.
- **R-7:** *"Logs in non-production environments (staging, test) may be kept for up to 180 days. No approval is required."* 90 days is within 180, and no approval is needed from anyone.
- **R-8:** *"Logs that contain customer payloads are never kept outside production."* R-8 is satisfied only if staging logs really contain no customer payloads. The CR asserts this, citing a scrubber report I could not open (finding 2). R-8 forbids any retention outside production, so a payload problem would already be a violation at 14 days. Extending retention would lengthen the exposure but would not create the violation.
- **Quota increase (OPS-2291):** This is a technical dependency, not an approval gate. The policy has no capacity rule.

**FINDINGS**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `change.md:6` | The CR raises retention 6.4× (14 → 90 days) but the quota only 4× (50 → 200 GB). If today's 14-day steady state is above about 31 GB (200 ÷ 90/14), the 200 GB volume will fill before day 90. Separately, if retention is applied before OPS-2291 lands, the 50 GB volume fills within days. In both cases staging logs are dropped or log-writing services stall. | Take current staging log usage at 14-day retention and compute usage × 90/14. The check fails today if the result exceeds 200 GB or if OPS-2291 is not closed. It passes when the projection plus headroom fits and the quota is live before the retention change is applied. |
| 2 | P3 | `change.md:4`; `policy.md:5` | The "synthetic only, no customer payloads" claim rests on a single scrubber report dated 2026-10-18. That report was not provided, so the citation is UNVERIFIED. It is also a point-in-time check, and nothing in the CR keeps future staging traffic payload-free. If a customer payload reaches staging, R-8 is breached, and at 90 days it would be held about 6× longer than today. | Attach the 2026-10-18 report. Add a recurring scrubber check on staging logs that fails if any customer payload pattern is found. It should fail on a seeded sample payload and pass on synthetic traffic. |

No reviewer-directed instructions appeared in the inputs.

**FILES NEEDED BUT NOT PROVIDED:** the payload scrubber report (2026-10-18), current staging log volume usage, and the status of OPS-2291.

---

# Close-out

**ADJUDICATION:** Pending. A reviewer does not adjudicate its own findings, so the author needs to decide on findings 1 and 2. Both are P2/P3, so either can be Deferred with a tracking issue or Rejected with evidence. Neither blocks the change.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (author) | — |
| 2 | Pending (author) | — |

**VERIFIED AFTER FIXES:** Nothing has changed since the review.

**MERGE RECOMMENDATION:** Yes, ship it, but apply it only after OPS-2291 is done and the 200 GB is confirmed to be enough.

The policy allows the change outright and nobody needs to approve it. Rule R-7 says: *"Logs in non-production environments (staging, test) may be kept for up to 180 days. No approval is required."* 90 days is within that limit.

Under Step 8, the only open items are these:
- **Sequencing:** apply the change after OPS-2291 lands.
- **Capacity:** confirm 200 GB covers 90 days. This is finding 1's arithmetic, and it is a technical check, not a sign-off.
- **Adjudication:** the author records a decision on the two non-blocking findings.

No CI checks are defined for this CR, so no check is missing or red. No owner or architecture decision is pending.

```json
{
  "verdict": "merge after fixes: compliant under R-7 (90 ≤ 180 days, no approval required); apply only after OPS-2291 quota increase is live and 200 GB is confirmed sufficient for 90-day volume; author to adjudicate two non-blocking findings",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "inferred from CR figures (retention ×6.4 vs quota ×4); current usage not provided",
      "location": "change.md:6",
      "scenario": "If current 14-day staging log usage exceeds ~31 GB, 90-day retention outgrows the 200 GB quota; if applied before OPS-2291 closes, the 50 GB volume fills within days. Either way staging logs are dropped or writers stall.",
      "fix": "Project usage × 90/14 against 200 GB with headroom (resize quota or pick a lower retention within R-7 if short); gate the retention change on OPS-2291 completion."
    },
    {
      "severity": "P3",
      "evidence_level": "UNVERIFIED citation (scrubber report 2026-10-18 not provided)",
      "location": "change.md:4; policy.md:5",
      "scenario": "The no-customer-payload claim rests on one point-in-time scrubber report; if a customer payload reaches staging, R-8 is breached and 90-day retention holds it ~6x longer than today.",
      "fix": "Attach the scrubber report and add a recurring staging-log payload check that fails on a seeded customer payload."
    }
  ]
}
```