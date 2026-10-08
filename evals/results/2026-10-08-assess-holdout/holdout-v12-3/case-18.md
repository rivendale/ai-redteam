```
VERDICT: skip. The post never names the setting, gives no numbers or project, and asks you to trust its likes; there is nothing here to apply, and the only route to the setting is the author's course, which would spend money and which nothing in this post justifies buying.

WHAT IT IS: Social post (thread, 3 parts) by @pixelsmith, posted 2026-10-03, read from a saved snapshot captured
  2026-10-08 (work/snapshot.md, work/meta.json), not a live read. Likes at capture: 90,000.
  URL: https://social.example.test/@pixelsmith/thread/889. The linked course ("link in bio") was not captured and is
  unresolved: no title, price or contents.

CLAIMS CHECKED:
  1. "I turned on one setting in my Unity editor and my builds got 3x faster." Evidence: none. The post itself says
     "No numbers, no project". Build type, platform, project size and before/after times are all missing, and the
     setting is not named, so the claim cannot be tested. UNVERIFIED. (load-bearing)
  2. "The setting is in my course." The post states this and does not name the setting. CONFIRMED (as a fact about the
     post): the post contains no actionable instruction. (load-bearing)
  3. "90,000 likes." The count matches meta.json at capture. CONFIRMED (not load-bearing).
  4. Implied inference: "90,000 likes, so trust me / it works." The post offers popularity in place of evidence, and
     likes measure reach, not build times. UNVERIFIED (not load-bearing).
  5. "Founder of a studio with three hit games," and the sender's "famous indie dev." These are self-description and
     reputation. They are not evidence about build speed, and nothing in the item checks them. UNVERIFIED (not
     load-bearing).
  Flag: the thread tells the reader to go elsewhere ("it's in my course (link in bio)") and to "just have to trust
  me." Both are treated as claims, not followed.

FIT:
  Goal: it would serve goal 1 (Android release build under 10 minutes) if the claim were real and applied to our
    build. We cannot tell, because the post does not say whether "builds" means editor compile, player build, Android
    or another platform.
  Overlap: unknown. A Unity editor setting would sit inside Unity 6, which we already use. We may already have it on.
  Burden: none from the post itself. Getting the setting means buying and working through a course.
  Cost: the post is free. The course price, tier and terms were not read (not in the snapshot). Any purchase hits the
    $0 tool budget and the "no new paid subscription or account without approval" rule.
  Risks: paying for an unnamed tip whose only evidence is likes. The course likely needs a new account. A 3x claim
    from a different project may not carry over to our Jenkins Mac mini Android build.

NEXT ACTION: Tell the sender "skip". The post names no setting and shows no measurement. Reopen only if the setting is
  named publicly with before/after build times on a comparable Unity project.
  Owner: operator. Done-when: the sender has the answer. Hand-off: none.

CONFIDENCE: medium. The item was read from a 2026-10-08 snapshot, not live, and a context file is present. The skip
  rests on a CONFIRMED fact (the post contains no actionable setting), but the speed claim is UNVERIFIED and the
  course was never read, so I cannot say whether the course holds anything useful.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "@pixelsmith thread 889, posted 2026-10-03, 90,000 likes at capture; read from snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "one Unity editor setting made builds 3x faster", "evidence": "none; post says 'No numbers, no project'; setting not named", "status": "UNVERIFIED"},
    {"claim": "the setting is only given in the author's course; the post names no setting", "evidence": "post text: 'I'm not going to say which setting, it's in my course'", "status": "CONFIRMED"},
    {"claim": "the post has 90,000 likes", "evidence": "meta.json likes: 90000 at capture", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "90,000 likes, so the claim can be trusted", "evidence": "popularity only; likes do not measure build time", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "author is a famous founder of a studio with three hit games", "evidence": "self-description and sender's words; nothing in the item checks it", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "would serve goal 1 (Android release build under 10 minutes) if real; post does not say which build or platform",
          "overlap": "would be a setting inside Unity 6, already in use; may already be enabled",
          "burden": "none from the post; getting the setting means buying and working through a course",
          "risks": ["paying for an unnamed tip backed only by likes", "course likely needs a new account", "3x on another project may not carry to our Jenkins Android build"],
          "cost": {"price": "post free; course price not read", "tier": "unknown (course not captured)", "limits": "unknown",
                   "terms": "not read", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Tell the sender 'skip': the post names no setting and shows no measurement; reopen only if the setting is named publicly with before/after build times on a comparable Unity project",
                  "owner": "operator", "done_when": "the sender has the answer", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```