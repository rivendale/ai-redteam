VERDICT: try. EditClock is free with no account and keeps its data local, so it can measure editing time per episode for goal 1 at no cost and without breaking any rule; a short trial will show whether it tracks Reaper accurately.

WHAT IT IS: EditClock, a macOS menu-bar app (freeware, commercial use allowed). Free tier at $0 with no account and no limits, read from its terms page as captured on 2026-10-09. I worked from that saved snapshot (`work/snapshot.md`, `work/meta.json`), not a live read. There is an optional paid support plan at $60/year, which the app does not need.

CLAIMS CHECKED:
- **"Free for podcasters"** (the sender's words): CONFIRMED, and broader than that. The terms say "free for personal and commercial use, with no account and no limits." A podcast with a commercial side is covered. *Load-bearing.*
- **No account needed:** CONFIRMED by the terms ("no account"). *Load-bearing.*
- **Works with Reaper:** PROBABLE. The terms say "Works with any editor that saves a project file, Reaper included." This is the vendor's word, and the snapshot has no test or demo. It is plausible because the app tracks the front window and the project file. *Load-bearing; the trial checks it.*
- **Counts time only while the project window is in front and there was input in the last two minutes:** UNVERIFIED. This is the vendor's description, and a closed app can't be checked from text. It matters for accuracy but not for whether to trial it.
- **Everything stays on your Mac; nothing is sent anywhere:** UNVERIFIED. The vendor states it, but the app is closed freeware, so the snapshot can't settle it. It is not load-bearing, because the app sees editor window and project names, not listener or subscriber data.
- **Signed and notarized:** UNVERIFIED. The vendor states it; macOS Gatekeeper will show whether it is true at install.

FIT:
- **Goal:** Goal 1 (cut editing to under 2 hours per episode). It gives a baseline of editing time per episode and per week, which you need before you can show any cut. One limit: it reports total time per project, not which tasks use it. It won't tell you whether silences, filler words or something else take the time. Per-task detail would need manual notes alongside it.
- **Overlap:** None. Nothing in use tracks time. Reaper, ffmpeg, loudness.py and the others do other jobs.
- **Burden:** One app install on the Mac mini and one Accessibility permission grant. No account and no daily steps once it runs.
- **Cost:** $0, free tier, no limits, commercial use allowed (read 2026-10-09). The optional $60/year support is not needed. Buying it would need the host's approval, because the budget is $0 unless approved.
- **Risks:** The Accessibility permission lets it see the front window, which is a broad permission for a closed app. The local-only claim is unverified. There is no account, so no lock-in. It is freeware, and the license rules only cover code that ships on the show site, so they don't apply here.

NEXT ACTION: The editor installs EditClock on the Mac mini (checking that Gatekeeper accepts it as notarized) and leaves it running through the next 2 episodes.
- **Done when:** It shows a time per episode project that roughly matches the editor's own estimate for each edit.
- **Stop condition:** Remove it if it doesn't detect Reaper projects, if its times are clearly wrong (for example, counting idle time or missing whole sessions), if Gatekeeper flags it, or if it asks for an account or payment.
- **Hand-off:** None.

CONFIDENCE: medium. The item is resolved and the context file is present. The confidence is held back because I worked from a saved snapshot rather than a live read, Reaper support is the vendor's word only, and the closed binary means the local-only and idle-detection claims can't be verified from text.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "product",
           "identity": "EditClock macOS menu-bar app, freeware (commercial use allowed), free tier $0, no account, no limits; terms read from snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "free for podcasters (sender)", "evidence": "terms: free for personal and commercial use, no account, no limits", "status": "CONFIRMED"},
    {"claim": "no account needed", "evidence": "terms: 'with no account'", "status": "CONFIRMED"},
    {"claim": "works with Reaper", "evidence": "terms: 'any editor that saves a project file, Reaper included'; vendor statement, no test shown", "status": "PROBABLE"},
    {"claim": "counts time only while window in front and input in last two minutes", "evidence": "vendor description only; closed app", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "everything stays on your Mac, nothing sent anywhere", "evidence": "vendor statement; closed freeware, cannot inspect", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "signed and notarized", "evidence": "vendor statement; Gatekeeper will confirm at install", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1 (cut editing to under 2 hours per episode): baseline of editing time per episode; per project only, not per task",
          "overlap": "none; nothing in use tracks time",
          "burden": "one install on the Mac mini and one Accessibility permission grant; no account or daily steps",
          "risks": ["Accessibility permission lets a closed app see the front window", "local-only claim unverified", "freeware, not a site license issue", "no account, no lock-in"],
          "cost": {"price": "$0", "tier": "free", "limits": "none stated", "terms": "freeware, commercial use allowed; optional paid support $60/year not required", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Install EditClock on the Mac mini (check Gatekeeper accepts it as notarized) and leave it running through the next 2 episode edits",
                  "owner": "editor",
                  "done_when": "it shows a time per episode project that roughly matches the editor's own estimate for both edits",
                  "stop_condition": "remove it if it does not detect Reaper projects, gives clearly wrong times, is flagged by Gatekeeper, or asks for an account or payment",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```