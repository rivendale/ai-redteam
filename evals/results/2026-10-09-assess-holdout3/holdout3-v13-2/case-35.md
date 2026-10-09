VERDICT: try. A free MIT Reaper template could shave the per-episode project setup, which counts toward goal 1, but the template file itself is not in the snapshot and our context file does not say setup is done by hand, so trial it on one episode before switching.

WHAT IT IS: example-org/interview-template, a GitHub repo. Read from the saved snapshot captured 2026-10-09, not live:
- License: MIT (meta.json and README agree).
- Health: 45 stars, last push 2026-09-21, not archived, default branch `main`.
- Release: README names release v1.1.0 (2026-09-21) at commit `a40e7c19d2b86f35e1c0a9748d3b5f62c1e8097b`. meta.json does not record that SHA.
- Contents: the .RPP file is not in the snapshot. Only the README text was captured.

CLAIMS CHECKED:
- **Licensed MIT.** meta.json license field and README agree. CONFIRMED.
- **Maintained, last release 2026-09-21.** meta.json last_push is 2026-09-21 and it is not archived. CONFIRMED. The v1.1.0 tag itself is only in the README. Not load-bearing.
- **What the template contains.** The README says it has two voice tracks with high-pass and de-esser, a music-and-effects track, a stereo bus with a −16 LUFS meter, and a markers track. This is only the README's description; the .RPP was not captured. PROBABLE. Load-bearing.
- **No third-party plugins, no scripts, one plain-text .RPP.** This is the README's self-description, not checked against the file. PROBABLE. Load-bearing for the risk check.
- **Sender: "we set up every episode project by hand."** Our context file says every *cut* is made by hand. It says nothing about how projects are set up or whether a template exists. UNVERIFIED. Load-bearing.
- **Sender: "goal 1".** I split this:
  - Fact: goal 1 is "cut editing time to under 2 hours per episode." CONFIRMED.
  - Inference: a template serves it. PROBABLE, but only partly. A template removes setup steps. It does not touch the hand-made cuts, which our context names as the manual work.
- **Bus meter set to −16 LUFS.** This matches loudness.py's −16 LUFS target. PROBABLE, because it rests on the README. Not load-bearing.

FIT:
- **Goal:** Goal 1 (editing time), and only the setup part of it. It does not automate cuts, silences or fillers.
- **Overlap:** The −16 LUFS meter is monitoring only. loudness.py still does the normalization and the logging. Keep loudness.py; the meter does not replace it. Nothing in use provides a project template.
- **Burden:** Copy one file into Reaper's ProjectTemplates folder. No accounts, services or daily steps.
- **Cost:** Free, MIT, as read in the snapshot dated 2026-10-09. No tiers. The template runs locally and does not ship on the show site, so license rules are satisfied either way.
- **Risks:**
  - Low. Reaper-native plugins only, per the README. No scripts. No data leaves the machine.
  - The install is pinned to a specific commit rather than a moving branch, and the README says to read the file first.
  - The inserted high-pass and de-esser could change the sound compared with the current chain.
  - Small project: 45 stars.

NEXT ACTION:
- **Action:** Read the .RPP at commit a40e7c1, confirm it has only Reaper-native FX and no scripts, then copy it into ProjectTemplates and use it for the next episode. Note setup time and compare the voice sound with the last episode.
- **Owner:** Operator (the editor).
- **Done when:** One episode is edited from the template, and its setup time is compared with a hand-built project.
- **Stop condition:** Stop if setup is not noticeably faster, or if the inserted high-pass or de-esser audibly changes the voices and can't be removed.
- **Hand-off:** None. This is using a tool, not borrowing.

CONFIDENCE: medium. Three things limit it:
- The item is a saved snapshot, and the .RPP file itself was not captured.
- The template's contents rest on the README alone.
- The sender's premise that setup is done by hand is not in our context file.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "repo",
           "identity": "example-org/interview-template@a40e7c19d2b86f35e1c0a9748d3b5f62c1e8097b (MIT, 45 stars, last push 2026-09-21, not archived, default branch main; SHA from README, snapshot 2026-10-09)",
           "resolved": true},
  "claims": [
    {"claim": "licensed MIT", "evidence": "meta.json license field and README agree", "status": "CONFIRMED"},
    {"claim": "last release v1.1.0 on 2026-09-21, not archived", "evidence": "meta.json last_push 2026-09-21, archived false; tag named only in README", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "template has two voice tracks with high-pass and de-esser, an M&E track, a -16 LUFS bus meter and a markers track", "evidence": "README description only; the .RPP is not in the snapshot", "status": "PROBABLE"},
    {"claim": "no third-party plugins, no scripts, one plain-text .RPP", "evidence": "README self-description, file not read", "status": "PROBABLE"},
    {"claim": "we set up every episode project by hand (sender)", "evidence": "context file says every cut is made by hand but says nothing about project setup", "status": "UNVERIFIED"},
    {"claim": "goal 1 is cutting editing time to under 2 hours per episode", "evidence": "context file, Goals 1", "status": "CONFIRMED"},
    {"claim": "the template serves goal 1 (sender's inference)", "evidence": "a template removes setup steps but not the hand-made cuts the context names as the manual work", "status": "PROBABLE"},
    {"claim": "bus meter targets -16 LUFS, matching our loudness.py target", "evidence": "README; loudness.py normalizes to -16 LUFS per context file", "status": "PROBABLE", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1 (editing time), the setup part only; does not automate cuts",
          "overlap": "the -16 LUFS meter only monitors; loudness.py still normalizes and logs and stays; no template in use today",
          "burden": "copy one file into Reaper's ProjectTemplates folder; no accounts or services",
          "risks": ["MIT; runs locally, not shipped on the site", "Reaper-native plugins only and no scripts per README, unverified until the .RPP is read", "inserted high-pass and de-esser may change the voice sound", "small project, 45 stars, last push 2026-09-21", "install pinned to a commit, read before copying"],
          "cost": {"price": "free", "tier": "open source", "limits": "none", "terms": "MIT",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Read the .RPP at commit a40e7c1, confirm Reaper-native FX only and no scripts, copy it into ProjectTemplates and edit the next episode from it, timing setup and comparing voice sound with the last episode",
                  "owner": "operator",
                  "done_when": "one episode is edited from the template and its setup time is compared with a hand-built project",
                  "stop_condition": "stop if setup is not noticeably faster, or the inserted high-pass/de-esser audibly changes the voices and cannot be removed",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```