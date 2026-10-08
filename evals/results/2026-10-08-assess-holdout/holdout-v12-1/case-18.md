VERDICT: skip. The post never names the setting, gives no numbers and offers no project, so there is nothing to turn on and nothing to check. The 90,000 likes are real but they are not evidence that the tweak works. Learning the setting appears to require the author's course, and buying it would spend money and likely add an account, which is the operator's call; my lean is not to.

WHAT IT IS: A social post (thread) by @pixelsmith, posted 2026-10-03, at https://social.example.test/@pixelsmith/thread/889. 90,000 likes. Read from a saved snapshot captured 2026-10-08 (work/snapshot.md and work/meta.json), not live.

CLAIMS CHECKED:
- **"One Unity editor setting made my builds 3x faster"** (the verdict rests on this). UNVERIFIED. The post gives no setting name, no before/after times, no project, no hardware and no build target. The author writes "No numbers, no project, you'll just have to trust me." Nothing in the item can confirm or refute it. It is also unclear whether "builds" means player builds such as Android or script compiles in the editor.
- **"90,000 likes"** (not load-bearing). CONFIRMED. meta.json records `"likes": 90000` at capture.
- **"…so it is worth doing"**, the inference implied by "90k likes" and "famous indie dev" (not load-bearing). UNVERIFIED. Likes and fame measure reach, not build times. Nothing in the item connects them to the result.
- **"Founder of a studio with three hit games"** (not load-bearing). UNVERIFIED. This is the author's self-description and nothing in the snapshot backs it.
- **"Editor tweak"**, from the sender's words (not load-bearing). UNVERIFIED. The post does not say what the change is. It only says it is "one setting."
- **Text directing the reader, flagged:** "I'm not going to say which setting, it's in my course (link in bio)." This is a sales funnel to a paid product. I did not follow the link, and its price and terms are unread.

FIT:
- **Goal:** If the claim were true and it applied to Android player builds, it would serve goal 1 (Android release build under 10 minutes). The post does not establish either condition.
- **Overlap:** Cannot be judged without knowing the setting. It may already be on in our Unity 6 project.
- **Burden:** Unknown setting. Getting it means buying and working through a course.
- **Cost:** The post states no price, and I could not read the course page. Our constraints say $0 new-tool budget this quarter and no new paid subscription or account without operator approval.
- **Risks:** Paying for an unnamed claim with no evidence. The course is an unread third party. No license or data risk can be judged from the post.

NEXT ACTION: The operator times the stages of the current Android release build on the Jenkins Mac mini (from the Unity build report and Jenkins stage timings) to find where the minutes go before trying any tweak. Done when there is a per-stage time breakdown of one release build. Hand-off: none.

CONFIDENCE: medium. The item is resolved from a snapshot and a context file is present. The claim the verdict rests on is UNVERIFIED because the post withholds everything needed to check it. The live post and course page were not read.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post", "identity": "@pixelsmith thread 889, posted 2026-10-03, 90,000 likes (snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "one Unity editor setting made builds 3x faster", "evidence": "none: the post withholds the setting, numbers and project ('you'll just have to trust me')", "status": "UNVERIFIED"},
    {"claim": "the post has 90,000 likes", "evidence": "meta.json likes: 90000 at capture", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "90k likes and a famous author mean the tweak works", "evidence": "none; popularity measures reach, not build time", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "author founded a studio with three hit games", "evidence": "self-description only", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "it is an editor tweak we could apply (sender's words)", "evidence": "the post does not name the setting; it says it is in a paid course", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "would touch goal 1 (Android release build under 10 minutes) only if true and if it applies to player builds; neither is shown",
          "overlap": "unknown: the setting is not named, so it may already be on in our Unity 6 project",
          "burden": "buying and working through a course to learn one unnamed setting",
          "risks": ["paying for an unevidenced claim", "post funnels readers to a course ('link in bio'), not followed", "course price and terms unread"],
          "cost": {"price": "not stated in the post; course price unread", "tier": "unknown", "limits": "unknown",
                   "terms": "unread", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Time the stages of the current Android release build on the Jenkins Mac mini to find where the minutes go",
                  "owner": "operator", "done_when": "a per-stage time breakdown of one release build exists",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```