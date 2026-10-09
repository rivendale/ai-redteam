VERDICT: skip. The post does not say what the "one setting" is; it is held back for a paid course. It also claims more downloads, while goal 2 is newsletter signups. That leaves nothing to try and no goal it serves.

WHAT IT IS: Post by @mic_drop, posted 2026-10-02, https://social.example.test/@mic_drop/post/9087. 61,000 likes per meta.json. Read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. The full text is the four sentences quoted in the claims below. It has no numbers, no screenshots and no method.
  Flagged text that tries to direct the reader: "Not telling you which until you join my course." and "trust me." This is a sales funnel, not evidence. Neither line was acted on.

CLAIMS CHECKED:
- "I changed ONE setting on my feed and my downloads DOUBLED". The only evidence offered is the author's word, and the post says so itself: "No numbers, no screenshots, trust me." It gives no baseline, time window, platform, or control for other changes such as season, guests or promotion. **UNVERIFIED.** Not load-bearing: even if it were true, there is no setting to copy.
- The setting is revealed only in a paid course. The post's own text says "Not telling you which until you join my course." **CONFIRMED.** Load-bearing.
- "host of a top-ten show, 300,000 followers" and 61,000 likes. The follower count is the snapshot's header text and the likes come from meta.json. Likes **CONFIRMED** (meta.json); follower count and top-ten status **PROBABLE** (header only, no chart or profile data captured). Not load-bearing. These numbers show popularity, not that the trick works.
- Sender's framing, "this hosting trick" for goal 2. The post talks about a feed setting that raised downloads. Nothing in it mentions newsletter signups, Buzzsprout, or the path from listener to signup. Whether doubled downloads would turn into more signups is **UNVERIFIED**: the item says nothing about it. Not load-bearing on its own; the fit section below carries this point.

FIT:
- Goal: none found. Goal 2 is "Grow the newsletter: more listeners sign up". The post is about downloads, not signups. No stated goal is about raw downloads (currently about 3,000 per episode).
- Overlap: any feed setting would live in Buzzsprout, which is already in use and already decided. We do not need a course to read Buzzsprout's own feed settings.
- Burden: unknown, because the action is undisclosed. Getting it means buying a course and creating an account.
- Cost: course price is not stated in the post (as read 2026-10-09). Any price would break the $0 quarterly budget and the "no new paid subscription or account without the host's approval" rule. Since the item serves no goal, this is a skip, not a decision for the host.
- Risks: a paywalled, unevidenced claim used to drive course sales. Possible upsell funnel. No license or data concerns, because there is nothing to adopt.

NEXT ACTION: Close this item as skip with no follow-up. Owner: operator. Done when: the sender has been told "skip: setting undisclosed, paywalled, and about downloads rather than newsletter signups (goal 2)". Hand-off: none.

CONFIDENCE: high. The item is fully readable (four sentences). The load-bearing claim is confirmed by the item's own text. The context file is present. Limit: this was read from the 2026-10-09 snapshot, not live, so a later edit that reveals the setting would mean reassessing it.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "@mic_drop post 9087, posted 2026-10-02, 61,000 likes (saved snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "changing one feed setting doubled the author's downloads",
     "evidence": "author's word only; the post says 'No numbers, no screenshots, trust me'",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the setting is only revealed by joining the author's paid course",
     "evidence": "post text: 'Not telling you which until you join my course'",
     "status": "CONFIRMED"},
    {"claim": "the post has 61,000 likes",
     "evidence": "meta.json likes: 61000, read live at capture",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "the author hosts a top-ten show with 300,000 followers",
     "evidence": "snapshot header text only; no chart or profile data captured",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "the trick would help goal 2 (newsletter signups)",
     "evidence": "the post mentions only downloads; nothing about signups or the newsletter",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found: goal 2 is newsletter signups, the post is about downloads",
          "overlap": "any feed setting would be in Buzzsprout, already in use and already decided",
          "burden": "unknown action; getting it requires buying a course and creating an account",
          "risks": ["paywalled, unevidenced claim used to sell a course",
                    "a course purchase would break the $0 budget and the no-new-account rule"],
          "cost": {"price": "not stated (course)", "tier": "paid course", "limits": "setting only disclosed inside the course",
                   "terms": "not stated", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Close the item as skip and tell the sender why: setting undisclosed and paywalled, and about downloads rather than newsletter signups",
                  "owner": "operator",
                  "done_when": "the sender has the skip and the one-line reason",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```