VERDICT: try. A free, MIT, plain-text Reaper template could save the per-episode project setup the sender describes, but that is a small part of goal 1 (editing time is mostly hand cutting), and the template's contents are known only from its README, so run a short, measured trial.

WHAT IT IS: example-org/interview-template, MIT, 45 stars, last push 2026-09-21, not archived, default branch `main`, release v1.1.0 at commit `a40e7c19d2b86f35e1c0a9748d3b5f62c1e8097b`. Read from the saved snapshot and meta.json captured 2026-10-09, not live. It is one `.RPP` Reaper project template for a two-person interview recorded on separate tracks: two voice tracks with a high-pass and de-esser inserted, a music-and-effects track, a stereo bus with a loudness meter set to -16 LUFS, and an empty markers track.

CLAIMS CHECKED:
- **"interview-template is a reaper project template for a two-person interview"** (sender). The snapshot describes exactly that. **CONFIRMED.**
- **"We set up every episode project by hand"** (sender). The context file says every *cut* is made by hand in Reaper but says nothing about project setup, and nothing in the item settles it. **UNVERIFIED.** It is load-bearing: the trial exists to measure it.
- **"It serves goal 1"** (sender, by implication). Goal 1 is "under 2 hours editing per episode". A template removes track and FX setup, not cutting, and the context says cutting is all manual. That setup time is part of editing time is **PROBABLE**, but the saving is likely minutes, not the bulk of the gap. Load-bearing.
- **"No plugins other than Reaper's own and no scripts; one plain text .RPP file"** (README). The snapshot holds the README, not the `.RPP` itself, so I could not check it. **UNVERIFIED.** Load-bearing for the risk check, so the trial starts by reading the file, as the README itself advises.
- **License MIT.** meta.json and the README agree. **CONFIRMED.**
- **Maintained: last release v1.1.0 on 2026-09-21.** This matches meta.json `last_push` 2026-09-21 and not archived. **CONFIRMED** (not load-bearing).
- **"Loudness meter set to -16 LUFS."** This is stated in the README and matches our -16 LUFS target, but it is only a meter. **PROBABLE**, not load-bearing.

FIT:
- **Goal:** Goal 1 (editing time), only through project setup. Goal 4 (consistent loudness) is touched by the meter, but loudness.py already normalizes every episode to -16 LUFS and logs it.
- **Overlap:** We already edit in Reaper (decided), so this is a starting file for it, not a new tool. The -16 LUFS meter duplicates what loudness.py already enforces. That is harmless, since a meter does not process audio, but it adds nothing for goal 4.
- **Burden:** Copy one file into Reaper's ProjectTemplates folder. No account, no service, no daily step.
- **Cost:** Free, MIT, open source, no limits (read 2026-10-09). Within the $0 budget.
- **Risks:**
  - The MIT license is fine, and the file never ships on the show site anyway.
  - The install path is a manual copy from a pinned release commit, with no `curl | bash` and no unsigned binary.
  - No data leaves the machine.
  - The inserted high-pass and de-esser change the voice sound before loudness.py runs, so we should compare by ear.
  - It is unconfirmed that our show is a two-person, separate-track interview. The context file does not say.
  - The "no scripts" claim is unchecked until the `.RPP` is read.

NEXT ACTION: The operator (whoever edits in Reaper) reads the `.RPP` at commit `a40e7c19…` and confirms it contains only Reaper's own plugins and no scripts or ReaScript references. They then copy it into ProjectTemplates and use it for the next 2 episodes, noting setup time and total editing time against the last 2 episodes.
- **Done when:** both episodes are edited from the template, and the setup and editing times are written down next to the previous two.
- **Stop condition:** stop and delete the template if:
  - the `.RPP` references any third-party plugin or script, or
  - setup time does not drop by at least a few minutes per episode, or
  - the high-pass or de-esser audibly worsens the voices compared with our current chain.
- **Hand-off:** none (this is using a file, not borrowing ideas).

CONFIDENCE: medium. The item was read from a 2026-10-09 snapshot, not live, and the `.RPP` itself was not in it. The sender's "set up by hand" premise and the show's two-person format are not in the context file. The goal-1 benefit is probable but likely small.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/interview-template@a40e7c19d2b86f35e1c0a9748d3b5f62c1e8097b (MIT, 45 stars, last push 2026-09-21, not archived, default branch main; read from snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "interview-template is a Reaper project template for a two-person interview (sender)",
     "evidence": "snapshot.md: two voice tracks on separate tracks, music-and-effects track, bus with -16 LUFS meter, markers track",
     "status": "CONFIRMED"},
    {"claim": "we set up every episode project by hand (sender)",
     "evidence": "context file says every cut is made by hand but says nothing about project setup; the item cannot settle it",
     "status": "UNVERIFIED"},
    {"claim": "the template serves goal 1, cutting editing time (sender, implied)",
     "evidence": "a template removes setup work, which is part of editing time, but the context says cutting, not setup, is the manual work",
     "status": "PROBABLE"},
    {"claim": "contains no plugins other than Reaper's own and no scripts; one plain text .RPP file",
     "evidence": "README statement only; the .RPP itself is not in the snapshot",
     "status": "UNVERIFIED"},
    {"claim": "license is MIT",
     "evidence": "meta.json license field and README agree",
     "status": "CONFIRMED"},
    {"claim": "maintained: last release v1.1.0 on 2026-09-21",
     "evidence": "meta.json last_push 2026-09-21, archived false",
     "status": "CONFIRMED", "load_bearing": false},
    {"claim": "stereo bus has a loudness meter set to -16 LUFS",
     "evidence": "README statement; matches our -16 LUFS target, but loudness.py already normalizes",
     "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1 (editing time under 2 hours), through project setup only; touches goal 4 but loudness.py already covers it",
          "overlap": "Reaper is already our editor (decided); the -16 LUFS meter duplicates what loudness.py enforces",
          "burden": "copy one file into Reaper's ProjectTemplates folder; no account, service or daily step",
          "risks": ["MIT, and the file never ships on the show site",
                    "manual copy from a pinned release commit, no curl | bash",
                    "no data leaves the machine",
                    "inserted high-pass and de-esser change the voice sound before loudness.py",
                    "two-person separate-track format not confirmed in our context",
                    "no-scripts claim unchecked until the .RPP is read"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the .RPP at commit a40e7c19 to confirm only Reaper's own plugins and no scripts, then copy it into ProjectTemplates and use it for the next 2 episodes, recording setup and total editing time against the previous 2",
                  "owner": "operator (whoever edits in Reaper)",
                  "done_when": "two episodes edited from the template, with setup and editing times recorded next to the previous two",
                  "stop_condition": "stop and remove it if the .RPP references any third-party plugin or script, setup time does not drop by a few minutes per episode, or the inserted high-pass/de-esser audibly worsens the voices",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```