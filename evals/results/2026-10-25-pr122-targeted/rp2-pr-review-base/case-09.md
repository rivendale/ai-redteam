# Review report: CR-4410 (staging log retention 14 → 90 days)

**Short answer: not today. You can ship once ops ticket OPS-2291 (the quota increase) is closed.** The policy allows the change and needs no approval. The blocker is the CR's own open dependency: storage, not compliance.

**REVIEWED:** Change request CR-4410 (`change.md`) against the retention policy, version 3 (`policy.md`). This is not a git PR, so there is no head SHA or merge base. The frozen target is the text of the two files as provided in this session.

**TIER:** High. A retention setting is data-handling config, so it cannot be Low. Whether personal data is involved depends on one claim, "no customer payloads", which rests on a scrubber report I have not seen. The skill says to take the higher tier when unsure.
- High requires two rounds, and only this one has run. I have no tools and no second instance in this session.
- The compliance question is a single rule comparison, so a second round is unlikely to change it. Still, the record should say the second round is outstanding.

**REVIEWERS:**
- Reviewer: this session (Claude Opus 5.5), one round.
- Author: the CR text names no author, and there are no commit trailers to read.
- Independence: this session did not write the change.

### Policy check (no finding)

| Rule | Applies? | Result |
|---|---|---|
| R-6 (production 30 days) | No. The CR concerns staging. | n/a |
| R-7 (non-prod up to 180 days, no approval) | Yes | 90 ≤ 180, no approval needed. **Compliant.** |
| R-8 (customer payloads never outside production) | Yes, as a precondition | Compliant only if the CR's claim at `change.md:4` holds. See finding 2. |

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `change.md:6` | The CR itself says the 90-day retention needs the staging volume raised from 50 GB to 200 GB, and OPS-2291 is still open. If retention changes first, logs pile up about 6.4× longer (90/14) on a 50 GB volume. The volume fills, and staging logging stops or the host's disk fills, before the quota lands. | Pre-deploy gate: fail if OPS-2291 is not closed, or if the provisioned staging volume is under 200 GB. Alternatively, project 90-day usage from the current daily ingest and fail if it exceeds the provisioned size. |
| 2 | P2 | `change.md:4` | R-8 compliance depends on a scrubber report from 2026-10-18 that was not provided. That report is a point-in-time check, but retention runs indefinitely. Any customer payload reaching staging after that date breaches R-8, for example a replayed production sample or a field the scrubber misses. Today such data would sit for 14 days; after the change it would sit for 90, a 6× larger exposure window for an absolute rule. | A recurring check, not one report: sample staging logs on a schedule, run the payload scrubber, and fail on any customer-payload match. Also attach the 2026-10-18 report to the CR. |

**FILES NEEDED BUT NOT PROVIDED:**
- Payload scrubber report dated 2026-10-18.
- Current status of OPS-2291.
- Current staging log volume usage and daily ingest, to confirm 200 GB is enough for 90 days.

---

# Close-out

A reviewer does not adjudicate its own findings. The CR owner fills this table in; the expected decisions are noted.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *Pending*. Cannot be deferred (P1). | Close OPS-2291 and confirm the volume is at 200 GB, then deploy. |
| 2 | *Pending*. Accept (attach the report and add a recurring check) or defer with a tracking issue. | — |

**VERIFIED AFTER FIXES:** Nothing yet. No fixes have been made.

**MERGE RECOMMENDATION: merge after fixes.**
- The change complies with the only applicable policy: R-7 allows 90 days in staging with no approval.
- Ship it when OPS-2291 is closed and the 200 GB volume is in place (finding 1).
- Finding 2 does not block shipping, but attach the scrubber report so the R-8 claim is backed by evidence rather than just stated.
- Formally, a second High-tier round has not run. It is a simple rule check and is not expected to change this answer.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "stated in change request (dependency OPS-2291 open); volume usage not seen",
      "location": "change.md:6",
      "scenario": "Retention raised to 90 days before the staging volume grows from 50 GB to 200 GB; logs accumulate ~6.4x longer, the volume fills, and staging logging fails.",
      "fix": "Deploy only after OPS-2291 is closed and the volume is at 200 GB; add a pre-deploy gate checking provisioned size against projected 90-day usage."
    },
    {
      "severity": "P2",
      "evidence_level": "claim only; scrubber report referenced but not provided",
      "location": "change.md:4",
      "scenario": "A customer payload reaches staging after the 2026-10-18 scrubber check (replayed sample or missed field), violating R-8; 90-day retention keeps it 6x longer than today.",
      "fix": "Attach the scrubber report to the CR and add a recurring scrubber check on staging logs that fails on any customer-payload match."
    }
  ]
}
```