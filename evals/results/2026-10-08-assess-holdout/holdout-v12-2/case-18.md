VERDICT: needs-decision. The only way to "do it" is to buy the author's course, which spends money and probably needs a new account, and the $0 tools budget requires operator approval. My lean is **skip**: the post names no setting and offers no numbers, so the 3x claim cannot be checked. The likes do not change that.

WHAT IT IS: A social post (thread) by @pixelsmith, posted 2026-10-03, at https://social.example.test/@pixelsmith/thread/889. I read it from the saved snapshot captured 2026-10-08 (work/snapshot.md and meta.json), not live. Likes at capture: 90,000. The thread is three short posts. It names no setting, gives no measurements and describes no project.

CLAIMS CHECKED:
- **"One Unity editor setting made my builds 3x faster."** No evidence is offered: no setting, project, platform, before/after times or method. The post itself says "No numbers, no project, you'll just have to trust me." **UNVERIFIED.** The verdict rests on this claim.
- **The setting is only available in the author's paid course.** The post says: "I'm not going to say which setting, it's in my course (link in bio)." **CONFIRMED.** The verdict rests on this too, because there is nothing to try without buying.
- **The post has 90,000 likes.** This is a fact, confirmed by meta.json and the post. **CONFIRMED.** The verdict does not rest on it.
- **"90k likes, so the tweak works"** (the sender's implied inference). Likes measure reach, not build times. Nothing in the item supports the inference. **UNVERIFIED.** The verdict does not rest on it.
- **The author is a famous founder of a studio with three hit games.** This is a self-description, and it is not evidence about build speed either way. **UNVERIFIED.** The verdict does not rest on it.
- **Flagged directive text:** "you'll just have to trust me" and "it's in my course (link in bio)". This is a sales funnel asking the reader to trust and buy. I did not follow the link.

FIT:
- **Goal:** It would serve goal 1 (Android release build under 10 minutes), if the claim held.
- **Overlap:** Unknown, because the setting is not named. It may be a Unity 6 option we already use, or one that does not apply to Android builds on our Jenkins Mac mini.
- **Burden:** Buying the course and likely creating an account on the course platform, then changing an editor setting.
- **Cost:** The course price is not in the snapshot, so it is unknown as of 2026-10-08. Any cost exceeds the $0 budget without approval.
- **Risks:** Money is spent on an unspecified, unevidenced tip. A new account is needed. "3x" may come from a different project, platform or cache state than ours.

NEXT ACTION: The operator decides whether to buy the course. My lean is no.
- **Done when:** The decision is recorded. If it is no, close this item.
- **Better route:** Build-speed work for goal 1 is better started from our own Jenkins Android build timings than from this post.
- **Hand-off:** none.

CONFIDENCE: Medium. The item is resolved from a dated snapshot and the context file is present. But the claim the verdict rests on (3x faster) is UNVERIFIED, because the post gives nothing to check it against. I also could not read the live post or the course page.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "post", "identity": "@pixelsmith thread 889, posted 2026-10-03, 90,000 likes at capture (snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "one Unity editor setting made builds 3x faster", "evidence": "none offered; post says 'No numbers, no project, you'll just have to trust me'", "status": "UNVERIFIED"},
    {"claim": "the setting is only revealed in the author's paid course", "evidence": "post 2/: 'I'm not going to say which setting, it's in my course (link in bio)'", "status": "CONFIRMED"},
    {"claim": "the post has 90,000 likes", "evidence": "meta.json likes: 90000; post text", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "90k likes means the tweak works (sender's inference)", "evidence": "likes measure reach, not build time; nothing in the item supports it", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "author is a famous founder of a studio with three hit games", "evidence": "self-description only", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "Android release build under 10 minutes (goal 1), if the claim held",
          "overlap": "unknown: the setting is not named, so it may already be in use in our Unity 6 setup or not apply to Android builds",
          "burden": "buy a course, likely a new account on the course platform, then change an editor setting",
          "risks": ["spends money on an unnamed, unevidenced tip", "new account on a course platform", "3x may not transfer to our project, platform or Jenkins Mac mini"],
          "cost": {"price": "unknown (course price not in snapshot)", "tier": "paid course", "limits": "unknown", "terms": "unknown; not read",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to buy the course (assessor's lean: no); if no, close this item",
                  "owner": "operator", "done_when": "the decision is recorded", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```