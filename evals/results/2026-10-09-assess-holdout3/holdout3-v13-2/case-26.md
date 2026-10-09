```
VERDICT: try. The post's three-pass method uses only the editor we already have (Reaper), costs nothing, and targets goal 1. Its evidence is one team's self-report over six episodes, so we should time it on our own episodes before adopting it.
WHAT IT IS: Post "Edit an episode in three passes", posted 2026-09-19, at https://posts.example.test/three-pass-edit. No author is named in the snapshot. I read it from the saved copy (work/snapshot.md, captured 2026-10-09), not live.
CLAIMS CHECKED:
  1. "Over six episodes our editing time fell from a median of 190 minutes to 140." The only evidence is the authors' own before/after medians. There is no method, no control and no per-episode data, and the sample is n=6.
     The drop itself is PROBABLE. It is a specific reported figure, but we cannot check it.
     "The three-pass method caused the drop" is UNVERIFIED. The post does not rule out practice effects, easier episodes, or the authors simply timing themselves more closely. The verdict does not rest on this part, because the trial is what tests it.
  2. "It needs only the editor you already use; the post names no product to buy." CONFIRMED by the post's own text. Pass 1 is listening at 1.5x and marking cuts, pass 2 is cutting and tightening, and pass 3 is listening on earbuds. All of this can be done in Reaper. The verdict rests on this claim.
  3. Sender's claim: "we could borrow the technique for goal 1." PROBABLE as a fit. It does address editing time. However, even the post's own result (140 min) is above our target of under 2 hours (120 min), so the method alone may not reach goal 1.
  The snapshot contains no text that tries to direct the reader.
FIT:
  Goal: goal 1 (cut editing time to under 2 hours per episode). Pass 3, checking levels and clicks by ear, also touches goal 4.
  Overlap: none for cutting. Every cut is made by hand in Reaper, and this method changes the order of that manual work rather than replacing a tool. There is partial overlap on levels: loudness.py already normalizes each episode to -16 LUFS. Pass 3 is still useful for clicks and local level jumps that loudnorm does not fix.
  Burden: no new account, tool or service. It is a change to the editing routine, plus timing each edit during the trial.
  Cost: free, with no tier and no terms attached (read from the snapshot, 2026-10-09).
  Risks: none of license, data or lock-in. The main risk is wasted effort if the gain does not transfer. Our current editing time is not recorded in the context file, so we need a baseline before we can judge any change.
NEXT ACTION: Hand the post to `harvest` to turn the three passes into a written editing checklist. The editor then uses that checklist on the next 3 weekly episodes and logs the minutes for each edit. The comparison baseline is the last 3 episodes' times, or the editor's best estimate if those were not logged.
  Owner: the editor (operator), with `harvest` writing the checklist.
  Done when: three episodes are edited with the checklist and their median time is compared to the baseline.
  Stop condition: if the median does not drop by at least 15% against the baseline, or if quality slips (missed cuts or clicks caught after publishing), drop the method.
CONFIDENCE: medium. Context file present and the post is resolved from a saved copy, but the post's evidence is a small self-reported sample, causation is untested, and we do not know our own baseline editing time.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Edit an episode in three passes\", posted 2026-09-19, https://posts.example.test/three-pass-edit (read from saved snapshot captured 2026-10-09; no author named)",
           "resolved": true},
  "claims": [
    {"claim": "over six episodes editing time fell from a median of 190 minutes to 140",
     "evidence": "the authors' own before/after medians; no method, no control, n=6",
     "status": "PROBABLE"},
    {"claim": "the three-pass method caused the drop",
     "evidence": "nothing in the post rules out practice effects or easier episodes",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "it needs only the editor you already use; no product to buy",
     "evidence": "the post's three passes use only an editor and earbuds; it names no product",
     "status": "CONFIRMED"},
    {"claim": "(sender) we could borrow the technique for goal 1",
     "evidence": "it targets editing time, but the post's own result (140 min) is still above our 120-minute target",
     "status": "PROBABLE"}
  ],
  "fit": {"goal": "goal 1: cut editing time to under 2 hours per episode (pass 3 also touches goal 4)",
          "overlap": "none for cutting (all cuts are manual in Reaper); partial on levels, since loudness.py already normalizes to -16 LUFS",
          "burden": "a change to the editing routine plus timing each edit during the trial; no new account or service",
          "risks": ["no license, data or lock-in risk", "gain may not transfer; our current editing time is not recorded, so a baseline is needed"],
          "cost": {"price": "free", "tier": "none", "limits": "none", "terms": "none (a technique in a post)",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Hand the post to harvest to write the three passes as an editing checklist, then the editor uses it on the next 3 episodes and logs minutes per edit against a baseline from the last 3 episodes",
                  "owner": "operator (the editor), with harvest writing the checklist",
                  "done_when": "three episodes are edited with the checklist and their median time is compared to the baseline",
                  "stop_condition": "stop if the median does not drop at least 15% against the baseline, or if missed cuts or clicks are found after publishing",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```