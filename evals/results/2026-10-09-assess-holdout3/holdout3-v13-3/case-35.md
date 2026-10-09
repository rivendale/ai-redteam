VERDICT: try. It is a free MIT Reaper template that serves goal 1, because you set up every episode project by hand. It needs no account, money or new party, but it removes only the setup step, not the hand cutting that takes most of the editing time, so trial it on one episode first.

WHAT IT IS: example-org/interview-template, a public GitHub repo. I worked only from the saved snapshot (work/snapshot.md and meta.json, captured 2026-10-09), not a live read.
- License: MIT. Stars: 45. Last push: 2026-09-21. Not archived. Default branch: main.
- Last release: v1.1.0 (2026-09-21), at commit `a40e7c19d2b86f35e1c0a9748d3b5f62c1e8097b`.
- It is a single plain-text `.RPP` project template with:
  - two voice tracks, each with a high-pass and a de-esser
  - a music-and-effects track
  - a stereo bus with a loudness meter set to -16 LUFS
  - a markers track

CLAIMS CHECKED:
- **"License: MIT"**: CONFIRMED. The README and the live license field in meta.json both say MIT. *Verdict rests on this.*
- **"We set up every episode project by hand"** (the sender's words): PROBABLE. The item cannot settle this, but it fits the context file, which says everything in Reaper is done by hand and nothing is automated. *Verdict rests on this.*
- **"A template helps goal 1 (editing under 2 hours)"** (inference from the sender's words): PROBABLE, but small. A template removes the per-episode setup: making tracks, inserting the high-pass and de-esser, adding the meter. The context file says every cut, silence and filler word is made by hand, which is likely most of the time. Setup is probably minutes, and nothing in the item measures it. *Verdict rests on this.*
- **"No plugins other than Reaper's own and no scripts; one plain text .RPP file"**: UNVERIFIED. Only the README says so, and the `.RPP` itself is not in the snapshot. The trial below reads the file before copying it. *Not load-bearing.*
- **Track layout, with the bus meter at -16 LUFS**: PROBABLE. This is the README's own description, again not checked against the file. *Not load-bearing.*

FIT:
- **Goal:** Goal 1 (cut editing time), through setup only. No other goal is served.
- **Overlap:** Nothing in use provides a project template.
  - The -16 LUFS meter is the same target as loudness.py. It only displays loudness; it does not replace the normalization in loudness.py, so keep that script as the step that sets loudness.
- **Burden:** None ongoing. You copy one file into Reaper's ProjectTemplates folder once. There is no account and no service.
- **Cost:** Free, MIT, as read 2026-10-09. There are no tiers or terms beyond the license.
- **Risks:**
  - License: MIT is fine. It is a local tool, and MIT would be allowed even on the site.
  - Install path: a manual copy from a pinned release commit. There is no `curl | bash`.
  - Data: nothing leaves the machine. The README reports no telemetry or scripts, but that is not yet verified.
  - Health: a small project (45 stars), but active (pushed 2026-09-21).
  - Fit: the context file does not say the show is a two-person interview recorded on separate tracks, so the layout may not match.

NEXT ACTION:
1. The operator reads the `.RPP` at commit `a40e7c19…`.
2. They copy it into Reaper's ProjectTemplates folder on the Mac mini.
3. They start the next episode from it and note the setup time against a hand-built project.

- **Done when:** one episode has been edited from the template, and its setup time has been compared with the usual.
- **Stop if any of these happen:**
  - The file contains a script or any plugin that is not Reaper's own.
  - The track layout does not match how the show records.
  - Setup takes no less time than building the project by hand.
- **Hand-off:** none.

CONFIDENCE: medium. The context file is present and the license is confirmed. Four things limit it:
- I worked only from the snapshot.
- The `.RPP` contents are not in the snapshot.
- The context file does not state the show's recording format.
- Nothing measures how much of the editing time goes to setup.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/interview-template@a40e7c19d2b86f35e1c0a9748d3b5f62c1e8097b (MIT, 45 stars, last push 2026-09-21, not archived, default branch main; read from snapshot captured 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "License: MIT", "evidence": "README and meta.json license field (read live at capture) both say MIT", "status": "CONFIRMED"},
    {"claim": "we set up every episode project by hand (sender)", "evidence": "sender's words; consistent with the context file: everything in Reaper is done by hand, nothing automated", "status": "PROBABLE"},
    {"claim": "a template helps goal 1, cutting editing time", "evidence": "inference: removes per-episode track and plugin setup, but hand cutting is likely most of the time and nothing measures setup time", "status": "PROBABLE"},
    {"claim": "no plugins other than Reaper's own and no scripts; one plain text .RPP file", "evidence": "README only; the .RPP is not in the snapshot", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "two voice tracks with high-pass and de-esser, music track, bus with a -16 LUFS meter, markers track", "evidence": "README description, not checked against the file", "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1, cut editing time to under 2 hours per episode (setup step only)",
          "overlap": "nothing in use provides a project template; the -16 LUFS meter only displays the target loudness.py already normalizes to, it does not replace it",
          "burden": "copy one file into Reaper's ProjectTemplates folder once; no account or service",
          "risks": ["MIT, fine for a local tool and even for the site",
                    "manual copy from a pinned release commit, no curl | bash",
                    "README says no scripts or third-party plugins, unverified until the .RPP is read",
                    "small but active project (45 stars, pushed 2026-09-21)",
                    "context file does not say the show records a two-person interview on separate tracks, so the layout may not fit"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the .RPP at commit a40e7c19, copy it into Reaper's ProjectTemplates folder on the Mac mini, start the next episode from it and note setup time against a hand-built project",
                  "owner": "operator",
                  "done_when": "one episode edited from the template and its setup time compared with the usual",
                  "stop_condition": "stop if the file contains a script or a non-Reaper plugin, if its track layout does not match how the show records, or if setup takes no less time than building the project by hand",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```