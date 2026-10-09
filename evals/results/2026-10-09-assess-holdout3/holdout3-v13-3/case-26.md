VERDICT: try. The three-pass method is free, runs in Reaper (which we already use for every cut), and targets goal 1. The post's own time saving is self-reported and still ends above our 2-hour goal, so it needs a timed trial on our episodes before we adopt it.

WHAT IT IS: A post, "Edit an episode in three passes", dated 2026-09-19, at https://posts.example.test/three-pass-edit. The snapshot does not name an author. I read the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not the live page. The snapshot is readable and complete for this purpose.

CLAIMS CHECKED:
- "This post describes a three-pass way to edit an episode" (sender). **CONFIRMED.** The method is:
  - Pass 1: listen at 1.5x and mark only the obvious cuts.
  - Pass 2: make those cuts, then listen at normal speed and tighten.
  - Pass 3: listen on earbuds for levels and clicks.
- "Over six episodes our editing time fell from a median of 190 minutes to 140" (post). **UNVERIFIED.** *Load-bearing.*
  - The evidence is the author's own before/after figure. There are no per-episode times, and the post gives no "before" sample size or episode length.
  - It is one show with no comparison group. Practice with a new routine, or easier episodes, could explain part of the drop.
  - It would change the conclusion if the drop holds on our 45-minute weekly episodes when we time them ourselves.
- "We could borrow the technique for goal 1" (sender). This joins a fact to an inference, so I split it.
  - The technique addresses editing time: **CONFIRMED**. That is its stated purpose, and it applies to hand-editing like ours.
  - That it would bring us under 2 hours: **UNVERIFIED**. The post's own result, 140 minutes, is still above 120. Our current baseline is not in the context file. *Load-bearing.*
- "It needs only the editor you already use; the post names no product to buy" (post). **CONFIRMED.** The snapshot names no product, plugin or service. *Load-bearing* for cost and burden.

FIT:
- **Goal:** Goal 1 (cut editing to under 2 hours per episode).
- **Overlap:** None on cutting. Every cut is made by hand in Reaper today, and the method is a way of ordering that same hand work. Pass 3's "levels" check partly overlaps loudness.py, which already normalizes the whole episode to -16 LUFS (goal 4). Pass 3 is still useful for clicks and for level jumps within an episode, which loudness.py does not fix.
- **Burden:** No new accounts, services or installs. It changes the editor's routine, and timing each pass adds a small step.
- **Cost:** Free. No tier, no limits, and the post names no product. Checked against the 2026-10-09 snapshot.
- **Risks:** It may not reach goal 1 on its own, since the post's result is 140 minutes. A 1.5x first pass could miss cuts that a normal-speed pass would catch. No data leaves the machine, and there are no license concerns because we borrow a technique, not code.

NEXT ACTION: The editor (operator) times the next three episodes with the three-pass method in Reaper and records minutes per pass.
- **Baseline:** Use the median of the last three hand-edited episodes. If those times were never recorded, time the next ordinary edit first.
- **Done when:** All three trial episodes are timed and their median is compared with the baseline and with the 120-minute goal.
- **Stop condition:** Stop if the trial median is not lower than the baseline, or if a published episode needs a fix for a cut the 1.5x pass missed.
- **Hand-off:** `harvest`, to capture the method from the post into our editing notes.

CONFIDENCE: Medium. The context file is present and the item is resolved from a dated snapshot. The two claims the verdict rests on (the 190→140 drop and whether it gets us under 2 hours) are UNVERIFIED. The author is unnamed, and our own baseline editing time is not recorded.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Edit an episode in three passes\", posted 2026-09-19, author not named, https://posts.example.test/three-pass-edit (snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "the post describes a three-pass way to edit an episode", "evidence": "snapshot: pass 1 at 1.5x marking obvious cuts, pass 2 cut and tighten at normal speed, pass 3 earbuds for levels and clicks",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "editing time fell from a median of 190 minutes to 140 over six episodes", "evidence": "author's self-reported before/after on one show, no per-episode data, no comparison",
     "status": "UNVERIFIED"},
    {"claim": "the technique addresses editing time and applies to hand-editing", "evidence": "the method is an ordering of manual listening and cutting passes; we cut by hand in Reaper",
     "status": "CONFIRMED"},
    {"claim": "borrowing it would bring our editing under 2 hours", "evidence": "the post's own result is 140 minutes, above 120; our baseline is not recorded",
     "status": "UNVERIFIED"},
    {"claim": "it needs only the editor you already use and names no product to buy", "evidence": "snapshot names no product, plugin or service",
     "status": "CONFIRMED"}
  ],
  "fit": {"goal": "goal 1: cut editing time to under 2 hours per episode",
          "overlap": "none for cutting (all cuts are manual in Reaper); pass 3 levels check partly overlaps loudness.py whole-episode normalization",
          "burden": "a change to the editor's routine plus timing each pass; no new accounts or installs",
          "risks": ["may not reach the 120-minute goal alone (post's own result is 140 minutes)",
                    "a 1.5x first pass may miss cuts",
                    "no data leaves the machine; no license issue for borrowing a technique"],
          "cost": {"price": "free", "tier": "none", "limits": "none", "terms": "post names no product to buy",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Edit the next three episodes with the three-pass method in Reaper, timing each pass, and compare the median with the median of the last three hand-edited episodes",
                  "owner": "operator (the editor)",
                  "done_when": "three episodes are timed and their median is compared with the baseline and with 120 minutes",
                  "stop_condition": "stop if the trial median is not lower than the baseline, or if a published episode needs a fix for a cut the 1.5x pass missed",
                  "handoff": "harvest"},
  "confidence": "medium",
  "context_file": "present"
}
```