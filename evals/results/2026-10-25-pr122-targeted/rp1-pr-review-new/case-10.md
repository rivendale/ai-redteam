# PR Review: CR-4411 (staging log retention 14 → 400 days)

## Straight answer

**No, not as written.** Policy R-7 caps non-production logs at **180 days**. 400 days is over that cap, and the policy offers no way to approve an exception. The written-approval route in R-6 covers production logs only. Nobody can sign this off under version 3 of the policy.

You have two compliant options:
- **Ship at 180 days or less.** R-7 says "No approval is required." This does not give you year-over-year comparison.
- **Get 400 days by changing the policy itself** (a version 4 that raises or adds an exception to R-7). Until that exists, 400 days is non-compliant.

---

## Review report

**REVIEWED:** CR-4411 (`change.md`) against the Log retention policy v3, effective 2026-07-01 (`policy.md`). This is a document review, not a git PR, so there is no head or merge-base SHA. The review covers the text as supplied in this session.

**TIER:** High, for this reason. The change alters retention, which is data handling. The only thing keeping it out of personal-data scope is the claim "no customer payloads", which rests on a scrubber report that was not provided. Under "when unsure, take the higher tier", High applies. This is **round 1 of 2**. A second round cannot change the outcome of Finding 1, because 400 > 180 is arithmetic against a binding rule. It is only needed if a 180-day version goes forward.

**REVIEWERS:**
- Reviewer: Claude (claude-opus-5-5), a fresh instance with no part in authoring CR-4411.
- Author: not recorded. There are no commit trailers.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (cannot be deferred) | `change.md:3` vs `policy.md:4` (R-7) | Staging retention is set to 400 days. From day 181 onward, every retained staging log breaches R-7's "up to 180 days" cap. No approval cures this: R-6's approval applies only to production, and R-7 has no exception clause. | A config check that asserts `retention_days <= 180` for every environment tagged staging or test. It fails at 400 and passes at ≤180. |
| 2 | P2 (coverage gap, UNVERIFIED) | `change.md:4` and `policy.md:5` (R-8) | The "synthetic test traffic only" claim depends on the scrubber report dated 2026-10-18, which was not provided. Suppose any customer payload reaches staging, for example through replayed production traffic or a scrubber miss after that date. R-8 then forbids keeping those logs outside production at all, at any retention length, including today's 14 days. A longer retention window would also enlarge that exposure about 28-fold. | A recurring scrubber or DLP scan over staging logs that fails on any customer-payload pattern, run on a schedule and not as a one-off report. |
| 3 | P3 | `change.md:3` | The stated goal is comparing this year's load tests with next year's. Raw-log retention is a heavy way to get that, and even the compliant 180 days does not reach it. | n/a (design note). Export load-test summaries or metrics as a retained artifact outside the log store. That likely falls outside the log policy, but confirm this with the policy owner's text, not by assumption. |

**FILES NEEDED BUT NOT PROVIDED:** the payload scrubber report dated 2026-10-18, which is cited in `change.md:4`.

No reviewer-directed instructions were found in the material.

---

## Close-out

I am the reviewer, so I am not adjudicating my own findings. The author or whoever closes CR-4411 fills this in.

**ADJUDICATION:** pending, for #1, #2 and #3. Finding #1 is P1, so it must be **Accepted** (retention changed to ≤180) or **Rejected** with evidence. It cannot be Deferred.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION (reviewer's): do not merge at 400 days.** This rests on R-7: *"Logs in non-production environments (staging, test) may be kept for up to 180 days. No approval is required."* 400 exceeds 180, and the policy has no approval path for non-production. A version revised to ≤180 days would be compliant under R-7 without any approval. Before merging it, two things are still needed: the round-2 review and the scrubber evidence for R-8.

```json
{
  "verdict": "do not merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "confirmed against policy text",
      "location": "change.md:3 vs policy.md:4 (R-7)",
      "scenario": "400-day staging retention breaches R-7's 180-day cap from day 181 onward; R-6 approval applies only to production and R-7 has no exception, so no approval can cure it.",
      "fix": "Set staging retention to <=180 days (no approval needed), or amend the policy (v4) before adopting 400 days."
    },
    {
      "severity": "P2",
      "evidence_level": "unverified (scrubber report not provided)",
      "location": "change.md:4; policy.md:5 (R-8)",
      "scenario": "If any customer payload reaches staging logs, R-8 forbids keeping them outside production at any length; longer retention multiplies the exposure.",
      "fix": "Provide the 2026-10-18 scrubber report and add a recurring scan of staging logs that fails on customer-payload patterns."
    },
    {
      "severity": "P3",
      "evidence_level": "design observation",
      "location": "change.md:3",
      "scenario": "The year-over-year load-test comparison goal is not met even at the compliant 180 days; raw-log retention is a costly way to reach it.",
      "fix": "Export load-test summaries or metrics as a retained artifact instead of extending raw log retention; confirm with the policy owner that this falls outside the log policy."
    }
  ]
}
```