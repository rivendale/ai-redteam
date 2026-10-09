VERDICT: try. Binding three Reaper actions to keys is free, needs no plugin or account, and targets goal 1 (editing under 2 hours). The post's 60→41 minute gain comes from six uncontrolled episodes, so we should measure it on our own episodes before treating it as real.

WHAT IT IS: A post, "Bind the cut keys: the cut step from 60 to 41 minutes", posted 2026-09-11 at https://posts.example.test/bind-the-cut-keys. The author is not named in the snapshot. I worked from the saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not a live read. The item is resolved: its full text is in the snapshot.

CLAIMS CHECKED:
- **"Median 60 against 41 minutes": CONFIRMED.** This is arithmetic from the post's own table: the median of 62, 58 and 60 is 60, and the median of 41, 44 and 40 is 41. Not load-bearing.
- **"Binding the keys caused the drop": PROBABLE.** Load-bearing for the direction of the effect, not its size.
  - The design is an uncontrolled before/after test with three episodes per arm.
  - Episodes 1-3 were all done by mouse and 4-6 all by keys, so practice gains and episode-to-episode differences are mixed in with the method.
  - The post gives no episode lengths and no count of cuts per episode.
  - The direction is plausible because there are fewer mouse trips per cut. The 19-minute size is not established.
  - A same-period alternating trial, or a reversal back to the mouse, would change the conclusion.
- **"It costs nothing and needs no plugin": PROBABLE.** Load-bearing. The post says it only rebinds built-in actions ("split at cursor", "ripple delete", "next marker"). That fits Reaper, which we already use. I did not check Reaper's action list itself.
- **The sender's "cut the cut step from 60 to 41": PROBABLE.** This restates the post. It holds as a report of the post's numbers, and the causal part carries the caveats above.

FIT:
- **Goal:** Goal 1, cut editing time to under 2 hours per episode. Every cut is made by hand in Reaper, so the cut step is exactly the work this targets.
- **Overlap:** Nothing in use automates or speeds cutting. The context file does not say whether these actions are already bound to keys, so check that first. If they are, the post has nothing for us.
- **Burden:** A one-time change to Reaper's shortcuts on the Mac mini, plus a few episodes of habit change. There are no new services and no maintenance.
- **Cost:** Free, with no tier and no limits. Checked from the snapshot as of 2026-10-09.
- **Risks:** No new software, no data leaving the machine, no license question and no lock-in. Bindings can be reverted. A new binding may collide with an existing Reaper shortcut.

NEXT ACTION:
- **Action:** The operator checks Reaper's current shortcuts. If the three actions are not already bound, they bind them, then time the cut step on the next three episodes. They compare those times against a mouse-cut time recorded on a recent episode, or note the 45-minute episode lengths so the comparison is fair.
- **Done when:** Three timed key-bound cut steps are recorded alongside at least one mouse baseline.
- **Stop condition:** Revert if the key-bound median is not at least 10% faster than the baseline after three episodes, or if the bindings clash with shortcuts in daily use.
- **Hand-off:** None. This uses a feature of a tool we already have and borrows nothing.

CONFIDENCE: Medium. The item is resolved and the context file is present, and the load-bearing claims are PROBABLE. Two things limit it: I don't know whether these keys are already bound in our Reaper, and the post's six-episode design cannot separate the binding from practice effects.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Bind the cut keys: the cut step from 60 to 41 minutes\", posted 2026-09-11, posts.example.test/bind-the-cut-keys (author not named; saved snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "median cut step 60 minutes by mouse against 41 with key bindings",
     "evidence": "the post's own table: 62, 58, 60 against 41, 44, 40; medians are 60 and 41",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "binding split, ripple delete and next marker to keys makes cutting faster",
     "evidence": "uncontrolled before/after on 6 episodes (3 per arm), arms in sequence so practice and episode differences are confounded; no episode lengths or cut counts given",
     "status": "PROBABLE"},
    {"claim": "it costs nothing and needs no plugin",
     "evidence": "the post says it only rebinds built-in Reaper actions; Reaper is already in use; action list not checked",
     "status": "PROBABLE"},
    {"claim": "sender: binding the keys cut the cut step from 60 to 41 minutes",
     "evidence": "restates the post's figures; holds as reported, causal part as above",
     "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "cut editing time to under 2 hours per episode (goal 1); every cut is made by hand in Reaper",
          "overlap": "nothing in use automates or speeds cutting; context does not say whether these actions are already bound",
          "burden": "one-time shortcut change in Reaper on the Mac mini, a few episodes of habit change",
          "risks": ["no new software, account or data flow", "possible clash with existing Reaper shortcuts", "post's gain may be practice effect, not the bindings"],
          "cost": {"price": "free", "tier": "built-in Reaper feature", "limits": "none", "terms": "none beyond the existing Reaper use",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Check Reaper's shortcuts; if split at cursor, ripple delete and next marker are not bound, bind them and time the cut step on the next three episodes against a recorded mouse baseline",
                  "owner": "operator",
                  "done_when": "three timed key-bound cut steps are recorded beside at least one mouse baseline",
                  "stop_condition": "revert if the key-bound median is not at least 10% faster than the baseline after three episodes, or the bindings clash with shortcuts in daily use",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```