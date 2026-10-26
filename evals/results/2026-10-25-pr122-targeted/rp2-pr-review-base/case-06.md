# Review report: fact check of the research synthesis (Track C)

This is a document review, not a code PR, so I adapted the pr-review steps where they don't fit. I've noted each adaptation.

**REVIEWED:** `synthesis.md` plus the three local source copies in `sources/`, as provided in this session. There are no SHAs: the work is not a git repository. Please freeze the reviewed text before release by committing it or hashing the four files. Any later edit to `synthesis.md` has not been reviewed. Line references count from line 1 of each file as provided.

**TIER:** High. Item 4 tells operations leads to change a retention setting that governs how long data is kept. That setting interacts with a regulator's deletion requirement for account data, which counts as data handling and personal data. The leads will act on the document directly. High needs two rounds, ideally from two vendors. **This is round 1 of 2. Round 2 has not run, so under Step 2 the review is not complete.**

**REVIEWERS:** Round 1 was a separate instance (Claude Opus 5.5, `claude-opus-5-5`) with no part in writing the synthesis. The author is unknown because there are no commit trailers. Data handling: only the provided local copies were read, nothing was sent anywhere, and nothing was executed.

**Coverage limits:**
- I had no tools or network. I checked the synthesis against the local source copies, retrieved 2026-10-20, but could not confirm those copies match the live URLs.
- I did not visit any endpoint.

### Claims checked and supported

| Synthesis claim | Source | Result |
|---|---|---|
| Rule 14, 72 hours' notice before a planned outage (`synthesis.md:3-4`) | `sources/northline-rulebook.md:6` | Rule number and period are correct. The scope qualifier is dropped (finding 3). |
| Quote "Account data is deleted within 45 days of account closure" (`synthesis.md:5-6`) | `sources/eastport-gn3.md:7` | The quote is verbatim. |
| Deletion requirement is GN-3 paragraph 3.4 (`synthesis.md:7`) | `sources/eastport-gn3.md:7` | Correct. |
| Vaultline values: `standard` = 30 days, `extended` = 365 days (`synthesis.md:8`) | `sources/vaultline-retention.md:4` | The values and durations are correct. |

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `synthesis.md:8-9` (cites `sources/vaultline-retention.md:4-5`) | **Unsupported claim and recommendation.** The cited source only lists the allowed values and their durations. It does not say which records are "still needed", for how long, or that `standard` deletes anything. It also gives no reason to choose `extended`. Leads who act on this would change a production retention setting based on a reason no cited source contains. | For each sentence in item 4, find supporting text in a cited source. Today "would delete records still needed" and "set … extended" have none. The check passes once a source for the retention need is cited, or the sentence is reworded as an unsourced recommendation with an owner. |
| 2 | P1 | `synthesis.md:8-9` against `sources/eastport-gn3.md:7` | **Cross-source conflict the synthesis does not mention.** GN-3 3.4 requires account data to be deleted within 45 days of account closure. Item 4 recommends 365-day retention. Suppose Vaultline holds account data, or backups of it (GN-3 3.2 covers backups), and the organisation is in GN-3's scope (3.1, "processors of account data"). Then `extended` could keep closed-account data for up to 365 days, well past the 45-day limit, and following the synthesis would put the organisation out of line with the guidance. Evidence level: inference. No provided source says what data Vaultline stores, or whether `retention_mode` keeps or deletes data after the stated period. | Ask whoever owns Vaultline whether the buckets under `retention_mode` contain GN-3 account data. If they do, the synthesis must reconcile items 2 and 4: a 45-day ceiling for account data, or a documented exception. Today the synthesis passes items 2 and 4 together without flagging any conflict. |
| 3 | P3 | `synthesis.md:3-4` against `sources/northline-rulebook.md:6` | **Scope qualifier dropped.** Rule 14 covers planned outages "of a customer-facing service" and binds "Members". The synthesis says it covers any planned outage. Leads might give 72 hours' notice for internal maintenance, which is over-compliance with low harm. They might also assume the rule binds the organisation without checking membership. | The paraphrase keeps both "customer-facing service" and the members-only applicability. Today it keeps neither. |
| 4 | P3 | `synthesis.md:5-6` against `sources/eastport-gn3.md:4` | **Applicability omitted.** GN-3 applies only to "processors of account data" (3.1), and it is a guidance note. The synthesis presents the 45-day deletion as a general obligation without saying who it binds. | Item 2 states GN-3's scope, or states that the organisation has confirmed it is in scope. Today it does neither. |

**FILES NEEDED BUT NOT PROVIDED:**
- Any source for the claim that records are needed beyond 30 days (finding 1).
- A Vaultline description of what data sits under `retention_mode`, and what happens when the period ends (finding 2).
- Confirmation that the organisation is a Northline member and a GN-3-scope processor (findings 3 and 4).
- Live source versions, to confirm the 2026-10-20 local copies are faithful.

### Close-out

**ADJUDICATION:** Pending. The author must decide every finding (Accepted, Deferred or Rejected, with evidence). The reviewer does not adjudicate its own findings. Findings 1 and 2 are P1 and cannot be deferred.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | pending | |
| 2 | pending | |
| 3 | pending | |
| 4 | pending | |

**VERIFIED AFTER FIXES:** None yet. Each correction should get a targeted re-read of the changed text against its cited source, not a full re-review.

**MERGE RECOMMENDATION:** **Do not send to the operations leads yet.**
- Two P1 findings are open. Item 4's recommendation is unsupported by its source, and it may conflict with GN-3 3.4.
- The High tier's second independent round has not run.
- An owner decision is pending on which retention period applies to Vaultline data in GN-3's scope.

Items 1–3 are accurate as citations. Once findings 3 and 4 are addressed they could go out separately.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "source-text (absence of support in cited source)",
      "location": "synthesis.md:8-9; sources/vaultline-retention.md:4-5",
      "scenario": "The cited source only lists retention_mode values (off, standard 30 days, extended 365 days). It does not support the claim that 'standard would delete records still needed' or the recommendation to set extended. Leads would change a production retention setting on an unsourced rationale.",
      "fix": "Cite a source for the retention need and its duration, or reword item 4 as an unsourced recommendation with a named owner."
    },
    {
      "severity": "P1",
      "evidence_level": "inference (cross-source conflict; Vaultline data contents unknown)",
      "location": "synthesis.md:8-9 vs sources/eastport-gn3.md:7 (and 4-5)",
      "scenario": "GN-3 3.4 requires account data deleted within 45 days of closure (3.2 covers backups). If Vaultline holds in-scope account data, setting extended (365 days) could keep closed-account data up to 365 days, against the guidance. The synthesis presents items 2 and 4 without reconciling them.",
      "fix": "Confirm what data Vaultline stores and what retention_mode does when the period ends. Reconcile item 4 with the 45-day ceiling or document an exception approved by the owner."
    },
    {
      "severity": "P3",
      "evidence_level": "source-text",
      "location": "synthesis.md:3-4 vs sources/northline-rulebook.md:6",
      "scenario": "The synthesis drops 'of a customer-facing service' and the fact that the rule binds Members. Leads may over-apply notice to internal outages, or assume the rule applies without confirming membership.",
      "fix": "Restore the customer-facing qualifier and state the members-only applicability."
    },
    {
      "severity": "P3",
      "evidence_level": "source-text",
      "location": "synthesis.md:5-6 vs sources/eastport-gn3.md:4",
      "scenario": "The synthesis omits GN-3 3.1's scope (processors of account data) and presents the 45-day deletion as a general obligation.",
      "fix": "State GN-3's scope, or that the organisation is confirmed in scope."
    }
  ]
}
```