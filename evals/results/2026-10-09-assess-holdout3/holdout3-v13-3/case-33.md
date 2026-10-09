VERDICT: try. EditClock is free with no account and no limits, keeps its log on the Mac, and would measure editing time per episode, which goal 1 needs before the time can be cut. One open question decides whether it is worth keeping: whether its two-minute idle rule drops the time spent listening back in Reaper.

WHAT IT IS: EditClock, a macOS menu-bar time tracker (product). Its terms page was read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. Tier: free, $0. License: freeware, commercial use allowed. Optional paid support costs $60/year and is not needed to use the app. No account is needed.

CLAIMS CHECKED:
- **"Free for podcasters" (the sender's words): CONFIRMED.** The terms go further: "free for personal and commercial use, with no account and no limits". meta.json says tier free, $0. *Load-bearing.*
- **Logs time per project file while its window is in front, shown per project and per week: PROBABLE.** This is the vendor's own description, and nothing shows it in use. *Load-bearing.*
- **Works with Reaper: PROBABLE.** The terms say "any editor that saves a project file, Reaper included". There is no demo or test. *Load-bearing.*
- **Counts time only if the keyboard or mouse was used in the last two minutes: CONFIRMED as stated.** Inference (my own, not the item's): stretches of listening back to audio with hands off the keyboard and mouse for more than two minutes would not be counted. The log could therefore show less than the real editing time. *Load-bearing:* the trial below exists to test this.
- **"Everything stays on your Mac… nothing is sent anywhere": PROBABLE.** This is the vendor's statement about closed freeware, so there is no source to read. It is consistent with "no account". *Load-bearing* for the data constraint.
- **Signed and notarized: PROBABLE.** It is stated in the terms. Gatekeeper will show whether it holds when the app is downloaded. Not load-bearing.
- **Paid support is optional: CONFIRMED.** The terms say so. Not load-bearing.

FIT:
- **Goal:** Goal 1, cutting editing to under 2 hours per episode. It does not cut time itself. It gives the per-episode measurement that tells whether the goal is met and where the time goes, which is what the sender asked for.
- **Overlap:** Nothing in use tracks time. loudness.log records loudness only, and Reaper is the editor.
- **Burden:** One app to install. The Accessibility permission has to be granted once. You choose a log folder. There are no daily steps once it is running.
- **Cost:** $0, free tier, no limits, commercial use allowed (as read 2026-10-09). It needs no account, so the "no new account" and "$0 budget" constraints are not touched.
- **Risks:**
  - The Accessibility permission lets the app see the front window.
  - The app is closed freeware, so "nothing sent" rests on the vendor's word.
  - The license rule covers code that ships on the site, not a local tool, so it does not apply.
  - No listener data is involved.
  - The idle rule may undercount listening time.

NEXT ACTION: The editor installs EditClock (Gatekeeper should accept it as notarized) and runs it for the next 3 episode edits. For one of those edits, they also note the wall-clock start and end of each session.
- **Done when:** There are per-episode editing times for 3 episodes, plus one comparison between EditClock's total and the hand-noted time.
- **Stop condition:**
  - Stop and remove it if its total for the comparison episode is more than 20% below the hand-noted time, because listening time is then being dropped.
  - Also stop if macOS shows it reaching the network (for example a firewall prompt or an outbound connection).
- **Hand-off:** none. This is using a tool, not borrowing.

CONFIDENCE: high. The item is resolved from a same-day snapshot, the context file is present, and every load-bearing claim is CONFIRMED or PROBABLE. What limits it:
- The functional and privacy claims rest on the vendor's own text, not on observed behaviour.
- Whether the idle rule fits audio editing is an inference that only the trial settles.

```json
{
  "schema_version": "assess-1",
  "verdict": "try",
  "item": {"type": "product",
           "identity": "EditClock macOS menu-bar time tracker, terms page (snapshot 2026-10-09): free tier, $0, freeware, commercial use allowed, no account; optional paid support $60/year",
           "resolved": true},
  "claims": [
    {"claim": "free for podcasters (sender's words)", "evidence": "terms: free for personal and commercial use, no account, no limits; meta.json tier free, $0", "status": "CONFIRMED"},
    {"claim": "logs time per project file while its window is in front, per project and per week", "evidence": "vendor's terms text only", "status": "PROBABLE"},
    {"claim": "works with Reaper", "evidence": "terms: any editor that saves a project file, Reaper included", "status": "PROBABLE"},
    {"claim": "counts time only with keyboard or mouse use in the last two minutes", "evidence": "stated in terms; inference: hands-off listening longer than two minutes may go uncounted", "status": "CONFIRMED"},
    {"claim": "everything stays on the Mac, nothing is sent anywhere", "evidence": "vendor statement about closed freeware; consistent with no account", "status": "PROBABLE"},
    {"claim": "signed and notarized", "evidence": "stated in terms; checkable at install via Gatekeeper", "status": "PROBABLE", "load_bearing": false},
    {"claim": "paid support ($60/year) is optional", "evidence": "terms: separate and not needed to use the app", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "goal 1 (cut editing time to under 2 hours per episode): measures editing time per episode",
          "overlap": "none found: nothing in use tracks time; loudness.log records loudness only",
          "burden": "one app install, one Accessibility permission, a log folder; no daily steps",
          "risks": ["Accessibility permission lets it see the front window",
                    "closed freeware: 'nothing sent' is the vendor's word",
                    "two-minute idle rule may undercount listening time",
                    "license rule covers site code only; local tool, no listener data involved"],
          "cost": {"price": "$0", "tier": "free", "limits": "none stated", "terms": "freeware, personal and commercial use allowed, no account; optional paid support $60/year",
                   "checked_at": "2026-10-09"}},
  "next_action": {"action": "Install EditClock and run it for the next 3 episode edits, noting wall-clock start and end of each session for one of them to compare",
                  "owner": "editor (operator)",
                  "done_when": "per-episode editing times exist for 3 episodes, plus one comparison with hand-noted time",
                  "stop_condition": "stop and remove it if its total is more than 20% below the hand-noted time, or if macOS shows it reaching the network",
                  "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```