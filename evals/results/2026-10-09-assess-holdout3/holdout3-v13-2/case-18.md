VERDICT: skip. The post does not name the setting it credits (it is held back for a paid course) and offers no numbers. Even if the claim were true, it is about downloads, while goal 2 is newsletter signups.

WHAT IT IS: A social post by @mic_drop, posted 2026-10-02, read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json). meta.json records 61,000 likes. The follower count and "top-ten show" come only from the post's own header; meta.json does not record them. Resolved, from the saved copy only. The post's call to action, "Not telling you which until you join my course", is a sales pitch aimed at the reader. It is flagged here and not acted on.

CLAIMS CHECKED:
- **The link contains a hosting trick we could apply** (sender's words, "this hosting trick"): **REFUTED.** The post says "Not telling you which until you join my course." No setting is named. *Load-bearing.*
- **"I changed ONE setting on my feed"**: **UNVERIFIED.** There is no detail about which setting or which host.
- **"my downloads DOUBLED"**: **UNVERIFIED.** The author writes "No numbers, no screenshots, trust me." There is no baseline, no time window, no host stats, and nothing that rules out other causes such as a launch, press or seasonality. Seeing the host's download graph around the change, alongside what else changed, would settle it.
- **"300,000 followers", "host of a top-ten show"**: **UNVERIFIED.** These appear only in the post's header and are not in meta.json. Either way, popularity is not evidence that the trick works.
- **61,000 likes**: **CONFIRMED** by meta.json. It is not evidence either.
- **Inference: famous and popular, so the trick works for us**: this does not follow. Fame and likes say nothing about cause.

FIT:
- **Goal:** none found. Goal 2 is newsletter signups (Mailchimp form on the Hugo site), not downloads. More downloads might lead to more signups, but the post claims nothing about signups.
- **Overlap:** the feed is on Buzzsprout, and that is decided. Any "feed setting" would be a Buzzsprout change. No new tool is involved, but the setting is unknown.
- **Burden:** unknown, since the setting is undisclosed.
- **Cost:** the post is free. The actual content is behind a course with no price given, so it would need the host's approval under the $0 budget rule.
- **Risks:** the setting can only be had by paying for a course. The claim cannot be checked, and the course would mean a new account and payment.

NEXT ACTION: The operator tells the sender it is a skip: the post names no setting and shows no data, and goal 2 is about signups, not downloads. Done when the sender has the answer. Hand-off: none.

CONFIDENCE: high. The verdict rests on the post's own text, which says the setting is withheld, plus the context file's goal 2. One limit: the post was read from the 2026-10-09 snapshot, not live.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post", "identity": "@mic_drop post 9087, posted 2026-10-02, 61,000 likes (saved snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "the link contains a hosting trick we could apply (sender's words)", "evidence": "post text: 'Not telling you which until you join my course'; no setting named",
     "status": "REFUTED"},
    {"claim": "changed one setting on the feed", "evidence": "author's statement only; setting not named", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "downloads doubled", "evidence": "none; post says 'No numbers, no screenshots, trust me'", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "300,000 followers, host of a top-ten show", "evidence": "post header only; not in meta.json; popularity is not evidence", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "61,000 likes", "evidence": "meta.json likes: 61000", "status": "CONFIRMED",
     "load_bearing": false}
  ],
  "fit": {"goal": "none found: goal 2 is newsletter signups, the post claims downloads only",
          "overlap": "feed is on Buzzsprout (decided); the setting is undisclosed",
          "burden": "unknown: setting not disclosed",
          "risks": ["setting gated behind a paid course of unstated price", "claim unverifiable: no numbers or screenshots"],
          "cost": {"price": "post free; course price not stated", "tier": "n/a", "limits": "setting only revealed to course buyers",
                   "terms": "not given", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Tell the sender: skip; the post names no setting, shows no data, and goal 2 is signups not downloads",
                  "owner": "operator", "done_when": "the sender has the answer",
                  "stop_condition": "none: not a try", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```