# pr-review: fact check of `synthesis.md` (Track C)

**Where the skill doesn't fit:** This is a research synthesis, not a pull request. I adapted three things:

- **No commits:** There is no repository, head SHA or merge base. The frozen target is the text of the four files exactly as supplied in this session.
- **"Run it" became "check every claim against its source copy":** Each claim in `synthesis.md` was compared with the local copy it cites.
- **Live pages not checked:** I had no tools and no network, so I could not compare the local copies with the live URLs. The copies are dated 2026-10-20.

## Review report

**REVIEWED:** `synthesis.md` plus `sources/northline-rulebook.md`, `sources/eastport-gn3.md` and `sources/vaultline-retention.md`, as supplied in this session. No head SHA or merge base exists because there is no VCS.

**TIER: High.**
- The synthesis covers data deletion and retention obligations (data handling) and paraphrases regulator guidance (regulated text).
- Operations leads will act on it.
- High tier needs two rounds, ideally on two vendors. **This is round 1 of 2, and the second round has not run.** Under the skill's rules, this synthesis is not yet reviewed.

**REVIEWERS:**
- Reviewer: this session, Claude Opus 5.5 (`claude-opus-5-5`), with no part in writing the synthesis.
- Author: unknown. No commit trailers or authorship metadata were supplied.

**Data handling (Step 3):** The material is public regulatory and vendor-documentation text with no personal data. It was not sent anywhere outside this session.

**Instructions addressed to the reviewer:** None found in the work.

**Claims that check out:**
- Claim 2's quote matches `sources/eastport-gn3.md:7` word for word.
- Claim 3's citation of paragraph 3.4 is correct.
- Claim 1 has the right rule number (Rule 14) and the right notice period (72 hours).
- Claim 4 gives the 30-day value for `standard` correctly.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `synthesis.md:8-9` (claim 4) vs `sources/eastport-gn3.md:7` | **Recommendation may conflict with the 45-day deletion rule.** Claim 4 recommends `retention_mode = extended`, which keeps data 365 days (`vaultline-retention.md:4`). Claim 2 says account data is deleted within 45 days of account closure. If the Vaultline store holds account data, following claim 4 keeps closed accounts' data for up to 365 days, against GN-3 3.4. `standard` (30 days) would fall inside 45 days. The synthesis does not acknowledge or resolve the conflict. Neither source says what Vaultline stores or how its "retention" relates to closure deletion. That makes this an unresolved conflict found by inference, not a confirmed breach, but leads acting on claim 4 could create a compliance exposure. | Add an explicit check: "Does the Vaultline store hold Eastport account data? If so, show that the chosen retention_mode meets GN-3 3.4's 45-day deletion." Claim 4 fails this today because it is silent. |
| 2 | P1 | `synthesis.md:8-9` (claim 4) | **Unsupported claim.** "`standard` (30 days) would delete records still needed" appears in no cited source. `vaultline-retention.md` lists only the allowed values and their durations. It says nothing about which records are needed or for how long. The whole recommendation rests on this uncited claim, and leads may change a production retention setting because of it. | Map each assertion in claim 4 to a quoted source sentence. "Would delete records still needed" has no match today. Either cite the source that sets the need, or remove the recommendation and state only the facts. |
| 3 | P2 | `synthesis.md:3-4` (claim 1) vs `sources/northline-rulebook.md:6` | **Scope dropped.** Rule 14 covers "a planned outage of a customer-facing service" and binds "Members". The synthesis says "a planned outage" with no qualifier. Leads may apply 72-hour notice to internal-only maintenance, which is unnecessary process and possibly delayed work. The paraphrase also hides that the rule binds only Council members. Workaround: read the rule text. | Compare the scope qualifiers in each paraphrase with the source sentence. "customer-facing service" is missing today. |
| 4 | P2 | `synthesis.md:7` (claim 3) vs `sources/eastport-gn3.md:1,7` | **Overstated legal force.** Claim 3 calls 3.4 "the deletion requirement". The source is a regulator's *Guidance Note*, and 3.4 is written descriptively ("is deleted"), not as a "must". The copy does not show whether GN-3 is binding. Leads may treat guidance as a hard legal obligation, or later find the synthesis overstated its legal force. Note also that GN-3 3.1 limits it to "processors of account data". | Check that each "requirement" or "obligation" label is backed by source text establishing binding force. Claim 3 fails this today. Reword as "GN-3 guidance, paragraph 3.4", or cite the instrument that makes it binding. |

**FILES NEEDED BUT NOT PROVIDED:**
- **Live sources:** Current versions of the three URLs, to confirm the 2026-10-20 copies are still accurate. I did not visit them.
- **What Vaultline stores:** A description of what the Vaultline store holds and what "retention" means there (kept after deletion vs. deleted after the period). Needed to settle finding 1.
- **Basis for "records still needed":** Any internal requirement behind the retention-need claim. Needed to settle finding 2.
- **GN-3's legal status:** The instrument that makes GN-3 binding, if any. Needed to settle finding 4.
- **Membership:** Whether the organisation is a Northline Council member. Needed for finding 3's scope question.

## Close-out

Pending. Under the skill, the author adjudicates these findings and whoever closes the review writes the close-out. A reviewer never adjudicates its own findings.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1–4 | Awaiting author | — |

**VERIFIED AFTER FIXES:** Nothing yet. Fixes should be checked with a targeted re-read of the changed claims against the source lines cited above, not a full new round.

**MERGE RECOMMENDATION: do not release to operations leads yet.**
- Two P1 findings are open (1 and 2), and P0/P1 findings cannot be deferred.
- The High-tier second review round has not run.
- An owner decision is pending on whether Vaultline holds Eastport account data, which decides the retention-mode recommendation.

Claims 2 and 3's citations, and claim 1's rule number and period, can stand once the wording fixes in findings 3 and 4 are made.

```json
{
  "verdict": "do_not_release",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "inference (sources do not state what Vaultline stores; conflict is unresolved, not confirmed)",
      "location": "synthesis.md:8-9 vs sources/eastport-gn3.md:7",
      "scenario": "Claim 4 recommends retention_mode=extended (365 days). If the Vaultline store holds account data, this retains closed accounts' data far beyond GN-3 3.4's 45-day deletion, contradicting claim 2. The synthesis does not address the conflict.",
      "fix": "Establish whether Vaultline holds Eastport account data and how retention relates to closure deletion; reconcile claim 4 with GN-3 3.4 or scope the recommendation explicitly."
    },
    {
      "severity": "P1",
      "evidence_level": "confirmed (absent from cited source)",
      "location": "synthesis.md:8-9",
      "scenario": "'standard (30 days) would delete records still needed' is not in sources/vaultline-retention.md, which only lists values and durations. Leads may change a production retention setting on an uncited premise.",
      "fix": "Cite the source of the retention need, or remove the recommendation and state only the documented values."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed (source text comparison)",
      "location": "synthesis.md:3-4 vs sources/northline-rulebook.md:6",
      "scenario": "Rule 14 applies to Members and to planned outages of customer-facing services; the synthesis drops both qualifiers, so leads may impose 72-hour notice on internal maintenance or assume applicability without membership.",
      "fix": "Restore 'of a customer-facing service' and note the rule binds Council members."
    },
    {
      "severity": "P2",
      "evidence_level": "confirmed (source text comparison); binding status unknown",
      "location": "synthesis.md:7 vs sources/eastport-gn3.md:1,4,7",
      "scenario": "Claim 3 labels GN-3 3.4 a 'requirement', but the source is a guidance note phrased descriptively and scoped to processors of account data; leads may misjudge its legal force.",
      "fix": "Reword as 'GN-3 guidance, paragraph 3.4 (applies to processors of account data)', or cite the instrument that makes it binding."
    }
  ]
}
```