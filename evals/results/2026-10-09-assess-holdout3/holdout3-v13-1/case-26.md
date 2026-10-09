VERDICT: try. A free workflow change that targets goal 1 and needs only Reaper, which we already use. Time it on our next three episodes before keeping it, because the post's evidence is thin and its own result (140 min) is still above our 2-hour target.

WHAT IT IS: Post "Edit an episode in three passes", posted 2026-09-19 at https://posts.example.test/three-pass-edit. The post names no author. I read it from the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. The post is resolved, and the snapshot holds its full text.

CLAIMS CHECKED:
- **The method is three listening passes.** Pass 1 is at 1.5x, marking only obvious cuts. Pass 2 makes those cuts and tightens at normal speed. Pass 3 is on earbuds, checking levels and clicks. The post describes this in full. CONFIRMED. *The verdict rests on this.*
- **"It needs only the editor you already use; the post names no product to buy."** The post's text names no tool, plugin or service. CONFIRMED. *The verdict rests on this.*
- **"Over six episodes our editing time fell from a median of 190 minutes to 140."** This is the author's own report. The sample is six episodes, and the post gives no episode length, no method of timing and no per-episode data. PROBABLE as a report of their own times.
- **(Inference) The three-pass method caused the drop.** There is no comparison group. Six consecutive episodes could also show learning, easier material or shorter episodes. Nothing in the post settles it. UNVERIFIED.
- **Sender: "we could borrow the technique for goal 1."** Goal 1 is "cut editing time to under 2 hours per episode", so the technique does target it. CONFIRMED as a fit. Whether it gets us under 120 min is UNVERIFIED:
  - The post's own result, 140 min, does not reach 120.
  - For our 45-minute episodes, the listening alone is about 30 min (pass 1) + up to 45 (pass 2) + 45 (pass 3) before any cutting work. That leaves little room under 2 hours.

FIT:
- **Goal:** goal 1 (editing time). There may be a minor link to goal 4, since pass 3 checks levels, but loudness.py already normalizes to −16 LUFS. The levels part of pass 3 partly duplicates that. The click check does not.
- **Overlap:** none for the method itself. We cut by hand in Reaper and have no structured pass order today. The method keeps us in Reaper, which is already decided.
- **Burden:** a change to how the editor works. There are no new accounts, services or maintenance. It needs earbuds for pass 3.
- **Cost:** free (it is a technique). There are no terms, and no tier applies. Checked 2026-10-09.
- **Risks:**
  - No license or install concerns, and no data leaves our machines.
  - The main risk is spending trial weeks on a method that cannot reach 120 min for a 45-minute show, because listening time alone nearly fills it.
  - We have no recorded baseline editing time, so we need one to judge the trial.

NEXT ACTION: The editor writes the three passes into the editing checklist (hand-off: `harvest`, since this is borrowing from a post). The editor then uses the method on the next three episodes and records the minutes spent on each, next to the minutes for the last three episodes edited the current way.
- **Owner:** operator (the editor).
- **Done when:** three episodes are edited with the method and their times are logged against a baseline of three.
- **Stop condition:** stop if the median of the three trial episodes is not lower than the baseline median, or if pass 3 catches nothing that loudness.py and the old process missed while adding about 45 min.

CONFIDENCE: high. The post is resolved from a dated snapshot, the claims the verdict rests on are CONFIRMED, and the context file is present. Two things limit what this confidence means. The time saving is unproven: six self-reported episodes, no causal evidence, and a result above our target. Our own baseline editing time is unknown, so whether the method meets goal 1 is left to the trial.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "post 'Edit an episode in three passes', posted 2026-09-19, https://posts.example.test/three-pass-edit, author not named; read from snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "the method is three passes: 1.5x listen marking obvious cuts; cut then tighten at normal speed; earbuds pass for levels and clicks",
     "evidence": "the post describes each pass in full", "status": "CONFIRMED"},
    {"claim": "it needs only the editor you already use; no product to buy",
     "evidence": "the post names no tool, plugin or service", "status": "CONFIRMED"},
    {"claim": "over six episodes median editing time fell from 190 to 140 minutes",
     "evidence": "author's own report; six episodes, no episode length, timing method or per-episode data",
     "status": "PROBABLE", "load_bearing": false},
    {"claim": "the three-pass method caused the drop in editing time",
     "evidence": "no comparison; learning or easier episodes could explain it; nothing in the post settles it",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "sender: the technique can be borrowed for goal 1",
     "evidence": "context goal 1 is cutting editing time; the method targets editing time",
     "status": "CONFIRMED"},
    {"claim": "the technique would bring our editing under 2 hours per episode",
     "evidence": "post's own result is 140 min; for a 45-min episode the three listens alone take roughly 30+45+45 min",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1: cut editing time to under 2 hours per episode",
          "overlap": "no structured pass method in use; pass 3 levels check partly overlaps loudness.py normalization; stays in Reaper",
          "burden": "workflow change for the editor; earbuds for pass 3; no new accounts or services",
          "risks": ["listening time alone for a 45-min episode leaves little room under 120 min",
                    "no recorded baseline editing time to measure against",
                    "no license, install or data risks"],
          "cost": {"price": "free", "tier": "none (a technique)", "limits": "none", "terms": "none",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Write the three passes into the editing checklist and use them on the next three episodes, logging minutes per episode against the last three edited the current way",
                  "owner": "operator (the editor)",
                  "done_when": "three episodes edited with the method and their times logged against a three-episode baseline",
                  "stop_condition": "stop if the trial median is not lower than the baseline median, or if pass 3 catches nothing loudness.py and the old process missed while adding about 45 minutes",
                  "handoff": "harvest"},
  "confidence": "high",
  "context_file": "present"
}
```