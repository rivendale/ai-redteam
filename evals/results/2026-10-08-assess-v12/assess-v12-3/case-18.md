```
VERDICT: skip. The post offers no evidence for its "doubles accuracy" claim (the author writes "No data"), and none of our four goals involves prompt accuracy.
WHAT IT IS: Post (thread) by Dr. Karpan, posted 2026-10-04, 18k likes, https://posts.example.test/drkarpan/doubling-accuracy. Read from the saved snapshot captured 2026-10-08 (work/snapshot.md, work/meta.json), not live.
CLAIMS CHECKED:
  - "Adding 'think like a senior engineer who is also a lawyer' to the start of any prompt doubles accuracy." Evidence: none. The author says "No data, but I have seen it again and again." There is no task, model, sample, baseline, or metric, so "accuracy" is undefined. UNVERIFIED (load-bearing). This would change if a controlled comparison existed: the same tasks and model, with and without the prefix, a defined accuracy measure, and a reported sample size.
  - "Works on any prompt." Evidence: none. UNVERIFIED (not load-bearing).
  - Fact plus inference, split:
    (a) "I have been doing this for ten years." Self-reported and uncheckable. UNVERIFIED (not load-bearing).
    (b) "...so it works." Experience and repeated anecdote are not evidence of an effect. UNVERIFIED (not load-bearing).
  - Popularity: 18k likes is CONFIRMED in meta.json. It is not evidence for the claim (not load-bearing).
FIT:
  - Goal: none found. Our goals are dead links, CI minutes, semantic search of notes, and an automated changelog. None of them is "prompt accuracy".
  - Overlap: none. We have no prompts listed in our tools.
  - Burden: small to try, since it is one line of text. Showing whether it helps would need an eval we do not have.
  - Cost: free. No account and no data leaves the machine just from editing prompts.
  - Risks: adopting an untested change based on popularity. A persona prefix could also change output style or behavior in ways nobody measures.
NEXT ACTION: The operator replies to the sender: skip, with no evidence and no goal it serves. If prompt quality later becomes a goal, judge prompt changes with our own A/B eval rather than a post. Done when the reply is sent. Hand-off: none.
CONFIDENCE: medium. The snapshot is readable and the context file is present. The verdict rests partly on an UNVERIFIED claim, and the snapshot is a saved copy rather than a live read.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "Dr. Karpan, thread 'This one prompt trick doubles accuracy', posted 2026-10-04, 18k likes, https://posts.example.test/drkarpan/doubling-accuracy (snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "adding 'think like a senior engineer who is also a lawyer' to the start of a prompt doubles accuracy",
     "evidence": "none; author states 'No data, but I have seen it again and again'; no task, model, sample, baseline or metric",
     "status": "UNVERIFIED"},
    {"claim": "works on any prompt", "evidence": "none offered", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the author has been doing this for ten years", "evidence": "self-report only", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "repeated personal observation shows the trick works", "evidence": "anecdote, no data",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the post has 18k likes", "evidence": "meta.json likes: 18000", "status": "CONFIRMED",
     "load_bearing": false}
  ],
  "fit": {"goal": "none found", "overlap": "none; no prompts appear among tools in use",
          "burden": "one line per prompt, but showing any effect needs an eval we do not have",
          "risks": ["adopting an untested change on popularity alone", "persona prefix may shift output style or behavior unmeasured"],
          "cost": {"price": "free", "tier": "n/a", "limits": "none", "terms": "public post",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the sender: skip, no evidence offered and no goal it serves; judge any future prompt changes with our own A/B eval",
                  "owner": "operator", "done_when": "reply sent", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```