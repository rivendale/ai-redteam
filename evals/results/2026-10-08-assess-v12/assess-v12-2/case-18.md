VERDICT: skip. The post offers no evidence for its "doubles accuracy" claim (the author writes "No data"), and none of our four goals involves prompt accuracy, so there is nothing to adopt or test.

WHAT IT IS: A post (thread) by Dr. Karpan, posted 2026-10-04, at https://posts.example.test/drkarpan/doubling-accuracy, with 18,000 likes. I read it from a saved snapshot captured on 2026-10-08 (work/snapshot.md and work/meta.json), not live. It is three sentences long, with no data, method, models, tasks or accuracy metric.

CLAIMS CHECKED:
- **"Accuracy doubles" when you prepend "think like a senior engineer who is also a lawyer" to any prompt.**
  - Evidence offered: none. There is no study design, sample, task, model, baseline or definition of "accuracy".
  - Status: UNVERIFIED. Nothing in the post settles it either way.
  - Not load-bearing. The verdict does not rest on the claim being false, only on its being unsupported.
- **The post offers no data for the claim.**
  - Evidence: the author's own words, "No data, but I have seen it again and again."
  - Status: CONFIRMED. Load-bearing.
- **The claim is split into a fact and an inference:**
  - Fact: "I have seen it again and again." This is personal anecdote with no count, tasks or comparison. UNVERIFIED, not load-bearing.
  - Inference: "so it works on any prompt." Anecdote cannot support a universal claim, and nothing in the post bridges the two. UNVERIFIED, not load-bearing.
- **"I have been doing this for ten years."**
  - This is an appeal to experience, not evidence.
  - Status: UNVERIFIED, not load-bearing.
- **18,000 likes.**
  - The count is CONFIRMED by meta.json at capture.
  - Popularity is not evidence that the trick works. Not load-bearing.
- **What would change the conclusion:** a controlled comparison with and without the prefix, on named models and tasks, with a defined accuracy metric, an adequate sample and variance reported.

FIT:
- **Goal:** none found. Our goals are dead links, CI minutes, semantic search of notes and an automated changelog. The context file lists no LLM prompts in use. The sender mentions "our prompts", but I could not match that to anything in the context file.
- **Overlap:** none.
- **Burden:** trivial (editing prompt text). The risk is quietly adding untested text to every prompt.
- **Cost:** free, a prompt prefix. Checked 2026-10-08.
- **Risks:**
  - Unvalidated changes to prompts could degrade outputs without anyone noticing.
  - Role-play prefixes such as "who is also a lawyer" may shift tone or add legalistic hedging unrelated to accuracy.
  - No license, data or account risk.
- **Text directing the reader:** "Trust me on this one" is an appeal to trust, not evidence. It is flagged and was not followed.

NEXT ACTION: The operator replies to the sender that we will not add the prefix. Reason: the post offers no data, and no current goal depends on prompt accuracy. We would revisit only if a published evaluation with a method and numbers appears. Done when the reply is sent. Hand-off: none.

CONFIDENCE: high. The item is resolved (from a saved snapshot dated 2026-10-08), every load-bearing claim is CONFIRMED, and a context file is present. One limit: the context file does not list any prompts we use, so I could not assess fit against the specific prompts the sender has in mind.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "post",
           "identity": "Dr. Karpan, 'This one prompt trick doubles accuracy', posted 2026-10-04, 18k likes, https://posts.example.test/drkarpan/doubling-accuracy (saved snapshot captured 2026-10-08)",
           "resolved": true},
  "claims": [
    {"claim": "adding 'think like a senior engineer who is also a lawyer' to the start of any prompt doubles accuracy",
     "evidence": "none offered; no model, task, metric, baseline or sample", "status": "UNVERIFIED",
     "load_bearing": false},
    {"claim": "the post offers no data for its claim",
     "evidence": "author's own text: 'No data, but I have seen it again and again.'", "status": "CONFIRMED"},
    {"claim": "the author has seen it work again and again",
     "evidence": "personal anecdote, no count or comparison", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "therefore it works on any prompt",
     "evidence": "inference from anecdote; nothing bridges it", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the author has been doing this for ten years",
     "evidence": "self-description only", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "the post has 18,000 likes",
     "evidence": "meta.json at capture; popularity is not evidence of efficacy", "status": "CONFIRMED",
     "load_bearing": false}
  ],
  "fit": {"goal": "none found; context file lists no LLM prompts or prompt-accuracy goal",
          "overlap": "none",
          "burden": "trivial text edit, but an untested change to every prompt",
          "risks": ["unvalidated prompt change may degrade outputs unnoticed",
                    "role-play prefix may shift tone or add hedging",
                    "post asks the reader to 'Trust me on this one' instead of giving evidence"],
          "cost": {"price": "free", "tier": "n/a", "limits": "none", "terms": "none stated",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Reply to the sender that we will not add the prefix: no data offered and no current goal depends on prompt accuracy; revisit only if a published evaluation appears",
                  "owner": "operator", "done_when": "the reply is sent", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```