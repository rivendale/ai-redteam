```
VERDICT: try. A free change inside Reaper, which we already use and have already decided to keep, aimed squarely at goal 1; the post's six-episode timing suggests it helps, but the design can't separate key bindings from practice, so we should time it on our own episodes.
WHAT IT IS: Post "Bind the cut keys: the cut step from 60 to 41 minutes", posted 2026-09-11, posts.example.test/bind-the-cut-keys. Author not named in the snapshot. Read from a saved snapshot captured 2026-10-09 (meta.json), not live.
CLAIMS CHECKED:
  1. "The cut step went from 60 to 41 minutes" (the sender's words and the post's title). The table gives 62/58/60 with the mouse and 41/44/40 with key bindings; the medians are 60 and 41. The arithmetic matches the table. CONFIRMED (load-bearing).
  2. "Binding the keys caused the drop." The design is a before/after test on one show: 3 episodes then 3 episodes, in a fixed order, with no randomization. Episode length and content are not reported, and the editor's practice on episodes 1-3 could explain some of the gain. The two groups don't overlap, the gap is large (about 32%), and the cause is plausible: fewer mouse trips for split, ripple-delete and next-marker. PROBABLE (load-bearing). What would change it: a mouse-cut episode after episode 6 that also came in near 41 minutes.
  3. "It costs nothing and needs no plugin." The post asserts this, and the three actions it names ("split at cursor", "ripple delete", "next marker") are bound through Reaper's own action list. Not checked against Reaper's documentation in this session. PROBABLE (load-bearing).
  4. Implied by "goal 1": this would get us under 2 hours per episode. Our context doesn't say how long editing takes now or how much of it is the cut step, and our episodes (45 min) may differ in length from theirs. UNVERIFIED (not load-bearing; the trial settles it).
  No text in the post tries to direct the reader.
FIT:
  Goal: goal 1 (cut editing time to under 2 hours per episode). Every cut is made by hand in Reaper, so the cut step is where this would land.
  Overlap: none found. Nothing automates cutting, and this is a setting in the editor we already use, not a new tool. Unknown: whether our editor already uses key bindings for these actions. If they do, the gain is already taken.
  Burden: a one-time keymap setup and a few episodes of getting used to it. No account, no new service.
  Cost: free, no plugin, per the post (checked 2026-10-09 from the snapshot).
  Risks: none of note. No data leaves the machine and there is no license question. Reaper keymaps can be exported, so the change is easy to undo.
NEXT ACTION: Our editor times the cut step on the next episode as they cut it now, to get a baseline. Then they bind split-at-cursor, ripple-delete and next-marker to single keys and time the cut step on the following 3 episodes.
  Owner: operator (the editor).
  Done when: the baseline and 3 timed key-binding episodes are logged, with the median compared against the baseline.
  Stop condition: if the median is not clearly below the baseline after 3 episodes, or the editor already uses key bindings for these actions, revert the keymap and stop.
  Hand-off: none. This uses a setting in our own tool; nothing is borrowed.
CONFIDENCE: high. The item is resolved (from the snapshot), the context file is present, and every load-bearing claim is CONFIRMED or PROBABLE. Two limits: the post's design confounds key bindings with practice, and we don't know our current cut-step time or keymap. The trial is built to settle both.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "post 'Bind the cut keys: the cut step from 60 to 41 minutes', posted 2026-09-11, posts.example.test/bind-the-cut-keys (snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "the cut step went from 60 to 41 minutes",
     "evidence": "table: mouse 62/58/60, key bindings 41/44/40; medians 60 and 41",
     "status": "CONFIRMED"},
    {"claim": "binding the keys caused the drop",
     "evidence": "before/after on 6 episodes (3 vs 3), fixed order, not randomized, episode lengths not given; practice is a confounder, but the groups do not overlap",
     "status": "PROBABLE"},
    {"claim": "it costs nothing and needs no plugin",
     "evidence": "the post asserts it; the named actions are built-in Reaper actions bound through the action list; Reaper docs not checked here",
     "status": "PROBABLE"},
    {"claim": "this would get our editing under 2 hours per episode (goal 1)",
     "evidence": "the context gives no current editing or cut-step time; episode lengths may differ",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "cut editing time to under 2 hours per episode (goal 1); every cut is made by hand in Reaper",
          "overlap": "none found; it is a setting in Reaper, which is already in use (unknown whether the editor already uses key bindings)",
          "burden": "one-time keymap setup and a short adjustment period",
          "risks": ["no data leaves the machine", "no license question", "the keymap can be exported, so the change is easy to undo"],
          "cost": {"price": "free", "tier": "built into Reaper", "limits": "none", "terms": "no plugin needed, per the post",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Time the cut step on the next episode as cut now, then bind split-at-cursor, ripple-delete and next-marker to single keys and time the cut step on the following 3 episodes",
                  "owner": "operator",
                  "done_when": "the baseline and 3 timed key-binding episodes are logged and the median is compared with the baseline",
                  "stop_condition": "revert and stop if the median is not clearly below the baseline after 3 episodes, or if these actions are already bound to keys",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```