VERDICT: skip. The post offers no evidence for its "doubles accuracy" claim, and none of our four goals involve LLM prompts, so there is nothing for it to improve here.

WHAT IT IS: A thread by Dr. Karpan, posted 2026-10-04 at https://posts.example.test/drkarpan/doubling-accuracy, with 18,000 likes. I read it from the saved snapshot captured 2026-10-08 (work/snapshot.md and work/meta.json), not live. The whole post is three sentences. It advises adding "think like a senior engineer who is also a lawyer" to the start of any prompt.

CLAIMS CHECKED:
- **"Accuracy doubles" (load-bearing): UNVERIFIED.** The post gives no study design, no sample, no task, no metric and no baseline. It says so itself: "No data, but I have seen it again and again." There is nothing to define "accuracy," so the claim cannot be tested as written. Nothing in the item shows it is false either. It is simply unsupported.
  - What would change this: a controlled comparison on a stated task, with and without the prefix, on a named model, with a measured metric.
- **"Works on any prompt": UNVERIFIED.** It is stated with no evidence, and the post names no model and no task type.
- **"I have been doing this for ten years": UNVERIFIED, not load-bearing.** It is a personal claim with nothing to check it against. Experience is also not evidence for the size of the effect.
- **"18k likes, so it works": split into two parts.**
  - The 18,000 likes are CONFIRMED by meta.json (not load-bearing).
  - The inference that popularity means it works is UNVERIFIED. Likes are not evidence.
- **"Trust me on this one"** is a request for trust, not evidence.

FIT:
- **Goal:** none found. Our goals are dead links, CI minutes, semantic search over notes, and an automated changelog. The context file lists no LLM prompts in use. changelog.py builds its draft from commit messages, and nothing indicates an LLM is involved.
- **Overlap:** none. There are no prompts in our listed stack to put it in.
- **Burden:** trivial, a one-line prefix, if we had prompts.
- **Cost:** free.
- **Risks:**
  - Adding an untested prefix to prompts could change outputs in ways nobody measures.
  - The "lawyer" framing could add hedging or legal-style caveats that we don't want.
  - No license, data or account concerns.

NEXT ACTION: The operator closes this item as skip. Done when it is marked skip in the tracker or inbox. Hand-off: none.

If LLM prompts are added to our stack later, any prompt change like this should be A/B tested on our own task before adoption. That would be a new assessment, not this one.

CONFIDENCE: medium. Three things limit it:
- The main claim is UNVERIFIED rather than REFUTED. We are skipping it for lack of evidence and lack of fit, not because it was shown false.
- I worked from a saved snapshot, not a live read.
- The context file does not say whether we use LLM prompts anywhere. If we do, the fit judgement should be revisited, though the evidence judgement stands.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "Dr. Karpan thread, posted 2026-10-04, https://posts.example.test/drkarpan/doubling-accuracy, 18k likes (read from snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "adding 'think like a senior engineer who is also a lawyer' doubles accuracy",
     "evidence": "none; the post states 'No data, but I have seen it again and again'; no task, metric, model or baseline",
     "status": "UNVERIFIED"},
    {"claim": "works on any prompt", "evidence": "assertion only; no model or task named",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the author has been doing this for ten years", "evidence": "self-report only",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the post has 18,000 likes", "evidence": "meta.json likes: 18000",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "its popularity shows the trick works", "evidence": "likes are not evidence of effect",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goals cover dead links, CI minutes, semantic search, changelog; no LLM prompts listed)",
          "overlap": "none; no prompts in the listed stack",
          "burden": "one-line prompt prefix, if prompts existed",
          "risks": ["unmeasured change to model outputs", "'lawyer' framing may add unwanted hedging", "no license, data or account risk"],
          "cost": {"price": "free", "tier": "n/a", "limits": "none", "terms": "none stated in the post",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Close this item as skip; if LLM prompts are added later, A/B test any prompt change on our own task before adopting it",
                  "owner": "operator", "done_when": "item is marked skip in the tracker", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```