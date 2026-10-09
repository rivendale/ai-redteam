```
VERDICT: try. It is relevant to goal 1, because we cut every silence and slip by hand in Reaper. The post's own six-episode timing suggests key bindings speed that step, so a free three-episode trial against our own baseline will show whether it helps us.

WHAT IT IS: Post "Bind the cut keys: the cut step from 60 to 41 minutes". Posted 2026-09-11, author not named in the
  snapshot, at https://posts.example.test/bind-the-cut-keys. Read from the saved snapshot captured 2026-10-09
  (work/snapshot.md, work/meta.json), not live.

CLAIMS CHECKED:
  1. "The cut step went from 60 to 41 minutes" (median). Evidence: the post's table, mouse 62/58/60 and keys
     41/44/40. The arithmetic holds: the medians are 60 and 41. CONFIRMED as a report of their numbers.
  2. "Binding the keys caused the drop" (the inference behind 1). Evidence: a before/after comparison of 3 episodes
     per method. The mouse episodes (1-3) were always cut before the key episodes (4-6), so practice, easier later
     episodes, or different episode lengths could explain part of the gap. Episode length and the amount of cutting
     needed are not given. The mechanism is plausible: single keys replace menu and mouse trips for actions repeated
     many times per episode. The effect is consistent across all six episodes, but small samples, no randomisation
     and no control for order limit it. PROBABLE. The verdict rests on this.
  3. "We would save ~19 minutes per episode." Not claimed for us. It depends on our episode length (45 min), our
     cut density and our current habits. Nothing in the item settles it. UNVERIFIED. Not load-bearing; the trial
     measures it.
  4. "It costs nothing and needs no plugin." Evidence: the post's statement. The three actions (split at cursor,
     ripple delete, next marker) are standard Reaper actions that can be bound in its Actions list. PROBABLE.
     The verdict rests on this.

FIT:
  Goal: goal 1, "Cut editing time to under 2 hours per episode". The cut step is done entirely by hand in
    Reaper, which is the exact workflow the post timed.
  Overlap: nothing in use automates or speeds cutting. The context file does not say whether these actions are
    already bound to keys. If they are, this adds nothing.
  Burden: a one-time setup of a few minutes in Reaper's Actions list, and a short period of learning the keys.
    No new account, service or plugin.
  Cost: free, a built-in Reaper feature (as read from the snapshot, 2026-10-09). No terms involved.
  Risks: no license, telemetry, data or lock-in issues. The only risk is clashing with existing Reaper shortcuts.
    Back up the keymap before changing it.

NEXT ACTION: The editor records the cut-step time on the next episode cut the usual way, as a baseline. They then
  bind "split at cursor", "ripple delete" and "next marker" to single keys and time the cut step on the following
  3 episodes.
  Owner: whoever edits in Reaper (operator to assign).
  Done when: the baseline and 3 timed key-binding episodes are logged and compared.
  Stop condition: stop and revert to the backed-up keymap if the median cut step is not shorter than the baseline
  after 3 episodes. Also stop at once if these actions are already bound.
  Hand-off: none (a workflow change, not borrowing).

CONFIDENCE: medium. Limits: the item is read from a saved snapshot. The causal claim rests on 6 episodes with order
  confounded. We have no baseline for our own cut step. The context file does not say whether bindings are already
  in use.
```

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "post",
           "identity": "\"Bind the cut keys: the cut step from 60 to 41 minutes\", author not named, posted 2026-09-11, https://posts.example.test/bind-the-cut-keys (saved snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "the cut step went from a median of 60 to 41 minutes", "evidence": "post's table: mouse 62/58/60, keys 41/44/40; medians recompute to 60 and 41", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "binding the cut and ripple actions to keys caused the drop", "evidence": "before/after on 3+3 episodes, mouse episodes always first; order, practice and episode differences not controlled; consistent gap and plausible mechanism", "status": "PROBABLE"},
    {"claim": "we would save about 19 minutes per episode", "evidence": "nothing in the item; depends on our episode length, cut density and current habits", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "it costs nothing and needs no plugin", "evidence": "post's statement; split, ripple delete and next marker are built-in Reaper actions bindable in the Actions list", "status": "PROBABLE"}
  ],
  "fit": {"goal": "goal 1: cut editing time to under 2 hours per episode (every cut is made by hand in Reaper)",
          "overlap": "none found; context does not say whether these actions are already bound",
          "burden": "one-time key setup in Reaper and a short learning period; no new account, service or plugin",
          "risks": ["possible clash with existing Reaper shortcuts; back up the keymap first", "no license, telemetry or data concerns"],
          "cost": {"price": "free", "tier": "built-in Reaper feature", "limits": "none", "terms": "none beyond our existing Reaper use",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Time the cut step on one episode as usual, then bind split at cursor, ripple delete and next marker to single keys and time the cut step on the next 3 episodes",
                  "owner": "the Reaper editor (operator assigns)",
                  "done_when": "baseline and 3 key-binding cut-step times are logged and compared",
                  "stop_condition": "revert the keymap if the median cut step is not shorter than the baseline after 3 episodes, or stop at once if these actions are already bound",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```