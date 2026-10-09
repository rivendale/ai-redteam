VERDICT: skip. The post doesn't name the setting, offers no numbers, and is about downloads, while goal 2 is newsletter signups, so there is nothing here to act on for that goal.

WHAT IT IS: A social post by @mic_drop, posted 2026-10-02, at https://social.example.test/@mic_drop/post/9087. I read it from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. meta.json records 61,000 likes. The "300,000 followers" and "host of a top-ten show" appear only in the post header, and meta.json does not record either. The post is three sentences and has no link to a method or data.

Text in the post that directs the reader, flagged: *"Not telling you which until you join my course."* and *"trust me"*. This is a sales pitch for a paid course. I did not follow it.

CLAIMS CHECKED:
- **"I changed ONE setting on my feed and my downloads DOUBLED."** The evidence is the author's word only. The post itself says "No numbers, no screenshots", and it gives no baseline, time window or source for the download counts. Nothing in the item settles it either way: **UNVERIFIED**. The verdict does not rest on it. Even if true, the setting is unknown and downloads are not goal 2.
- **"The setting is not disclosed in the post"** (from the post's own text: "Not telling you which until you join my course"): **CONFIRMED**. The verdict rests on this. There is no change we could make.
- **"Famous podcaster, host of a top-ten show, 300,000 followers"** (the sender's words and the post header): this is self-description with no chart or ranking cited: **UNVERIFIED**. The verdict does not rest on it. Fame and follower counts are not evidence for the trick in any case.
- **"61,000 likes"**: matches meta.json: **CONFIRMED**. The verdict does not rest on it. Likes measure popularity, not whether the trick works.
- **The sender's inference that this helps goal 2.** Two parts:
  - The post claims downloads only. It says nothing about newsletter signups.
  - A download gain for a top-ten show would not necessarily carry over to a 3,000-download show.

  Nothing in the item supports either step: **UNVERIFIED**. The verdict does not rest on it; it is covered under Fit.

FIT:
- **Goal:** none found. Goal 2 is "Grow the newsletter: more listeners sign up". The post is about feed downloads, which is not goal 2 and not any other listed goal.
- **Overlap:** any feed setting would be a Buzzsprout setting. Buzzsprout is our host and keeping it is already decided. Newsletter signups run through Mailchimp's form on the Hugo site, which the post does not touch.
- **Burden:** unknown, because the setting is not named.
- **Cost:** the post is free to read (as of 2026-10-09). Learning the setting requires the author's course, whose price and terms are not given. Buying it would also need the host's approval under the paid-subscription, account and $0-budget constraints. I am not recommending it.
- **Risks:** an unverifiable claim used to sell a course. An undisclosed feed change could also affect our RSS feed on Buzzsprout.

NEXT ACTION: Reply to the sender that the post is a course pitch: it doesn't name the setting, gives no numbers, and is about downloads rather than newsletter signups, so there is nothing to do for goal 2.
- **Owner:** operator.
- **Done when:** the reply is sent.
- **Hand-off:** none.

CONFIDENCE: high. The post was read in full from the 2026-10-09 snapshot, the claims the verdict rests on are confirmed from the post's own text, and the context file is present. The doubling claim stays unverified, but the verdict does not depend on it.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post", "identity": "@mic_drop post 9087, posted 2026-10-02, 61,000 likes (snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "changing one feed setting doubled the author's downloads", "evidence": "author's word only; the post says 'No numbers, no screenshots'", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "the post does not disclose which setting was changed", "evidence": "post text: 'Not telling you which until you join my course'", "status": "CONFIRMED"},
    {"claim": "famous podcaster, host of a top-ten show, 300,000 followers", "evidence": "self-description in the post header; not in meta.json, no chart cited", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "61,000 likes", "evidence": "meta.json likes: 61000", "status": "CONFIRMED",
     "load_bearing": false},
    {"claim": "the trick would grow our newsletter signups (goal 2)", "evidence": "the post speaks only of downloads, says nothing of signups, and gives no reason a top show's result carries to a 3,000-download show", "status": "UNVERIFIED",
     "load_bearing": false}
  ],
  "fit": {"goal": "none found: goal 2 is newsletter signups; the post is about downloads",
          "overlap": "any feed setting lives in Buzzsprout (already decided as host); signups run through Mailchimp's form on the Hugo site",
          "burden": "unknown: the setting is not named",
          "risks": ["unverifiable claim used to sell a course", "undisclosed change to our RSS feed"],
          "cost": {"price": "post free; the course is required to learn the setting, price not given", "tier": "none",
                   "limits": "setting withheld behind the course", "terms": "not given",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Reply to the sender that the post is a course pitch with no named setting and no numbers, about downloads rather than newsletter signups, so nothing to do for goal 2",
                  "owner": "operator", "done_when": "the reply is sent", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```